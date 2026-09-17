import httpx
import pytest

from hiagent_api.chat import ChatService
from hiagent_api.observe import ObserveService
from hiagent_api.product_code import PRODUCT_CODE_HEADER, normalize_product_code


def test_app_api_adds_product_code_and_explicit_header_wins():
    seen = []

    def handler(request: httpx.Request):
        seen.append(request)
        return httpx.Response(200, json={"ok": True})

    service = ChatService(endpoint="https://example.com", region="cn-north-1")
    service.set_app_base_url("https://example.com/api")
    service.http_client = httpx.Client(transport=httpx.MockTransport(handler))
    service.set_product_code(" configured ")
    service._post("app-key", "create_conversation", {}, {PRODUCT_CODE_HEADER: "explicit"})
    assert seen[-1].headers[PRODUCT_CODE_HEADER] == "explicit"
    service._post("app-key", "create_conversation", {})
    assert seen[-1].headers[PRODUCT_CODE_HEADER] == "configured"


def test_signed_service_includes_product_code_before_signing():
    service = ObserveService(endpoint="https://example.com", region="cn-north-1")
    service.set_product_code("maas")
    request = service.prepare_request(service.api_info["CreateApiToken"], {})
    assert request.headers[PRODUCT_CODE_HEADER] == "maas"


def test_product_code_validation():
    assert normalize_product_code("  ") is None
    with pytest.raises(ValueError):
        normalize_product_code("bad\r\nvalue")
