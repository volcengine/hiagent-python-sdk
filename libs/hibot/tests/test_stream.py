"""Tests for the V1SessionChatStream wrapper (accumulate / final_message)."""

from __future__ import annotations

import json

import pytest
from hibot.v1.stream import V1SessionChatStream


class _FakeResp:
    """A minimal stand-in for the httpx-backed stream response."""

    def __init__(self, chunks):
        self._chunks = list(chunks)
        self.closed = False

    def iter_bytes(self):
        for c in self._chunks:
            yield c

    def close(self):
        self.closed = True


def _sse(*frames: tuple[str, dict]) -> list[bytes]:
    out = []
    for event, data in frames:
        block = f"event: {event}\ndata: {json.dumps(data)}\n\n"
        out.append(block.encode("utf-8"))
    return out


def test_stream_accumulate_concatenates_deltas():
    chunks = _sse(
        ("message_delta", {"text": "Hel"}),
        ("message_delta", {"text": "lo "}),
        ("message_delta", {"text": "world"}),
        ("run_completed", {"message": {"ID": "m-1", "Content": "Hello world"}}),
    )
    stream = V1SessionChatStream(resp=_FakeResp(chunks))
    msg = stream.accumulate()
    assert msg.id == "m-1"
    assert msg.content == "Hello world"


def test_stream_accumulate_falls_back_to_buffered_text_when_no_message():
    chunks = _sse(
        ("message_delta", {"text": "abc"}),
        ("run_completed", {}),
    )
    stream = V1SessionChatStream(resp=_FakeResp(chunks))
    msg = stream.accumulate()
    assert msg.role == "assistant"
    assert msg.content == "abc"


def test_stream_accumulate_raises_on_failed_event():
    chunks = _sse(
        ("message_delta", {"text": "hi"}),
        ("run_failed", {"error": {"code": "X", "message": "boom"}}),
    )
    stream = V1SessionChatStream(resp=_FakeResp(chunks))
    with pytest.raises(Exception) as exc:
        stream.accumulate()
    assert "boom" in str(exc.value)


def test_stream_iterator_yields_typed_events():
    chunks = _sse(
        ("message_delta", {"text": "x"}),
        ("run_completed", {"message": {"ID": "m-2"}}),
    )
    stream = V1SessionChatStream(resp=_FakeResp(chunks))
    events = list(stream)
    types = [e.type for e in events]
    assert types == ["delta", "completed"]
    assert stream.final_message().id == "m-2"


def test_stream_init_with_error_short_circuits():
    err = ValueError("boom")
    stream = V1SessionChatStream(error=err)
    assert stream.err is err
    assert stream.next() is False
    assert list(stream) == []
