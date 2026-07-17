"""V1 Skills service."""

from __future__ import annotations

from typing import List

from .._request import Action
from .._version import SERVER_VERSION
from ._helpers import from_dict, list_from_items
from .types import (
    V1ArkSkillHubGetParams,
    V1ArkSkillHubImportParams,
    V1ArkSkillHubListParams,
    V1ArkSkillHubSkill,
    V1ArkSkillHubSkillList,
    V1Page,
    V1Skill,
    V1SkillBatchGetParams,
    V1SkillCredentialInputParams,
    V1SkillDeleteParams,
    V1SkillGetParams,
    V1SkillListParams,
    V1SkillNewParams,
    V1SkillParseParams,
    V1SkillParseResult,
    V1SkillResolveVersionParams,
    V1SkillUpdateParams,
    V1SkillVersion,
    V1SkillVersionListParams,
)


def _credential_config_to_dict(cfg: V1SkillCredentialInputParams) -> dict:
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


class SkillsService:
    def __init__(self, v1) -> None:
        self._v1 = v1

    def _action(self, name: str, body):
        return self._v1.requester.do_action(
            Action(
                service=self._v1.services.server,
                version=SERVER_VERSION,
                action=name,
                body=body,
            )
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
        if params.credential_config is not None:
            body["CredentialConfig"] = _credential_config_to_dict(
                params.credential_config
            )
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

    def parse(self, params: V1SkillParseParams) -> V1SkillParseResult:
        if not params.blob_id:
            raise ValueError("hibot: skill blob id is required")
        body = {"BlobID": params.blob_id}
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        result = self._action("ParseSkill", body)
        return from_dict(V1SkillParseResult, result) or V1SkillParseResult()

    def list_ark_skill_hub(
        self, params: V1ArkSkillHubListParams = V1ArkSkillHubListParams()
    ) -> V1ArkSkillHubSkillList:
        body = {}
        if params.keyword:
            body["Keyword"] = params.keyword
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        if params.page is not None:
            body["Page"] = {
                "PageNum": params.page.page_num,
                "PageSize": params.page.page_size,
            }
        result = self._action("ListArkSkillHubSkills", body)
        out = V1ArkSkillHubSkillList()
        if isinstance(result, dict):
            out.items = list_from_items(V1ArkSkillHubSkill, result)
            out.page = from_dict(V1Page, result.get("Page"))
        return out

    def get_ark_skill_hub(self, params: V1ArkSkillHubGetParams) -> V1ArkSkillHubSkill:
        if not params.slug:
            raise ValueError("hibot: Ark Skill Hub slug is required")
        body = {"Slug": params.slug}
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        result = self._action("GetArkSkillHubSkill", body)
        skill = result.get("Skill") if isinstance(result, dict) else None
        decoded = from_dict(V1ArkSkillHubSkill, skill) or V1ArkSkillHubSkill()
        if not decoded.slug:
            raise ValueError("hibot: get Ark Skill Hub skill response missing Slug")
        return decoded

    def import_ark_skill_hub(
        self, params: V1ArkSkillHubImportParams
    ) -> V1SkillParseResult:
        if not params.slug:
            raise ValueError("hibot: Ark Skill Hub slug is required")
        body = {"Slug": params.slug}
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        result = self._action("ImportArkSkillHubSkill", body)
        return from_dict(V1SkillParseResult, result) or V1SkillParseResult()

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
        if params.page is not None:
            body["Page"] = {
                "PageNum": params.page.page_num,
                "PageSize": params.page.page_size,
            }
        result = self._action("ListSkills", body)
        return list_from_items(V1Skill, result)

    def batch_get(self, params: V1SkillBatchGetParams) -> List[V1Skill]:
        if not params.ids:
            raise ValueError("hibot: skill version IDs are required")
        body = {"IDs": list(params.ids)}
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        result = self._action("BatchGetSkills", body)
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
        blob_id = params.blob_id
        if blob_id is None:
            # Compatibility for the old SDK field; the current server accepts BlobID.
            blob_id = params.artifact_id
        if blob_id is not None:
            body["BlobID"] = blob_id
        if params.enabled is not None:
            body["Enabled"] = params.enabled
        if params.new_version is not None:
            body["NewVersion"] = params.new_version
        if params.slug_id is not None:
            body["SlugID"] = params.slug_id
        if params.credential_config is not None:
            body["CredentialConfig"] = _credential_config_to_dict(
                params.credential_config
            )
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
            body["Page"] = {
                "PageNum": params.page.page_num,
                "PageSize": params.page.page_size,
            }
        result = self._action("ListSkillVersions", body)
        return list_from_items(V1SkillVersion, result)

    def resolve_version(self, params: V1SkillResolveVersionParams) -> V1SkillVersion:
        if params.id:
            return V1SkillVersion(
                id=params.id, name=params.name, constraint=params.constraint
            )
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
