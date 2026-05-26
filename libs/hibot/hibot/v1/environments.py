"""V1 Environments service."""

from __future__ import annotations

from typing import List

from .._request import Action
from .._version import SERVER_VERSION
from ._helpers import from_dict, list_from_items
from .types import (
    V1Environment,
    V1EnvironmentNewParams,
    V1EnvironmentUpdateParams,
)


class EnvironmentsService:
    def __init__(self, v1) -> None:
        self._v1 = v1

    def _action(self, name: str, body):
        return self._v1.requester.do_action(
            Action(service=self._v1.services.server, version=SERVER_VERSION, action=name, body=body)
        )

    def create(self, **kwargs) -> V1Environment:
        params = kwargs.get("params") or V1EnvironmentNewParams(**kwargs)
        payload = {}
        if params.image_type:
            payload["ImageType"] = params.image_type
        if params.name:
            payload["Name"] = params.name
        if params.description:
            payload["Description"] = params.description
        if params.env_vars is not None:
            payload["EnvVars"] = params.env_vars
        if params.cpu_limit:
            payload["CpuLimit"] = params.cpu_limit
        if params.memory_limit:
            payload["MemoryLimit"] = params.memory_limit
        if params.pvc_size:
            payload["PVCSize"] = params.pvc_size
        if params.data_path:
            payload["DataPath"] = params.data_path
        body = {"Payload": payload}
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        result = self._action("CreateEnv", body)
        env = from_dict(V1Environment, result) or V1Environment()
        if not env.id:
            raise ValueError("hibot: create environment response missing ID")
        env.name = env.name or params.name
        env.image_type = env.image_type or params.image_type
        return env

    def list(self, *, workspace_id: str = "") -> List[V1Environment]:
        body = {}
        if workspace_id:
            body["WorkspaceID"] = workspace_id
        result = self._action("ListEnv", body)
        return list_from_items(V1Environment, result)

    def get(self, *, env_id: str, workspace_id: str = "") -> V1Environment:
        if not env_id:
            raise ValueError("hibot: env id is required")
        body = {"EnvID": env_id}
        if workspace_id:
            body["WorkspaceID"] = workspace_id
        result = self._action("GetEnv", body)
        env = from_dict(V1Environment, result) or V1Environment()
        if not env.id:
            raise ValueError("hibot: get environment response missing ID")
        return env

    def update(self, params: V1EnvironmentUpdateParams) -> None:
        if not params.env_id:
            raise ValueError("hibot: env id is required")
        payload = {}
        if params.name is not None:
            payload["Name"] = params.name
        if params.description is not None:
            payload["Description"] = params.description
        if params.image_type is not None:
            payload["ImageType"] = params.image_type
        if params.env_vars is not None:
            payload["EnvVars"] = params.env_vars
        if params.cpu_limit is not None:
            payload["CpuLimit"] = params.cpu_limit
        if params.memory_limit is not None:
            payload["MemoryLimit"] = params.memory_limit
        if params.pvc_size is not None:
            payload["PVCSize"] = params.pvc_size
        if params.data_path is not None:
            payload["DataPath"] = params.data_path
        body = {"EnvID": params.env_id, "Payload": payload}
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        self._action("UpdateEnv", body)

    def delete(self, *, env_id: str, workspace_id: str = "") -> None:
        if not env_id:
            raise ValueError("hibot: env id is required")
        body = {"EnvID": env_id}
        if workspace_id:
            body["WorkspaceID"] = workspace_id
        self._action("DeleteEnv", body)

    def default(self, *, workspace_id: str = "") -> V1Environment:
        items = self.list(workspace_id=workspace_id)
        if not items:
            raise ValueError("hibot: no environment found")
        items.sort(key=lambda e: e.created_at or "")
        return items[0]
