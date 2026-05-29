"""Offline full-journey e2e — mirrors go/examples/e2e/TestFullJourney_StreamingAndBatch.

Walks the SDK from blank workspace through every managed-agent step and
verifies action routing, request bodies and SSE consumption against a
``MockTransport`` queue that mimics ``examples/internal/mocktop``.
"""

from __future__ import annotations

import json
from urllib.parse import parse_qs, urlsplit

import httpx
from hibot import (
    V1AgentNewParams,
    V1AgentNewParamsToolUnion,
    V1CredentialSecretInputParams,
    V1ManagedAgentMCPToolParams,
    V1ManagedAgentModelConfigParams,
    V1ManagedAgentResourceRefParams,
    V1ManagedAgentSkillToolParams,
    V1MCPCredentialInputParams,
    V1MCPNewParams,
    V1ModelGetParams,
    V1PromptNewParams,
    V1ResourceNewParams,
    V1SessionChatParams,
    V1SessionNewParams,
    V1SkillNewParams,
    V1UploadBlobParams,
)

_V1_MANAGED_AGENT_MODEL_DOUBAO_SEED_PRO = "doubao-seed-2.0-pro-260215"


def _query(req: httpx.Request) -> dict:
    return parse_qs(urlsplit(str(req.url)).query)


def _action(req: httpx.Request) -> str:
    return _query(req).get("Action", [""])[0]


def _path(req: httpx.Request) -> str:
    return urlsplit(str(req.url)).path


def _sse_chat_body() -> bytes:
    """Mirror mocktop's Chat handler: one delta + one completed event."""
    return (
        b'event: delta\n'
        b'data: {"request_id":"req-test","delta":{"text":"ok"}}\n\n'
        b'event: completed\n'
        b'data: {"request_id":"req-test","message":{"ID":"message-1","Content":"ok"}}\n\n'
    )


