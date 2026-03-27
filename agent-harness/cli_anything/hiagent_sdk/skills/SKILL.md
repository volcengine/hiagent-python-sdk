---
name: "cli-anything-hiagent"
description: "Command-line interface for HiAgent Python SDK - manage AI agent conversations, workflows, tools, and knowledge retrieval via CLI"
---

# cli-anything-hiagent

Command-line interface for the HiAgent Python SDK built by Hiagent. This CLI provides programmatic access to HiAgent's AI agent capabilities, including chat conversations, workflow execution, tool management, and knowledge base operations.

## Installation

```bash
pip install cli-anything-hiagent
```

## Installation from source

```bash
uv pip install -e agent-harness
```

**Prerequisites:**
- HiAgent Python SDK (`hiagent-api`, `hiagent-components`)
- Volcano Engine credentials (request signing)
  - `VOLC_ACCESSKEY` / `VOLC_SECRETKEY` environment variables, or
  - `~/.volc/.env`

## Configuration

Set up HiAgent credentials using environment variables or CLI config:

```bash
# Environment variables
export VOLC_ACCESSKEY="..."
export VOLC_SECRETKEY="..."
export HIAGENT_AGENT_APP_KEY="your-app-key"
export HIAGENT_WORKSPACE_ID="your-workspace-id"
export HIAGENT_TOP_ENDPOINT="https://open.volcengineapi.com"

# Or use CLI config command
cli-anything-hiagent config set --app-key "your-app-key" --workspace-id "your-workspace-id"
```

View current configuration:

```bash
cli-anything-hiagent config show
```

## Session Management

Sessions store conversation/workflow/tool context for reuse:

```bash
# Create a session
cli-anything-hiagent session create my-session \
  --conversation-id conv-123 \
  --tool-id tool-456 \
  --dataset-ids ds-001,ds-002

# List all sessions
cli-anything-hiagent session list

# Show session details
cli-anything-hiagent session show my-session

# Delete a session
cli-anything-hiagent session delete my-session
```

## Chat Commands

Converse with AI agents:

```bash
# Create a new conversation
cli-anything-hiagent chat create --app-key "your-app-key" \
  --user-id "user123" \
  -v name="my_agent" \
  -v version="1.0"

# Send a message
# Non-streaming (waits for complete response)
cli-anything-hiagent chat send --app-key "your-app-key" \
  --conversation-id conv-123 \
  -q "What is the weather like?"

# Streaming (receives response chunks as generated)
cli-anything-hiagent chat send --app-key "your-app-key" \
  --conversation-id conv-123 \
  -q "Tell me a story" \
  --stream
```

## Tool Commands

Execute registered tools:

```bash
# Execute tool with inline JSON input
cli-anything-hiagent tool execute \
  --workspace-id ws-123 \
  --tool-id tool-456 \
  --input '{"input": "Hello world"}'

# Execute tool with JSON file input
cli-anything-hiagent tool execute \
  --workspace-id ws-123 \
  --tool-id tool-456 \
  --input @data.json
```

## Workflow Commands

Run AI workflows:

```bash
# Run workflow (non-streaming)
cli-anything-hiagent workflow run \
  --app-key "your-app-key" \
  --workspace-id ws-123 \
  --workflow-id wf-456 \
  --user-id "user123" \
  --input '{"question": "What is AI?"}'

# Run workflow (streaming)
cli-anything-hiagent workflow run \
  --app-key "your-app-key" \
  --workspace-id ws-123 \
  --workflow-id wf-456 \
  --user-id "user123" \
  --input '{"question": "What is AI?"}' \
  --stream
```

## Knowledge Commands

Retrieve information from knowledge datasets:

```bash
cli-anything-hiagent knowledge retrieve \
  --workspace-id ws-123 \
  --dataset-ids ds-001,ds-002 \
  -q "Python programming best practices" \
  --top-k 5 \
  --score-threshold 0.5
```

## Observe Commands

Observe service for API Token management and Trace/Span observability:

```bash
# Create API Token
cli-anything-hiagent observe token create \
  --workspace-id ws-123 \
  --custom-app-id app-456

# List trace spans
cli-anything-hiagent observe trace list \
  --workspace-id ws-123 \
  --page-size 10 \
  --sort-by StartTime \
  --sort-order Desc

# List trace spans with pagination
cli-anything-hiagent observe trace list \
  --workspace-id ws-123 \
  --page-size 20 \
  --last-id last-doc-id \
  --sort-by Latency \
  --sort-order Asc
```

### Observe Command Options

**token create:**
- `--workspace-id` (required): Workspace ID
- `--custom-app-id` (required): Custom App ID

**trace list:**
- `--workspace-id` (required): Workspace ID
- `--page-size`: Page size (default: 10)
- `--last-id`: Last ID for pagination
- `--sort-by`: Sort field (StartTime, Latency, LatencyFirstResp, TotalTokens)
- `--sort-order`: Sort order (Asc, Desc)

## File Commands

Upload and download files:

```bash
# Upload file
cli-anything-hiagent file upload \
  --file document.pdf \
  --expire 15h

# Download file
cli-anything-hiagent file download \
  --path "/path/from/upload" \
  --output document.pdf
```

## JSON Output Mode

Use `--json` flag for machine-readable output (essential for AI agents):

```bash
cli-anything-hiagent --json chat send --app-key key --conversation-id conv-123 -q "Hello"
cli-anything-hiagent --json session list
cli-anything-hiagent --json workflow run --app-key key --workspace-id ws-123 --workflow-id wf-456
```

JSON output format:
```json
{
  "success": true,
  "message": "Operation completed",
  "data": { ... }
}
```

## REPL Mode

Run without arguments to enter interactive REPL:

```bash
cli-anything-hiagent
```

REPL provides:
- Command history
- Colored output
- Inline help

## Return Codes

- `0` - Success
- `1` - Error (with error message in `message` field of JSON output)

## Error Handling

All commands output errors in both human-readable and JSON formats:

```bash
# Human-readable error
$ cli-anything-hiagent tool execute --workspace-id invalid-ws --tool-id tool-456
✗ Failed to execute tool: Invalid workspace ID

# JSON error
$ cli-anything-hiagent --json tool execute --workspace-id invalid-ws --tool-id tool-456
{
  "success": false,
  "message": "Invalid workspace ID",
  "data": null
}
```

## Examples

### Complete chat workflow

```bash
# 1. Create conversation
CONV_ID=$(cli-anything-hiagent --json chat create \
  --app-key "$APP_KEY" \
  --user-id "user123" \
  -v name="assistant" | jq -r '.data.conversation.app_conversation_id')

# 2. Send initial message
cli-anything-hiagent chat send \
  --app-key "$APP_KEY" \
  --conversation-id "$CONV_ID" \
  -q "Hello!"

# 3. Send follow-up message with streaming
cli-anything-hiagent --json chat send \
  --app-key "$APP_KEY" \
  --conversation-id "$CONV_ID" \
  -q "Tell me more" \
  --stream
```

### Batch tool execution

```bash
# Read tool configurations from file and execute
cat tools.json | jq -r '.tools[] | "\(.workspace_id) \(.tool_id)"' | \
while read ws tool; do
  cli-anything-hiagent tool execute --workspace-id "$ws" --tool-id "$tool"
done
```

## System Requirements

- Python >= 3.10
- HiAgent API access with valid Volcano Engine credentials
- Network access to HiAgent endpoints

## License

Apache-2.0

---

*Generated by Hiagent*
