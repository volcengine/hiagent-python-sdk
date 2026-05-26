"""Tests for SSE decoder + chat event normalization."""

from __future__ import annotations

import json

from hibot._sse import ByteStreamDecoder, iter_frames
from hibot.v1.stream import (
    decode_chat_event,
    normalize_chat_event_name,
)
from hibot.v1.types import (
    V1_SESSION_CHAT_EVENT_COMPLETED,
    V1_SESSION_CHAT_EVENT_DELTA,
    V1_SESSION_CHAT_EVENT_FAILED,
    V1_SESSION_CHAT_EVENT_TOOL_COMPLETE,
    V1_SESSION_CHAT_EVENT_TOOL_START,
)


def test_iter_frames_decodes_basic():
    payload = (
        ":heartbeat\n"
        "event: message_delta\n"
        'data: {"text":"hi"}\n'
        "\n"
        "event: run_completed\n"
        'data: {"message":{"ID":"m-1"}}\n'
        "\n"
    )
    frames = list(iter_frames(payload.split("\n")))
    assert len(frames) == 2
    assert frames[0].event == "message_delta"
    assert json.loads(frames[0].data)["text"] == "hi"
    assert frames[1].event == "run_completed"


def test_byte_stream_decoder_incremental():
    decoder = ByteStreamDecoder()
    decoder.feed(b"event: message_delta\n")
    decoder.feed(b'data: {"text":')
    decoder.feed(b'"abc"}\n\n')
    frames = decoder.pop_frames()
    assert len(frames) == 1
    assert frames[0].event == "message_delta"
    assert json.loads(frames[0].data) == {"text": "abc"}


def test_normalize_chat_event_name_legacy_aliases():
    assert normalize_chat_event_name("message.chunk") == V1_SESSION_CHAT_EVENT_DELTA
    assert normalize_chat_event_name("message_delta") == V1_SESSION_CHAT_EVENT_DELTA
    assert normalize_chat_event_name("message_chunk") == V1_SESSION_CHAT_EVENT_DELTA
    assert (
        normalize_chat_event_name("message.completed")
        == V1_SESSION_CHAT_EVENT_COMPLETED
    )
    assert (
        normalize_chat_event_name("run_completed") == V1_SESSION_CHAT_EVENT_COMPLETED
    )
    assert normalize_chat_event_name("run_failed") == V1_SESSION_CHAT_EVENT_FAILED
    assert normalize_chat_event_name("tool_started") == V1_SESSION_CHAT_EVENT_TOOL_START
    assert (
        normalize_chat_event_name("tool_completed") == V1_SESSION_CHAT_EVENT_TOOL_COMPLETE
    )
    # passthrough
    assert normalize_chat_event_name("delta") == V1_SESSION_CHAT_EVENT_DELTA
    assert normalize_chat_event_name("approval_request") == "approval_request"


def test_decode_chat_event_extracts_delta_text():
    event = decode_chat_event("message_delta", json.dumps({"delta": {"text": "hello"}}))
    assert event.type == V1_SESSION_CHAT_EVENT_DELTA
    assert event.delta.text == "hello"


def test_decode_chat_event_extracts_completed_message():
    data = json.dumps(
        {
            "message": {"ID": "m-1", "Role": "assistant", "Content": "ok"},
            "request_id": "req-x",
        }
    )
    event = decode_chat_event("run_completed", data)
    assert event.type == V1_SESSION_CHAT_EVENT_COMPLETED
    assert event.request_id == "req-x"
    assert event.message is not None
    assert event.message.id == "m-1"
    assert event.message.content == "ok"


def test_decode_chat_event_extracts_failed_error():
    data = json.dumps({"error": {"code": "Boom", "message": "explode"}})
    event = decode_chat_event("run_failed", data)
    assert event.type == V1_SESSION_CHAT_EVENT_FAILED
    assert event.error.code == "Boom"
    assert event.error.message == "explode"


def test_decode_chat_event_falls_back_to_top_level_message_id():
    data = json.dumps({"message_id": "m-2", "content": "fallback"})
    event = decode_chat_event("completed", data)
    assert event.type == V1_SESSION_CHAT_EVENT_COMPLETED
    assert event.message is not None
    assert event.message.id == "m-2"
    assert event.message.content == "fallback"
