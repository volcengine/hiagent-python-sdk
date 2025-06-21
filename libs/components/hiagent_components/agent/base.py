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
from concurrent.futures import Executor
from io import StringIO
from typing import Any, AsyncIterator, Iterator, Optional

from hiagent_api.chat import ChatService
from hiagent_api.chat_types import (
    ChatEvent,
    ChatRequest,
    CreateConversationRequest,
    GetAppConfigPreviewRequest,
    MessageChatEvent,
    StreamingChatEventType,
    ToolMessageChatEvent,
)

from hiagent_components.base.base import Executable


class Agent(Executable):
    def __init__(
        self,
        svc: ChatService,
        app_key: str,
        user_id: str,
        conversation_id: str,
        name: str,
        description: str,
    ) -> None:
        self.svc = svc
        self.app_key = app_key
        self.user_id = user_id
        self.conversation_id = conversation_id
        self.name = name or ""
        self.description = description or ""

    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "需要智能体解决的原始问题",
                }
            },
            "required": ["query"],
        }

    @classmethod
    def init(
        cls,
        svc: ChatService,
        app_key: str,
        user_id: str,
        variables: dict,
        conversation_id: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> "Agent":
        resp = svc.get_app(
            app_key=app_key,
            params=GetAppConfigPreviewRequest(
                app_key=app_key,
                user_id=user_id,
            ),
        )
        if not name:
            name = resp.name
        if not description:
            description = ""

        if not conversation_id:
            resp = svc.create_conversation(
                app_key=app_key,
                conversation=CreateConversationRequest(
                    app_key=app_key,
                    inputs=variables,
                    user_id=user_id,
                ),
            )
            conversation_id = resp.conversation.app_conversation_id

        agent = cls(
            svc=svc,
            app_key=app_key,
            user_id=user_id,
            conversation_id=conversation_id,
            name=name,
            description=description,
        )

        return agent

    @classmethod
    async def ainit(
        cls,
        svc: ChatService,
        app_key: str,
        user_id: str,
        variables: dict,
        conversation_id: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> "Agent":
        resp = await svc.aget_app(
            app_key=app_key,
            params=GetAppConfigPreviewRequest(
                app_key=app_key,
                user_id=user_id,
            ),
        )
        if not name:
            name = resp.name
        if not description:
            description = ""

        if not conversation_id:
            resp = svc.create_conversation(
                app_key=app_key,
                conversation=CreateConversationRequest(
                    app_key=app_key,
                    inputs=variables,
                    user_id=user_id,
                ),
            )
            conversation_id = resp.conversation.app_conversation_id

        agent = cls(
            svc=svc,
            app_key=app_key,
            user_id=user_id,
            conversation_id=conversation_id,
            name=name,
            description=description,
        )

        return agent

    def invoke(
        self,
        input: dict,
        **kwargs: Any,
    ) -> str:
        query = input.get("query")
        if not query:
            raise ValueError("agent invoke input should contains 'query'")

        resp_generator = self.svc.chat_streaming(
            self.app_key,
            ChatRequest(
                app_key=self.app_key,
                app_conversation_id=self.conversation_id,
                query=query,
                response_mode="streaming",
                user_id=self.user_id,
            ),
        )

        output = StringIO()
        for event in resp_generator:
            if event.event == StreamingChatEventType.tool_message:
                assert isinstance(event, ToolMessageChatEvent)
                output.write(event.answer)
            elif event.event == StreamingChatEventType.message:
                assert isinstance(event, MessageChatEvent)
                output.write(event.answer)

        return output.getvalue()

    async def ainvoke(
        self,
        input: dict,
        executor: Optional[Executor] = None,
        **kwargs: Any,
    ) -> str:
        query = input.get("query")
        if not query:
            raise ValueError("agent invoke input should contains 'query'")

        resp_generator = self.svc.achat_streaming(
            self.app_key,
            ChatRequest(
                app_key=self.app_key,
                app_conversation_id=self.conversation_id,
                query=query,
                response_mode="streaming",
                user_id=self.user_id,
            ),
        )

        output = StringIO()
        async for event in resp_generator:
            if event.event == StreamingChatEventType.tool_message:
                assert isinstance(event, ToolMessageChatEvent)
                output.write(event.answer)
            elif event.event == StreamingChatEventType.tool_message_output_end:
                output.write("\n\n")
            elif event.event == StreamingChatEventType.message:
                assert isinstance(event, MessageChatEvent)
                output.write(event.answer)

        return output.getvalue()

    def stream(
        self,
        input: dict,
        **kwargs: Optional[Any],
    ) -> Iterator[ChatEvent]:
        query = input.get("query")
        if not query:
            raise ValueError("agent invoke input should contains 'query'")

        resp_generator = self.svc.chat_streaming(
            self.app_key,
            ChatRequest(
                app_key=self.app_key,
                app_conversation_id=self.conversation_id,
                query=query,
                response_mode="streaming",
                user_id=self.user_id,
            ),
        )

        return resp_generator

    async def astream(
        self,
        input: dict,
        **kwargs: Optional[Any],
    ) -> AsyncIterator[ChatEvent]:
        query = input.get("query")
        if not query:
            raise ValueError("agent invoke input should contains 'query'")

        resp_generator = self.svc.achat_streaming(
            self.app_key,
            ChatRequest(
                app_key=self.app_key,
                app_conversation_id=self.conversation_id,
                query=query,
                response_mode="streaming",
                user_id=self.user_id,
            ),
        )

        async for event in resp_generator:
            yield event
