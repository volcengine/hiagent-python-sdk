"""Offline e2e — end-to-end CRUD plus chat over MockTransport."""

from __future__ import annotations

import json
from urllib.parse import parse_qs, urlsplit

import hibot
import httpx
import pytest
from hibot import (
    V1AgentNewParams,
    V1ManagedAgentModelConfigParams,
    V1ResourceNewParams,
    V1SessionChatParams,
    V1SessionNewParams,
    V1UploadBlobParams,
)


def _action(req: httpx.Request) -> str:
    return parse_qs(urlsplit(str(req.url)).query).get("Action", [""])[0]


def test_basic_e2e_offline(client_factory, make_handler, ok_envelope, sse):
    sse_body = (
        b'event: message_delta\n'
        b'data: {"text":"Hi"}\n\n'
        b'event: run_completed\n'
        b'data: {"message":{"ID":"msg-1","Role":"assistant","Content":"Hi"}}\n\n'
    )

    replies = [
        # uploads.upload_blob -> /up subpath
        ok_envelope({"BlobID": "blob-1"}),
        # resources.create
        ok_envelope({"ID": "res-1"}),
        # environments.list (default env lookup)
        ok_envelope({"Items": [{"ID": "env-1", "CreatedAt": "2026-01-01"}]}),
        # agents.create
        ok_envelope({"ID": "agent-1"}),
        # sessions.create
        ok_envelope({"ID": "sess-1"}),
        # sessions.chat (gateway, SSE)
        sse(sse_body),
    ]
    handler = make_handler(replies)
    client = client_factory(handler)

    blob = client.v1.uploads.upload_blob(
        V1UploadBlobParams(filename="x.txt"), b"content"
    )
    assert blob.blob_id == "blob-1"

    res = client.v1.resources.create(
        V1ResourceNewParams(name="r", blob_id=blob.blob_id, type="document_collection")
    )
    assert res.id == "res-1"

    agent = client.v1.agents.create(
        V1AgentNewParams(
            name="a",
            model=V1ManagedAgentModelConfigParams(id="model-1"),
        )
    )
    assert agent.id == "agent-1"

    session = client.v1.sessions.create(V1SessionNewParams(agent_id=agent.id))
    assert session.id == "sess-1"

    msg = client.v1.sessions.chat(session.id, V1SessionChatParams(input="hi"))
    assert msg.id == "msg-1"
    assert msg.content == "Hi"

    # Verify routing & envelope expectations
    actions = [_action(c) for c in handler.calls]
    assert actions == [
        "UploadBlob",
        "CreateResource",
        "ListEnv",
        "CreateAgent",
        "CreateSession",
        "Chat",
    ]
    # /up subpath check
    upload_url = str(handler.calls[0].url)
    assert urlsplit(upload_url).path.endswith("/up")
    # Other server actions stay at root
    assert urlsplit(str(handler.calls[1].url)).path in ("", "/")

    # All requests carry the VOLC v4 Authorization header
    for req in handler.calls:
        assert req.headers.get("authorization", "").startswith("HMAC-SHA256 ")
        # Workspace ID injected at body top-level on JSON requests
        if req.headers.get("content-type", "").startswith("application/json"):
            body = json.loads(req.content)
            assert body["WorkspaceID"] == "ws-1"


def test_config_requires_workspace_id():
    with pytest.raises(ValueError):
        hibot.Config(
            endpoint="https://x",
            access_key="ak",
            secret_key="sk",
            workspace_id="",
        )
