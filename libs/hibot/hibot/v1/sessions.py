"""V1 Sessions service (mirrors go/hibot/v1/sessions.go + stream.go entry)."""

from __future__ import annotations

import secrets
import threading

from .._request import Action
from .._response import APIError
from .._version import CHAT_VERSION, SERVER_VERSION
from ._helpers import from_dict
from .stream import V1SessionChatStream
from .types import (
    V1_SESSION_CHAT_EVENT_FAILED,
    V1Message,
    V1MessageGetParams,
    V1MessageInjectParams,
    V1MessageList,
    V1MessageListParams,
    V1Session,
    V1SessionArchiveParams,
    V1SessionChatParams,
    V1SessionDeleteParams,
    V1SessionGetByKeyParams,
    V1SessionGetParams,
    V1SessionList,
    V1SessionListParams,
    V1SessionNewParams,
)


def _generate_conversation_id() -> str:
    """生成符合 ``^[A-Za-z0-9_-]{1,64}$`` 的 ConversationID。

    使用 16 字节随机数转 32 位 hex，长度与字符集均严格满足，且各端 SDK 共用
    同一种生成策略。仅在 webchat 渠道下注入。
    """

    return secrets.token_hex(16)


class SessionsService:
    def __init__(self, v1) -> None:
        self._v1 = v1
        self._lock = threading.RLock()
        self._session_agents: dict[str, str] = {}

    def _action(self, name: str, body):
        return self._v1.requester.do_action(
            Action(service=self._v1.services.server, version=SERVER_VERSION, action=name, body=body)
        )

    # CRUD --------------------------------------------------------------

    def create(self, params: V1SessionNewParams) -> V1Session:
        if not params.agent_id:
            raise ValueError("hibot: agent id is required")
        body = {"AgentID": params.agent_id}
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        # Peer 仅在显式指定 IM 渠道或按 user 隔离会话时才需要传入；webchat
        # 主流程下 SDK 注入 webchat / system / agent_id 作为默认值。
        payload = {
            "Channel": "webchat",
            "PeerKind": "system",
            "PeerID": params.agent_id,
        }
        if params.peer is not None:
            if params.peer.channel:
                payload["Channel"] = params.peer.channel
            if params.peer.peer_kind:
                payload["PeerKind"] = params.peer.peer_kind
            if params.peer.peer_id:
                payload["PeerID"] = params.peer.peer_id
        # ConversationID 仅在 webchat 渠道由 SDK 自动生成并透传；其它渠道
        # 留空，这里直接跳过以避免污染请求体。
        if payload["Channel"] == "webchat":
            cid = _generate_conversation_id()
            if cid:
                payload["ConversationID"] = cid
        body["Payload"] = payload
        result = self._action("CreateSession", body)
        session = from_dict(V1Session, result) or V1Session()
        if not session.id:
            raise ValueError("hibot: create session response missing ID")
        session.agent_id = params.agent_id
        with self._lock:
            self._session_agents[session.id] = params.agent_id
        return session

    def list(self, params: V1SessionListParams = V1SessionListParams()) -> V1SessionList:
        body = {}
        if params.agent_id:
            body["AgentID"] = params.agent_id
        if params.status:
            body["Status"] = params.status
        if params.channel:
            body["Channel"] = params.channel
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        if params.page is not None:
            body["Page"] = {"PageNum": params.page.page_num, "PageSize": params.page.page_size}
        result = self._action("ListSessions", body)
        out = V1SessionList()
        if isinstance(result, dict):
            from ._helpers import list_from_items

            out.items = list_from_items(V1Session, result)
            page = result.get("Page")
            if isinstance(page, dict):
                from .types import V1Page

                out.page = from_dict(V1Page, page)
        return out

    def get(self, params: V1SessionGetParams) -> V1Session:
        if not params.session_id:
            raise ValueError("hibot: session id is required")
        body = {"SessionID": params.session_id}
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        result = self._action("GetSession", body)
        session = from_dict(V1Session, result) or V1Session()
        if not session.id:
            raise ValueError("hibot: get session response missing ID")
        return session

    def get_by_key(self, params: V1SessionGetByKeyParams) -> V1Session:
        if not params.session_key:
            raise ValueError("hibot: session key is required")
        body = {"SessionKey": params.session_key}
        if params.agent_id:
            body["AgentID"] = params.agent_id
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        result = self._action("GetSessionByKey", body)
        session = from_dict(V1Session, result) or V1Session()
        if not session.id:
            raise ValueError("hibot: get session by key response missing ID")
        return session

    def archive(self, params: V1SessionArchiveParams) -> None:
        if not params.session_id:
            raise ValueError("hibot: session id is required")
        payload = {}
        if params.summary:
            payload["Summary"] = params.summary
        if params.consolidate is not None:
            payload["Consolidate"] = params.consolidate
        body = {"SessionID": params.session_id}
        if payload:
            body["Payload"] = payload
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        self._action("ArchiveSession", body)

    def delete(self, params: V1SessionDeleteParams) -> None:
        if not params.session_id:
            raise ValueError("hibot: session id is required")
        body = {"SessionID": params.session_id}
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        self._action("DeleteSession", body)

    # Messages ----------------------------------------------------------

    def list_messages(self, params: V1MessageListParams) -> V1MessageList:
        if not params.session_id:
            raise ValueError("hibot: session id is required")
        body = {"SessionID": params.session_id}
        if params.visibility:
            body["Visibility"] = params.visibility
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        if params.page is not None:
            body["Page"] = {"PageNum": params.page.page_num, "PageSize": params.page.page_size}
        result = self._action("ListMessages", body)
        out = V1MessageList()
        if isinstance(result, dict):
            from ._helpers import list_from_items

            out.items = list_from_items(V1Message, result)
            page = result.get("Page")
            if isinstance(page, dict):
                from .types import V1Page

                out.page = from_dict(V1Page, page)
        return out

    def get_message(self, params: V1MessageGetParams) -> V1Message:
        if not params.session_id or not params.message_id:
            raise ValueError("hibot: session id and message id are required")
        body = {"SessionID": params.session_id, "MessageID": params.message_id}
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        result = self._action("GetMessage", body)
        msg = from_dict(V1Message, result) or V1Message()
        if not msg.id:
            raise ValueError("hibot: get message response missing ID")
        return msg

    def inject_message(self, params: V1MessageInjectParams) -> V1Message:
        if not params.session_id:
            raise ValueError("hibot: session id is required")
        payload = {}
        if params.role:
            payload["Role"] = params.role
        if params.content:
            payload["Content"] = params.content
        body = {"SessionID": params.session_id, "Payload": payload}
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        result = self._action("InjectMessage", body)
        msg = from_dict(V1Message, result) or V1Message()
        if not msg.id:
            raise ValueError("hibot: inject message response missing ID")
        return msg

    # Chat --------------------------------------------------------------

    def chat(self, session_id: str, params: V1SessionChatParams) -> V1Message:
        with self.chat_streaming(session_id, params) as stream:
            for event in stream:
                if event.type == V1_SESSION_CHAT_EVENT_FAILED:
                    msg = event.error.message or event.error.code or "unknown error"
                    raise APIError(status_code=0, message=f"hibot: chat failed: {msg}")
            if stream.err is not None:
                raise stream.err
            return stream.final_message()

    def chat_streaming(self, session_id: str, params: V1SessionChatParams) -> V1SessionChatStream:
        if not session_id:
            return V1SessionChatStream(error=ValueError("hibot: session id is required"))
        agent_id = params.agent_id
        if not agent_id:
            agent_id = self._agent_id_for_session(session_id)
        body = {
            "SessionID": session_id,
            "AgentID": agent_id,
            "Content": params.input,
        }
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        if params.client_message_id:
            body["ClientMessageID"] = params.client_message_id
        try:
            resp = self._v1.requester.stream_action(
                Action(
                    service=self._v1.services.gateway,
                    version=CHAT_VERSION,
                    action="Chat",
                    body=body,
                )
            )
        except Exception as exc:  # noqa: BLE001
            return V1SessionChatStream(error=exc)
        if resp.status_code >= 400:
            try:
                body_bytes = resp.read_all()
            finally:
                resp.close()
            return V1SessionChatStream(
                error=APIError(status_code=resp.status_code, message=body_bytes.decode("utf-8", "replace"))
            )
        return V1SessionChatStream(resp=resp)

    # internal ----------------------------------------------------------

    def _agent_id_for_session(self, session_id: str) -> str:
        with self._lock:
            return self._session_agents.get(session_id, "")


__all__ = ["SessionsService"]
