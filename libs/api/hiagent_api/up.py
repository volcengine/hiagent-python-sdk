# coding:utf-8
# Copyright (c) 2024 Bytedance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import contextlib
import hashlib
import json
import os
import shutil
import stat
import uuid
from typing import Any, BinaryIO, Dict, Optional, Tuple
from urllib.parse import urlparse

import requests
from requests.structures import CaseInsensitiveDict
from volcengine import VERSION as VOLC_SDK_VERSION
from volcengine.ApiInfo import ApiInfo
from volcengine.base.Service import Service
from volcengine.Credentials import Credentials
from volcengine.ServiceInfo import ServiceInfo

from hiagent_api import _up_signer, up_types
from hiagent_api.product_code import PRODUCT_CODE_HEADER, normalize_product_code

_API_VERSION = "2022-01-01"
_JSON = "application/json"
_OCTET_STREAM = "application/octet-stream"
_EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()
_CHUNK_SIZE = 64 * 1024


class UpService(Service):
    """Client for the UP (upload) service.

    Every request is a POST signed in headers by ``_up_signer`` from the exact
    method, URL and ``X-Content-Sha256`` that go on the wire. Without any
    AK/SK configured, requests are sent unsigned and the UP deployment decides
    whether to serve them.
    """

    def __init__(self, endpoint="https://open.volcengineapi.com", region="cn-north-1"):
        self.service_info = UpService.get_service_info(endpoint, region)
        self.api_info = UpService.get_api_info()
        super(UpService, self).__init__(self.service_info, self.api_info)

    def set_product_code(self, product_code):
        product_code = normalize_product_code(product_code)
        if product_code:
            self.service_info.header[PRODUCT_CODE_HEADER] = product_code
        else:
            self.service_info.header.pop(PRODUCT_CODE_HEADER, None)
        self.product_code = product_code
        return self

    def get_product_code(self):
        return getattr(self, "product_code", None)

    @staticmethod
    def get_service_info(endpoint, region):
        parsed = urlparse(endpoint)
        scheme = parsed.scheme
        hostname = parsed.hostname or ""
        if parsed.port:
            hostname = f"{hostname}:{parsed.port}"
        if not scheme or not hostname:
            raise Exception(f"invalid endpoint format: {endpoint}")
        service_info = ServiceInfo(
            hostname,
            {"Accept": "application/json"},
            Credentials("", "", "up", region),
            5,
            5,
            scheme=scheme,
        )
        return service_info

    @staticmethod
    def get_api_info():
        def api(path: str, action: str) -> ApiInfo:
            return ApiInfo("POST", path, {"Action": action, "Version": _API_VERSION}, {}, {})

        return {
            "UploadRaw": api("/up", "UploadRaw"),
            "LongLive": api("/up", "LongLive"),
            "DownloadKey": api("/up", "DownloadKey"),
            "Download": api("/down", "Download"),
            "Delete": api("/up", "Delete"),
        }

    def UploadRaw(
        self, params: up_types.UploadRawRequest, file: BinaryIO
    ) -> up_types.UploadRawResponse:
        """不分片上传文件，UP 会同时完成长期化。

        Args:
            params: `Id` 必填；`Sha256` 不传或为空白时 SDK 先从文件当前位置流式
                计算一遍（此时文件对象必须可 seek）；`ContentType` 不传时按
                application/octet-stream 上传；`Expire`、`Filename`、`ImageCompress` 可选。
            file: 文件对象，从当前位置读到末尾，流式发送。

        Returns:
            UploadRawResponse: `Path`、`Sha256`、`Size`、`ShortLink`、`PresignKey`。
        """
        _require(params.Id, "UploadRawRequest.Id")
        self._credentials()
        content_sha256 = _normalize_sha256(params.Sha256) or _sha256_from_here(file)
        query = {
            "Expire": params.Expire,
            "Id": params.Id,
            "Filename": params.Filename,
            "ImageCompress": params.ImageCompress,
        }
        content_type = params.ContentType or _OCTET_STREAM
        resp = self._send("UploadRaw", query, file, content_type, content_sha256)
        return up_types.UploadRawResponse.model_validate(_result(resp))

    def LongLive(self, params: up_types.LongLiveRequest) -> up_types.LongLiveResponse:
        """将某个文件转换成长效存储的文件。

        Args:
            params: `Path`、`Id` 必填（请求体中以 `ID` 发送），`Filename` 可选。

        Returns:
            LongLiveResponse: `Path`、`Size`、`Sha256`、`ShortLink`。
        """
        _require(params.Id, "LongLiveRequest.ID")
        resp = self._send_json("LongLive", params.model_dump(by_alias=True, exclude_none=True))
        return up_types.LongLiveResponse.model_validate(_result(resp))

    def DownloadKey(
        self, params: up_types.DownloadKeyRequest
    ) -> up_types.DownloadKeyResponse:
        """获取下载文件用的 Key。

        Args:
            params: `Path` 与 `Sha256` 二选一。

        Returns:
            DownloadKeyResponse: `Key`、`Size`、`ContentType`。
        """
        query = {"Path": params.Path, "Sha256": _normalize_sha256(params.Sha256)}
        resp = self._send("DownloadKey", query, b"", _JSON, _EMPTY_SHA256)
        return up_types.DownloadKeyResponse.model_validate(_result(resp))

    def Download(self, params: up_types.DownloadRequest) -> None:
        """下载文件到 `SaveTo`。

        先写入同目录下的临时文件，完整收到后再原子替换目标；失败时不留下临时
        文件，也不改动已有的目标文件。参数都放在 query 中（`SaveTo` 除外），
        与 UP 按 query 中的 `Key` 放行下载的方式一致。

        Args:
            params: `Key`、`SaveTo` 必填；`Path` 与 `Sha256` 二选一；
                `ID`、`Filename`、`ImageCompress` 可选。
        """
        if not params.SaveTo or not params.SaveTo.strip():
            raise ValueError("DownloadRequest.SaveTo must be set")
        target = _download_target(params.SaveTo)
        # SaveTo is excluded from model_dump, so the dump is exactly the query.
        query = {
            **params.model_dump(by_alias=True, exclude_none=True),
            "Sha256": _normalize_sha256(params.Sha256),
        }
        with self._send("Download", query, b"", _JSON, _EMPTY_SHA256, stream=True) as resp:
            _check_status(resp)
            _save_atomically(resp, target)

    def Delete(self, params: up_types.DeleteRequest) -> Dict[str, Any]:
        """删除文件的一条关联；关联全部删除后文件在下次回收时删除。

        Args:
            params: `Id`、`Sha256` 必填。

        Returns:
            UP 返回的 `Result`（成功时为空 dict）。
        """
        body = params.model_dump(by_alias=True, exclude_none=True)
        body["Sha256"] = _normalize_sha256(body.get("Sha256"))
        return _result(self._send_json("Delete", body))

    def _send_json(self, action: str, body: Dict[str, Any]) -> requests.Response:
        payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
        return self._send(action, {}, payload, _JSON, hashlib.sha256(payload).hexdigest())

    def _send(
        self,
        action: str,
        query: Dict[str, Any],
        body: Any,
        content_type: str,
        content_sha256: str,
        stream: bool = False,
    ) -> requests.Response:
        api_info = self.api_info[action]
        url = (
            f"{self.service_info.scheme}://{self.service_info.host}{api_info.path}"
            f"?{_encode_query({**api_info.query, **query})}"
        )
        headers = CaseInsensitiveDict(self.service_info.header)
        headers["Content-Type"] = content_type
        headers[_up_signer.HEADER_CONTENT_SHA256] = content_sha256
        headers["User-Agent"] = f"volc-sdk-python/{VOLC_SDK_VERSION}"

        credentials = self._credentials()
        if credentials is not None:
            ak, sk, token = credentials
            signing_headers = _up_signer.sign(
                api_info.method,
                url,
                content_sha256,
                ak=ak,
                sk=sk,
                region=self.service_info.credentials.region,
                session_token=token,
            )
            headers.update(signing_headers)
        return self.session.request(
            api_info.method,
            url,
            headers=headers,
            data=body,
            timeout=(
                self.service_info.connection_timeout,
                self.service_info.socket_timeout,
            ),
            stream=stream,
            # A redirect would resend the request with a signature for the old
            # URL (as GET for 301/302) and carry X-Security-Token to another host.
            allow_redirects=False,
        )

    def _credentials(self) -> Optional[Tuple[str, str, str]]:
        """None when no AK, SK or STS token is configured (send unsigned);
        raises ValueError for half-configured or malformed credentials."""
        credentials = self.service_info.credentials
        if (
            _is_blank(credentials.ak)
            and _is_blank(credentials.sk)
            and _is_blank(credentials.session_token)
        ):
            return None
        return _up_signer.check_credentials(
            credentials.ak, credentials.sk, credentials.session_token
        )


