"""V1 Runtime API key service."""

from __future__ import annotations

from typing import List

from ._helpers import from_dict, list_from_items
from ._server_service import ServerService, put_if
from .types import (
    V1RuntimeAPIKey,
    V1RuntimeAPIKeyCreateResult,
    V1RuntimeAPIKeyDeleteParams,
    V1RuntimeAPIKeyGetParams,
    V1RuntimeAPIKeyListParams,
    V1RuntimeAPIKeyNewParams,
    V1RuntimeAPIKeyUpdateParams,
)


class RuntimeAPIKeysService(ServerService):
    def create(self, params: V1RuntimeAPIKeyNewParams) -> V1RuntimeAPIKeyCreateResult:
        if not params.agent_id or not params.expired:
            raise ValueError("hibot: runtime API key agent id and expiry are required")
        body = {"AgentID": params.agent_id, "Expired": params.expired}
        put_if(body, "Description", params.description)
        put_if(body, "WorkspaceID", params.workspace_id)
        result = self._action("CreateRuntimeAPIKey", body)
        decoded = from_dict(V1RuntimeAPIKeyCreateResult, result)
        if decoded is None or not decoded.raw_key:
            raise ValueError("hibot: create runtime API key response missing RawKey")
        return decoded

    def list(self, params: V1RuntimeAPIKeyListParams) -> List[V1RuntimeAPIKey]:
        if not params.agent_id:
            raise ValueError("hibot: runtime API key agent id is required")
        body = {"AgentID": params.agent_id}
        put_if(body, "WorkspaceID", params.workspace_id)
        return list_from_items(
            V1RuntimeAPIKey, self._action("ListRuntimeAPIKeys", body)
        )

    def reveal(self, params: V1RuntimeAPIKeyGetParams) -> str:
        if not params.agent_id or not params.id:
            raise ValueError("hibot: runtime API key agent id and id are required")
        if not params.user_info.user_name or not params.user_info.password:
            raise ValueError(
                "hibot: user name and password are required to reveal a key"
            )
        body = {
            "AgentID": params.agent_id,
            "ID": params.id,
            "UserInfo": {
                "UserName": params.user_info.user_name,
                "Password": params.user_info.password,
            },
        }
        put_if(body, "WorkspaceID", params.workspace_id)
        result = self._action("GetRuntimeAPIKey", body)
        raw_key = result.get("RawKey") if isinstance(result, dict) else None
        if not raw_key:
            raise ValueError("hibot: get runtime API key response missing RawKey")
        return raw_key

    def update(self, params: V1RuntimeAPIKeyUpdateParams) -> None:
        if not params.agent_id or not params.id:
            raise ValueError("hibot: runtime API key agent id and id are required")
        body = {"AgentID": params.agent_id, "ID": params.id}
        put_if(body, "Description", params.description, allow_empty=True)
        put_if(body, "WorkspaceID", params.workspace_id)
        self._action("UpdateRuntimeAPIKey", body)

    def delete(self, params: V1RuntimeAPIKeyDeleteParams) -> None:
        if not params.agent_id or not params.id:
            raise ValueError("hibot: runtime API key agent id and id are required")
        body = {"AgentID": params.agent_id, "ID": params.id}
        put_if(body, "WorkspaceID", params.workspace_id)
        self._action("DeleteRuntimeAPIKey", body)


__all__ = ["RuntimeAPIKeysService"]
