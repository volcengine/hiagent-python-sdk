"""Offline fakes for UpService tests: a requests adapter that records what was
actually sent and replays canned responses."""

import hashlib
import io
import json
from datetime import datetime, timezone
from typing import Callable, List, Optional
from urllib.parse import parse_qsl, urlsplit

import requests
from hiagent_api import _up_signer
from hiagent_api.up import UpService
from requests.adapters import BaseAdapter

ENDPOINT = "https://up.example.com"
AK = "AKLTtestaccesskey"
SK = "test-secret-key"


class Sent:
    def __init__(self, prepared: requests.PreparedRequest, body: bytes):
        self.method = prepared.method
        self.url = prepared.url
        self.headers = prepared.headers
        self.body = body
        parts = urlsplit(prepared.url)
        self.path = parts.path
        self.query = dict(parse_qsl(parts.query, keep_blank_values=True))

    def json(self):
        return json.loads(self.body)


class FakeAdapter(BaseAdapter):
    def __init__(self, respond: Callable[[Sent], requests.Response]):
        super().__init__()
        self.respond = respond
        self.sent: List[Sent] = []

    def send(self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None):
        body = request.body
        if hasattr(body, "read"):
            body = body.read()
        elif body is None:
            body = b""
        elif isinstance(body, str):
            body = body.encode("utf-8")
        sent = Sent(request, bytes(body))
        self.sent.append(sent)
        response = self.respond(sent)
        response.request = request
        response.url = request.url
        return response

    def close(self):
        pass


class BrokenStream(io.RawIOBase):
    """A response body that fails after the first chunk."""

    def __init__(self, first: bytes):
        self.first = first
        self.done = False

    def readable(self):
        return True

    def read(self, size=-1):
        if not self.done:
            self.done = True
            return self.first
        raise ConnectionResetError("connection reset by peer")


def response(status=200, body=b"", headers=None, raw=None) -> requests.Response:
    resp = requests.Response()
    resp.status_code = status
    resp.headers.update(headers or {})
    resp.raw = raw if raw is not None else io.BytesIO(body)
    resp.encoding = "utf-8"
    return resp


def envelope(result) -> requests.Response:
    payload = {"ResponseMetadata": {"RequestId": "req-1"}}
    if result is not None:
        payload["Result"] = result
    return response(body=json.dumps(payload).encode("utf-8"))


def make_service(respond, *, ak=AK, sk=SK, product_code=None):
    service = UpService(endpoint=ENDPOINT, region="cn-north-1")
    service.set_ak(ak)
    service.set_sk(sk)
    service.set_session_token("")
    if product_code is not None:
        service.set_product_code(product_code)
    adapter = FakeAdapter(respond)
    service.session.mount("https://", adapter)
    return service, adapter


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def assert_signed_as_sent(sent: Sent, ak: str = AK, sk: str = SK, token: Optional[str] = None):
    """Recompute the signature from what was received, the way UP does."""
    assert sent.headers["X-Content-Sha256"] == sha256_hex(sent.body)
    x_date = sent.headers["X-Date"]
    expected = _up_signer.sign(
        sent.method,
        sent.url,
        {"X-Content-Sha256": sent.headers["X-Content-Sha256"]},
        ak=ak,
        sk=sk,
        region="cn-north-1",
        session_token=token,
        now=datetime.strptime(x_date, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc),
    )
    assert sent.headers["Authorization"] == expected["Authorization"]
