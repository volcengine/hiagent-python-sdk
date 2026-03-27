# HiAgent Python SDK SOP

## Overview
HiAgent-Python-SDK is a comprehensive SDK for building AI native applications. It provides APIs for chat, tools, workflows, knowledge retrieval, evaluation, and observability.

## Architecture

```
hiagent-sdk/
├── libs/api/                    # API clients for services
│   ├── chat.py                  # ChatService - conversation management
│   ├── tool.py                  # ToolService - tool execution
│   ├── workflow.py              # WorkflowService - workflow execution
│   ├── knowledgebase.py         # KnowledgebaseService - knowledge management
│   ├── eva.py                   # EvaService - evaluation
│   ├── observe.py               # ObserveService - tracing/observability
│   └── up.py                    # UPService - file upload/download
│
├── libs/components/             # High-level components
│   ├── agent/                   # Agent component
│   ├── tool/                    # Tool wrapper
│   ├── workflow/                # Workflow component
│   ├── retriever/               # Knowledge retriever
│   └── integrations/            # LangChain/MCP integrations
│
└── libs/eva/, libs/observe/     # Evaluation and observability modules
```

## Service Domains

### 1. Chat Service (`hiagent_api.chat`)
**Service**: `ChatService(endpoint="...", region="...")`

**Core Methods**:
- `create_conversation(app_key, conversation)` - Create new conversation
- `chat(app_key, req)` - Send chat message
- `get_app(app_key, params)` - Get app configuration
- `get_conversation_message(app_key, req)` - Get conversation messages
- Streaming support for real-time responses

**Types**:
- `ChatRequest`, `ChatAgainRequest`, `ChatContinueRequest`
- `CreateConversationRequest`, `CreateConversationResponse`
- `ChatEvent` types (Message, AgentThought, ToolMessage, etc.)

### 2. Tool Service (`hiagent_api.tool`)
**Service**: `ToolService(endpoint="...", region="...")`

**Core Methods**:
- `get_archived_tool(params)` - Get tool details
- `exec_archived_tool(params)` - Execute tool
- Async variants available

**Types**:
- `GetArchivedToolRequest`, `GetArchivedToolResponse`
- `ExecArchivedToolRequest`, `ExecArchivedToolResponse`

**Components**:
- `Tool.init(svc, workspace_id, tool_id)` - Initialize tool wrapper
- `ExecutableTool` - Execute any Executable

### 3. Workflow Service (`hiagent_api.workflow`)
**Service**: `WorkflowService(endpoint="...", region="...")`

**Core Methods**:
- `get_workflow(params)` - Get workflow details
- `run_workflow(params)` - Run workflow
- `query_workflow_status(params)` - Query status
- `resume_workflow(params)` - Resume execution
- Async variants available

**Types**:
- `GetWorkflowRequest`, `GetWorkflowResponse`
- `RunWorkflowRequest`, `RunWorkflowResponse`
- `QueryWorkflowStatusRequest`, `QueryWorkflowStatusResponse`

**Components**:
- `Workflow.init(svc, app_key, workspace_id, workflow_id, user_id)` - Initialize workflow

### 4. Knowledgebase Service (`hiagent_api.knowledgebase`)
**Service**: `KnowledgebaseService(endpoint="...", region="...")`

**Core Methods**:
- Knowledge dataset management
- Document retrieval and search

**Types**:
- Dataset and document management types

### 5. Evaluation Service (`hiagent_api.eva`, `hiagent_eva`)
**Service**: `EvaService` (EvaService in API + EvaluationClient in eva module)

**Core Methods**:
- Create evaluation tasks
- Run inference and evaluation
- Query evaluation results
- Manage evaluation datasets

**Types**:
- Evaluation task and dataset types

### 6. Observability Service (`hiagent_api.observe`, `hiagent_observe`)
**Service**: `ObserveService` (ObserveService in API + ObserveClient/Semantic conventions)

**Core Methods**:
- Create API tokens
- List traces and spans
- Tracing and metrics collection

**Components**:
- `ObserveClient` - High-level client
- Semantic conventions for tracing

### 7. UP Service (`hiagent_api.up`)
**Service**: `UPService` (Upload/Download Service)

**Core Methods**:
- `UploadRaw(params, file)` - Upload file stream
- `DownloadKey(params)` - Get download key for a path
- `Download(params)` - Download to local path (`SaveTo`)
- `Delete(params)` - Delete file by id/sha256

**Types**:
- Upload and download request/response types
- Long-lived upload session support

## Authentication and Configuration

### Environment Variables
```bash
HIAGENT_TOP_ENDPOINT=https://open.volcengineapi.com
HIAGENT_REGION=cn-north-1
HIAGENT_APP_BASE_URL=...
HIAGENT_AGENT_APP_KEY=...
HIAGENT_WORKSPACE_ID=...
```

### Service Initialization Pattern
```python
from hiagent_api.chat import ChatService
from hiagent_api.tool import ToolService

# Common pattern for all services
def get_chat_svc():
    return ChatService(
        endpoint=os.getenv("HIAGENT_TOP_ENDPOINT"),
        region=os.getenv("HIAGENT_REGION", "cn-north-1")
    )

def get_tool_svc():
    return ToolService(
        endpoint=os.getenv("HIAGENT_TOP_ENDPOINT"),
        region=os.getenv("HIAGENT_REGION", "cn-north-1")
    )
```

## Component Usage Patterns

### Agent Component
```python
from hiagent_components.agent import Agent
from hiagent_api.chat import ChatService

agent = Agent.init(
    svc=get_chat_svc(),
    app_key=app_key,
    user_id=user_id,
    variables={"name": "assistant"},
    name="My Assistant"
)

result = agent.invoke({"query": "Hello"})
```

### Tool Component
```python
from hiagent_components.tool import Tool
from hiagent_api.tool import ToolService

tool = Tool.init(
    svc=get_tool_svc(),
    workspace_id=workspace_id,
    tool_id=tool_id
)

result = tool.invoke({"input": data})
```

### Workflow Component
```python
from hiagent_components.workflow import Workflow
from hiagent_api.workflow import WorkflowService

workflow = Workflow.init(
    svc=get_workflow_svc(),
    app_key=app_key,
    workspace_id=workspace_id,
    workflow_id=workflow_id,
    user_id=user_id
)

result = workflow.invoke({"input": data})
```

### Knowledge Retriever
```python
from hiagent_components.retriever import KnowledgeRetriever
from hiagent_api.knowledgebase import KnowledgebaseService

retriever = KnowledgeRetriever(
    svc=get_knowledgebase_svc(),
    name="knowledge_tool",
    description="Search knowledge base",
    workspace_id=workspace_id,
    dataset_ids=[dataset_id],
    top_k=3,
    score_threshold=0.4
)

result = retriever.invoke({"query": "search term"})
```

## Error Handling

All services return error objects with common structure:
- BaseError with ResponseMetadata containing error Code and Error fields
- Check using `ChatService.IsErrorResult(json_str)` for error detection

## Streaming Support

Chat and Workflow services support streaming responses:
- Async generators for real-time event streams
- Event types: Message, AgentThought, ToolMessage, KnowledgeRetrieve, etc.
- Suitable for long-running operations and real-time updates

## Key Design Patterns

1. **Service + Component Pattern**: Low-level API services with high-level component wrappers
2. **Executable Interface**: Common `invoke()`/`ainvoke()` interface across components
3. **Pydantic Models**: Type-safe request/response handling
4. **Namespace Packages**: `hiagent_api.*` and `hiagent_components.*` namespaces
5. **LangChain Integration**: Components implement LangChain interfaces for easy integration
