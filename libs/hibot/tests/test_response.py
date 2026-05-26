"""Tests for the TOP envelope decoder."""

from __future__ import annotations

import json

import pytest
from hibot._response import APIError, decode_top


def test_decode_top_returns_result():
    body = json.dumps(
        {
            "ResponseMetadata": {"RequestId": "req-1"},
            "Result": {"ID": "agent-1"},
        }
    ).encode("utf-8")
    result = decode_top(200, body)
    assert result == {"ID": "agent-1"}


def test_decode_top_returns_none_for_missing_result():
    body = json.dumps({"ResponseMetadata": {"RequestId": "req-2"}}).encode("utf-8")
    assert decode_top(200, body) is None


def test_decode_top_raises_on_top_error_field():
    body = json.dumps(
        {
            "ResponseMetadata": {
                "RequestId": "req-3",
                "Error": {"Code": "InvalidParameter", "Message": "bad input"},
            }
        }
    ).encode("utf-8")
    with pytest.raises(APIError) as excinfo:
        decode_top(200, body)
    assert excinfo.value.code == "InvalidParameter"
    assert excinfo.value.message == "bad input"
    assert excinfo.value.request_id == "req-3"


def test_decode_top_raises_on_http_error_status():
    body = b"Internal Server Error"
    with pytest.raises(APIError) as excinfo:
        decode_top(500, body)
    assert excinfo.value.status_code == 500


def test_decode_top_handles_empty_body_with_2xx():
    assert decode_top(200, b"") is None
