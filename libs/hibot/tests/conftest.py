"""Shared pytest fixtures."""

from __future__ import annotations

import json
from typing import Any, List

import hibot
import httpx
import pytest


def sse_response(body: bytes, status: int = 200) -> httpx.Response:
    """Build a streaming SSE response that survives `client.stream(...)`.

    httpx.Response(content=bytes) marks the stream as consumed; for streaming
    responses we must wrap the bytes in a fresh ByteStream.
    """
    return httpx.Response(
        status,
        stream=httpx.ByteStream(body),
        headers={"content-type": "text/event-stream"},
    )


def _ok_envelope(result):
    return json.dumps(
        {"ResponseMetadata": {"RequestId": "req-test"}, "Result": result}
    ).encode("utf-8")


def _err_envelope(code: str, message: str):
    return json.dumps(
        {
            "ResponseMetadata": {
                "RequestId": "req-err",
                "Error": {"Code": code, "Message": message},
            }
        }
    ).encode("utf-8")


class RecordingHandler:
    """Records each HTTP request and replies with a queue of canned responses."""

    def __init__(self, replies: List[Any] = None) -> None:
        self.calls: list = []
        self.replies = list(replies or [])

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.calls.append(request)
        if not self.replies:
            return httpx.Response(200, content=_ok_envelope({}))
        reply = self.replies.pop(0)
        if isinstance(reply, httpx.Response):
            return reply
        if isinstance(reply, (bytes, bytearray)):
            return httpx.Response(200, content=bytes(reply))
        if isinstance(reply, dict):
            return httpx.Response(200, content=_ok_envelope(reply))
        if callable(reply):
            return reply(request)
        raise TypeError(f"unsupported reply: {reply!r}")


def make_client(handler: RecordingHandler, **overrides) -> hibot.Client:
    transport = httpx.MockTransport(handler)
    http_client = httpx.Client(transport=transport)
    cfg = hibot.Config(
        endpoint=overrides.pop("endpoint", "https://open.volcengineapi.com"),
        access_key=overrides.pop("access_key", "AKLTtest"),
        secret_key=overrides.pop("secret_key", "secret-key"),
        workspace_id=overrides.pop("workspace_id", "ws-1"),
        http_client=http_client,
        **overrides,
    )
    return hibot.Hibot(cfg)


@pytest.fixture
def ok_envelope():
    return _ok_envelope


@pytest.fixture
def err_envelope():
    return _err_envelope


@pytest.fixture
def make_handler():
    return RecordingHandler


@pytest.fixture
def client_factory():
    return make_client


@pytest.fixture
def sse():
    return sse_response