def test_full_journey_streaming_and_batch(
    client_factory, make_handler, ok_envelope, sse
):
    sse_body = _sse_chat_body()
    # Reply queue must match the SDK call order exactly:
    #   models.get -> prompts.create -> uploads.upload_blob (skill) ->
    #   uploads.upload_blob (resource) -> skills.create -> resources.create ->
    #   mcps.create -> agents.create (triggers ListEnv first) -> CreateAgent ->
    #   sessions.create -> sessions.chat_streaming -> sessions.chat
    replies = [
        # models.get -> GetModel
        ok_envelope({"Items": [{"ID": _V1_MANAGED_AGENT_MODEL_DOUBAO_SEED_PRO}]}),
        # prompts.create -> CreateAgentPromptTemplate
        ok_envelope(
            {
                "ID": "prompt-1",
                "SystemPrompt": "你是一个 SDK 端到端测试中的助手。",
            }
        ),
        # uploads.upload_blob (skill)
        ok_envelope({"BlobID": "blob-skill"}),
        # uploads.upload_blob (resource)
        ok_envelope({"BlobID": "blob-resource"}),
        # skills.create -> CreateSkill
        ok_envelope({"ID": "skill-version-1"}),
        # resources.create -> CreateResource
        ok_envelope({"ID": "resource-1"}),
        # mcps.create -> CreateMCP
        ok_envelope({"ID": "mcp-1"}),
        # agents.create env_id="" -> environments.default -> ListEnv first
        ok_envelope(
            {
                "Items": [
                    {
                        "ID": "env-1",
                        "Name": "default-env",
                        "ImageType": "hermes",
                        "CreatedAt": "2026-01-01T00:00:00Z",
                    }
                ]
            }
        ),
        # CreateAgent
        ok_envelope({"ID": "agent-1"}),
        # sessions.create -> CreateSession
        ok_envelope({"ID": "session-1"}),
        # sessions.chat_streaming -> Chat (SSE)
        sse(sse_body),
        # sessions.chat -> Chat (SSE)
        sse(sse_body),
    ]
    handler = make_handler(replies)
    client = client_factory(handler, workspace_id="workspace-e2e")

    # ---------------------------------------------------------------
    # Step 1: GetModel — Python SDK's models.get walks GetModel directly.
    # ---------------------------------------------------------------
    model = client.v1.models.get(
        V1ModelGetParams(id=_V1_MANAGED_AGENT_MODEL_DOUBAO_SEED_PRO)
    )
    assert model.id, f"model.id empty: {model!r}"
    assert model.id == _V1_MANAGED_AGENT_MODEL_DOUBAO_SEED_PRO

    # ---------------------------------------------------------------
    # Step 2: prompts.create -> CreateAgentPromptTemplate.
    # ---------------------------------------------------------------
    prompt = client.v1.prompts.create(
        V1PromptNewParams(
            name="e2e-prompt",
            content="你是一个 SDK 端到端测试中的助手。",
        )
    )
    assert prompt.content, f"prompt content empty: {prompt!r}"
    assert prompt.id == "prompt-1"

    # ---------------------------------------------------------------
    # Step 3: uploads.upload_blob -> UploadBlob (skill + resource).
    # ---------------------------------------------------------------
    skill_blob = client.v1.uploads.upload_blob(
        V1UploadBlobParams(filename="skill.zip", content_type="application/zip"),
        b"PK\x03\x04skill-bytes",
    )
    assert skill_blob.blob_id, "skill blob id empty"
    assert skill_blob.blob_id == "blob-skill"

    resource_blob = client.v1.uploads.upload_blob(
        V1UploadBlobParams(filename="runbook.md", content_type="text/markdown"),
        b"# runbook\nstep 1\n",
    )
    assert resource_blob.blob_id, "resource blob id empty"
    assert resource_blob.blob_id == "blob-resource"

    # ---------------------------------------------------------------
    # Step 4: skills.create -> CreateSkill.
    # ---------------------------------------------------------------
    skill = client.v1.skills.create(
        V1SkillNewParams(
            name="e2e-skill",
            description="skill registered by e2e test",
            blob_id=skill_blob.blob_id,
            enabled=True,
            version="1.0.0",
        )
    )
    assert skill.id, "skill.id empty"
    assert skill.id == "skill-version-1"

    # ---------------------------------------------------------------
    # Step 5: resources.create -> CreateResource.
    # ---------------------------------------------------------------
    resource = client.v1.resources.create(
        V1ResourceNewParams(
            name="e2e-resource",
            type="document_collection",
            blob_id=resource_blob.blob_id,
        )
    )
    assert resource.id, "resource.id empty"
    assert resource.id == "resource-1"

    # ---------------------------------------------------------------
    # Step 6: mcps.create -> CreateMCP.
    # ---------------------------------------------------------------
    mcp = client.v1.mcps.create(
        V1MCPNewParams(
            name="e2e-mcp",
            transport="streamable_http",
            endpoint="http://mcp.local/mcp",
            credential_config=V1MCPCredentialInputParams(
                name="e2e-token",
                provider_type="basic",
                secrets=[
                    V1CredentialSecretInputParams(
                        key_name="token",
                        secret_type="string",
                        secret_value="e2e-token-value",
                    )
                ],
            ),
        )
    )
    assert mcp.id, "mcp.id empty"
    assert mcp.id == "mcp-1"

    # ---------------------------------------------------------------
    # Step 7: agents.create — env_id empty triggers default env via ListEnv.
    # ---------------------------------------------------------------
    agent = client.v1.agents.create(
        V1AgentNewParams(
            name="e2e-agent",
            model=V1ManagedAgentModelConfigParams(id=model.id),
            system=prompt.content,
            tools=[
                V1AgentNewParamsToolUnion(
                    of_skill=V1ManagedAgentSkillToolParams(skill_version_id=skill.id)
                ),
                V1AgentNewParamsToolUnion(
                    of_mcp=V1ManagedAgentMCPToolParams(id=mcp.id)
                ),
            ],
            resources=[V1ManagedAgentResourceRefParams(id=resource.id)],
        )
    )
    assert agent.id, "agent.id empty"
    assert agent.id == "agent-1"

    # ---------------------------------------------------------------
    # Step 8: sessions.create — webchat default Channel/PeerKind/PeerID.
    # ---------------------------------------------------------------
    session = client.v1.sessions.create(V1SessionNewParams(agent_id=agent.id))
    assert session.id, "session.id empty"
    assert session.id == "session-1"

    # ---------------------------------------------------------------
    # Step 9 (streaming): chat_streaming must observe delta + completed.
    # ---------------------------------------------------------------
    saw_delta = False
    saw_completed = False
    streaming_event_names: list[str] = []
    with client.v1.sessions.chat_streaming(
        session.id,
        V1SessionChatParams(agent_id=agent.id, input="流式：请用一句话介绍自己。"),
    ) as stream:
        for event in stream:
            streaming_event_names.append(event.type)
            if event.type == "delta":
                saw_delta = True
            elif event.type == "completed":
                saw_completed = True
            elif event.type == "failed":
                raise AssertionError(
                    f"streaming chat failed: {event.error.message}"
                )
        assert (
            saw_completed
        ), f"streaming chat: no completed event observed (events={streaming_event_names})"
        assert (
            saw_delta
        ), f"streaming chat: no delta event observed (events={streaming_event_names})"
        streaming_final = stream.final_message()
    assert (
        streaming_final.id and streaming_final.content
    ), f"streaming final message incomplete: {streaming_final!r}"

    # ---------------------------------------------------------------
    # Step 10 (batch): sessions.chat returns the final V1Message.
    # ---------------------------------------------------------------
    batch_final = client.v1.sessions.chat(
        session.id, V1SessionChatParams(input="批量：再回答一次同样的问题。")
    )
    assert (
        batch_final.id and batch_final.content
    ), f"batch final message incomplete: {batch_final!r}"

    # ---------------------------------------------------------------
    # Step 11: action / routing / body / signing / SSE assertions.
    # ---------------------------------------------------------------
    actions = [_action(c) for c in handler.calls]
    expected_order = [
        "GetModel",
        "CreateAgentPromptTemplate",
        "UploadBlob",
        "UploadBlob",
        "CreateSkill",
        "CreateResource",
        "CreateMCP",
        "ListEnv",
        "CreateAgent",
        "CreateSession",
        "Chat",
        "Chat",
    ]
    assert actions == expected_order, f"action order mismatch: {actions!r}"

    # Required-actions superset (mirrors mocktop.RequireActions in Go test).
    required = {
        "GetModel",
        "CreateAgentPromptTemplate",
        "UploadBlob",
        "CreateSkill",
        "CreateResource",
        "CreateMCP",
        "ListEnv",
        "CreateAgent",
        "CreateSession",
        "Chat",
    }
    seen_actions = set(actions)
    missing = required - seen_actions
    assert not missing, f"missing required actions: {sorted(missing)}"

    # /up subpath only for UploadBlob requests; everything else stays at root.
    for req in handler.calls:
        if _action(req) == "UploadBlob":
            assert _path(req).endswith(
                "/up"
            ), f"UploadBlob path = {_path(req)}, want suffix /up"
        else:
            assert _path(req) in (
                "",
                "/",
            ), f"non-upload path = {_path(req)} for action={_action(req)}"

    # Every request carries a VOLC v4 Authorization header.
    for req in handler.calls:
        auth = req.headers.get("authorization", "")
        assert auth.startswith(
            "HMAC-SHA256 "
        ), f"missing/invalid Authorization header for action={_action(req)}: {auth!r}"

    # CreateAgent body verification.
    create_agent_idx = actions.index("CreateAgent")
    create_agent_body = json.loads(handler.calls[create_agent_idx].content)
    assert (
        create_agent_body.get("WorkspaceID") == "workspace-e2e"
    ), f"CreateAgent WorkspaceID = {create_agent_body.get('WorkspaceID')!r}, want workspace-e2e"
    assert (
        create_agent_body.get("ModelID") == model.id
    ), f"CreateAgent ModelID = {create_agent_body.get('ModelID')!r}, want {model.id!r}"
    assert (
        create_agent_body.get("EnvID") == "env-1"
    ), f"CreateAgent EnvID = {create_agent_body.get('EnvID')!r}, want env-1 (from ListEnv default)"
    assert isinstance(
        create_agent_body.get("Skills"), list
    ), f"CreateAgent Skills missing or wrong type: {create_agent_body.get('Skills')!r}"
    assert isinstance(
        create_agent_body.get("MCPs"), list
    ), f"CreateAgent MCPs missing or wrong type: {create_agent_body.get('MCPs')!r}"
    assert isinstance(
        create_agent_body.get("Resources"), dict
    ), f"CreateAgent Resources missing or wrong shape: {create_agent_body.get('Resources')!r}"

    # CreateSession body verification.
    create_session_idx = actions.index("CreateSession")
    create_session_body = json.loads(handler.calls[create_session_idx].content)
    assert (
        create_session_body.get("AgentID") == agent.id
    ), f"CreateSession AgentID = {create_session_body.get('AgentID')!r}, want {agent.id!r}"
    payload = create_session_body.get("Payload")
    assert isinstance(
        payload, dict
    ), f"CreateSession Payload missing: {create_session_body!r}"
    assert (
        payload.get("Channel") == "webchat"
    ), f"CreateSession Channel = {payload.get('Channel')!r}, want webchat"
    assert (
        payload.get("PeerKind") == "system"
    ), f"CreateSession PeerKind = {payload.get('PeerKind')!r}, want system"
    assert (
        payload.get("PeerID") == agent.id
    ), f"CreateSession PeerID = {payload.get('PeerID')!r}, want {agent.id!r}"

    # Chat body verification — use the *batch* (last) Chat request which carries
    # the "批量" content; both chat calls go to the same Action so disambiguate
    # by indexing the last occurrence.
    last_chat_idx = len(actions) - 1 - actions[::-1].index("Chat")
    chat_body = json.loads(handler.calls[last_chat_idx].content)
    assert (
        chat_body.get("SessionID") == session.id
    ), f"Chat SessionID = {chat_body.get('SessionID')!r}, want {session.id!r}"
    assert (
        chat_body.get("AgentID") == agent.id
    ), f"Chat AgentID = {chat_body.get('AgentID')!r}, want {agent.id!r} (SDK should infer agent from session)"
    content = chat_body.get("Content", "")
    assert (
        "批量" in content
    ), f"Chat Content = {content!r}, want contains '批量'"
