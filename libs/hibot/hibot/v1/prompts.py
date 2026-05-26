"""V1 Prompts service."""

from __future__ import annotations

from typing import List

from .._request import Action
from .._version import SERVER_VERSION
from ._helpers import list_from_items
from .types import (
    V1Prompt,
    V1PromptDeleteParams,
    V1PromptListParams,
    V1PromptNewParams,
    V1PromptUpdateParams,
)


class PromptsService:
    def __init__(self, v1) -> None:
        self._v1 = v1

    def _action(self, name: str, body):
        return self._v1.requester.do_action(
            Action(service=self._v1.services.server, version=SERVER_VERSION, action=name, body=body)
        )

    def create(self, params: V1PromptNewParams) -> V1Prompt:
        body = {
            "Payload": {
                "Name": params.name,
                "SystemPrompt": params.content,
            }
        }
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        result = self._action("CreateAgentPromptTemplate", body)
        new_id = result.get("ID") if isinstance(result, dict) else None
        return V1Prompt(id=new_id, name=params.name, content=params.content)

    def list(self, params: V1PromptListParams = V1PromptListParams()) -> List[V1Prompt]:
        body = {}
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        result = self._action("ListAgentPromptTemplates", body)
        return list_from_items(V1Prompt, result)

    def update(self, params: V1PromptUpdateParams) -> None:
        if not params.id:
            raise ValueError("hibot: prompt id is required")
        payload = {}
        if params.name is not None:
            payload["Name"] = params.name
        if params.content is not None:
            payload["SystemPrompt"] = params.content
        body = {"ID": params.id, "Payload": payload}
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        self._action("UpdateAgentPromptTemplate", body)

    def delete(self, params: V1PromptDeleteParams) -> None:
        if not params.id:
            raise ValueError("hibot: prompt id is required")
        body = {"ID": params.id}
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        self._action("DeleteAgentPromptTemplate", body)
