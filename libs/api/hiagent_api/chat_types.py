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
from typing import Optional

from pydantic import Field
from strenum import StrEnum

from hiagent_api.base import BaseSchema


class CreateConversationRequest(BaseSchema):
    app_key: str = Field(
        description="app key",
        serialization_alias="AppKey",
    )
    inputs: dict[str, str] = Field(
        description="inputs of variables",
        serialization_alias="Inputs",
    )
    user_id: str = Field(
        description="user id",
        serialization_alias="UserID",
    )


class Conversation(BaseSchema):
    app_conversation_id: str = Field(
        description="conversation id",
        validation_alias="AppConversationID",
    )
    conversation_name: str = Field(
        description="conversation name",
        validation_alias="ConversationName",
    )
    create_time: str = Field(
        description="create time",
        validation_alias="CreateTime",
    )
    last_chat_time: str = Field(
        description="last chat time",
        validation_alias="LastChatTime",
    )
    empty_conversation: bool = Field(
        description="empty conversation",
        validation_alias="EmptyConversation",
    )


class CreateConversationResponse(BaseSchema):
    conversation: Conversation = Field(
        description="conversation",
        validation_alias="Conversation",
    )


class GetAppConfigPreviewRequest(BaseSchema):
    app_key: str = Field(
        description="app key",
        serialization_alias="AppKey",
    )
    user_id: str = Field(
        description="user id",
        serialization_alias="UserID",
    )


class VariableConfig(BaseSchema):
    key: str = Field(
        description="key",
        validation_alias="Key",
    )
    description: str = Field(
        description="description",
        validation_alias="Name",
    )
    show_name: str = Field(
        description="show name",
        validation_alias="ShowName",
    )
    required: bool = Field(
        description="required",
        validation_alias="Required",
    )
    variable_type: str = Field(
        description="variable_type: Text, Paragraph, Enum",
        validation_alias="VariableType",
    )
    enum_values: Optional[list[str]] = Field(
        description="enum_values",
        validation_alias="EnumValues",
        default=None,
    )


class GetAppConfigPreviewResponse(BaseSchema):
    name: str = Field(
        description="app name",
        validation_alias="Name",
    )
    variable_configs: Optional[list[VariableConfig]] = Field(
        description="variable_configs", validation_alias="VariableConfigs", default=None
    )


class FileInfo(BaseSchema):
    path: str = Field(
        description="file path",
        serialization_alias="Path",
    )
    name: str = Field(
        description="file name",
        serialization_alias="Name",
    )
    size: int = Field(
        description="file size",
        serialization_alias="Size",
    )
    url: str = Field(
        description="file url",
        serialization_alias="Url",
    )


class QueryExtendsInfo(BaseSchema):
    files: list[FileInfo] = Field(
        description="files",
        serialization_alias="Files",
    )


class ChatRequest(BaseSchema):
    app_key: str = Field(
        description="app key",
        serialization_alias="AppKey",
    )
    app_conversation_id: str = Field(
        description="conversation id",
        serialization_alias="AppConversationID",
    )
    query: str = Field(
        description="query",
        serialization_alias="Query",
    )
    response_mode: str = Field(
        description="response mode: streaming or blocking",
        serialization_alias="ResponseMode",
    )
    user_id: str = Field(
        description="user id",
        serialization_alias="UserID",
    )
    query_extends: Optional[QueryExtendsInfo] = Field(
        default=None,
        description="query extends info",
        serialization_alias="QueryExtends",
    )


class BlockingChatResponse(BaseSchema):
    event: str = Field(
        description="event",
    )
    task_id: str = Field(
        description="task id",
    )
    id: str = Field(
        description="id",
    )
    conversation_id: str = Field(
        description="conversation id",
    )
    answer: str = Field(
        description="answer",
    )
    created_at: int = Field(
        description="created at",
    )
    think_messages: Optional[list[str]] = Field(
        description="think messages",
        default=None,
    )
    tool_messages: Optional[list[str]] = Field(
        default=None,
        description="tool messages",
    )


