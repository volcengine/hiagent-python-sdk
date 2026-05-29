"""Tests for chat() approve injection, file uploads, and CredentialConfig."""

from __future__ import annotations

import json

from hibot import (
    V1CredentialSecretInputParams,
    V1MCPCredentialInputParams,
    V1MCPNewParams,
    V1MCPUpdateParams,
    V1MessageFile,
    V1SessionChatParams,
)


def test_chat_non_streaming_injects_approve_all(
    client_factory, make_handler, ok_envelope, sse
):
    sse_body = (
        b'event: run_completed\n'
        b'data: {"message":{"ID":"m-1","Role":"assistant","Content":"ok"}}\n\n'
    )
    handler = make_handler([sse(sse_body)])
    client = client_factory(handler)

    msg = client.v1.sessions.chat(
        "s-1",
        V1SessionChatParams(input="hello", agent_id="agent-1"),
    )
    assert msg.id == "m-1"

    body = json.loads(handler.calls[0].content)
    assert body["Approve"] == "all"


def test_chat_streaming_does_not_inject_approve(
    client_factory, make_handler, ok_envelope, sse
):
    sse_body = (
        b'event: run_completed\n'
        b'data: {"message":{"ID":"m-1"}}\n\n'
    )
    handler = make_handler([sse(sse_body)])
    client = client_factory(handler)

    with client.v1.sessions.chat_streaming(
        "s-1", V1SessionChatParams(input="hello", agent_id="agent-1")
    ) as stream:
        for _ in stream:
            pass

    body = json.loads(handler.calls[0].content)
    assert "Approve" not in body


def test_chat_supports_files_and_empty_content(
    client_factory, make_handler, ok_envelope, sse
):
    sse_body = (
        b'event: run_completed\n'
        b'data: {"message":{"ID":"m-1"}}\n\n'
    )
    handler = make_handler([sse(sse_body)])
    client = client_factory(handler)

    client.v1.sessions.chat(
        "s-1",
        V1SessionChatParams(
            agent_id="agent-1",
            files=[
                V1MessageFile(
                    name="report.pdf",
                    content_type="application/pdf",
                    blob_id="blob-123",
                )
            ],
        ),
    )

    body = json.loads(handler.calls[0].content)
    # Content 缺省为空串；服务端允许仅传 Files。
    assert body.get("Content", "") == ""
    files = body["Files"]
    assert len(files) == 1
    assert files[0]["Name"] == "report.pdf"
    assert files[0]["ContentType"] == "application/pdf"
    assert files[0]["BlobID"] == "blob-123"


def test_create_mcp_serializes_credential_config_secret_value(
    client_factory, make_handler, ok_envelope
):
    handler = make_handler([ok_envelope({"ID": "mcp-1"})])
    client = client_factory(handler)

    client.v1.mcps.create(
        V1MCPNewParams(
            name="demo",
            transport="streamable_http",
            endpoint="https://example.com/mcp",
            credential_config=V1MCPCredentialInputParams(
                name="demo-cred",
                provider_type="basic",
                secrets=[
                    V1CredentialSecretInputParams(
                        key_name="token",
                        secret_type="string",
                        secret_value="s3cr3t",
                    )
                ],
            ),
        )
    )

    body = json.loads(handler.calls[0].content)
    cfg = body["CredentialConfig"]
    assert cfg["Name"] == "demo-cred"
    assert cfg["ProviderType"] == "basic"
    secret = cfg["Secrets"][0]
    assert secret["KeyName"] == "token"
    assert secret["SecretValue"] == "s3cr3t"
    # 旧 Value 字段不应再出现。
    assert "Value" not in secret
    # 旧 Credential 字段（Name 引用）也不应再被发送。
    assert "Credential" not in body


def test_update_mcp_passes_credential_config(
    client_factory, make_handler, ok_envelope
):
    handler = make_handler([ok_envelope({})])
    client = client_factory(handler)

    client.v1.mcps.update(
        V1MCPUpdateParams(
            id="mcp-1",
            credential_config=V1MCPCredentialInputParams(
                name="demo-cred",
                secrets=[
                    V1CredentialSecretInputParams(
                        key_name="token",
                        secret_value="new-secret",
                    )
                ],
            ),
        )
    )

    body = json.loads(handler.calls[0].content)
    cfg = body["CredentialConfig"]
    assert cfg["Secrets"][0]["SecretValue"] == "new-secret"
