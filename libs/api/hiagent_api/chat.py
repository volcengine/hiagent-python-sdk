# Copyright (c) 2024 Bytedance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json
from typing import AsyncGenerator, Generator, Optional
from urllib.parse import urlparse

from volcengine.ApiInfo import ApiInfo
from volcengine.Credentials import Credentials
from volcengine.ServiceInfo import ServiceInfo

from hiagent_api.base import AppAPIMixin, Service
from hiagent_api.chat_types import (
    AgentIntentionChatEvent,
    AgentJumpChatEvent,
    AgentTakeOverChatEvent,
    AgentThoughtChatEvent,
    AgentThoughtEndChatEvent,
    AgentThoughtUpdateChatEvent,
    BlockingChatResponse,
    ChatEvent,
    ChatRequest,
    CreateConversationRequest,
    CreateConversationResponse,
    GetAppConfigPreviewRequest,
    GetAppConfigPreviewResponse,
    InterruptedChatEvent,
    KnowledgeGraphRetrieveChatEvent,
    KnowledgeGraphRetrieveEndChatEvent,
    KnowledgeRetrieveChatEvent,
    KnowledgeRetrieveEndChatEvent,
    LongTermMemoryRetrieveChatEvent,
    LongTermMemoryRetrieveEndChatEvent,
    MessageChatEvent,
    MessageCostChatEvent,
    MessageEndChatEvent,
    MessageFailedChatEvent,
    MessageOutputEndChatEvent,
    MessageOutputStartChatEvent,
    MessageStartChatEvent,
    QARetrieveChatEvent,
    StreamingChatEventType,
    SuggestionChatEvent,
    SuggestionCostChatEvent,
    TerminologyRetrieveChatEvent,
    TerminologyRetrieveEndChatEvent,
    ThinkMessageChatEvent,
    ThinkMessageOutputEndChatEvent,
    ThinkMessageOutputStartChatEvent,
    ToolMessageChatEvent,
    ToolMessageOutputEndChatEvent,
    ToolMessageOutputStartChatEvent,
    ChatAgainRequest, GetConversationListRequest, GetConversationListResponse, GetConversationInputsRequest,
    GetConversationInputsResponse, UpdateConversationRequest, EmptyResponse, DeleteConversationRequest,
    StopMessageRequest, ClearMessageRequest, GetConversationMessageRequest, GetConversationMessageResponse,
    GetMessageInfoRequest, GetMessageInfoResponse, DeleteMessageRequest, FeedbackRequest, SetMessageAnswerUsedRequest,
    GetSuggestedQuestionsRequest, GetSuggestedQuestionsResponse, RunAppWorkflowRequest, RunAppWorkflowResponse,
    SyncRunAppWorkflowRequest, SyncRunAppWorkflowResponse, QueryRunAppProcessRequest, QueryRunAppProcessResponse,
    ListOauth2TokenRequest, ListOauth2TokenResponse, EventTriggerWebhookResponse, ChatContinueRequest,
    ListLongMemoryRequest, ListLongMemoryResponse, UpdateLongMemoryRequest, DeleteLongMemoryRequest,
    ClearLongMemoryRequest, AsyncResumeAppWorkflowRequest, AsyncResumeAppWorkflowResponse, SetConversationTopRequest,
    CancelConversationTopRequest, QueryAppSkillAsyncTaskRequest, QueryAppSkillAsyncTaskResponse,
    SyncResumeAppWorkflowRequest, SyncResumeAppWorkflowResponse, WorkflowEvent, StreamingWorkflowEventType,
    FlowStartWorkflowEvent, FlowEndWorkflowEvent, FlowErrorWorkflowEvent, ToolMessageOutputEndWorkflowEvent,
    ToolMessageOutputStartWorkflowEvent, ToolMessageWorkflowEvent, FlowCostWorkflowEvent, FlowInterruptedWorkflowEvent,
    MessageOutputStartWorkflowEvent, MessageOutputEndWorkflowEvent, MessageWorkflowEvent, GetAppUserVariablesRequest,
    GetAppUserVariablesResponse, SetAppUserVariablesRequest, QueryTriggerRunRecordsRequest,
    QueryTriggerRunRecordsResponse,
)


