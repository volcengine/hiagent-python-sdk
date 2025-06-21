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
import json
from typing import BinaryIO
from urllib.parse import urlparse

from volcengine.ApiInfo import ApiInfo
from volcengine.auth.SignerV4 import SignerV4
from volcengine.base.Service import Service
from volcengine.Credentials import Credentials
from volcengine.ServiceInfo import ServiceInfo

from hiagent_api import up_types


class UpService(Service):
    def __init__(self, endpoint="https://open.volcengineapi.com", region="cn-north-1"):
        self.service_info = UpService.get_service_info(endpoint, region)
        self.api_info = UpService.get_api_info()
        super(UpService, self).__init__(self.service_info, self.api_info)

    @staticmethod
    def get_service_info(endpoint, region):
        parsed = urlparse(endpoint)
        scheme, hostname = parsed.scheme, parsed.hostname + ":" + str(parsed.port)
        if not scheme or not hostname:
            raise Exception(f"invalid endpoint format: {endpoint}")
        service_info = ServiceInfo(
            hostname,
            {"Accept": "application/json"},
            Credentials("", "", "observe", region),
            5,
            5,
            scheme=scheme,
        )
        return service_info

    @staticmethod
    def get_api_info():
        api_info = {
            "UploadRaw": ApiInfo(
                "POST", "/up", {"Action": "UploadRaw", "Version": "2022-01-01"}, {}, {}
            ),
            "LongLive": ApiInfo(
                "POST", "/up", {"Action": "LongLive", "Version": "2022-01-01"}, {}, {}
            ),
            "DownloadKey": ApiInfo(
                "POST",
                "/up",
                {"Action": "DownloadKey", "Version": "2022-01-01"},
                {},
                {},
            ),
            "Download": ApiInfo(
                "POST", "/down", {"Action": "Download", "Version": "2022-01-01"}, {}, {}
            ),
            "Delete": ApiInfo(
                "POST", "/up", {"Action": "Delete", "Version": "2022-01-01"}, {}, {}
            ),
        }
        return api_info

    def UploadRaw(
        self, params: up_types.UploadRawRequest, file: BinaryIO
    ) -> up_types.UploadRawResponse:
        """不分片的上传接口

        Args:
            params (Dict):

                `File (BinaryIO)`: 必选, 文件流
                `Id (str)`: 必选, 文件 ID
                `ContentType (str)`: 可选, 文件类型
                `Expire (str)`: 可选, 文件过期时间，格式为 15h

        Returns:
            Dict:

                `Path (str)`: 文件路径
                    示例值: path/to/file

                `Sha256 (str)`: 文件的哈希值
                    示例值: xxxx

                `Size (int)`: 文件的大小，单位为字节
                    示例值: 1024

        """
        api = "UploadRaw"
        if api not in self.api_info:
            raise Exception("no such api")
        api_info = self.api_info[api]
        r = self.prepare_request(api_info, params.model_dump())
        if params.ContentType != "":
            r.headers["Content-Type"] = params.ContentType
        else:
            r.headers["Content-Type"] = "application/octet-stream"
        r.headers["X-Content-Sha256"] = params.Sha256
        SignerV4.sign_url(r, self.service_info.credentials)

        url = r.build()

        resp = self.session.post(
            url,
            headers=r.headers,
            data=file,
            timeout=(
                self.service_info.connection_timeout,
                self.service_info.socket_timeout,
            ),
        )
        if resp.status_code == 200:
            res_json = json.loads(resp.text)
            if "Result" not in res_json.keys():
                Exception(f"no Result in response: {resp.text}")
            return up_types.UploadRawResponse.model_validate(res_json["Result"])
        else:
            raise Exception(resp.text)

    def LongLive(self, params: up_types.LongLiveRequest) -> up_types.LongLiveResponse:
        """将某个文件转换成长效存储的文件。

        Args:
            params (Dict):

                `Path (str)`: 文件路径
                    示例值: path/to/file

                `Id (str)`: 必选, 文件 ID

        Returns:
            Dict:

                `Path (str)`: 文件路径
                    示例值: path/to/file

                `Size (int)`: 文件的大小，单位为字节
                    示例值: 1024

        """
        return up_types.LongLiveResponse.model_validate(
            self.__request("LongLive", params.model_dump())
        )

    def DownloadKey(
        self, params: up_types.DownloadKeyRequest
    ) -> up_types.DownloadKeyResponse:
        """将某个文件转换成长效存储的文件。

        Args:
            params (Dict):

                `Path (str)`: 文件路径
                    示例值: path/to/file

        Returns:
            Dict:

                `Key (str)`: 文件下载时可用的 key
                    示例值: xxxx

        """
        api = "DownloadKey"
        res = self.get(api, params.model_dump(), dict())
        if res == "":
            raise Exception("empty response")
        res_json = json.loads(res)
        if "Result" not in res_json.keys():
            Exception(f"no Result in response: {res}")
        return up_types.DownloadKeyResponse.model_validate(res_json["Result"])

    def Download(self, params: up_types.DownloadRequest) -> up_types.DownloadResponse:
        """下载某个文件

        Args:
            params (Dict):

                `Path (str)`: 文件路径
                    示例值: path/to/file

                `Key (str)`: 文件下载时可用的 key
                    示例值: xxxx

                `SaveTo (str)`: 文件保存路径`
        Returns:
            Dict:
        """
        api = "Download"
        if api not in self.api_info:
            raise Exception("no such api")
        api_info = self.api_info[api]

        r = self.prepare_request(api_info, params.model_dump(), 0)

        SignerV4.sign(r, self.service_info.credentials)

        url = r.build(0)
        resp = self.session.get(
            url,
            headers=r.headers,
            timeout=(
                self.service_info.connection_timeout,
                self.service_info.socket_timeout,
            ),
            stream=True,
        )
        if resp.status_code == 200:
            with open(params.SaveTo, "wb") as f:
                for chunk in resp.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
        else:
            raise Exception(resp.text)

    def Delete(self, params: up_types.DeleteRequest) -> up_types.DeleteResponse:
        """删除某个文件

        Args:
            params (Dict):

                `Id (str)`: 必选, 文件 ID

                `Sha256 (str)`: 文件的哈希值
                    示例值: xxxx

        Returns:
            Dict:
        """
        return self.__request("Delete", params.model_dump())

    def __request(self, action, params):
        res = self.json(action, dict(), json.dumps(params))
        if res == "":
            raise Exception("empty response")
        res_json = json.loads(res)
        if "Result" not in res_json.keys():
            return res_json
        return res_json["Result"]
