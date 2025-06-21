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
