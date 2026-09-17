import pytest

from hibot._config import Config
from hibot._request import Action, Requester
from hibot._signer import SIGNED_HEADERS_INCLUDE


def test_product_code_is_sent_and_signed():
    config = Config("https://example.com", "ak", "sk", "ws", product_code=" product-a ")
    requester = Requester(config)
    _, headers = requester._build_request(Action("hibot-server", "2025-01-01", "ListAgents"), b"{}", "application/json", None)
    assert headers["X-Trace-Product-Code"] == "product-a"
    assert "x-trace-product-code" in SIGNED_HEADERS_INCLUDE
    requester.close()


def test_blank_or_control_product_code():
    config = Config("https://example.com", "ak", "sk", "ws", product_code=" ")
    assert config.product_code is None
    with pytest.raises(ValueError):
        Config("https://example.com", "ak", "sk", "ws", product_code="bad\nvalue")
