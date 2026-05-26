"""Tests for AgentsService — covers default-env injection, payload shape, etc."""

from __future__ import annotations

import json
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest
from hibot import (
    V1AgentDeleteParams,
    V1AgentGetParams,
    V1AgentNewParams,
    V1AgentNewParamsToolUnion,
    V1ManagedAgentMCPToolParams,
    V1ManagedAgentModelConfigParams,
    V1ManagedAgentResourceRefParams,
    V1ManagedAgentSkillToolParams,
)


def _query_action(req: httpx.Request) -> str:
    q = parse_qs(urlsplit(str(req.url)).query)
    return q.get("Action", [""])[0]


def test_create_agent_auto_resolves_default_environment(client_factory, make_handler, ok_envelope):
    # Sequence: ListEnv -> [{ID:e1,...}, {ID:e2,...}], then CreateAgent.
    list_envs_reply = ok_envelope(
        {
            "Items": [
                {"ID": "env-old", "Name": "old", "CreatedAt": "2026-01-01T00:00:00Z"},
                {"ID": "env-new", "Name": "new", "CreatedAt": "2026-05-01T00:00:00Z"},
            ]
        }
    )
    create_agent_reply = ok_envelope({"ID": "agent-1"})

    handler = make_handler([list_envs_reply, create_agent_reply])
    client = client_factory(handler)

    params = V1AgentNewParams(
        name="a1",
        model=V1ManagedAgentModelConfigParams(id="model-1"),
        system="be helpful",
        tools=[
            V1AgentNewParamsToolUnion(
                of_skill=V1ManagedAgentSkillToolParams(skill_version_id="sv-1")
            ),
            V1AgentNewParamsToolUnion(
                of_mcp=V1ManagedAgentMCPToolParams(id="mcp-1")
            ),
        ],
        resources=[V1ManagedAgentResourceRefParams(id="res-1")],
    )
    agent = client.v1.agents.create(params)
    assert agent.id == "agent-1"

    # First request: ListEnv
    assert _query_action(handler.calls[0]) == "ListEnv"

    # Second request: CreateAgent — verify body
    create_req = handler.calls[1]
    assert _query_action(create_req) == "CreateAgent"
    body = json.loads(create_req.content)
    # workspace_id auto-injected at top level
    assert body["WorkspaceID"] == "ws-1"
    assert body["Name"] == "a1"
    assert body["ModelID"] == "model-1"
    # default env picked = earliest created_at
    assert body["EnvID"] == "env-old"
    assert body["SystemPrompt"] == "be helpful"
    assert body["Skills"] == [{"ID": "sv-1"}]
    assert body["MCPs"] == [{"ID": "mcp-1", "Enabled": True}]
    assert body["Resources"] == {"ResourceIDs": ["res-1"]}


def test_get_agent_requires_agent_id(client_factory, make_handler):
    handler = make_handler([])
    client = client_factory(handler)
    with pytest.raises(ValueError):
        client.v1.agents.get(V1AgentGetParams(agent_id=""))


def test_delete_agent_uses_server_service(client_factory, make_handler, ok_envelope):
    handler = make_handler([ok_envelope({})])
    client = client_factory(handler)
    client.v1.agents.delete(V1AgentDeleteParams(agent_id="a-1"))
    req = handler.calls[0]
    assert _query_action(req) == "DeleteAgent"
    body = json.loads(req.content)
    assert body == {"AgentID": "a-1", "WorkspaceID": "ws-1"}
    # Service routed to server
    q = parse_qs(urlsplit(str(req.url)).query)
    assert q["Version"][0] == "2026-04-23"
