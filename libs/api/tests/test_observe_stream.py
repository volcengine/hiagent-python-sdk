# coding: utf-8
"""Synthetic SSE tests for ObserveService.__stream_request on_event callback."""
import io
import json
from unittest.mock import MagicMock, patch

import pytest

from hiagent_api.observe import ObserveService


def _fake_sse_response(lines, status_code=200):
    """Build a fake requests Response that iter_lines() yields the given lines."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.text = ""
    resp.iter_lines = MagicMock(return_value=iter(lines))
    resp.__enter__ = MagicMock(return_value=resp)
    resp.__exit__ = MagicMock(return_value=False)
    return resp


@pytest.fixture
def svc():
    # Reuse singleton; endpoint not actually used because we mock the session.
    return ObserveService(endpoint="http://127.0.0.1:1/", region="cn-north-1")


def test_stream_request_invokes_on_event_per_event(svc):
    lines = [
        "event: reasoning",
        'data: {"text":"r1"}',
        "",
        "event: content",
        'data: {"text":"c1"}',
        "",
        "event: done",
        'data: {"content":"final","latency":42,"trace_id":"t1"}',
        "",
    ]
    events = []

    def on_event(name, payload):
        events.append((name, payload))

    with patch.object(svc, "session") as session, \
         patch("hiagent_api.observe.SignerV4.sign", return_value=None):
        session.post.return_value = _fake_sse_response(lines)
        result = svc._ObserveService__stream_request(
            "TraceAIProcess",
            {"WorkspaceID": "ws", "TraceIDs": ["t"], "IsStream": True},
            on_event=on_event,
        )

    assert result == {"content": "final", "latency": 42, "trace_id": "t1"}
    assert [n for n, _ in events] == ["reasoning", "content", "done"]
    assert events[0][1] == {"text": "r1"}
    assert events[1][1] == {"text": "c1"}


def test_stream_request_error_event_raises(svc):
    lines = ["event: error", 'data: {"msg":"oops"}', ""]
    with patch.object(svc, "session") as session, \
         patch("hiagent_api.observe.SignerV4.sign", return_value=None):
        session.post.return_value = _fake_sse_response(lines)
        with pytest.raises(Exception, match="oops"):
            svc._ObserveService__stream_request(
                "TraceAIProcess",
                {"WorkspaceID": "ws", "TraceIDs": ["t"], "IsStream": True},
                on_event=None,
            )


def test_stream_request_no_on_event_still_returns_final(svc):
    lines = [
        "event: content",
        'data: {"text":"c1"}',
        "",
        "event: done",
        'data: {"content":"final","trace_id":"t1"}',
        "",
    ]
    with patch.object(svc, "session") as session, \
         patch("hiagent_api.observe.SignerV4.sign", return_value=None):
        session.post.return_value = _fake_sse_response(lines)
        result = svc._ObserveService__stream_request(
            "TraceAIProcess",
            {"WorkspaceID": "ws", "TraceIDs": ["t"], "IsStream": True},
        )
    assert result == {"content": "final", "trace_id": "t1"}


def test_trace_ai_process_stream_routes_to_stream_request(svc):
    sentinel = {"content": "ok"}
    with patch.object(svc, "_ObserveService__stream_request",
                      return_value=sentinel) as m_stream, \
         patch.object(svc, "_ObserveService__request") as m_sync:
        cb = lambda n, p: None
        out = svc.TraceAIProcess(
            {"WorkspaceID": "ws", "TraceIDs": ["t"], "IsStream": True},
            on_event=cb,
        )
        assert out is sentinel
        m_stream.assert_called_once_with(
            "TraceAIProcess",
            {"WorkspaceID": "ws", "TraceIDs": ["t"], "IsStream": True},
            on_event=cb,
        )
        m_sync.assert_not_called()


def test_trace_ai_process_no_stream_routes_to_sync(svc):
    sentinel = {"content": "ok"}
    with patch.object(svc, "_ObserveService__stream_request") as m_stream, \
         patch.object(svc, "_ObserveService__request",
                      return_value=sentinel) as m_sync:
        out = svc.TraceAIProcess({"WorkspaceID": "ws", "TraceIDs": ["t"]})
        assert out is sentinel
        m_sync.assert_called_once()
        m_stream.assert_not_called()


def test_alert_ai_process_stream_routes_to_stream_request(svc):
    sentinel = {"content": "ok"}
    with patch.object(svc, "_ObserveService__stream_request",
                      return_value=sentinel) as m_stream:
        cb = lambda n, p: None
        out = svc.AlertAIProcess(
            {"WorkspaceID": "ws", "RuleID": "r", "IsStream": True},
            on_event=cb,
        )
        m_stream.assert_called_once_with(
            "AlertAIProcess",
            {"WorkspaceID": "ws", "RuleID": "r", "IsStream": True},
            on_event=cb,
        )
