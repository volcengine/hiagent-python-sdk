# Hibot Python SDK

Python client for the Hibot Managed Agent platform. The public API is aligned
to `hibot_engine/api/idl/server.thrift`: every Hibot Action is signed for
`hibot-server` at version `2026-04-23`; artifact uploads use the separate `up`
service. The SDK also preserves VOLC v4 signing and SSE event normalization.

> Distribution name: `hibot` (PyPI). Top-level import: `hibot`.
>
> Requires **Python 3.10+**, depends on `httpx>=0.28.1`.

---

## Install

```bash
# editable / dev (recommended for source checkout):
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# or as a wheel:
pip install hibot
```

## Quick start

```python
import hibot

cfg = hibot.Config(
    endpoint="https://open.volcengineapi.com",
    access_key="AKLT...",
    secret_key="...",
    workspace_id="WS-12345",
)

with hibot.Hibot(cfg) as client:
    # 1. Pick a base model (no Provider/Type filter ⇒ first match)
    model = client.v1.models.get(hibot.V1ModelGetParams(
        model_name="doubao-seed-2-0-pro-260215",
    ))

    # 2. Create an agent (default Environment auto-selected)
    agent = client.v1.agents.create(hibot.V1AgentNewParams(
        name="weather-bot",
        system="You are a weather assistant.",
        model=hibot.V1ManagedAgentModelConfigParams(id=model.id),
    ))

    # 3. Open a session (Peer auto-injected: webchat / system / agent_id)
    session = client.v1.sessions.create(
        hibot.V1SessionNewParams(agent_id=agent.id)
    )

    # 4a. Streaming chat
    with client.v1.sessions.chat_streaming(
        session.id,
        hibot.V1SessionChatParams(input="What's the weather?"),
    ) as stream:
        for event in stream:
            if event.type == "delta":
                print(event.delta.text, end="", flush=True)
            elif event.type == "completed":
                print()  # newline at end
        final = stream.final_message()

    # 4b. Or block until completion
    msg = client.v1.sessions.chat(
        session.id,
        hibot.V1SessionChatParams(input="Same question."),
    )
    print(msg.content)
```

## Public surface

Top-level (`hibot`):

| Symbol                        | Description                                                |
| ----------------------------- | ---------------------------------------------------------- |
| `Hibot` / `Client`            | Main SDK client (alias)                                    |
| `Config`                      | Endpoint + AK/SK + WorkspaceID + region/services overrides |
| `APIError`                    | Raised on non-2xx or non-empty `ResponseMetadata.Error`    |
| `V1*` types                   | All resource & param dataclasses (re-exported from `v1`)   |
| `BASE_MODELS` / `BASE_MODEL_*`| Built-in model catalog & constants                         |

Resource services live under `client.v1.*`:

- `client.v1.uploads` — `upload_blob` (routes to `/up` subpath via `up` service)
- `client.v1.environments` — `create / list / get / update / delete / default / list_workspace_specs`
- `client.v1.models` — `get / list / create / update / delete / list_providers / list_model_providers / get_model_provider / get_model_provider_credential_schema`
- `client.v1.prompts` — `create / list / update / delete`
- `client.v1.resources` — resource/directory CRUD plus `batch_create / batch_get / move`
- `client.v1.mcps` — CRUD plus `batch_get / test_connection / resolve`
- `client.v1.skills` — CRUD/version resolution plus parse, batch-get, and Ark Skill Hub operations
- `client.v1.agents` — CRUD, batch-get, and `retry_create / stop / resume`
- `client.v1.channels` — channel CRUD
- `client.v1.sessions` — session/message CRUD, batch-get, timeline history, `chat / chat_streaming / chat_resume / approve / cancel_run`
- `client.v1.runtime_api_keys` — runtime key create/list/reveal/update/delete
- `client.v1.runs` — persisted Run list/detail read model
- `client.v1.cron_jobs` — Cron CRUD, run history/sync, toggle, and run-now
- `client.v1.observations` — Trace list, Span list, and Span detail
- `client.v1.overview` — workspace overview aggregation
- `client.v1.metrics` — overview, trend, TopK, and breakdown queries
- `client.v1.memories` — MemoryStore and MemoryFile CRUD/search

