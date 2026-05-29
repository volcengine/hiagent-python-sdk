"""V1 MCPs service."""

from __future__ import annotations

from typing import List

from .._request import Action
from .._version import SERVER_VERSION
from ._helpers import from_dict, list_from_items
from .types import (
    V1MCP,
    V1MCPCredentialInputParams,
    V1MCPDeleteParams,
    V1MCPGetParams,
    V1MCPListParams,
    V1MCPNewParams,
    V1MCPResolveParams,
    V1MCPTestConnectionParams,
    V1MCPTestConnectionResult,
    V1MCPUpdateParams,
)


def _credential_config_to_dict(cfg: V1MCPCredentialInputParams) -> dict:
    body: dict = {}
    if cfg.name:
        body["Name"] = cfg.name
    if cfg.description:
        body["Description"] = cfg.description
    if cfg.source:
        body["Source"] = cfg.source
    if cfg.provider_type:
        body["ProviderType"] = cfg.provider_type
    if cfg.config is not None:
        body["Config"] = cfg.config
    if cfg.secrets:
        secrets_list = []
        for s in cfg.secrets:
            entry: dict = {}
            if s.secret_id:
                entry["SecretID"] = s.secret_id
            if s.key_name:
                entry["KeyName"] = s.key_name
            if s.description:
                entry["Description"] = s.description
            if s.secret_type:
                entry["SecretType"] = s.secret_type
            if s.secret_value:
                entry["SecretValue"] = s.secret_value
            secrets_list.append(entry)
        body["Secrets"] = secrets_list
    return body


class MCPsService:
    def __init__(self, v1) -> None:
        self._v1 = v1

    def _action(self, name: str, body):
        return self._v1.requester.do_action(
            Action(service=self._v1.services.server, version=SERVER_VERSION, action=name, body=body)
        )

    def create(self, params: V1MCPNewParams) -> V1MCP:
        body = {
            "Name": params.name,
            "Transport": params.transport,
        }
        if params.endpoint:
            body["URL"] = params.endpoint
        if params.description:
            body["Description"] = params.description
        if params.headers is not None:
            body["Headers"] = params.headers
        if params.env is not None:
            body["Env"] = params.env
        if params.command:
            body["Command"] = params.command
        if params.args:
            body["Args"] = list(params.args)
        if params.auth_type:
            body["AuthType"] = params.auth_type
        if params.credential_config is not None:
            body["CredentialConfig"] = _credential_config_to_dict(params.credential_config)
        if params.tool_allowlist is not None:
            body["ToolAllowlist"] = list(params.tool_allowlist)
        if params.tool_denylist is not None:
            body["ToolDenylist"] = list(params.tool_denylist)
        if params.tool_prefix:
            body["ToolPrefix"] = params.tool_prefix
        if params.timeout:
            body["Timeout"] = params.timeout
        if params.source:
            body["Source"] = params.source
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        result = self._action("CreateMCP", body)
        new_id = result.get("ID") if isinstance(result, dict) else None
        if not new_id:
            raise ValueError("hibot: create mcp response missing ID")
        return V1MCP(id=new_id, name=params.name, transport=params.transport, endpoint=params.endpoint)

    def list(self, params: V1MCPListParams = V1MCPListParams()) -> List[V1MCP]:
        body = {}
        if params.keyword:
            body["Keyword"] = params.keyword
        if params.status:
            body["Status"] = params.status
        if params.source:
            body["Source"] = params.source
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        result = self._action("ListMCPs", body)
        return list_from_items(V1MCP, result)

    def get(self, params: V1MCPGetParams) -> V1MCP:
        if not params.id:
            raise ValueError("hibot: mcp id is required")
        body = {"ID": params.id}
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        result = self._action("GetMCP", body)
        decoded = from_dict(V1MCP, result) or V1MCP()
        if not decoded.id:
            raise ValueError("hibot: get mcp response missing ID")
        return decoded

    def update(self, params: V1MCPUpdateParams) -> None:
        if not params.id:
            raise ValueError("hibot: mcp id is required")
        body = {"ID": params.id}
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        if params.name is not None:
            body["Name"] = params.name
        if params.description is not None:
            body["Description"] = params.description
        if params.transport is not None:
            body["Transport"] = params.transport
        if params.endpoint is not None:
            body["URL"] = params.endpoint
        if params.headers is not None:
            body["Headers"] = params.headers
        if params.env is not None:
            body["Env"] = params.env
        if params.command is not None:
            body["Command"] = params.command
        if params.args is not None:
            body["Args"] = list(params.args)
        if params.auth_type is not None:
            body["AuthType"] = params.auth_type
        if params.credential_config is not None:
            body["CredentialConfig"] = _credential_config_to_dict(params.credential_config)
        if params.tool_allowlist is not None:
            body["ToolAllowlist"] = list(params.tool_allowlist)
        if params.tool_denylist is not None:
            body["ToolDenylist"] = list(params.tool_denylist)
        if params.tool_prefix is not None:
            body["ToolPrefix"] = params.tool_prefix
        if params.timeout is not None:
            body["Timeout"] = params.timeout
        if params.status is not None:
            body["Status"] = params.status
        if params.source is not None:
            body["Source"] = params.source
        self._action("UpdateMCP", body)

    def delete(self, params: V1MCPDeleteParams) -> None:
        if not params.id:
            raise ValueError("hibot: mcp id is required")
        body = {"ID": params.id}
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        self._action("DeleteMCP", body)

    def test_connection(self, params: V1MCPTestConnectionParams) -> V1MCPTestConnectionResult:
        body = {}
        if params.transport:
            body["Transport"] = params.transport
        if params.endpoint:
            body["URL"] = params.endpoint
        if params.headers is not None:
            body["Headers"] = params.headers
        if params.env is not None:
            body["Env"] = params.env
        if params.command:
            body["Command"] = params.command
        if params.args:
            body["Args"] = list(params.args)
        if params.auth_type:
            body["AuthType"] = params.auth_type
        if params.credential_config is not None:
            body["CredentialConfig"] = _credential_config_to_dict(params.credential_config)
        if params.timeout:
            body["Timeout"] = params.timeout
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        result = self._action("TestMCPConnection", body)
        return from_dict(V1MCPTestConnectionResult, result) or V1MCPTestConnectionResult()

    def resolve(self, params: V1MCPResolveParams) -> V1MCP:
        if params.id:
            return V1MCP(id=params.id, name=params.name)
        if not params.name:
            raise ValueError("hibot: mcp id or name is required")
        items = self.list(V1MCPListParams(keyword=params.name, workspace_id=params.workspace_id))
        for item in items:
            if item.name == params.name and item.id:
                return item
        raise ValueError(f'hibot: mcp "{params.name}" not found')
