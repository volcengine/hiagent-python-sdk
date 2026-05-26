"""V1 Agents service."""

from __future__ import annotations

from typing import List, Optional

from .._request import Action
from .._version import SERVER_VERSION
from ._helpers import from_dict, list_from_items
from .types import (
    V1Agent,
    V1AgentBatchGetParams,
    V1AgentDeleteParams,
    V1AgentGetParams,
    V1AgentListParams,
    V1AgentNewParams,
    V1AgentUpdateParams,
)


def _build_resource_input(resources):
    if not resources:
        return None
    resource_ids = []
    directory_ids = []
    for r in resources:
        if r.directory_id:
            directory_ids.append(r.directory_id)
        elif r.id:
            resource_ids.append(r.id)
    out = {}
    if resource_ids:
        out["ResourceIDs"] = resource_ids
    if directory_ids:
        out["DirectoryIDs"] = directory_ids
    return out or None


def _build_tool_bindings(tools):
    skills = []
    mcps = []
    if not tools:
        return skills, mcps
    for t in tools:
        if t.of_skill is not None and t.of_skill.skill_version_id:
            skills.append({"ID": t.of_skill.skill_version_id})
        if t.of_mcp is not None and t.of_mcp.id:
            mcps.append({"ID": t.of_mcp.id, "Enabled": True})
    return skills, mcps


class AgentsService:
    def __init__(self, v1) -> None:
        self._v1 = v1

    def _action(self, name: str, body):
        return self._v1.requester.do_action(
            Action(service=self._v1.services.server, version=SERVER_VERSION, action=name, body=body)
        )

    def create(self, params: Optional[V1AgentNewParams] = None, **kwargs) -> V1Agent:
        if params is None:
            params = V1AgentNewParams(**kwargs)
        env_id = params.env_id
        if not env_id:
            env = self._v1.environments.default(workspace_id=params.workspace_id)
            env_id = env.id
        body = {
            "Name": params.name,
            "ModelID": params.model.id,
            "EnvID": env_id,
        }
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        if params.system is not None:
            body["SystemPrompt"] = params.system
        resources = _build_resource_input(params.resources)
        if resources:
            body["Resources"] = resources
        skills, mcps = _build_tool_bindings(params.tools)
        if skills:
            body["Skills"] = skills
        if mcps:
            body["MCPs"] = mcps
        result = self._action("CreateAgent", body)
        agent = from_dict(V1Agent, result) or V1Agent()
        if not agent.id:
            raise ValueError("hibot: create agent response missing ID")
        agent.name = agent.name or params.name
        agent.model_id = agent.model_id or params.model.id
        return agent

    def list(self, params: V1AgentListParams = V1AgentListParams()) -> List[V1Agent]:
        body = {}
        if params.keyword:
            body["Keyword"] = params.keyword
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        result = self._action("ListAgents", body)
        return list_from_items(V1Agent, result)

    def get(self, params: V1AgentGetParams) -> V1Agent:
        if not params.agent_id:
            raise ValueError("hibot: agent id is required")
        body = {"AgentID": params.agent_id}
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        result = self._action("GetAgent", body)
        agent = from_dict(V1Agent, result) or V1Agent()
        if not agent.id:
            raise ValueError("hibot: get agent response missing ID")
        return agent

    def batch_get(self, params: V1AgentBatchGetParams) -> List[V1Agent]:
        if not params.agent_ids:
            raise ValueError("hibot: AgentIDs is required")
        body = {"AgentIDs": list(params.agent_ids)}
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        result = self._action("BatchGetAgents", body)
        return list_from_items(V1Agent, result)

    def update(self, params: V1AgentUpdateParams) -> None:
        if not params.agent_id:
            raise ValueError("hibot: agent id is required")
        body = {"AgentID": params.agent_id}
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        if params.description is not None:
            body["Description"] = params.description
        if params.model_id is not None:
            body["ModelID"] = params.model_id
        if params.env_id is not None:
            body["EnvID"] = params.env_id
        if params.system is not None:
            body["SystemPrompt"] = params.system
        if params.skills is not None:
            skills_list = []
            for t in params.skills:
                if not t.skill_version_id:
                    continue
                skills_list.append({"ID": t.skill_version_id})
            body["Skills"] = skills_list
        if params.mcps is not None:
            mcps_list = []
            for t in params.mcps:
                if not t.id:
                    continue
                mcps_list.append({"ID": t.id, "Enabled": True})
            body["MCPs"] = mcps_list
        if params.reset_resources or params.resources:
            resources = _build_resource_input(params.resources)
            body["Resources"] = resources or {}
        self._action("UpdateAgent", body)

    def delete(self, params: V1AgentDeleteParams) -> None:
        if not params.agent_id:
            raise ValueError("hibot: agent id is required")
        body = {"AgentID": params.agent_id}
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        self._action("DeleteAgent", body)
