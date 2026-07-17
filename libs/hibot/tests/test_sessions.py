"""Tests for SessionsService — peer injection + session->agent map + chat()."""

from __future__ import annotations

import json
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest
from hibot import (
    V1ChatApproveParams,
    V1ChatCancelRunParams,
    V1ChatResumeParams,
    V1MessageListParams,
    V1SessionBatchGetParams,
    V1SessionChatParams,
    V1SessionDeleteParams,
    V1SessionListParams,
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
    payload = body["Payload"]
    assert payload["Channel"] == "webchat"
    assert payload["PeerKind"] == "system"
    assert payload["PeerID"] == "agent-1"
    assert "ConversationID" not in payload


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
    payload = body["Payload"]
    assert payload["Channel"] == "webchat"
    assert payload["PeerKind"] == "user"
    assert payload["PeerID"] == "u-77"
    assert "ConversationID" not in payload


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
    # 非 webchat 渠道 SDK 不注入 ConversationID。
    assert body["Payload"] == {
        "Channel": "feishu",
        "PeerKind": "user",
        "PeerID": "ou_xxx",
    }


def test_create_session_passes_explicit_conversation_identity(
    client_factory, make_handler, ok_envelope
):
    handler = make_handler([ok_envelope({"ID": "s-1"})])
    client = client_factory(handler)
    client.v1.sessions.create(
        V1SessionNewParams(
            agent_id="agent-1",
            conversation_id="conversation-1",
            session_key="agent:agent-1:webchat:user:user-1:conv:conversation-1",
            peer=V1SessionPeerParams(peer_kind="user", peer_id="user-1"),
        )
    )
    payload = json.loads(handler.calls[0].content)["Payload"]
    assert payload["ConversationID"] == "conversation-1"
    assert payload["SessionKey"].endswith(":conv:conversation-1")


def test_chat_uses_remembered_agent_id_and_routes_to_server(
    client_factory, make_handler, ok_envelope, sse
):
    create_reply = ok_envelope({"ID": "s-1"})
    chat_reply = ok_envelope({"Message": "hello", "TokenCount": 2})
    handler = make_handler([create_reply, chat_reply])
    client = client_factory(handler)

    session = client.v1.sessions.create(V1SessionNewParams(agent_id="agent-1"))
    msg = client.v1.sessions.chat(session.id, V1SessionChatParams(input="hi"))
    assert msg.id is None
    assert msg.content == "hello"
    assert msg.token_count == 2

    chat_req = handler.calls[1]
    assert _action(chat_req) == "Chat"
    assert _version(chat_req) == "2026-04-23"
    assert chat_req.headers["x-top-service"] == "hibot-server"
    body = json.loads(chat_req.content)
    # AgentID resolved from internal map (was not provided in params)
    assert body["AgentID"] == "agent-1"
    assert body["SessionID"] == "s-1"
    assert body["Content"] == "hi"
    assert body["WorkspaceID"] == "ws-1"
    assert body["Approve"] == "all"
    assert body["Stream"] is False


def test_chat_streaming_yields_events_in_order(
    client_factory, make_handler, ok_envelope, sse
):
    sse_body = (
        b"event: message_delta\n"
        b'data: {"text":"a"}\n\n'
        b"event: message_delta\n"
        b'data: {"text":"b"}\n\n'
        b"event: run_completed\n"
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
    chat_req = handler.calls[1]
    assert _version(chat_req) == "2026-04-23"
    assert chat_req.headers["x-top-service"] == "hibot-server"
    assert json.loads(chat_req.content)["Stream"] is True


def test_chat_resolves_agent_id_from_server_for_unknown_session(
    client_factory, make_handler, ok_envelope
):
    handler = make_handler(
        [
            ok_envelope({"ID": "s-existing", "AgentID": "agent-from-server"}),
            ok_envelope({"Message": "ok"}),
        ]
    )
    client = client_factory(handler)

    msg = client.v1.sessions.chat("s-existing", V1SessionChatParams(input="hello"))

    assert msg.content == "ok"
    assert [_action(req) for req in handler.calls] == ["GetSession", "Chat"]
    assert json.loads(handler.calls[1].content)["AgentID"] == "agent-from-server"


def test_current_session_query_and_timeline_contract(
    client_factory, make_handler, ok_envelope
):
    handler = make_handler(
        [
            ok_envelope({"Items": [{"ID": "s-1"}]}),
            ok_envelope({"Items": [{"ID": "s-2"}]}),
            ok_envelope(
                {
                    "Items": [{"ID": "m-1", "Content": "hello"}],
                    "ResumeHint": {
                        "RunID": "run-1",
                        "RequestID": "request-1",
                        "Status": "running",
                    },
                }
            ),
        ]
    )
    client = client_factory(handler)

    listed = client.v1.sessions.list(
        V1SessionListParams(session_keys=["key-1"], user_id="user-1")
    )
    batched = client.v1.sessions.batch_get(V1SessionBatchGetParams(session_ids=["s-2"]))
    messages = client.v1.sessions.list_messages(
        V1MessageListParams(
            session_id="s-1",
            display_mode="timeline",
            base_message_id="m-2",
        )
    )

    assert listed.items[0].id == "s-1"
    assert batched.items[0].id == "s-2"
    assert messages.resume_hint is not None
    assert messages.resume_hint.run_id == "run-1"
    assert messages.resume_hint.status == "running"
    assert [_action(req) for req in handler.calls] == [
        "ListSessions",
        "BatchGetSessions",
        "ListMessages",
    ]
    list_body = json.loads(handler.calls[0].content)
    assert list_body["SessionKeys"] == ["key-1"]
    assert list_body["UserID"] == "user-1"
    batch_body = json.loads(handler.calls[1].content)
    assert batch_body["SessionIDs"] == ["s-2"]
    message_body = json.loads(handler.calls[2].content)
    assert message_body["DisplayMode"] == "timeline"
    assert message_body["BaseMessageID"] == "m-2"


def test_chat_resume_approve_and_cancel_route_to_server(
    client_factory, make_handler, ok_envelope, sse
):
    handler = make_handler(
        [
            sse(b'event: run_completed\ndata: {"message":{"ID":"m-1"}}\n\n'),
            ok_envelope({"Accepted": True}),
            ok_envelope({"Accepted": False}),
        ]
    )
    client = client_factory(handler)

    with client.v1.sessions.chat_resume(
        V1ChatResumeParams(
            session_id="s-1",
            agent_id="agent-1",
            run_id="run-1",
            last_event_id="run-1:3",
            approve="all",
        )
    ) as stream:
        assert [event.type for event in stream] == ["completed"]
    approved = client.v1.sessions.approve(
        V1ChatApproveParams(
            session_id="s-1",
            run_id="run-1",
            approval_request_id="approval-1",
            choice_id="once",
        )
    )
    cancelled = client.v1.sessions.cancel_run(
        V1ChatCancelRunParams(
            session_id="s-1",
            run_id="run-1",
            reason="user requested",
        )
    )

    assert approved.accepted is True
    assert cancelled.accepted is False
    assert [_action(req) for req in handler.calls] == [
        "ChatResume",
        "Approve",
        "CancelRun",
    ]
    for req in handler.calls:
        assert _version(req) == "2026-04-23"
        assert req.headers["x-top-service"] == "hibot-server"
    resume_body = json.loads(handler.calls[0].content)
    assert resume_body["RunID"] == "run-1"
    assert resume_body["LastEventID"] == "run-1:3"
    assert resume_body["Approve"] == "all"


def test_chat_streaming_propagates_http_error(
    client_factory, make_handler, ok_envelope, sse
):
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