class StreamingChatEventType(StrEnum):
    message_start = "message_start"
    agent_jump = "agent_jump"
    agent_take_over = "agent_take_over"
    qa_retrieve = "qa_retrieve"
    qa_retrieve_end = "qa_retrieve_end"
    terminology_retrieve = "terminology_retrieve"
    terminology_retrieve_end = "terminology_retrieve_end"
    long_term_memory_retrieve = "long_term_memory_retrieve"
    long_term_memory_retrieve_end = "long_term_memory_retrieve_end"
    knowledge_retrieve = "knowledge_retrieve"
    knowledge_retrieve_end = "knowledge_retrieve_end"
    knowledge_graph_retrieve = "knowledge_graph_retrieve"
    knowledge_graph_retrieve_end = "knowledge_graph_retrieve_end"
    agent_thought = "agent_thought"
    agent_thought_end = "agent_thought_end"
    agent_thought_update = "agent_thought_update"
    tool_message_output_start = "tool_message_output_start"
    tool_message = "tool_message"
    tool_message_output_end = "tool_message_output_end"
    interrupted = "interrupted"
    agent_intention = "agent_intention"
    message_output_start = "message_output_start"
    message = "message"
    message_output_end = "message_output_end"
    message_cost = "message_cost"
    suggestion = "suggestion"
    suggestion_cost = "suggestion_cost"
    message_end = "message_end"
    message_failed = "message_failed"
    think_message_output_start = "think_message_output_start"
    think_message = "think_message"
    think_message_output_end = "think_message_output_end"


class ChatEvent(BaseSchema):
    event: str = Field(
        description="event",
    )
    task_id: str = Field(
        description="task id",
    )
    id: str = Field(
        description="id",
    )
    conversation_id: str = Field(
        description="conversation id",
    )
    created_at: int = Field(
        default=-1,
        description="created at",
    )


class MessageStartChatEvent(ChatEvent): ...


class AgentJumpChatEvent(ChatEvent):
    jump_reason: str = Field(
        description="jump reason",
    )
    jump_latency: float = Field(
        description="jump latency",
    )
    jump_to: str = Field(
        description="jump to",
    )
    message_id: str = Field(
        description="message id",
    )


class AgentTakeOverChatEvent(ChatEvent):
    agent: str = Field(
        description="agent name",
    )
    reason: str = Field(
        description="agent reason",
    )
    message_id: str = Field(
        description="message id",
    )


class QARetrieveChatEvent(ChatEvent):
    workspace_id: str = Field(
        description="workspace id",
    )
    dataset_ids: list[str] = Field(
        description="dataset ids",
    )
    query: str = Field(
        description="query",
    )
    message_id: str = Field(
        description="message id",
    )


class QARetrieveEndChatEvent(ChatEvent):
    latency: float = Field(
        description="latency",
    )
    docs: dict = Field(
        description="docs",
    )
    message_id: str = Field(
        description="message id",
    )


class TerminologyRetrieveChatEvent(ChatEvent):
    message_id: str = Field(
        description="message id",
    )
    workspace_id: str = Field(
        description="workspace id",
    )
    dataset_ids: list[str] = Field(
        description="dataset ids",
    )
    query: str = Field(
        description="query",
    )


class TerminologyRetrieveEndChatEvent(ChatEvent):
    message_id: str = Field(
        description="message id",
    )
    docs: dict = Field(
        description="docs",
    )
    latency: float = Field(
        description="latency",
    )


class LongTermMemoryRetrieveChatEvent(ChatEvent):
    message_id: str = Field(
        description="message id",
    )
    query: str = Field(
        description="query",
    )


class LongTermMemoryRetrieveEndChatEvent(ChatEvent):
    message_id: str = Field(
        description="message id",
    )
    answer: str = Field(
        description="answer",
    )
    latency: float = Field(
        description="latency",
    )


class KnowledgeRetrieveChatEvent(ChatEvent):
    message_id: str = Field(
        description="message id",
    )
    workspace_id: str = Field(
        description="workspace id",
    )
    dataset_ids: list[str] = Field(
        description="dataset ids",
    )
    query: str = Field(
        description="query",
    )
    top_k: int = Field(
        description="top k",
    )
    score_threshold: float = Field(
        description="score threshold",
    )


