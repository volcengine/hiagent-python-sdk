# HiAgent SDK CLI

Command-line interface for the HiAgent Python SDK.

## Installation

### From Source

```bash
cd agent-harness
pip install -e .
```

### Requirements

- Python >= 3.10
- HiAgent Python SDK (`hiagent-api`, `hiagent-components`)
- Access to HiAgent API (requires Volcano Engine credentials)
  - `VOLC_ACCESSKEY` / `VOLC_SECRETKEY` environment variables, or
  - `~/.volc/.env`

## Usage

### Configuration

Set up your HiAgent credentials:

```bash
# Method 1: Using environment variables
export VOLC_ACCESSKEY="..."
export VOLC_SECRETKEY="..."
export HIAGENT_AGENT_APP_KEY="your-app-key"
export HIAGENT_WORKSPACE_ID="your-workspace-id"
export HIAGENT_TOP_ENDPOINT="https://open.volcengineapi.com"

# Method 2: Using CLI config command
cli-anything-hiagent config set --app-key "your-app-key" --workspace-id "your-workspace-id"
```

Show current configuration:

```bash
cli-anything-hiagent config show
```

### REPL Mode

Run without arguments to enter interactive REPL mode:

```bash
cli-anything-hiagent
```

### Commands

#### Session Management

Create a session:

```bash
cli-anything-hiagent session create my-session --conversation-id conv-123 --tool-id tool-456
```

List sessions:

```bash
cli-anything-hiagent session list
```

Show session:

```bash
cli-anything-hiagent session show my-session
```

Delete session:

```bash
cli-anything-hiagent session delete my-session
```

#### Chat Commands

Create a conversation:

```bash
cli-anything-hiagent chat create --app-key "your-app-key" --user-id "user123" -v name="test_agent"
```

Send a message:

```bash
# Non-streaming
cli-anything-hiagent chat send --app-key "your-app-key" --conversation-id conv-123 -q "Hello, world!"

# Streaming
cli-anything-hiagent chat send --app-key "your-app-key" --conversation-id conv-123 -q "Hello!" --stream
```

#### Tool Commands

Execute a tool:

```bash
# With inline JSON
cli-anything-hiagent tool execute --workspace-id ws-123 --tool-id tool-456 --input '{"input": "test"}'

# With file input
cli-anything-hiagent tool execute --workspace-id ws-123 --tool-id tool-456 --input @input.json
```

#### Workflow Commands

Run a workflow:

```bash
# Non-streaming
cli-anything-hiagent workflow run --app-key key --workspace-id ws-123 --workflow-id wf-456 \
  --input '{"question": "What is AI?"}'

# Streaming
cli-anything-hiagent workflow run --app-key key --workspace-id ws-123 --workflow-id wf-456 \
  --input '{"question": "What is AI?"}' --stream
```

#### Knowledge Commands

Retrieve knowledge from datasets:

```bash
cli-anything-hiagent knowledge retrieve \
  --workspace-id ws-123 \
  --dataset-ids ds-001,ds-002 \
  -q "Python programming tips" \
  --top-k 5 \
  --score-threshold 0.5
```

#### File Commands

Upload a file:

```bash
cli-anything-hiagent file upload --file document.pdf --expire 15h
```

Download a file:

```bash
cli-anything-hiagent file download --path "/path/from/upload" --output document.pdf
```

### JSON Output

Use `--json` flag for machine-readable output:

```bash
cli-anything-hiagent --json session list
cli-anything-hiagent --json chat send --app-key key --conversation-id conv-123 -q "Hello"
```

## Development

### Running Tests

```bash
# Install in development mode
pip install -e ".[dev]"

# Run all tests
pytest cli_anything/hiagent_sdk/tests/ -v

# Run specific test types
pytest cli_anything/hiagent_sdk/tests/test_core.py -v

# Run tests against installed CLI
CLI_ANYTHING_FORCE_INSTALLED=1 pytest cli_anything/hiagent_sdk/tests/test_full_e2e.py -v
```

### Project Structure

```
agent-harness/
├── setup.py                      # Package configuration
├── cli_anything/                 # Namespace package (no __init__.py)
│   └── hiagent_sdk/              # HiAgent SDK CLI sub-package
│       ├── __init__.py
│       ├── __main__.py           # python -m cli_anything.hiagent_sdk
│       ├── hiagent_cli.py        # Main CLI entry point
│       ├── core/                 # Core modules
│       │   ├── project.py        # Project configuration
│       │   ├── session.py        # Session management
│       │   ├── services.py       # Service manager
│       │   └── export.py         # Output formatting
│       ├── utils/                # Utilities
│       │   ├── hiagent_backend.py # Backend helpers (invokes real services)
│       │   ├── repl.py           # REPL loop
│       │   └── repl_skin.py      # Unified REPL skin
│       ├── skills/               # Skill definition (installed with package)
│       │   └── SKILL.md
│       └── tests/                # Test suite
│           ├── __init__.py
│           └── TEST.md           # Test documentation
└── README.md                     # This file
```

## API Reference

### Command Groups

- `config` - Configuration management
- `session` - Session management for conversation/workflow/tool context
- `chat` - Chat conversation commands
- `tool` - Tool execution commands
- `workflow` - Workflow execution commands
- `knowledge` - Knowledge base commands
- `file` - File upload/download commands

### Service Classes

All services use the same initialization pattern:
- `ChatService(endpoint, region)` - Conversation management
- `ToolService(endpoint, region)` - Tool execution
- `WorkflowService(endpoint, region)` - Workflow management
- `KnowledgebaseService(endpoint, region)` - Knowledge base access
- `UpService(endpoint, region)` - File upload/download
- `EvaService(endpoint, region)` - Evaluation
- `ObserveService(endpoint, region)` - Observability/tracing

### Component Classes

- `Agent` - AI agent wrapper
- `Tool` - Tool wrapper with LangChain integration
- `Workflow` - Workflow wrapper
- `KnowledgeRetriever` - Knowledge retrieval component

All components integrate with LangChain's ecosystem for maximum compatibility.

## License

Apache-2.0

---

Generated with [Hiagent](https://www.volcengine.com/product/hiagent)
