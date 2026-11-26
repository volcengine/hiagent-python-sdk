"""Real UP round trip. Opt in explicitly:

    HIAGENT_UP_E2E=1 HIAGENT_UP_UPLOAD_ENDPOINT=... HIAGENT_UP_DOWNLOAD_ENDPOINT=... \
    VOLC_ACCESSKEY=... VOLC_SECRETKEY=... uv run pytest libs/api/tests/test_up_e2e.py -q

Best run against a UP with anonymous access disabled, so signatures are checked.
"""

import hashlib
import io
import os
import uuid

import pytest
from hiagent_api import up_types
from hiagent_api.up import UpService

_REQUIRED = (
    "HIAGENT_UP_UPLOAD_ENDPOINT",
    "HIAGENT_UP_DOWNLOAD_ENDPOINT",
    "VOLC_ACCESSKEY",
    "VOLC_SECRETKEY",
)

pytestmark = [
    pytest.mark.e2e,
    pytest.mark.skipif(
        os.environ.get("HIAGENT_UP_E2E") != "1"
        or not all(os.environ.get(name) for name in _REQUIRED),
        reason="set HIAGENT_UP_E2E=1 plus " + ", ".join(_REQUIRED),
    ),
]


def _service(endpoint_env: str) -> UpService:
    service = UpService(endpoint=os.environ[endpoint_env], region="cn-north-1")
    service.set_ak(os.environ["VOLC_ACCESSKEY"])
    service.set_sk(os.environ["VOLC_SECRETKEY"])
    return service


def test_upload_long_live_download_delete(tmp_path):
    upload = _service("HIAGENT_UP_UPLOAD_ENDPOINT")
    download = _service("HIAGENT_UP_DOWNLOAD_ENDPOINT")
    content = f"hiagent-python-sdk up e2e {uuid.uuid4()}\n".encode()
    digest = hashlib.sha256(content).hexdigest()
    upload_id = f"sdk-e2e-{uuid.uuid4().hex}"
    long_live_id = f"sdk-e2e-{uuid.uuid4().hex}"
    uploaded = False
    long_lived = False

    try:
        raw = upload.UploadRaw(
            up_types.UploadRawRequest(
                Id=upload_id, ContentType="text/plain", Expire="1h", Filename="e2e.txt"
            ),
            io.BytesIO(content),
        )
        uploaded = True
        assert raw.Sha256 == digest
        assert raw.Size == len(content)
        assert raw.PresignKey is not None

        live = upload.LongLive(
            up_types.LongLiveRequest(Path=raw.Path, Id=long_live_id, Filename="e2e.txt")
        )
        long_lived = True
        assert live.Path == raw.Path

        key = upload.DownloadKey(up_types.DownloadKeyRequest(Sha256=digest.upper()))
        assert key.Size == len(content)

        target = tmp_path / "e2e.txt"
        download.Download(
            up_types.DownloadRequest(Key=key.Key, Sha256=digest, SaveTo=str(target))
        )
        assert target.read_bytes() == content
    finally:
        if long_lived:
            upload.Delete(up_types.DeleteRequest(Id=long_live_id, Sha256=digest))
        if uploaded:
            upload.Delete(up_types.DeleteRequest(Id=upload_id, Sha256=digest))
