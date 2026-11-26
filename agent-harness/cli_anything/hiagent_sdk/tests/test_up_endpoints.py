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


def test_backend_helpers_work_with_real_up_service(tmp_path, monkeypatch):
    import hashlib
    import io
    import json
    from urllib.parse import parse_qsl, urlsplit

    import requests
    from hiagent_api.up import UpService
    from requests.adapters import BaseAdapter

    content = b"harness round trip"
    digest = hashlib.sha256(content).hexdigest()
    sent = []

    class _Adapter(BaseAdapter):
        def send(self, request, **kwargs):
            body = request.body.read() if hasattr(request.body, "read") else request.body
            query = dict(parse_qsl(urlsplit(request.url).query))
            sent.append((request, query, body or b""))
            resp = requests.Response()
            resp.status_code = 200
            if query["Action"] == "UploadRaw":
                payload = {"Result": {"Path": "/p", "Sha256": digest, "Size": len(content)}}
                resp.raw = io.BytesIO(json.dumps(payload).encode())
            elif query["Action"] == "DownloadKey":
                resp.raw = io.BytesIO(json.dumps({"Result": {"Key": "k"}}).encode())
            else:
                resp.headers["Content-Length"] = str(len(content))
                resp.raw = io.BytesIO(content)
            resp.request = request
            return resp

        def close(self):
            pass

    monkeypatch.setattr(hiagent_backend, "ensure_volc_credentials", lambda: None)
    service = UpService(endpoint="https://up.example.com", region="cn-north-1")
    service.set_ak("AKLTharness")
    service.set_sk("harness-secret")
    service.session.mount("https://", _Adapter())

    source = tmp_path / "in.txt"
    source.write_bytes(content)
    uploaded = hiagent_backend.upload_raw_file(service, source, file_id="cli-0001")
    assert uploaded == {"id": "cli-0001", "path": "/p", "sha256": digest, "size": len(content)}

    out = tmp_path / "out" / "file.txt"
    hiagent_backend.download_file(service, path="/p", save_to=out)
    assert out.read_bytes() == content

    assert [q["Action"] for _, q, _ in sent] == ["UploadRaw", "DownloadKey", "Download"]
    upload_request, upload_query, upload_body = sent[0]
    assert upload_body == content
    assert upload_request.headers["X-Content-Sha256"] == digest
    assert "Sha256" not in upload_query
    assert all(r.method == "POST" and "Authorization" in r.headers for r, _, _ in sent)
