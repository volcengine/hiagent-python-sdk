import time

import requests

from hiagent_observe.client import AuthSession


def test_otlp_session_adds_product_code(monkeypatch):
    captured = {}

    def fake_request(self, method, url, **kwargs):
        captured.update(kwargs)
        return requests.Response()

    monkeypatch.setattr(requests.Session, "request", fake_request)
    session = AuthSession("https://example.com", "ak", "sk", "ws", "app", " trace-a ")
    session.token = "token"
    session.expires_at = time.time() + 3600
    session.request("POST", "https://example.com/v1/traces", headers={})
    assert captured["headers"]["X-Trace-Product-Code"] == "trace-a"


def test_observe_token_model_does_not_contain_product_code():
    from hiagent_api.observe_types import CreateApiTokenRequest

    payload = CreateApiTokenRequest(WorkspaceID="ws", CustomAppID="app").model_dump()
    assert payload == {"WorkspaceID": "ws", "CustomAppID": "app"}
