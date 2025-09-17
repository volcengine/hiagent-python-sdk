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
        default="",
    )
    conversation_name: str = Field(
        description="conversation name",
        validation_alias="ConversationName",
        default="",
    )
    create_time: str = Field(
        description="create time",
        validation_alias="CreateTime",
        default="",
    )
    last_chat_time: str = Field(
        description="last chat time",
        validation_alias="LastChatTime",
        default="",
    )
    empty_conversation: bool = Field(
        description="empty conversation",
        validation_alias="EmptyConversation",
        default=False,
    )


class CreateConversationResponse(BaseSchema):
    conversation: Conversation = Field(
        description="conversation",
        validation_alias="Conversation",
        default=None,
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
        default="",
    )
    show_name: str = Field(
        description="show name",
        validation_alias="ShowName",
        default="",
    )
    required: bool = Field(
        description="required",
        validation_alias="Required",
        default=False,
    )
    variable_type: str = Field(
        description="variable_type: Text, Paragraph, Enum",
        validation_alias="VariableType",
        default="",
    )
    enum_values: Optional[list[str]] = Field(
        description="enum_values",
        validation_alias="EnumValues",
        default=None,
    )


class GetAppConfigPreviewResponse(BaseSchema):
    tenant_id: str = Field(
        description="tenant id",
        validation_alias="TenantID",
        default="",
    )
    workspace_id: str = Field(
        description="workspace id",
        validation_alias="WorkspaceID",
        default="",
    )
    variable_configs: Optional[list[VariableConfig]] = Field(
        description="variable_configs", validation_alias="VariableConfigs", default=[]
    )
    name: str = Field(
        description="app name",
        validation_alias="Name",
        default="",
    )
    open_message: str = Field(
        description="open message",
        validation_alias="OpenMessage",
        default="",
    )
    open_query: str = Field(
        description="open query",
        validation_alias="OpenQuery",
        default="",
    )
    icon: str = Field(
        description="icon",
        validation_alias="Icon",
        default="",
    )
    background: str = Field(
        description="icon background color",
        validation_alias="Background",
        default="",
    )
    suggest_enabled: bool = Field(
        description="chat suggestion enabled ",
        validation_alias="SuggestEnabled",
        default=False,
    )
    image: str = Field(
        description="image",
        validation_alias="Image",
        default="",
    )
    agent_mode: str = Field(
        description="agent mode: Single or Multi",
        validation_alias="AgentMode",
        default="",
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
        validation_alias="Files",
        default=[],
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


class StreamingWorkflowEventType(StrEnum):
    tool_message_output_start = "tool_message_output_start"
    tool_message = "tool_message"
    tool_message_output_end = "tool_message_output_end"
    message_output_start = "message_output_start"
    message = "message"
    message_output_end = "message_output_end"
    flow_interrupted = "flow_interrupted"
    flow_start = "flow_start"
    flow_cost = "flow_cost"
    flow_end = "flow_end"
    flow_error = "flow_error"


class WorkflowEvent(BaseSchema):
    event: str = Field(
        description="event",
    )
    task_id: str = Field(
        description="task id",
    )
    id: str = Field(
        description="id",
    )
    run_id: str = Field(
        description="run id",
    )


class FlowStartWorkflowEvent(WorkflowEvent):
    pass


class ToolMessageOutputStartWorkflowEvent(WorkflowEvent):
    message_title: str = Field(
        description="message title",
    )


class ToolMessageWorkflowEvent(WorkflowEvent):
    answer: str = Field(
        description="answer",
    )
    message_title: str = Field(
        description="message title",
    )
    created_at: int = Field(
        description="created at",
    )


class ToolMessageOutputEndWorkflowEvent(WorkflowEvent):
    message_title: str = Field(
        description="message title",
    )


class FlowInterruptedWorkflowEvent(WorkflowEvent):
    interrupted_msg: str = Field(
        description="interrupted message",
    )
    interrupted_node_id: str = Field(
        description="interrupted node id",
    )
    interrupted_type: str = Field(
        description="interrupted type",
    )


class MessageOutputStartWorkflowEvent(WorkflowEvent):
    think_message_id: str = Field(
        description="think message id",
    )


class MessageWorkflowEvent(WorkflowEvent):
    think_message_id: str = Field(
        description="think message id",
    )
    answer: str = Field(
        description="answer",
    )
    created_at: int = Field(
        description="created at",
    )


class MessageOutputEndWorkflowEvent(WorkflowEvent):
    think_message_id: str = Field(
        description="think message id",
    )


class FlowCostWorkflowEvent(WorkflowEvent):
    cost_tokens: int = Field(
        description="cost tokens",
    )
    latency: int = Field(
        description="latency",
    )


class FlowEndWorkflowEvent(WorkflowEvent):
    pass


class FlowErrorWorkflowEvent(WorkflowEvent):
    error_message: str = Field(
        description="error message",
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
    interrupted_type: str = Field(
        description="interrupted type",
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


class ChatAgainRequest(BaseSchema):
    app_key: str = Field(
        description="app key",
        serialization_alias="AppKey",
    )
    app_conversation_id: str = Field(
        description="conversation id",
        serialization_alias="AppConversationID",
    )
    message_id: str = Field(
        description="message id",
        serialization_alias="MessageID",
    )
    user_id: str = Field(
        description="user id",
        serialization_alias="UserID",
    )


class GetConversationListRequest(BaseSchema):
    app_key: str = Field(
        description="app key",
        serialization_alias="AppKey",
    )
    user_id: str = Field(
        description="user id",
        serialization_alias="UserID",
    )


class ConversationInfo(BaseSchema):
    app_conversation_id: str = Field(
        description="conversation id",
        validation_alias="AppConversationID",
        default="",
    )
    conversation_id: str = Field(
        description="conversation id",
        validation_alias="ConversationID",
        default="",
    )
    conversation_name: str = Field(
        description="conversation name",
        validation_alias="ConversationName",
        default="",
    )


class GetConversationListResponse(BaseSchema):
    conversation_list: list[ConversationInfo] = Field(
        description="conversation list",
        validation_alias="ConversationList",
        default=[],
    )

class GetConversationInputsRequest(BaseSchema):
    app_key: str = Field(
        description="app key",
        serialization_alias="AppKey",
    )
    user_id: str = Field(
        description="user id",
        serialization_alias="UserID",
    )
    app_conversation_id: str = Field(
        description="conversation id",
        serialization_alias="AppConversationID",
    )


class GetConversationInputsResponse(BaseSchema):
    inputs: dict[str, str] = Field(
        description="conversation inputs",
        validation_alias="Inputs",
        default={},
    )


class UpdateConversationRequest(BaseSchema):
    app_key: str = Field(
        description="app key",
        serialization_alias="AppKey",
    )
    user_id: str = Field(
        description="user id",
        serialization_alias="UserID",
    )
    inputs: dict[str, str] = Field(
        description="inputs of variables",
        serialization_alias="Inputs",
    )
    app_conversation_id: str = Field(
        description="conversation id",
        serialization_alias="AppConversationID",
    )
    conversation_name: str = Field(
        description="conversation name",
        serialization_alias="ConversationName",
    )


class DeleteConversationRequest(BaseSchema):
    app_key: str = Field(
        description="app key",
        serialization_alias="AppKey",
    )
    user_id: str = Field(
        description="user id",
        serialization_alias="UserID",
    )
    app_conversation_id: str = Field(
        description="conversation id",
        serialization_alias="AppConversationID",
    )


class StopMessageRequest(BaseSchema):
    app_key: str = Field(
        description="app key",
        serialization_alias="AppKey",
    )
    user_id: str = Field(
        description="user id",
        serialization_alias="UserID",
    )
    task_id: str = Field(
        description="task id",
        serialization_alias="TaskID",
    )
    message_id: str = Field(
        description="message id",
        serialization_alias="MessageID",
    )


class ClearMessageRequest(BaseSchema):
    app_key: str = Field(
        description="app key",
        serialization_alias="AppKey",
    )
    user_id: str = Field(
        description="user id",
        serialization_alias="UserID",
    )
    app_conversation_id: str = Field(
        description="conversation id",
        serialization_alias="AppConversationID",
    )


class EmptyResponse(BaseSchema):
    pass


class GetConversationMessageRequest(BaseSchema):
    app_key: str = Field(
        description="app key",
        serialization_alias="AppKey",
    )
    user_id: str = Field(
        description="user id",
        serialization_alias="UserID",
    )
    app_conversation_id: str = Field(
        description="conversation id",
        serialization_alias="AppConversationID",
    )
    limit: int = Field(
        description="limit",
        serialization_alias="Limit",
    )


class MessageAnswerInfo(BaseSchema):
    answer: str = Field(
        description="answer",
        validation_alias="Answer",
        default="",
    )
    message_id: str = Field(
        description="message id",
        validation_alias="MessageID",
        default="",
    )
    create_time: int = Field(
        description="create time",
        validation_alias="CreatedTime",
        default=0,
    )
    task_id: str = Field(
        description="task id",
        validation_alias="TaskID",
        default="",
    )
    like: int = Field(
        description="like, -1:dislike;0:normal;1:like",
        validation_alias="Like",
        default=0,
    )
    total_tokens: int = Field(
        description="total tokens",
        validation_alias="TotalTokens",
        default=0,
    )
    latency: float = Field(
        description="latency",
        validation_alias="Latency",
        default=0.0,
    )
    tracing_json_str: str = Field(
        description="tracing json str",
        validation_alias="TracingJsonStr",
        default="",
    )


class ChatMessageInfo(BaseSchema):
    conversation_id: str = Field(
        description="conversation id",
        validation_alias="ConversationID",
        default="",
    )
    query_id: str = Field(
        description="query id",
        validation_alias="QueryID",
        default="",
    )
    query: str = Field(
        description="query",
        validation_alias="Query",
        default="",
    )
    answer_info: MessageAnswerInfo = Field(
        description="answer info",
        validation_alias="AnswerInfo",
        default=None,
    )
    other_answers: list[MessageAnswerInfo] = Field(
        description="other answers",
        validation_alias="OtherAnswers",
        default=[],
    )
    query_extends: Optional[QueryExtendsInfo] = Field(
        description="query extends",
        validation_alias="QueryExtends",
        default=None,
    )


class GetConversationMessageResponse(BaseSchema):
    messages: list[ChatMessageInfo] = Field(
        description="messages",
        validation_alias="Messages",
        default=[],
    )


class GetMessageInfoRequest(BaseSchema):
    app_key: str = Field(
        description="app key",
        serialization_alias="AppKey",
    )
    user_id: str = Field(
        description="user id",
        serialization_alias="UserID",
    )
    message_id: str = Field(
        description="message id",
        serialization_alias="MessageID",
    )


class GetMessageInfoResponse(BaseSchema):
    message_info: ChatMessageInfo = Field(
        description="message info",
        validation_alias="MessageInfo",
        default=None,
    )


class DeleteMessageRequest(BaseSchema):
    app_key: str = Field(
        description="app key",
        serialization_alias="AppKey",
    )
    user_id: str = Field(
        description="user id",
        serialization_alias="UserID",
    )
    message_id: str = Field(
        description="message id",
        serialization_alias="MessageID",
    )
    query_id: str = Field(
        description="query id",
        serialization_alias="QueryID",
    )


class FeedbackInfo(BaseSchema):
    problem_categories: list[str] = Field(
        description="problem categories",
        serialization_alias="ProblemCategories",
    )
    problem_detail: Optional[str] = Field(
        description="problem detail",
        serialization_alias="ProblemDetail",
    )


class FeedbackRequest(BaseSchema):
    app_key: str = Field(
        description="app key",
        serialization_alias="AppKey",
    )
    user_id: str = Field(
        description="user id",
        serialization_alias="UserID",
    )
    message_id: str = Field(
        description="message id",
        serialization_alias="MessageID",
    )
    like_type: int = Field(
        description="like type, -1:dislike;0:normal;1:like",
        serialization_alias="LikeType",
    )
    feedback_info: Optional[FeedbackInfo] = Field(
        description="feedback info",
        serialization_alias="FeedbackInfo",
    )


class SetMessageAnswerUsedRequest(BaseSchema):
    app_key: str = Field(
        description="app key",
        serialization_alias="AppKey",
    )
    user_id: str = Field(
        description="user id",
        serialization_alias="UserID",
    )
    message_id: str = Field(
        description="message id",
        serialization_alias="MessageID",
    )


class GetSuggestedQuestionsRequest(BaseSchema):
    app_key: str = Field(
        description="app key",
        serialization_alias="AppKey",
    )
    user_id: str = Field(
        description="user id",
        serialization_alias="UserID",
    )
    message_id: str = Field(
        description="message id",
        serialization_alias="MessageID",
    )


class GetSuggestedQuestionsResponse(BaseSchema):
    suggested_questions: list[str] = Field(
        description="suggested questions",
        validation_alias="SuggestedQuestions",
        default=[],
    )


class RunAppWorkflowRequest(BaseSchema):
    app_key: str = Field(
        description="app key",
        serialization_alias="AppKey",
    )
    user_id: str = Field(
        description="user id",
        serialization_alias="UserID",
    )
    input_data: str = Field(
        description="input data",
        serialization_alias="InputData",
    )
    no_debug: bool = Field(
        description="no debug",
        serialization_alias="NoDebug",
    )


class RunAppWorkflowResponse(BaseSchema):
    run_id: str = Field(
        description="run id",
        validation_alias="runId",
        default="",
    )


class SyncRunAppWorkflowRequest(BaseSchema):
    app_key: str = Field(
        description="app key",
        serialization_alias="AppKey",
    )
    user_id: str = Field(
        description="user id",
        serialization_alias="UserID",
    )
    input_data: str = Field(
        description="input data",
        serialization_alias="InputData",
    )
    no_debug: bool = Field(
        description="no debug",
        serialization_alias="NoDebug",
    )


class BizCode(BaseSchema):
    code: str = Field(
        description="biz code",
        validation_alias="Code",
        default="",
    )
    message: str = Field(
        description="biz message",
        validation_alias="Message",
        default="",
    )
    data: dict[str, str] = Field(
        description="biz data",
        validation_alias="Data",
        default={},
    )


class WorkflowLoopBlock(BaseSchema):
    nodes: dict[str, "WorkflowNode"] = Field(
        description="nodes",
        validation_alias="nodes",
        default={},
    )
    steps: list[str] = Field(
        description="steps",
        validation_alias="steps",
        default=[],
    )
    status: str = Field(
        description="status",
        validation_alias="status",
        default="",
    )


class WorkflowNode(BaseSchema):
    input: str = Field(
        description="input data",
        validation_alias="input",
        default="",
    )
    output: str = Field(
        description="output data",
        validation_alias="output",
        default="",
    )
    status: str = Field(
        description="status",
        validation_alias="status",
        default="",
    )
    message: str = Field(
        description="message",
        validation_alias="message",
        default="",
    )
    cost_ms: int = Field(
        description="cost ms",
        validation_alias="costMs",
        default=0,
    )
    cost_token: int = Field(
        description="cost token",
        validation_alias="costToken",
        default=0,
    )
    biz_code: BizCode = Field(
        description="biz code",
        validation_alias="BizCode",
        default=None,
    )
    node_type: str = Field(
        description="node type",
        validation_alias="nodeType",
        default="",
    )
    loop_block: WorkflowLoopBlock = Field(
        description="loop block",
        validation_alias="loopBlock",
        default=None,
    )


class SyncRunAppWorkflowResponse(BaseSchema):
    run_id: str = Field(
        description="run id",
        validation_alias="runId",
        default="",
    )
    status: str = Field(
        description="status",
        validation_alias="status",
        default="",
    )
    nodes: dict[str, WorkflowNode] = Field(
        description="nodes",
        validation_alias="nodes",
        default={},
    )
    steps: list[str] = Field(
        description="steps",
        validation_alias="steps",
        default=[],
    )
    code: int = Field(
        description="code",
        validation_alias="code",
        default=0,
    )
    message: str = Field(
        description="message",
        validation_alias="message",
        default="",
    )
    cost_ms: int = Field(
        description="cost ms",
        validation_alias="costMs",
        default=0,
    )
    output: str = Field(
        description="output",
        validation_alias="output",
        default="",
    )
    last_interrupted_node_id: str = Field(
        description="last interrupted node id",
        validation_alias="lastInterruptedNodeId",
        default="",
    )
    checkpoint_expire_timestamp: int = Field(
        description="checkpoint expire timestamp",
        validation_alias="checkpointExpireTimestamp",
        default=0,
    )
    msg: str = Field(
        description="msg",
        validation_alias="msg",
        default="",
    )
    cost_token: int = Field(
        description="cost token",
        validation_alias="costToken",
        default=0,
    )


class QueryRunAppProcessRequest(BaseSchema):
    app_key: str = Field(
        description="app key",
        serialization_alias="AppKey",
    )
    user_id: str = Field(
        description="user id",
        serialization_alias="UserID",
    )
    run_id: str = Field(
        description="run id",
        serialization_alias="RunID",
    )


class QueryRunAppProcessResponse(SyncRunAppWorkflowResponse):
    pass


class Oauth2TokenItem(BaseSchema):
    plugin_id: str = Field(
        description="plugin id",
        serialization_alias="PluginID",
        default="",
    )
    app_id: str = Field(
        description="app id",
        serialization_alias="APPID",
        default="",
    )
    app_user_id: str = Field(
        description="app user id",
        serialization_alias="APPUserID",
        default="",
    )
    token_expires_at: Optional[str] = Field(
        description="token expires at",
        serialization_alias="TokenExpiresAt",
        default="",
    )
    is_token_valid: bool = Field(
        description="is token valid",
        serialization_alias="IsTokenValid",
        default=False,
    )
    is_refresh_token_valid: bool = Field(
        description="is refresh token valid",
        serialization_alias="IsRefreshTokenValid",
        default=False,
    )


class ListOauth2TokenRequest(BaseSchema):
    app_key: str = Field(
        description="app key",
        serialization_alias="AppKey",
    )
    user_id: str = Field(
        description="user id",
        serialization_alias="UserID",
    )


class ListOauth2TokenResponse(BaseSchema):
    total: int = Field(
        description="total",
        serialization_alias="Total",
        default=0,
    )
    items: list[Oauth2TokenItem] = Field(
        description="items",
        serialization_alias="Items",
        default=[],
    )


class EventTriggerWebhookResponse(BaseSchema):
    run_id: str = Field(
        description="run id",
        validation_alias="runID",
        default="",
    )


class ChatContinueRequest(BaseSchema):
    app_key: str = Field(
        description="app key",
        serialization_alias="AppKey",
    )
    user_id: str = Field(
        description="user id",
        serialization_alias="UserID",
    )
    message_id: str = Field(
        description="message id",
        serialization_alias="MessageID",
    )
    resp_data_standard: bool = Field(
        description="is resp data standard or not",
        serialization_alias="RespDataStandard",
    )


class Sorter(BaseSchema):
    sort_field: str = Field(
        description="sort field",
        validation_alias="SortField",
        default="",
    )
    sort_order: str = Field(
        description="sort order: desc or asc, default desc",
        validation_alias="SortOrder",
        default="",
    )


class ListOpt(BaseSchema):
    sort: list[Sorter] = Field(
        description="sort list",
        serialization_alias="Sort",
    )
    page_number: int = Field(
        description="page number",
        serialization_alias="PageNumber",
    )
    page_size: int = Field(
        description="page size",
        serialization_alias="PageSize",
    )


class ListLongMemoryFilter(BaseSchema):
    start_time: str = Field(
        description="start time, timeRFC3339 format",
        serialization_alias="StartTime",
    )
    end_time: str = Field(
        description="end time, timeRFC3339 format",
        serialization_alias="EndTime",
    )
    keyword: str = Field(
        description="keyword",
        serialization_alias="Keyword",
    )


class ListLongMemoryRequest(BaseSchema):
    app_key: str = Field(
        description="app key",
        serialization_alias="AppKey",
    )
    user_id: str = Field(
        description="user id",
        serialization_alias="UserID",
    )
    list_opt: Optional[ListOpt] = Field(
        description="list opt",
        serialization_alias="ListOpt",
    )
    filter: Optional[ListLongMemoryFilter] = Field(
        description="list long memory filter",
        serialization_alias="Filter",
    )


class LongMemoryItem(BaseSchema):
    memory_id: str = Field(
        description="long memory id",
        validation_alias="MemoryID",
        default="",
    )
    memory: str = Field(
        description="long memory",
        validation_alias="Memory",
        default="",
    )
    memory_vector_raw_dim: int = Field(
        description="memory vector raw dim",
        validation_alias="MemoryVectorRawDim",
        default=0,
    )
    created_timestamp: int = Field(
        description="created timestamp, seconds granularity",
        validation_alias="CreateTimestamp",
        default=0,
    )
    updated_timestamp: int = Field(
        description="updated timestamp, seconds granularity",
        validation_alias="UpdateTimestamp",
        default=0,
    )


class ListLongMemoryResponse(BaseSchema):
    total: int = Field(
        description="total",
        validation_alias="Total",
        default=0,
    )
    items: list[LongMemoryItem] = Field(
        description="items",
        validation_alias="Items",
        default=[],
    )


class UpdateLongMemoryRequest(BaseSchema):
    app_key: str = Field(
        description="app key",
        serialization_alias="AppKey",
    )
    user_id: str = Field(
        description="user id",
        serialization_alias="UserID",
    )
    memory_id: str = Field(
        description="long memory id",
        serialization_alias="MemoryID",
    )
    memory: str = Field(
        description="long memory",
        serialization_alias="Memory",
    )


class DeleteLongMemoryRequest(BaseSchema):
    app_key: str = Field(
        description="app key",
        serialization_alias="AppKey",
    )
    user_id: str = Field(
        description="user id",
        serialization_alias="UserID",
    )
    memory_ids: list[str] = Field(
        description="long memory ids",
        serialization_alias="MemoryIDs",
    )


class ClearLongMemoryRequest(BaseSchema):
    app_key: str = Field(
        description="app key",
        serialization_alias="AppKey",
    )
    user_id: str = Field(
        description="user id",
        serialization_alias="UserID",
    )


class AsyncResumeAppWorkflowRequest(BaseSchema):
    app_key: str = Field(
        description="app key",
        serialization_alias="AppKey",
    )
    user_id: str = Field(
        description="user id",
        serialization_alias="UserID",
    )
    user_type: str = Field(
        description="user type, App:openapi user;IAM:hiagent user;Visitor:web user;Lark:lark user;Wechat: wechat user",
        serialization_alias="UserType",
    )
    run_id: str = Field(
        description="run id",
        serialization_alias="RunID",
    )
    input: str = Field(
        description="input json str",
        serialization_alias="Input",
    )
    debug: bool = Field(
        description="debug mode, if true will not output fully node info, but faster",
        serialization_alias="Debug",
    )


class AsyncResumeAppWorkflowResponse(SyncRunAppWorkflowResponse):
    pass


class SetConversationTopRequest(BaseSchema):
    app_key: str = Field(
        description="app key",
        serialization_alias="AppKey",
    )
    user_id: str = Field(
        description="user id",
        serialization_alias="UserID",
    )
    app_conversation_id: str = Field(
        description="app conversation id",
        serialization_alias="AppConversationID",
    )


class CancelConversationTopRequest(BaseSchema):
    app_key: str = Field(
        description="app key",
        serialization_alias="AppKey",
    )
    user_id: str = Field(
        description="user id",
        serialization_alias="UserID",
    )
    app_conversation_id: str = Field(
        description="app conversation id",
        serialization_alias="AppConversationID",
    )


class QueryAppSkillAsyncTaskRequest(BaseSchema):
    app_key: str = Field(
        description="app key",
        serialization_alias="AppKey",
    )
    user_id: str = Field(
        description="user id",
        serialization_alias="UserID",
    )
    app_conversation_id: str = Field(
        description="app conversation id",
        serialization_alias="AppConversationID",
    )
    task_ids: list[str] = Field(
        description="task ids",
        serialization_alias="TaskIDs",
    )


class AppSkillAsyncTaskInfo(BaseSchema):
    task_id: str = Field(
        description="task id",
        validation_alias="TaskID",
        default="",
    )
    status: str = Field(
        description="status: PROCESSING,SUCCEED,FAILED,INVALID",
        validation_alias="Status",
        default="",
    )
    origin_message_id: str = Field(
        description="origin message id",
        validation_alias="OriginMessageID",
        default="",
    )
    reason: str = Field(
        description="reason",
        validation_alias="Reason",
        default="",
    )
    message_id: str = Field(
        description="message id",
        validation_alias="MessageID",
        default="",
    )


class QueryAppSkillAsyncTaskResponse(BaseSchema):
    infos: list[AppSkillAsyncTaskInfo] = Field(
        description="infos",
        validation_alias="Infos",
        default=[],
    )


class SyncResumeAppWorkflowRequest(BaseSchema):
    app_key: str = Field(
        description="app key",
        serialization_alias="AppKey",
    )
    user_id: str = Field(
        description="user id",
        serialization_alias="UserID",
    )
    user_type: Optional[str] = Field(
        description="user type, App:openapi user;IAM:hiagent user;Visitor:web user;Lark:lark user;Wechat: wechat user",
        serialization_alias="UserType",
    )
    run_id: str = Field(
        description="run id",
        serialization_alias="RunID",
    )
    input: Optional[str] = Field(
        description="input json str",
        serialization_alias="Input",
    )
    debug: Optional[bool] = Field(
        description="debug mode, if true will not output fully node info, but faster",
        serialization_alias="Debug",
    )
    is_stream: Optional[bool] = Field(
        description="is stream or not",
        serialization_alias="IsStream",
    )


class SyncResumeAppWorkflowResponse(SyncRunAppWorkflowResponse):
    pass


class GetAppUserVariablesRequest(BaseSchema):
    app_key: str = Field(
        description="app key",
        serialization_alias="AppKey",
    )
    user_id: str = Field(
        description="user id",
        serialization_alias="UserID",
    )
    conversation_id: str = Field(
        description="conversation id",
        serialization_alias="ConversationID",
    )


class UserVariables(BaseSchema):
    name: str = Field(
        description="user variable name",
        validation_alias="Name",
        serialization_alias="Name",
        default="",
    )
    description: str = Field(
        description="user variable description",
        validation_alias="Description",
        serialization_alias="Description",
        default="",
    )
    scope: str = Field(
        description="user variable scope: Agent,Conversation",
        validation_alias="Scope",
        serialization_alias="Scope",
        default="",
    )
    value: str = Field(
        description="user variable value",
        validation_alias="Value",
        serialization_alias="Value",
        default="",
    )
    default: str = Field(
        description="default value",
        validation_alias="Default",
        serialization_alias="Default",
        default="",
    )
    update_time: str = Field(
        description="update time",
        validation_alias="UpdateTime",
        serialization_alias="UpdateTime",
        default="",
    )


class GetAppUserVariablesResponse(BaseSchema):
    user_variables: list[UserVariables] = Field(
        description="user variables",
        validation_alias="UserVariables",
        default=[],
    )


class SetAppUserVariablesRequest(BaseSchema):
    app_key: str = Field(
        description="app key",
        serialization_alias="AppKey",
    )
    user_id: str = Field(
        description="user id",
        serialization_alias="UserID",
    )
    conversation_id: str = Field(
        description="conversation id",
        serialization_alias="ConversationID",
    )
    user_variables: list[UserVariables] = Field(
        description="user variables",
        serialization_alias="UserVariables",
    )


class QueryTriggerRunRecordsRequest(BaseSchema):
    app_key: str = Field(
        description="app key",
        serialization_alias="AppKey",
    )
    user_id: str = Field(
        description="user id",
        serialization_alias="UserID",
    )
    run_ids: list[str] = Field(
        description="run ids",
        serialization_alias="RunIDs",
    )
    page: int = Field(
        description="page number",
        serialization_alias="Page",
    )
    size: int = Field(
        description="page size",
        serialization_alias="Size",
    )


class TriggerPromptConfig(BaseSchema):
    content: str = Field(
        description="content",
        validation_alias="Content",
        default="",
    )
    inputs: dict[str, str] = Field(
        description="inputs",
        validation_alias="Inputs",
        default={},
    )


class TriggerToolConfig(BaseSchema):
    tool_id: str = Field(
        description="tool id",
        validation_alias="ToolID",
        default="",
    )
    input_data: str = Field(
        description="input data json str",
        validation_alias="InputData",
        default="",
    )
    input_data_schema: str = Field(
        description="input data schema",
        validation_alias="InputDataSchema",
        default="",
    )


class TriggerWorkflowConfig(BaseSchema):
    workflow_id: str = Field(
        description="workflow id",
        validation_alias="WorkflowID",
        default="",
    )
    input_data: str = Field(
        description="input data json str",
        validation_alias="InputData",
        default="",
    )
    input_data_schema: str = Field(
        description="input data schema",
        validation_alias="InputDataSchema",
        default="",
    )


class NodeParameters(BaseSchema):
    name: str = Field(
        description="node parameter name",
        validation_alias="Name",
        default="",
    )
    desc: str = Field(
        description="node parameter description",
        validation_alias="Desc",
        default="",
    )
    required: bool = Field(
        description="node parameter required",
        validation_alias="Required",
        default=False,
    )
    type: str = Field(
        description="node parameter type:-1:Unknown;0:String;1Integer;2:Boolean;3:Number;4:Object;5:ArrayOfString;6:ArrayOfInteger;7:ArrayOfBoolean;8:ArrayOfNumber;9:ArrayOfObject;10:File;11:ArrayOfFile",
        validation_alias="Type",
        default="",
    )
    sub_parameters: list["NodeParameters"] = Field(
        description="sub parameters",
        validation_alias="SubParameters",
        default=[],
    )
    default: str = Field(
        description="default value",
        validation_alias="Default",
        default="",
    )
    is_secret: bool = Field(
        description="is secret",
        validation_alias="IsSecret",
        default=False,
    )
    is_visible: Optional[bool] = Field(
        description="is visible",
        validation_alias="IsVisible",
        default=False,
    )
    file_category: Optional[str] = Field(
        description="file category: Doc,Txt,Image,Audio,Video,Compressed",
        validation_alias="FileCategory",
        default="",
    )
    desc_en: str = Field(
        description="description en",
        validation_alias="DescEn",
        default="",
    )
    desc_zh_hans: str = Field(
        description="description zh",
        validation_alias="DescZhHans",
        default="",
    )
    desc_zh_hant: str = Field(
        description="description zh-hant",
        validation_alias="DescZhHant",
        default="",
    )


class TriggerConfig(BaseSchema):
    name: str = Field(
        description="trigger name",
        validation_alias="Name",
        default="",
    )
    trigger_type: str = Field(
        description="trigger type: Cron,Event",
        validation_alias="Type",
        default="",
    )
    cron_expr: Optional[str] = Field(
        description="cron expr",
        validation_alias="CronExpr",
        default="",
    )
    show_cron_expr: bool = Field(
        description="show cron expr",
        validation_alias="ShowCronExpr",
        default=False,
    )
    task_type: str = Field(
        description="task type: Prompt,Plugin,Workflow",
        validation_alias="TaskType",
        default="",
    )
    prompt_config: Optional[TriggerPromptConfig] = Field(
        description="prompt config",
        validation_alias="PromptConfig",
        default=None,
    )
    tool_config: Optional[TriggerToolConfig] = Field(
        description="tool config",
        validation_alias="ToolConfig",
        default=None,
    )
    workflow_config: Optional[TriggerWorkflowConfig] = Field(
        description="workflow config",
        validation_alias="WorkflowConfig",
        default=None,
    )
    webhook_key: Optional[str] = Field(
        description="webhook key",
        validation_alias="WebhookKey",
        default="",
    )
    bearer_token: Optional[str] = Field(
        description="bearer token",
        validation_alias="BearerToken",
        default="",
    )
    request_parameter_schema: list[NodeParameters] = Field(
        description="request parameters schema",
        validation_alias="RequestParameterSchema",
        default=[],
    )

class TriggerRunRecord(BaseSchema):
    run_id: str = Field(
        description="run id",
        validation_alias="RunID",
        default="",
    )
    name: str = Field(
        description="trigger name",
        validation_alias="Name",
        default="",
    )
    trigger_config: Optional[TriggerConfig] = Field(
        description="trigger config",
        validation_alias="TriggerConfig",
        default=None,
    )
    scene: str = Field(
        description="trigger scene: debug,production",
        validation_alias="Scene",
        default="",
    )
    query: Optional[str] = Field(
        description="query string",
        validation_alias="Query",
        default="",
    )
    answer: Optional[str] = Field(
        description="answer string",
        validation_alias="Answer",
        default="",
    )
    user_id: Optional[str] = Field(
        description="user id",
        validation_alias="UserID",
        default="",
    )
    status: str = Field(
        description="run status: running,succeed,failed",
        validation_alias="Status",
        default="",
    )
    reason: Optional[str] = Field(
        description="reason string",
        validation_alias="Reason",
        default="",
    )


class QueryTriggerRunRecordsResponse(BaseSchema):
    total: int = Field(
        description="total number",
        validation_alias="total",
        default=0,
    )
    records: list[TriggerRunRecord] = Field(
        description="trigger records",
        validation_alias="records",
        default=[],
    )