## Routing & versioning

| Domain                         | Service (default)  | Version      |
| ------------------------------ | ------------------ | ------------ |
| Hibot API (CRUD/model/chat)    | `hibot-server`     | `2026-04-23` |
| Uploads                        | `up` (under `/up`) | `2022-01-01` |

The active service identifiers can be overridden on `Config` for private
deployments (`server_service` / `up_service`). The deprecated
`gateway_service` and `model_service` inputs remain as compatibility aliases
but all Hibot Actions are signed and routed with `server_service`.

The SDK injects `WorkspaceID` only at the **top level** of each Action body
(never inside `Payload`), matching the current server IDL.

## Stream events

`V1SessionChatStream` normalizes the server’s several event-name dialects
(message.chunk / message_delta / run_completed / message.failed / run_failed /
tool_started / tool_completed / …) into the canonical three-state set:

```
delta            — incremental token chunk; access via event.delta.text
completed        — final V1Message; access via event.message or stream.final_message()
failed           — populated event.error.code / event.error.message
tool_start       — tool invocation began
tool_complete    — tool invocation finished
approval_request / approval_responded / run_cancelling / run_cancelled — passthrough
```

Two helpers are available on the stream:

- `accumulate()` — drains the stream, concatenates all `delta.text`, returns the
  final `V1Message` (server-supplied content takes precedence).
- `final_message()` — returns the last `completed` message or raises if none.

## Failure semantics

`Config.__post_init__` performs **fail-fast** validation: missing
`endpoint` / `access_key` / `secret_key` / `workspace_id` raises immediately.

Service methods reject empty required identifiers (e.g. `agent_id`, `session_id`)
the same way the Go SDK does.

## Field alignment with Hibot server

The wire-format JSON schema is identical: response classes deserialize from
PascalCase keys (e.g. `ID`, `WorkspaceID`, `CreatedAt`). Notable mappings that
deviate from a literal field name:

| Python attribute       | JSON key on the wire                       |
| ---------------------- | ------------------------------------------ |
| `V1MCP.endpoint`       | `URL` (server stores as URL)               |
| `V1Prompt.content`     | `SystemPrompt` (the action payload field)  |
| `V1ManagedAgentSkillToolParams.skill_version_id` → `Skills[].ID` (binding refs the version) |

Skill bindings use the **version ID** in the `Skills[].ID` slot — pass the
`SkillVersion.ID` from `client.v1.skills.list_versions` / `resolve_version`.

## Running tests

```bash
pytest -q
```

The normal suite is offline: it uses `httpx.MockTransport` to inspect
URL/Action/Version/Authorization headers and request bodies, plus simulated
SSE payloads to exercise the chat stream.

Real create → runtime-ready → session → streaming Chat → synchronous Chat →
cleanup tests are enabled when these variables are present:

```bash
export HIBOT_ENDPOINT="http://..."
export HIBOT_AK="..."
export HIBOT_SK="..."
export HIBOT_WORKSPACE_ID="..."
pytest -q libs/hibot/tests/test_real_env.py -s
```

`HIBOT_E2E_ENV_IMAGE_TYPE` and `HIBOT_E2E_MODEL_ID` can select a known-good
runtime and model. The real test fails unless the Agent reaches
`RuntimeStatus.Ready` and both Chat modes complete; created resources are
removed in `finally` blocks.

## Differences from the Go SDK

The Python SDK aims for behavioural parity but is implemented as a single
synchronous client (no goroutine-style ctx). Other notable differences:

- **No `context.Context`.** `httpx.Client.timeout` (set on `Config.timeout`)
  governs total request time. Streaming chat disables the per-call timeout
  (parity with Go's `DoStream`).
- **dataclasses, not pydantic.** Result classes use Python `dataclass` with
  field metadata for JSON name mapping; param classes use `dataclass` with
  snake_case Python attributes. (See `hibot/v1/types.py`.)
- **No async client** is provided in this MVP. The `async_http_client` slot
  on `Config` is reserved for future use.