def _encode_query(params: Dict[str, Any]) -> str:
    pairs = []
    for name, value in params.items():
        if value is None:
            continue
        if isinstance(value, bool):
            value = "true" if value else "false"
        pairs.append(f"{_up_signer.sign_encode(name)}={_up_signer.sign_encode(str(value))}")
    return "&".join(pairs)


def _check_status(resp: requests.Response) -> None:
    if resp.status_code == 200:
        return
    if resp.is_redirect:
        raise Exception(
            f"UP answered HTTP {resp.status_code} redirecting to "
            f"{resp.headers['Location']}; redirects are not followed, "
            "check the endpoint"
        )
    raise Exception(resp.text or f"UP answered HTTP {resp.status_code}")


def _result(resp: requests.Response) -> Any:
    _check_status(resp)
    data = resp.json()
    if not isinstance(data, dict) or "Result" not in data:
        raise Exception(f"no Result in response: {resp.text}")
    return data["Result"]


def _require(value: Optional[str], name: str) -> None:
    # Same test as UP's validate:"required": only None and "" are rejected.
    if value is None or value == "":
        raise ValueError(f"{name} must be set")


def _is_blank(value: Optional[str]) -> bool:
    return not value or not value.strip()


def _normalize_sha256(value: Optional[str]) -> Optional[str]:
    if _is_blank(value):
        return None
    return value.strip().lower()


