"""Tests for SessionsService — peer injection + session->agent map + chat()."""

from __future__ import annotations

import json
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest
from hibot import (
    V1SessionChatParams,
    V1SessionDeleteParams,
    V1SessionNewParams,
    V1SessionPeerParams,
)


def _action(req: httpx.Request) -> str:
    return parse_qs(urlsplit(str(req.url)).query).get("Action", [""])[0]


def _version(req: httpx.Request) -> str:
    return parse_qs(urlsplit(str(req.url)).query).get("Version", [""])[0]


def test_create_session_injects_default_peer(client_factory, make_handler, ok_envelope):
    handler = make_handler([ok_envelope({"ID": "s-1"})])
    client = client_factory(handler)
    session = client.v1.sessions.create(V1SessionNewParams(agent_id="agent-1"))
    assert session.id == "s-1"
    assert session.agent_id == "agent-1"

    req = handler.calls[0]
    assert _action(req) == "CreateSession"
    body = json.loads(req.content)
    assert body["AgentID"] == "agent-1"
    assert body["WorkspaceID"] == "ws-1"
    assert body["Payload"] == {
        "Channel": "webchat",
        "PeerKind": "system",
        "PeerID": "agent-1",
    }


def test_create_session_with_explicit_peer_overrides_kind_and_id(
    client_factory, make_handler, ok_envelope
):
    handler = make_handler([ok_envelope({"ID": "s-1"})])
    client = client_factory(handler)
    client.v1.sessions.create(
        V1SessionNewParams(
            agent_id="agent-1",
            peer=V1SessionPeerParams(peer_kind="user", peer_id="u-77"),
        )
    )
    body = json.loads(handler.calls[0].content)
    assert body["Payload"] == {
        "Channel": "webchat",
        "PeerKind": "user",
        "PeerID": "u-77",
    }


def test_create_session_with_im_channel_passes_through(
    client_factory, make_handler, ok_envelope
):
    handler = make_handler([ok_envelope({"ID": "s-1"})])
    client = client_factory(handler)
    client.v1.sessions.create(
        V1SessionNewParams(
            agent_id="agent-1",
            peer=V1SessionPeerParams(
                channel="feishu", peer_kind="user", peer_id="ou_xxx"
            ),
        )
    )
    body = json.loads(handler.calls[0].content)
    assert body["Payload"] == {
        "Channel": "feishu",
        "PeerKind": "user",
        "PeerID": "ou_xxx",
    }


def test_chat_uses_remembered_agent_id_and_routes_to_gateway(
    client_factory, make_handler, ok_envelope, sse
):
    sse_body = (
        b'event: message_delta\n'
        b'data: {"text":"hel"}\n\n'
        b'event: message_delta\n'
        b'data: {"text":"lo"}\n\n'
        b'event: run_completed\n'
        b'data: {"message":{"ID":"m-9","Role":"assistant","Content":"hello"}}\n\n'
    )
    create_reply = ok_envelope({"ID": "s-1"})
    chat_reply = sse(sse_body)
    handler = make_handler([create_reply, chat_reply])
    client = client_factory(handler)

    session = client.v1.sessions.create(V1SessionNewParams(agent_id="agent-1"))
    msg = client.v1.sessions.chat(session.id, V1SessionChatParams(input="hi"))
    assert msg.id == "m-9"
    assert msg.content == "hello"

    chat_req = handler.calls[1]
    assert _action(chat_req) == "Chat"
    assert _version(chat_req) == "2026-05-11"
    body = json.loads(chat_req.content)
    # AgentID resolved from internal map (was not provided in params)
    assert body["AgentID"] == "agent-1"
    assert body["SessionID"] == "s-1"
    assert body["Content"] == "hi"
    assert body["WorkspaceID"] == "ws-1"


def test_chat_streaming_yields_events_in_order(
    client_factory, make_handler, ok_envelope, sse
):
    sse_body = (
        b'event: message_delta\n'
        b'data: {"text":"a"}\n\n'
        b'event: message_delta\n'
        b'data: {"text":"b"}\n\n'
        b'event: run_completed\n'
        b'data: {"message":{"ID":"m-1","Content":"ab"}}\n\n'
    )
    handler = make_handler(
        [
            ok_envelope({"ID": "s-1"}),
            sse(sse_body),
        ]
    )
    client = client_factory(handler)
    client.v1.sessions.create(V1SessionNewParams(agent_id="agent-1"))

    events = []
    with client.v1.sessions.chat_streaming(
        "s-1", V1SessionChatParams(input="ping")
    ) as stream:
        for evt in stream:
            events.append((evt.type, evt.delta.text))
        final = stream.final_message()

    assert events == [("delta", "a"), ("delta", "b"), ("completed", "")]
    assert final.id == "m-1"


def test_chat_streaming_propagates_http_error(client_factory, make_handler, ok_envelope, sse):
    handler = make_handler(
        [
            ok_envelope({"ID": "s-1"}),
            sse(b"boom", status=500),
        ]
    )
    client = client_factory(handler)
    client.v1.sessions.create(V1SessionNewParams(agent_id="agent-1"))
    with client.v1.sessions.chat_streaming(
        "s-1", V1SessionChatParams(input="x")
    ) as stream:
        assert stream.err is not None
        assert getattr(stream.err, "status_code", None) == 500


def test_delete_session_requires_id(client_factory, make_handler):
    handler = make_handler([])
    client = client_factory(handler)
    with pytest.raises(ValueError):
        client.v1.sessions.delete(V1SessionDeleteParams(session_id=""))
