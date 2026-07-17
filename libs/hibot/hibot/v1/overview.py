"""V1 workspace overview service."""

from __future__ import annotations

from ._helpers import from_dict
from ._server_service import ServerService, put_if
from .types import V1Overview


class OverviewService(ServerService):
    def get(self, *, workspace_id: str = "") -> V1Overview:
        body = {}
        put_if(body, "WorkspaceID", workspace_id)
        return from_dict(V1Overview, self._action("GetOverview", body)) or V1Overview()


__all__ = ["OverviewService"]