class KnowledgeRetrieveEndChatEvent(ChatEvent):
    message_id: str = Field(
        description="message id",
    )
    docs: dict = Field(
        description="docs",
    )
    latency: float = Field(
        description="latency",
    )


class KnowledgeGraphRetrieveChatEvent(ChatEvent):
    message_id: str = Field(
        description="message id",
    )
    workspace_id: str = Field(
        description="workspace id",
    )
    dataset_ids: list[str] = Field(
        description="dataset ids",
    )
    query: str = Field(
        description="query",
    )
    top_k: int = Field(
        description="top k",
    )
    search_depth: int = Field(
        description="search depth",
    )
    search_type: int = Field(
        description="search type",
    )


class KnowledgeGraphRetrieveEndChatEvent(ChatEvent):
    message_id: str = Field(
        description="message id",
    )
    docs: dict = Field(
        description="docs",
    )
    latency: float = Field(
        description="latency",
    )


class AgentThoughtChatEvent(ChatEvent):
    message_id: str = Field(
        description="message id",
    )
    position: int = Field(
        description="position",
    )
    thought: str = Field(
        description="thought",
    )
    skill_type: str = Field(
        description="skill type",
    )
    tool: str = Field(
        description="tool",
    )
    tool_input: str = Field(
        description="tool input",
    )


class AgentThoughtEndChatEvent(ChatEvent):
    position: int = Field(
        description="position",
    )
    observation: str = Field(
        description="observation",
    )
    latency: float = Field(
        description="latency",
    )
    tool_latency: float = Field(
        description="tool latency",
    )
    thought_latency: float = Field(
        description="thought latency",
    )


class AgentThoughtUpdateChatEvent(ChatEvent):
    position: int = Field(
        description="position",
    )
    observation: str = Field(
        description="observation",
    )
    latency: float = Field(
        description="latency",
    )
    tool_latency: float = Field(
        description="tool latency",
    )
    thought_latency: float = Field(
        description="thought latency",
    )


class ToolMessageOutputStartChatEvent(ChatEvent):
    message_title: str = Field(
        description="message title",
    )


class ToolMessageChatEvent(ChatEvent):
    answer: str = Field(
        description="answer",
    )
    message_title: str = Field(
        description="message title",
    )


class ToolMessageOutputEndChatEvent(ChatEvent):
    message_title: str = Field(
        description="message title",
    )


class InterruptedChatEvent(ChatEvent):
    message_id: str = Field(
        description="message id",
    )
    interrupted_msg: str = Field(
        description="interrupted message",
    )


class AgentIntentionChatEvent(ChatEvent):
    message_id: str = Field(
        description="message id",
    )
    intention: str = Field(
        description="intention",
    )
    data: dict = Field(
        description="data",
    )


class MessageOutputStartChatEvent(ChatEvent): ...


class MessageChatEvent(ChatEvent):
    answer: str = Field(
        description="answer",
    )


class MessageOutputEndChatEvent(ChatEvent): ...


class MessageCostChatEvent(ChatEvent):
    input_tokens: int = Field(
        description="input tokens",
    )
    output_tokens: int = Field(
        description="output tokens",
    )
    start_time_first_resp: int = Field(
        description="start time first resp",
    )
    latency_first_resp: int = Field(
        description="latency first resp",
    )
    latency: float = Field(
        description="latency",
    )


class SuggestionChatEvent(ChatEvent):
    suggested_questions: list[str] = Field(
        description="suggested questions",
    )


class SuggestionCostChatEvent(ChatEvent):
    input_tokens: int = Field(
        description="input tokens",
    )
    output_tokens: int = Field(
        description="output tokens",
    )
    latency: float = Field(
        description="latency",
    )


class MessageEndChatEvent(ChatEvent):
    agent_configuration: Optional[dict] = Field(
        description="agent configuration",
        default=None,
    )


class MessageFailedChatEvent(ChatEvent):
    error: str = Field(
        description="error message",
    )


class ThinkMessageOutputStartChatEvent(ChatEvent): ...


class ThinkMessageChatEvent(ChatEvent):
    answer: str = Field(
        description="answer",
    )


class ThinkMessageOutputEndChatEvent(ChatEvent): ...