class ChatService(Service, AppAPIMixin):
    def __init__(self, endpoint="https://open.volcengineapi.com", region="cn-north-1"):
        self.service_info = ChatService.get_service_info(endpoint, region)
        self.api_info = ChatService.get_api_info()
        super().__init__(self.service_info, self.api_info)
        AppAPIMixin.__init__(self, self.http_client, self.async_http_client)

    @staticmethod
    def get_service_info(endpoint: str, region: str):
        parsed = urlparse(endpoint)
        scheme, hostname = parsed.scheme, parsed.hostname + ":" + str(parsed.port)
        if not scheme or not hostname:
            raise Exception(f"invalid endpoint format: {endpoint}")
        service_info = ServiceInfo(
            hostname,
            {"Accept": "application/json"},
            Credentials("", "", "app", region),
            connection_timeout=5,
            socket_timeout=5 * 60,
            scheme=scheme,
        )
        return service_info

    @staticmethod
    def get_api_info() -> dict[str, ApiInfo]:
        api_info = {}
        return api_info

    def create_conversation(
            self, app_key: str, conversation: CreateConversationRequest
    ) -> CreateConversationResponse:
        """创建会话
        Args:
            app_key: app key
            conversation: CreateConversationRequest

        Returns:
            CreateConversationResponse
        """
        return CreateConversationResponse.model_validate_json(
            self._post(
                app_key, "create_conversation", conversation.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    async def acreate_conversation(
            self, app_key: str, conversation: CreateConversationRequest
    ) -> CreateConversationResponse:
        """创建会话
        Args:
            app_key: app key
            conversation: CreateConversationRequest

        Returns:
            CreateConversationResponse
        """
        return CreateConversationResponse.model_validate_json(
            await self._apost(
                app_key, "create_conversation", conversation.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    def get_app(
            self, app_key: str, params: GetAppConfigPreviewRequest
    ) -> GetAppConfigPreviewResponse:
        return GetAppConfigPreviewResponse.model_validate_json(
            self._post(
                app_key, "get_app_config_preview", params.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    async def aget_app(
            self, app_key: str, params: GetAppConfigPreviewRequest
    ) -> GetAppConfigPreviewResponse:
        return GetAppConfigPreviewResponse.model_validate_json(
            await self._apost(
                app_key, "get_app_config_preview", params.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    def chat_blocking(self, app_key: str, chat: ChatRequest) -> BlockingChatResponse:
        chat.response_mode = "blocking"
        res = self._post(app_key, "chat_query_v2", chat.model_dump(by_alias=True))

        return BlockingChatResponse.model_validate_json(res, by_alias=True)

    async def achat_blocking(
            self, app_key: str, chat: ChatRequest
    ) -> BlockingChatResponse:
        chat.response_mode = "blocking"
        res = await self._apost(
            app_key, "chat_query_v2", chat.model_dump(by_alias=True)
        )

        return BlockingChatResponse.model_validate_json(res, by_alias=True)

    def chat_streaming(
            self, app_key: str, chat: ChatRequest
    ) -> Generator[ChatEvent, None, None]:
        chat.response_mode = "streaming"
        params = chat.model_dump(by_alias=True)
        g = self._sse_post(app_key, "chat_query_v2", params)
        for event in g:
            event_data = json.loads(event.data)
            chat_event = parse_chat_event(event_data)
            if chat_event:
                yield chat_event

    async def achat_streaming(
            self, app_key: str, chat: ChatRequest
    ) -> AsyncGenerator[ChatEvent, None]:
        chat.response_mode = "streaming"
        params = chat.model_dump(by_alias=True)
        g = self._asse_post(app_key, "chat_query_v2", params)
        async for event in g:
            event_data = json.loads(event.data)
            chat_event = parse_chat_event(event_data)
            if chat_event:
                yield chat_event

    def chat_again(
            self, app_key: str, chat_again: ChatAgainRequest
    ) -> Generator[ChatEvent, None, None]:
        params = chat_again.model_dump(by_alias=True)
        g = self._sse_post(app_key, "query_again_v2", params)
        for event in g:
            event_data = json.loads(event.data)
            chat_event = parse_chat_event(event_data)
            if chat_event:
                yield chat_event

    async def achat_again(
            self, app_key: str, chat_again: ChatAgainRequest
    ) -> AsyncGenerator[ChatEvent, None]:
        params = chat_again.model_dump(by_alias=True)
        g = self._asse_post(app_key, "query_again_v2", params)
        async for event in g:
            event_data = json.loads(event.data)
            chat_event = parse_chat_event(event_data)
            if chat_event:
                yield chat_event

    def get_conversation_list(
            self, app_key: str, req: GetConversationListRequest
    ) -> GetConversationListResponse:
        return GetConversationListResponse.model_validate_json(
            self._post(
                app_key, "get_conversation_list", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    async def aget_conversation_list(
            self, app_key: str, req: GetConversationListRequest
    ) -> GetConversationListResponse:
        return GetConversationListResponse.model_validate_json(
            await self._apost(
                app_key, "get_conversation_list", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    def get_conversation_inputs(
            self, app_key: str, req: GetConversationInputsRequest
    ) -> GetConversationInputsResponse:
        return GetConversationInputsResponse.model_validate_json(
            self._post(
                app_key, "get_conversation_inputs", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    async def aget_conversation_inputs(
            self, app_key: str, req: GetConversationInputsRequest
    ) -> GetConversationInputsResponse:
        return GetConversationInputsResponse.model_validate_json(
            await self._apost(
                app_key, "get_conversation_inputs", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    def update_conversation(
            self, app_key: str, req: UpdateConversationRequest
    ) -> EmptyResponse:
        return EmptyResponse.model_validate_json(
            self._post(
                app_key, "update_conversation", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    async def aupdate_conversation(
            self, app_key: str, req: UpdateConversationRequest
    ) -> EmptyResponse:
        return EmptyResponse.model_validate_json(
            await self._apost(
                app_key, "update_conversation", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    def delete_conversation(
            self, app_key: str, req: DeleteConversationRequest
    ) -> EmptyResponse:
        return EmptyResponse.model_validate_json(
            self._post(
                app_key, "delete_conversation", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    async def adelete_conversation(
            self, app_key: str, req: DeleteConversationRequest
    ) -> EmptyResponse:
        return EmptyResponse.model_validate_json(
            await self._apost(
                app_key, "delete_conversation", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    def stop_message(
            self, app_key: str, req: StopMessageRequest
    ) -> EmptyResponse:
        return EmptyResponse.model_validate_json(
            self._post(
                app_key, "stop_message", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    async def astop_message(
            self, app_key: str, req: StopMessageRequest
    ) -> EmptyResponse:
        return EmptyResponse.model_validate_json(
            await self._apost(
                app_key, "stop_message", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    def clear_message(
            self, app_key: str, req: ClearMessageRequest
    ) -> EmptyResponse:
        return EmptyResponse.model_validate_json(
            self._post(
                app_key, "clear_message", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    async def aclear_message(
            self, app_key: str, req: ClearMessageRequest
    ) -> EmptyResponse:
        return EmptyResponse.model_validate_json(
            await self._apost(
                app_key, "clear_message", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    def get_conversation_messages(
            self, app_key: str, req: GetConversationMessageRequest
    ) -> GetConversationMessageResponse:
        return GetConversationMessageResponse.model_validate_json(
            self._post(
                app_key, "get_conversation_messages", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    async def aget_conversation_messages(
            self, app_key: str, req: GetConversationMessageRequest
    ) -> GetConversationMessageResponse:
        return GetConversationMessageResponse.model_validate_json(
            await self._apost(
                app_key, "get_conversation_messages", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    def get_message_info(
            self, app_key: str, req: GetMessageInfoRequest
    ) -> GetMessageInfoResponse:
        return GetMessageInfoResponse.model_validate_json(
            self._post(
                app_key, "get_message_info", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    async def aget_message_info(
            self, app_key: str, req: GetMessageInfoRequest
    ) -> GetMessageInfoResponse:
        return GetMessageInfoResponse.model_validate_json(
            await self._apost(
                app_key, "get_message_info", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    def delete_message(
            self, app_key: str, req: DeleteMessageRequest
    ) -> EmptyResponse:
        return EmptyResponse.model_validate_json(
            self._post(
                app_key, "delete_message", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    async def adelete_message(
            self, app_key: str, req: DeleteMessageRequest
    ) -> EmptyResponse:
        return EmptyResponse.model_validate_json(
            await self._apost(
                app_key, "delete_message", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    def feedback(
            self, app_key: str, req: FeedbackRequest
    ) -> EmptyResponse:
        return EmptyResponse.model_validate_json(
            self._post(
                app_key, "feedback", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    async def afeedback(
            self, app_key: str, req: FeedbackRequest
    ) -> EmptyResponse:
        return EmptyResponse.model_validate_json(
            await self._apost(
                app_key, "feedback", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    def set_message_answer_used(
            self, app_key: str, req: SetMessageAnswerUsedRequest
    ) -> EmptyResponse:
        return EmptyResponse.model_validate_json(
            self._post(
                app_key, "set_message_answer_used", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    async def aset_message_answer_used(
            self, app_key: str, req: SetMessageAnswerUsedRequest
    ) -> EmptyResponse:
        return EmptyResponse.model_validate_json(
            await self._apost(
                app_key, "set_message_answer_used", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    def get_suggested_questions(
            self, app_key: str, req: GetSuggestedQuestionsRequest
    ) -> GetSuggestedQuestionsResponse:
        return GetSuggestedQuestionsResponse.model_validate_json(
            self._post(
                app_key, "get_suggested_questions", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    async def aget_suggested_questions(
            self, app_key: str, req: GetSuggestedQuestionsRequest
    ) -> GetSuggestedQuestionsResponse:
        return GetSuggestedQuestionsResponse.model_validate_json(
            await self._apost(
                app_key, "get_suggested_questions", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    def run_app_workflow(
            self, app_key: str, req: RunAppWorkflowRequest
    ) -> RunAppWorkflowResponse:
        return RunAppWorkflowResponse.model_validate_json(
            self._post(
                app_key, "run_app_workflow", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    async def arun_app_workflow(
            self, app_key: str, req: RunAppWorkflowRequest
    ) -> RunAppWorkflowResponse:
        return RunAppWorkflowResponse.model_validate_json(
            await self._apost(
                app_key, "run_app_workflow", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    def sync_run_app_workflow(
            self, app_key: str, req: SyncRunAppWorkflowRequest
    ) -> SyncRunAppWorkflowResponse:
        return SyncRunAppWorkflowResponse.model_validate_json(
            self._post(
                app_key, "sync_run_app_workflow", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    async def async_run_app_workflow(
            self, app_key: str, req: SyncRunAppWorkflowRequest
    ) -> SyncRunAppWorkflowResponse:
        return SyncRunAppWorkflowResponse.model_validate_json(
            await self._apost(
                app_key, "sync_run_app_workflow", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    def query_run_app_process(
            self, app_key: str, req: QueryRunAppProcessRequest
    ) -> QueryRunAppProcessResponse:
        return QueryRunAppProcessResponse.model_validate_json(
            self._post(
                app_key, "query_run_app_process", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    async def aquery_run_app_process(
            self, app_key: str, req: QueryRunAppProcessRequest
    ) -> QueryRunAppProcessResponse:
        return QueryRunAppProcessResponse.model_validate_json(
            await self._apost(
                app_key, "query_run_app_process", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    def list_oauth2_token(
            self, app_key: str, req: ListOauth2TokenRequest
    ) -> ListOauth2TokenResponse:
        return ListOauth2TokenResponse.model_validate_json(
            self._post(
                app_key, "list_oauth2_token", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    async def alist_oauth2_token(
            self, app_key: str, req: ListOauth2TokenRequest
    ) -> ListOauth2TokenResponse:
        return ListOauth2TokenResponse.model_validate_json(
            await self._apost(
                app_key, "list_oauth2_token", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    def event_trigger_webhook(
            self, app_key: str, webhook_key: str, webhook_token: str
    ) -> EventTriggerWebhookResponse:
        return EventTriggerWebhookResponse.model_validate_json(
            self._post(
                app_key, "trigger/webhook?key={}".format(webhook_key), {},
                {"Authorization": "Bearer {}".format(webhook_token)}
            ),
            by_alias=True,
        )

    async def aevent_trigger_webhook(
            self, app_key: str, webhook_key: str, webhook_token: str
    ) -> EventTriggerWebhookResponse:
        return EventTriggerWebhookResponse.model_validate_json(
            await self._apost(
                app_key, "trigger/webhook?key={}".format(webhook_key), {},
                {"Authorization": "Bearer {}".format(webhook_token)}
            ),
            by_alias=True,
        )

    def chat_continue(
            self, app_key: str, chat_continue: ChatContinueRequest
    ) -> Generator[ChatEvent, None, None]:
        params = chat_continue.model_dump(by_alias=True)
        g = self._sse_post(app_key, "chat_continue", params)
        for event in g:
            event_data = json.loads(event.data)
            chat_event = parse_chat_event(event_data)
            if chat_event:
                yield chat_event

    async def achat_continue(
            self, app_key: str, chat_continue: ChatContinueRequest
    ) -> AsyncGenerator[ChatEvent, None]:
        params = chat_continue.model_dump(by_alias=True)
        g = self._asse_post(app_key, "chat_continue", params)
        async for event in g:
            event_data = json.loads(event.data)
            chat_event = parse_chat_event(event_data)
            if chat_event:
                yield chat_event

    def list_long_memory(
            self, app_key: str, req: ListLongMemoryRequest
    ) -> ListLongMemoryResponse:
        return ListLongMemoryResponse.model_validate_json(
            self._post(
                app_key, "list_long_memory", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    async def alist_long_memory(
            self, app_key: str, req: ListLongMemoryRequest
    ) -> ListLongMemoryResponse:
        return ListLongMemoryResponse.model_validate_json(
            await self._apost(
                app_key, "list_long_memory", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    def update_long_memory(
            self, app_key: str, req: UpdateLongMemoryRequest
    ) -> EmptyResponse:
        return EmptyResponse.model_validate_json(
            self._post(
                app_key, "update_long_memory", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    async def aupdate_long_memory(
            self, app_key: str, req: UpdateLongMemoryRequest
    ) -> EmptyResponse:
        return EmptyResponse.model_validate_json(
            await self._apost(
                app_key, "update_long_memory", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    def delete_long_memory(
            self, app_key: str, req: DeleteLongMemoryRequest
    ) -> EmptyResponse:
        return EmptyResponse.model_validate_json(
            self._post(
                app_key, "delete_long_memory", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    async def adelete_long_memory(
            self, app_key: str, req: DeleteLongMemoryRequest
    ) -> EmptyResponse:
        return EmptyResponse.model_validate_json(
            await self._apost(
                app_key, "delete_long_memory", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    def clear_long_memory(
            self, app_key: str, req: ClearLongMemoryRequest
    ) -> EmptyResponse:
        return EmptyResponse.model_validate_json(
            self._post(
                app_key, "clear_long_memory", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    async def aclear_long_memory(
            self, app_key: str, req: ClearLongMemoryRequest
    ) -> EmptyResponse:
        return EmptyResponse.model_validate_json(
            await self._apost(
                app_key, "clear_long_memory", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    def async_resume_app_workflow(
            self, app_key: str, req: AsyncResumeAppWorkflowRequest
    ) -> AsyncResumeAppWorkflowResponse:
        return AsyncResumeAppWorkflowResponse.model_validate_json(
            self._post(
                app_key, "async_resume_app_workflow", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    async def a_async_resume_app_workflow(
            self, app_key: str, req: AsyncResumeAppWorkflowRequest
    ) -> AsyncResumeAppWorkflowResponse:
        return AsyncResumeAppWorkflowResponse.model_validate_json(
            await self._apost(
                app_key, "async_resume_app_workflow", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    def set_conversation_top(
            self, app_key: str, req: SetConversationTopRequest
    ) -> EmptyResponse:
        return EmptyResponse.model_validate_json(
            self._post(
                app_key, "set_conversation_top", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    async def aset_conversation_top(
            self, app_key: str, req: SetConversationTopRequest
    ) -> EmptyResponse:
        return EmptyResponse.model_validate_json(
            await self._apost(
                app_key, "set_conversation_top", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    def cancel_conversation_top(
            self, app_key: str, req: CancelConversationTopRequest
    ) -> EmptyResponse:
        return EmptyResponse.model_validate_json(
            self._post(
                app_key, "cancel_conversation_top", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    async def acancel_conversation_top(
            self, app_key: str, req: CancelConversationTopRequest
    ) -> EmptyResponse:
        return EmptyResponse.model_validate_json(
            await self._apost(
                app_key, "cancel_conversation_top", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    def query_skill_async_task(
            self, app_key: str, req: QueryAppSkillAsyncTaskRequest
    ) -> QueryAppSkillAsyncTaskResponse:
        return QueryAppSkillAsyncTaskResponse.model_validate_json(
            self._post(
                app_key, "query_skill_async_task", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    async def aquery_skill_async_task(
            self, app_key: str, req: QueryAppSkillAsyncTaskRequest
    ) -> QueryAppSkillAsyncTaskResponse:
        return QueryAppSkillAsyncTaskResponse.model_validate_json(
            await self._apost(
                app_key, "query_skill_async_task", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    def sync_resume_app_workflow_blocking(
            self, app_key: str, req: SyncResumeAppWorkflowRequest
    ) -> SyncResumeAppWorkflowResponse:
        req.is_stream = False
        res = self._post(app_key, "sync_resume_app_workflow", req.model_dump(by_alias=True))
        return SyncResumeAppWorkflowResponse.model_validate_json(res, by_alias=True)

    async def a_sync_resume_app_workflow_blocking(
            self, app_key: str, req: SyncResumeAppWorkflowRequest
    ) -> SyncResumeAppWorkflowResponse:
        req.is_stream = False
        res = await self._apost(
            app_key, "sync_resume_app_workflow", req.model_dump(by_alias=True)
        )
        return SyncResumeAppWorkflowResponse.model_validate_json(res, by_alias=True)

    def sync_resume_app_workflow_streaming(
            self, app_key: str, req: SyncResumeAppWorkflowRequest
    ) -> Generator[ChatEvent, None, None]:
        req.is_stream = True
        params = req.model_dump(by_alias=True)
        g = self._sse_post(app_key, "sync_resume_app_workflow", params)
        for event in g:
            event_data = json.loads(event.data)
            chat_event = parse_workflow_event(event_data)
            if chat_event:
                yield chat_event

    async def a_sync_resume_app_workflow_streaming(
            self, app_key: str, req: SyncResumeAppWorkflowRequest
    ) -> AsyncGenerator[ChatEvent, None]:
        req.is_stream = True
        params = req.model_dump(by_alias=True)
        g = self._asse_post(app_key, "sync_resume_app_workflow", params)
        async for event in g:
            event_data = json.loads(event.data)
            chat_event = parse_workflow_event(event_data)
            if chat_event:
                yield chat_event

    def get_app_user_variables(
            self, app_key: str, req: GetAppUserVariablesRequest
    ) -> GetAppUserVariablesResponse:
        return GetAppUserVariablesResponse.model_validate_json(
            self._post(
                app_key, "get_app_user_variables", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    async def aget_app_user_variables(
            self, app_key: str, req: GetAppUserVariablesRequest
    ) -> GetAppUserVariablesResponse:
        return GetAppUserVariablesResponse.model_validate_json(
            await self._apost(
                app_key, "get_app_user_variables", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    def set_app_user_variables(
            self, app_key: str, req: SetAppUserVariablesRequest
    ) -> EmptyResponse:
        return EmptyResponse.model_validate_json(
            self._post(
                app_key, "set_app_user_variables", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    async def aset_app_user_variables(
            self, app_key: str, req: SetAppUserVariablesRequest
    ) -> EmptyResponse:
        return EmptyResponse.model_validate_json(
            await self._apost(
                app_key, "set_app_user_variables", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    def query_trigger_run_records(
            self, app_key: str, req: QueryTriggerRunRecordsRequest
    ) -> QueryTriggerRunRecordsResponse:
        return QueryTriggerRunRecordsResponse.model_validate_json(
            self._post(
                app_key, "query_trigger_run_records", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )

    async def aquery_trigger_run_records(
            self, app_key: str, req: QueryTriggerRunRecordsRequest
    ) -> QueryTriggerRunRecordsResponse:
        return QueryTriggerRunRecordsResponse.model_validate_json(
            await self._apost(
                app_key, "query_trigger_run_records", req.model_dump(by_alias=True)
            ),
            by_alias=True,
        )


def parse_chat_event(event_data: dict) -> Optional[ChatEvent]:
    match event_data["event"]:
        case StreamingChatEventType.message_start:
            return MessageStartChatEvent.model_validate(event_data)
        case StreamingChatEventType.message_end:
            return MessageEndChatEvent.model_validate(event_data)
        case StreamingChatEventType.message_failed:
            return MessageFailedChatEvent.model_validate(event_data)
        case StreamingChatEventType.message_output_start:
            return MessageOutputStartChatEvent.model_validate(event_data)
        case StreamingChatEventType.message_output_end:
            return MessageOutputEndChatEvent.model_validate(event_data)
        case StreamingChatEventType.message:
            return MessageChatEvent.model_validate(event_data)
        case StreamingChatEventType.message_cost:
            return MessageCostChatEvent.model_validate(event_data)
        case StreamingChatEventType.agent_jump:
            return AgentJumpChatEvent.model_validate(event_data)
        case StreamingChatEventType.agent_take_over:
            return AgentTakeOverChatEvent.model_validate(event_data)
        case StreamingChatEventType.qa_retrieve:
            return QARetrieveChatEvent.model_validate(event_data)
        case StreamingChatEventType.qa_retrieve_end:
            return QARetrieveChatEvent.model_validate(event_data)
        case StreamingChatEventType.terminology_retrieve:
            return TerminologyRetrieveChatEvent.model_validate(event_data)
        case StreamingChatEventType.terminology_retrieve_end:
            return TerminologyRetrieveEndChatEvent.model_validate(event_data)
        case StreamingChatEventType.long_term_memory_retrieve:
            return LongTermMemoryRetrieveChatEvent.model_validate(event_data)
        case StreamingChatEventType.long_term_memory_retrieve_end:
            return LongTermMemoryRetrieveEndChatEvent.model_validate(event_data)
        case StreamingChatEventType.knowledge_retrieve:
            return KnowledgeRetrieveChatEvent.model_validate(event_data)
        case StreamingChatEventType.knowledge_retrieve_end:
            return KnowledgeRetrieveEndChatEvent.model_validate(event_data)
        case StreamingChatEventType.knowledge_graph_retrieve:
            return KnowledgeGraphRetrieveChatEvent.model_validate(event_data)
        case StreamingChatEventType.knowledge_graph_retrieve_end:
            return KnowledgeGraphRetrieveEndChatEvent.model_validate(event_data)
        case StreamingChatEventType.agent_thought:
            return AgentThoughtChatEvent.model_validate(event_data)
        case StreamingChatEventType.agent_thought_end:
            return AgentThoughtEndChatEvent.model_validate(event_data)
        case StreamingChatEventType.agent_thought_update:
            return AgentThoughtUpdateChatEvent.model_validate(event_data)
        case StreamingChatEventType.tool_message_output_start:
            return ToolMessageOutputStartChatEvent.model_validate(event_data)
        case StreamingChatEventType.tool_message_output_end:
            return ToolMessageOutputEndChatEvent.model_validate(event_data)
        case StreamingChatEventType.tool_message:
            return ToolMessageChatEvent.model_validate(event_data)
        case StreamingChatEventType.interrupted:
            return InterruptedChatEvent.model_validate(event_data)
        case StreamingChatEventType.agent_intention:
            return AgentIntentionChatEvent.model_validate(event_data)
        case StreamingChatEventType.suggestion:
            return SuggestionChatEvent.model_validate(event_data)
        case StreamingChatEventType.suggestion_cost:
            return SuggestionCostChatEvent.model_validate(event_data)
        case StreamingChatEventType.think_message_output_start:
            return ThinkMessageOutputStartChatEvent.model_validate(event_data)
        case StreamingChatEventType.think_message_output_end:
            return ThinkMessageOutputEndChatEvent.model_validate(event_data)
        case StreamingChatEventType.think_message:
            return ThinkMessageChatEvent.model_validate(event_data)

    return None


def parse_workflow_event(event_data: dict) -> Optional[WorkflowEvent]:
    match event_data["event"]:
        case StreamingWorkflowEventType.flow_start:
            return FlowStartWorkflowEvent.model_validate(event_data)
        case StreamingWorkflowEventType.flow_interrupted:
            return FlowInterruptedWorkflowEvent.model_validate(event_data)
        case StreamingWorkflowEventType.flow_end:
            return FlowEndWorkflowEvent.model_validate(event_data)
        case StreamingWorkflowEventType.flow_cost:
            return FlowCostWorkflowEvent.model_validate(event_data)
        case StreamingWorkflowEventType.flow_error:
            return FlowErrorWorkflowEvent.model_validate(event_data)
        case StreamingWorkflowEventType.tool_message_output_start:
            return ToolMessageOutputStartWorkflowEvent.model_validate(event_data)
        case StreamingWorkflowEventType.tool_message:
            return ToolMessageWorkflowEvent.model_validate(event_data)
        case StreamingWorkflowEventType.tool_message_output_end:
            return ToolMessageOutputEndWorkflowEvent.model_validate(event_data)
        case StreamingWorkflowEventType.message_output_start:
            return MessageOutputStartWorkflowEvent.model_validate(event_data)
        case StreamingWorkflowEventType.message_output_end:
            return MessageOutputEndWorkflowEvent.model_validate(event_data)
        case StreamingWorkflowEventType.message:
            return MessageWorkflowEvent.model_validate(event_data)

    return None
