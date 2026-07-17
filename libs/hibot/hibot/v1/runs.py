"""V1 Runtime read-model service."""

from __future__ import annotations

from typing import List

from ._helpers import from_dict, list_from_items
from ._server_service import ServerService, put_if
from .types import V1Run, V1RunGetParams, V1RunListParams


class RunsService(ServerService):
    def list(self, params: V1RunListParams = V1RunListParams()) -> List[V1Run]:
        body = {}
        for key, value in (
            ("AgentID", params.agent_id),
            ("SessionID", params.session_id),
            ("Status", params.status),
            ("WorkspaceID", params.workspace_id),
        ):
            put_if(body, key, value)
        return list_from_items(V1Run, self._action("ListRuns", body))

    def get(self, params: V1RunGetParams) -> V1Run:
        if not params.run_id:
            raise ValueError("hibot: run id is required")
        body = {"RunID": params.run_id}
        put_if(body, "WorkspaceID", params.workspace_id)
        result = self._action("GetRun", body)
        decoded = from_dict(V1Run, result) or V1Run()
        if not decoded.id:
            raise ValueError("hibot: get run response missing ID")
        return decoded


__all__ = ["RunsService"]
