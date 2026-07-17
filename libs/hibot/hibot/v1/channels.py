"""V1 Channel service."""

from __future__ import annotations

from typing import List

from ._helpers import from_dict, list_from_items
from ._server_service import ServerService, put_if
from .types import (
    V1Channel,
    V1ChannelDeleteParams,
    V1ChannelGetParams,
    V1ChannelListParams,
    V1ChannelNewParams,
    V1ChannelUpdateParams,
    V1FeishuChannelConfigParams,
    V1WeComChannelConfigParams,
)


def _feishu_config(params: V1FeishuChannelConfigParams) -> dict:
    body = {"AppID": params.app_id, "AppSecret": params.app_secret}
    for key, value in (
        ("EncryptKey", params.encrypt_key),
        ("VerificationToken", params.verification_token),
        ("Domain", params.domain),
        ("ConnectionMode", params.connection_mode),
        ("WebhookPath", params.webhook_path),
        ("RequireMention", params.require_mention),
        ("RenderMode", params.render_mode),
        ("Streaming", params.streaming),
        ("ReactionLevel", params.reaction_level),
        ("TextChunkLimit", params.text_chunk_limit),
        ("MediaMaxMB", params.media_max_mb),
        ("BlockReply", params.block_reply),
    ):
        put_if(body, key, value, allow_empty=True)
    return body


def _wecom_config(params: V1WeComChannelConfigParams) -> dict:
    return {"BotID": params.bot_id, "Secret": params.secret}


def _channel_payload(params) -> dict:
    body = {}
    for key, value in (
        ("Name", params.name),
        ("ChannelType", params.channel_type),
        ("DmPolicy", params.dm_policy),
        ("GroupPolicy", params.group_policy),
        ("Allowlist", params.allowlist),
    ):
        put_if(body, key, value, allow_empty=isinstance(params, V1ChannelUpdateParams))
    if params.feishu_config is not None:
        body["FeishuConfig"] = _feishu_config(params.feishu_config)
    if params.wecom_config is not None:
        body["WeComConfig"] = _wecom_config(params.wecom_config)
    return body


class ChannelsService(ServerService):
    def create(self, params: V1ChannelNewParams) -> V1Channel:
        if not params.agent_id or not params.name:
            raise ValueError("hibot: channel agent id and name are required")
        payload = _channel_payload(params)
        payload["AgentID"] = params.agent_id
        body = {"Payload": payload}
        put_if(body, "WorkspaceID", params.workspace_id)
        result = self._action("CreateChannel", body)
        new_id = result.get("ID") if isinstance(result, dict) else None
        if not new_id:
            raise ValueError("hibot: create channel response missing ID")
        return V1Channel(id=new_id, agent_id=params.agent_id, name=params.name)

    def list(
        self, params: V1ChannelListParams = V1ChannelListParams()
    ) -> List[V1Channel]:
        body = {}
        put_if(body, "AgentID", params.agent_id)
        put_if(body, "WorkspaceID", params.workspace_id)
        return list_from_items(V1Channel, self._action("ListChannels", body))

    def get(self, params: V1ChannelGetParams) -> V1Channel:
        if not params.channel_id:
            raise ValueError("hibot: channel id is required")
        body = {"ChannelID": params.channel_id}
        put_if(body, "WorkspaceID", params.workspace_id)
        result = self._action("GetChannel", body)
        decoded = from_dict(V1Channel, result) or V1Channel()
        if not decoded.id:
            raise ValueError("hibot: get channel response missing ID")
        return decoded

    def update(self, params: V1ChannelUpdateParams) -> None:
        if not params.channel_id:
            raise ValueError("hibot: channel id is required")
        payload = _channel_payload(params)
        put_if(payload, "TargetAgentID", params.target_agent_id, allow_empty=True)
        body = {"ChannelID": params.channel_id, "Payload": payload}
        put_if(body, "WorkspaceID", params.workspace_id)
        self._action("UpdateChannel", body)

    def delete(self, params: V1ChannelDeleteParams) -> None:
        if not params.channel_id:
            raise ValueError("hibot: channel id is required")
        body = {"ChannelID": params.channel_id}
        put_if(body, "WorkspaceID", params.workspace_id)
        self._action("DeleteChannel", body)


__all__ = ["ChannelsService"]