def _sha256_from_here(file: BinaryIO) -> str:
    """Hash the file from its current position to the end, then seek back so
    the upload sends exactly the hashed bytes."""
    try:
        seekable = file.seekable()
    except Exception:
        seekable = False
    if not seekable:
        raise ValueError(
            "UploadRawRequest.Sha256 must be set when the file object cannot seek"
        )
    start = file.tell()
    digest = hashlib.sha256()
    for chunk in iter(lambda: file.read(_CHUNK_SIZE), b""):
        digest.update(chunk)
    file.seek(start)
    return digest.hexdigest()


def _download_target(save_to: str) -> str:
    """Resolve SaveTo and reject what an atomic replace must not touch, before
    anything is downloaded."""
    # realpath: a symlinked SaveTo gets its target replaced, as open(SaveTo) did.
    target = os.path.realpath(save_to)
    try:
        mode = os.stat(target).st_mode
    except FileNotFoundError:
        return target
    if stat.S_ISDIR(mode):
        raise IsADirectoryError(f"DownloadRequest.SaveTo is a directory: {save_to}")
    if not stat.S_ISREG(mode):
        # Replacing a device or FIFO (e.g. /dev/null as root) would swap the
        # node itself for a regular file.
        raise ValueError(f"DownloadRequest.SaveTo is not a regular file: {save_to}")
    return target


def _save_atomically(resp: requests.Response, target: str) -> None:
    directory = os.path.dirname(target)
    temp = os.path.join(directory, f".{os.path.basename(target)}.{uuid.uuid4().hex}.part")
    exists = os.path.exists(target)
    # Overwriting: stay private until the old mode is copied over, so a 0600
    # file's content is never readable through the partial file. New file:
    # 0o666 & ~umask, like open().
    mode = 0o600 if exists else 0o666
    # Outside the try: on a name collision there is nothing of ours to remove.
    out = open(temp, "xb", opener=lambda path, flags: os.open(path, flags, mode))
    try:
        written = 0
        with out:
            for chunk in resp.iter_content(chunk_size=_CHUNK_SIZE):
                out.write(chunk)
                written += len(chunk)
        _check_length(resp, written)
        if exists:
            shutil.copymode(target, temp)
        os.replace(temp, target)
    except BaseException:
        with contextlib.suppress(FileNotFoundError):
            os.remove(temp)
        raise


def _check_length(resp: requests.Response, written: int) -> None:
    """urllib3 1.26 does not enforce Content-Length, so a short read would
    otherwise be installed as a complete download."""
    declared = resp.headers.get("Content-Length")
    if declared is None or "Content-Encoding" in resp.headers:
        return
    if written != int(declared):
        raise Exception(
            f"download incomplete: received {written} bytes, Content-Length is {declared}"
        )
