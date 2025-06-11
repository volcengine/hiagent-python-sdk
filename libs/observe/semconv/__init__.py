from enum import Enum


class SpanType(Enum):
    START: str = "start"
    """
    START 表示开始调用模型或者工作流
    """
    END: str = "end"
    """
    END 停止调用模型或者工作流
    """
    LLM: str = "llm"
    """
    LLM 大模型调用节点
    """
    QA: str = "qa"
    """
    QA 代表问答库调用节点
    """
    KNOWLEDGE: str = "knowledge"
    """
    KNOWLEDGE 代表知识库调用节点
    """
    WORKFLOW: str = "workflow"
    """
    WORKFLOW 代表工作流的调用节点
    """
    RERANK: str = "rerank"
    """
    RERANK 代表 rerank 模型调用节点
    """
    EMBEDDINGS: str = "embeddings"
    """
    EMBEDDINGS 代表向量化模型调用节点
    """
    TOOL: str = "tool"
    """
    TOOL 代表工具调用节点
    """
    TERMINLOGY: str = "terminology"
    """
    TOOL_CALL 代表术语库调用节点
    """


class SemanticConvention:
    """
    定义常用的语义化的属性
    """

    APP_ID: str = "app_id"
    """
    APP_ID 是应用中的保留字，不允许设置，如果设置，将会在 collector 中被覆盖为当前自定义应用的 ID
    """

    WORKSPACE_ID: str = "workspace_id"
    """
    WORKSPACE_ID 是工作区的保留字，是 HiAgent 平台内工作区的唯一标识符，如果设置，将会在 collector 中被覆盖为当前自定义应用所在工作区的 ID
    """

    USER_ID: str = "user_id"
    """
    USER_ID 当前会话的用户 ID
    """

    TENANT_ID: str = "tenant_id"
    """
    TENANT_ID 是当前会话的租户 ID
    """

    CONVERSATION_ID: str = "conversation_id"
    """
    Conversation ID 是会话的保留字，是用户在一个有完整上下文的会话唯一标识符
    """

    MESSAGE_ID: str = "message_id"
    """
    Message ID 是会话中的保留字，是用户在一个问答中的唯一标识符
    """

    MODEL_ID: str = "model_id"
    """
    Model ID 是在对话中使用的模型的 ID
    """

    MODEL_NAME: str = "model_name"
    """
    Model Name 是在对话中使用的模型名称
    """

    MODEL_PROVIDER: str = "model_provider"
    """
    Model Provider 是模型提供者的保留字，是模型提供者的名称
    """

    NODE_ID: str = "node_id"
    """
    Node ID 如果在工作流中则是工作流的节点 ID
    """

    WORKFLOW_ID: str = "workflow_id"
    """
    Workflow ID 如果在有工作流中的工作流 ID
    """

    TOP_P: str = "top_p"
    """
    TOP_P 是模型生成的概率阈值
    """

    TEMPERATURE: str = "temperature"
    """
    TEMPERATURE 是模型生成的温度阈值
    """

    TOP_K: str = "top_k"
    """
    TOP_K 是知识库的召回数量阈值
    """

    STREAM: str = "stream"
    """
    STREAM 是否是流式返回
    """

    SPAN_TYPE: str = "span_type"
    """
    SPAN_TYPE 是 span 的类型，用于在页面上拆分不同的展示类型
    """

    REQUEST_ID: str = "request_id"
    """
    Request ID 是请求的唯一标识符
    """

    LATENCY: str = "latency"
    """
    LATENCY 是请求的延迟时间，毫秒为单位
    """

    LATENCT_FIRST_RESP: str = "latencyFirstResp"
    """
    LATENCT_FIRST_RESP 是首 token 的延迟时间，毫秒为单位
    """

    INPUT: str = "input"
    """
    INPUT 是用户输入
    """

    INPUT_RAW: str = "inputRaw"
    """
    INPUT_RAW 是用户输入的原始数据
    """

    OUTPUT: str = "output"
    """
    OUTPUT 是模型生成的结果
    """

    OUTPUT_RAW: str = "outputRaw"
    """
    OUTPUT_RAW 是模型生成的结果的原始数据
    """
