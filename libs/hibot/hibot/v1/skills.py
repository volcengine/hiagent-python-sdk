"""V1 Skills service."""

from __future__ import annotations

from typing import List

from .._request import Action
from .._version import SERVER_VERSION
from ._helpers import from_dict, list_from_items
from .types import (
    V1Skill,
    V1SkillDeleteParams,
    V1SkillGetParams,
    V1SkillListParams,
    V1SkillNewParams,
    V1SkillResolveVersionParams,
    V1SkillUpdateParams,
    V1SkillVersion,
    V1SkillVersionListParams,
)


class SkillsService:
    def __init__(self, v1) -> None:
        self._v1 = v1

    def _action(self, name: str, body):
        return self._v1.requester.do_action(
            Action(service=self._v1.services.server, version=SERVER_VERSION, action=name, body=body)
        )

    def create(self, params: V1SkillNewParams) -> V1SkillVersion:
        body = {
            "Name": params.name,
            "Description": params.description,
            "Source": params.source or "manual",
            "Version": params.version,
        }
        if params.skill_id:
            body["SkillID"] = params.skill_id
        if params.blob_id:
            body["BlobID"] = params.blob_id
        if params.enabled is not None:
            body["Enabled"] = params.enabled
        if params.slug_id:
            body["SlugID"] = params.slug_id
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        result = self._action("CreateSkill", body)
        new_id = result.get("ID") if isinstance(result, dict) else None
        if not new_id:
            raise ValueError("hibot: create skill response missing ID")
        return V1SkillVersion(
            id=new_id,
            skill_id=params.skill_id,
            name=params.name,
            version=params.version,
        )

    def list(self, params: V1SkillListParams = V1SkillListParams()) -> List[V1Skill]:
        body = {}
        if params.keyword:
            body["Keyword"] = params.keyword
        if params.source:
            body["Source"] = params.source
        if params.name:
            body["Name"] = params.name
        if params.slug_id:
            body["SlugID"] = params.slug_id
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        result = self._action("ListSkills", body)
        return list_from_items(V1Skill, result)

    def get(self, params: V1SkillGetParams) -> V1Skill:
        if not params.id and not params.skill_id:
            raise ValueError("hibot: skill id or skill_id is required")
        body = {}
        if params.id:
            body["ID"] = params.id
        if params.skill_id:
            body["SkillID"] = params.skill_id
        if params.version:
            body["Version"] = params.version
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        result = self._action("GetSkill", body)
        decoded = from_dict(V1Skill, result) or V1Skill()
        if not decoded.id:
            raise ValueError("hibot: get skill response missing ID")
        return decoded

    def update(self, params: V1SkillUpdateParams) -> None:
        if not params.id and not params.skill_id:
            raise ValueError("hibot: skill id or skill_id is required")
        body = {}
        if params.id:
            body["ID"] = params.id
        if params.skill_id:
            body["SkillID"] = params.skill_id
        if params.version:
            body["Version"] = params.version
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        if params.description is not None:
            body["Description"] = params.description
        if params.source is not None:
            body["Source"] = params.source
        if params.artifact_id is not None:
            body["ArtifactID"] = params.artifact_id
        if params.enabled is not None:
            body["Enabled"] = params.enabled
        if params.new_version is not None:
            body["NewVersion"] = params.new_version
        if params.slug_id is not None:
            body["SlugID"] = params.slug_id
        self._action("UpdateSkill", body)

    def delete(self, params: V1SkillDeleteParams) -> None:
        if not params.id and not params.skill_id:
            raise ValueError("hibot: skill id or skill_id is required")
        body = {}
        if params.id:
            body["ID"] = params.id
        if params.skill_id:
            body["SkillID"] = params.skill_id
        if params.version:
            body["Version"] = params.version
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        self._action("DeleteSkill", body)

    def list_versions(self, params: V1SkillVersionListParams) -> List[V1SkillVersion]:
        if not params.skill_id:
            raise ValueError("hibot: skill_id is required")
        body = {"SkillID": params.skill_id}
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        if params.sort_by:
            body["SortBy"] = params.sort_by
        if params.sort_order:
            body["SortOrder"] = params.sort_order
        if params.page is not None:
            body["Page"] = {"PageNum": params.page.page_num, "PageSize": params.page.page_size}
        result = self._action("ListSkillVersions", body)
        return list_from_items(V1SkillVersion, result)

    def resolve_version(self, params: V1SkillResolveVersionParams) -> V1SkillVersion:
        if params.id:
            return V1SkillVersion(id=params.id, name=params.name, constraint=params.constraint)
        skill_id = self._resolve_skill_id(params)
        body = {"SkillID": skill_id}
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        result = self._action("ListSkillVersions", body)
        items = list_from_items(V1SkillVersion, result)
        if not items or not items[0].id:
            raise ValueError(
                f'hibot: no skill version matched name="{params.name}" constraint="{params.constraint}"'
            )
        v = items[0]
        v.name = params.name
        v.constraint = params.constraint
        return v

    def _resolve_skill_id(self, params: V1SkillResolveVersionParams) -> str:
        body = {"Name": params.name}
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        result = self._action("ListSkills", body)
        if isinstance(result, dict):
            for item in result.get("Items") or []:
                if item.get("Name") == params.name and item.get("SkillID"):
                    return item["SkillID"]
            for item in result.get("Items") or []:
                if item.get("SkillID"):
                    return item["SkillID"]
        raise ValueError(f'hibot: skill "{params.name}" not found')
