import sys
import types
from pathlib import Path

from cli_anything.hiagent_sdk.core.services import ServiceManager
from cli_anything.hiagent_sdk.utils import hiagent_backend
from hiagent_api import up_types


def test_service_manager_uses_up_upload_and_download_endpoints(monkeypatch):
    class _DummyUpService:
        def __init__(self, endpoint: str, region: str):
            self.endpoint = endpoint
            self.region = region

    pkg = types.ModuleType("hiagent_api")
    mod = types.ModuleType("hiagent_api.up")
    mod.UpService = _DummyUpService

    monkeypatch.setitem(sys.modules, "hiagent_api", pkg)
    monkeypatch.setitem(sys.modules, "hiagent_api.up", mod)

    manager = ServiceManager(
        {
            "endpoint": "https://top.example.com",
            "region": "cn-north-1",
            "up_upload_endpoint": "https://up-upload.example.com",
            "up_download_endpoint": "https://up-download.example.com",
        }
    )

    upload = manager.get_up_upload_service()
    download = manager.get_up_download_service()

    assert upload.endpoint == "https://up-upload.example.com"
    assert download.endpoint == "https://up-download.example.com"
    assert upload is not download


def test_download_file_uses_separate_download_service(tmp_path, monkeypatch):
    monkeypatch.setattr(hiagent_backend, "ensure_volc_credentials", lambda: None)

    class _UploadSvc:
        def DownloadKey(self, params):
            return up_types.DownloadKeyResponse(Key="k")

    class _DownloadSvc:
        def Download(self, req):
            Path(req.SaveTo).write_bytes(b"ok")

    out = tmp_path / "out.bin"
    result = hiagent_backend.download_file(
        _UploadSvc(),
        path="path/to/file",
        save_to=out,
        key=None,
        up_download_service=_DownloadSvc(),
    )

    assert result["saved_to"] == str(out)
    assert out.read_bytes() == b"ok"
