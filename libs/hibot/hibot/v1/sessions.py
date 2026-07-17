"""V1 Sessions service (mirrors go/hibot/v1/sessions.go + stream.go entry)."""

from __future__ import annotations

import threading

from .._request import Action
from .._response import APIError
from .._version import SERVER_VERSION
from ._helpers import from_dict
from .stream import V1SessionChatStream
from .types import (
    V1ChatApproveParams,
    V1ChatCancelRunParams,
    V1ChatCommandResult,
    V1ChatResumeParams,
    V1Message,
    V1MessageGetParams,
    V1MessageInjectParams,
    V1MessageList,
    V1MessageListParams,
    V1Session,
    V1SessionArchiveParams,
    V1SessionBatchGetParams,
    V1SessionChatParams,
    V1SessionDeleteParams,
    V1SessionGetByKeyParams,
    V1SessionGetParams,
    V1SessionList,
    V1SessionListParams,
    V1SessionNewParams,
    V1WebChatResumeHint,
)


class SessionsService:
    def __init__(self, v1) -> None:
        self._v1 = v1
        self._lock = threading.RLock()
        self._session_agents: dict[str, str] = {}

    def _action(self, name: str, body):
        return self._v1.requester.do_action(
            Action(
                service=self._v1.services.server,
                version=SERVER_VERSION,
                action=name,
                body=body,
            )
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
        # For a new WebChat session the server derives identity from the new
        # SessionID. ConversationID is sent only when the caller explicitly
        # opts into a stable multi-session identity.
        for key, value in (
            ("SessionKey", params.session_key),
            ("RiskLevel", params.risk_level),
            ("Config", params.config),
            ("AuthContext", params.auth_context),
            ("Metadata", params.metadata),
            ("ConversationID", params.conversation_id),
        ):
            if value not in (None, ""):
                payload[key] = value
        body["Payload"] = payload
        result = self._action("CreateSession", body)
        session = from_dict(V1Session, result) or V1Session()
        if not session.id:
            raise ValueError("hibot: create session response missing ID")
        session.agent_id = params.agent_id
        with self._lock:
            self._session_agents[session.id] = params.agent_id
        return session

    def list(
        self, params: V1SessionListParams = V1SessionListParams()
    ) -> V1SessionList:
        body = {}
        if params.agent_id:
            body["AgentID"] = params.agent_id
        if params.status:
            body["Status"] = params.status
        if params.channel:
            body["Channel"] = params.channel
        if params.session_keys:
            body["SessionKeys"] = params.session_keys
        if params.user_id:
            body["UserID"] = params.user_id
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        if params.page is not None:
            body["Page"] = {
                "PageNum": params.page.page_num,
                "PageSize": params.page.page_size,
            }
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

    def batch_get(self, params: V1SessionBatchGetParams) -> V1SessionList:
        if not params.session_ids:
            raise ValueError("hibot: session ids are required")
        body = {"SessionIDs": params.session_ids}
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        result = self._action("BatchGetSessions", body)
        out = V1SessionList()
        if isinstance(result, dict):
            from ._helpers import list_from_items

            out.items = list_from_items(V1Session, result)
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
        if params.display_mode:
            body["DisplayMode"] = params.display_mode
        if params.base_message_id:
            body["BaseMessageID"] = params.base_message_id
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        if params.page is not None:
            body["Page"] = {
                "PageNum": params.page.page_num,
                "PageSize": params.page.page_size,
            }
        result = self._action("ListMessages", body)
        out = V1MessageList()
        if isinstance(result, dict):
            from ._helpers import list_from_items

            out.items = list_from_items(V1Message, result)
            page = result.get("Page")
            if isinstance(page, dict):
                from .types import V1Page

                out.page = from_dict(V1Page, page)
            out.resume_hint = from_dict(V1WebChatResumeHint, result.get("ResumeHint"))
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
        if params.tool_calls is not None:
            payload["ToolCalls"] = params.tool_calls
        if params.tool_result is not None:
            payload["ToolResult"] = params.tool_result
        if params.metadata is not None:
            payload["Metadata"] = params.metadata
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
        body = self._chat_body(session_id, params)
        body["Approve"] = "all"
        body["Stream"] = False
        result = self._v1.requester.do_long_action(
            Action(
                service=self._v1.services.server,
                version=SERVER_VERSION,
                action="Chat",
                body=body,
            )
        )
        message = V1Message(
            session_id=session_id,
            role="assistant",
            content=result.get("Message", "") if isinstance(result, dict) else "",
            token_count=result.get("TokenCount") if isinstance(result, dict) else None,
        )
        if isinstance(result, dict) and isinstance(result.get("Files"), list):
            from ._helpers import list_from_items
            from .types import V1MessageFile

            message.files = list_from_items(V1MessageFile, {"Items": result["Files"]})
        return message

    def chat_streaming(
        self, session_id: str, params: V1SessionChatParams
    ) -> V1SessionChatStream:
        return self._chat_streaming(session_id, params, auto_approve_all=False)

    def chat_resume(self, params: V1ChatResumeParams) -> V1SessionChatStream:
        if not params.session_id:
            return V1SessionChatStream(
                error=ValueError("hibot: session id is required")
            )
        agent_id = self._resolve_agent_id(
            params.session_id,
            V1SessionChatParams(
                agent_id=params.agent_id,
                workspace_id=params.workspace_id,
            ),
        )
        body = {"SessionID": params.session_id, "AgentID": agent_id}
        for key, value in (
            ("RunID", params.run_id),
            ("RequestID", params.request_id),
            ("LastEventID", params.last_event_id),
            ("Approve", params.approve),
            ("WorkspaceID", params.workspace_id),
        ):
            if value:
                body[key] = value
        return self._open_stream("ChatResume", body)

    def approve(self, params: V1ChatApproveParams) -> V1ChatCommandResult:
        if not all(
            (
                params.session_id,
                params.run_id,
                params.approval_request_id,
                params.choice_id,
            )
        ):
            raise ValueError(
                "hibot: session id, run id, approval request id, and choice id are required"
            )
        body = {
            "SessionID": params.session_id,
            "RunID": params.run_id,
            "ApprovalRequestID": params.approval_request_id,
            "ChoiceID": params.choice_id,
        }
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        result = self._action("Approve", body)
        return from_dict(V1ChatCommandResult, result) or V1ChatCommandResult()

    def cancel_run(self, params: V1ChatCancelRunParams) -> V1ChatCommandResult:
        if not params.session_id or not params.run_id:
            raise ValueError("hibot: session id and run id are required")
        body = {"SessionID": params.session_id, "RunID": params.run_id}
        if params.reason:
            body["Reason"] = params.reason
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        result = self._action("CancelRun", body)
        return from_dict(V1ChatCommandResult, result) or V1ChatCommandResult()

    def _chat_streaming(
        self,
        session_id: str,
        params: V1SessionChatParams,
        auto_approve_all: bool,
    ) -> V1SessionChatStream:
        if not session_id:
            return V1SessionChatStream(
                error=ValueError("hibot: session id is required")
            )
        body = self._chat_body(session_id, params)
        if auto_approve_all:
            body["Approve"] = "all"
        body["Stream"] = True
        return self._open_stream("Chat", body)

    def _chat_body(self, session_id: str, params: V1SessionChatParams) -> dict:
        if not session_id:
            raise ValueError("hibot: session id is required")
        agent_id = self._resolve_agent_id(session_id, params)
        body = {
            "SessionID": session_id,
            "AgentID": agent_id,
            "Content": params.input,
        }
        if params.files:
            files_payload = []
            for f in params.files:
                entry: dict = {}
                if f.file_id:
                    entry["FileID"] = f.file_id
                if f.name:
                    entry["Name"] = f.name
                if f.content_type:
                    entry["ContentType"] = f.content_type
                if f.url:
                    entry["URL"] = f.url
                if f.blob_id:
                    entry["BlobID"] = f.blob_id
                files_payload.append(entry)
            body["Files"] = files_payload
        if params.workspace_id:
            body["WorkspaceID"] = params.workspace_id
        if params.client_message_id:
            body["ClientMessageID"] = params.client_message_id
        if params.conversation_id:
            body["ConversationID"] = params.conversation_id
        return body

    # internal ----------------------------------------------------------

    def _open_stream(self, action: str, body: dict) -> V1SessionChatStream:
        try:
            resp = self._v1.requester.stream_action(
                Action(
                    service=self._v1.services.server,
                    version=SERVER_VERSION,
                    action=action,
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
                error=APIError(
                    status_code=resp.status_code,
                    message=body_bytes.decode("utf-8", "replace"),
                )
            )
        return V1SessionChatStream(resp=resp)

    def _agent_id_for_session(self, session_id: str) -> str:
        with self._lock:
            return self._session_agents.get(session_id, "")

    def _resolve_agent_id(self, session_id: str, params: V1SessionChatParams) -> str:
        if params.agent_id:
            return params.agent_id
        cached = self._agent_id_for_session(session_id)
        if cached:
            return cached
        try:
            session = self.get(
                V1SessionGetParams(
                    session_id=session_id,
                    workspace_id=params.workspace_id,
                )
            )
        except Exception as exc:  # noqa: BLE001
            raise ValueError(
                f"hibot: resolve agent id for session {session_id!r}: {exc}"
            ) from exc
        if not session.agent_id:
            raise ValueError(
                f"hibot: session {session_id!r} response missing AgentID; "
                "pass V1SessionChatParams.agent_id explicitly"
            )
        with self._lock:
            self._session_agents[session_id] = session.agent_id
        return session.agent_id


__all__ = ["SessionsService"]
