# Hibot Python SDK

Python client for the Hibot Managed Agent platform. Behaviorally aligned 1:1
with the Go SDK in `hiagent-go-sdk/hibot` — same TOP routing, same VOLC v4
signing, same SSE event normalization, same default-environment + peer
injection semantics.

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
        model_name="doubao-seed-2.0-pro-260215",
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
| `BASE_MODELS` / `BASE_MODEL_*`| Built-in aigw model catalog & constants                    |

Resource services live under `client.v1.*`:

- `client.v1.uploads` — `upload_blob` (routes to `/up` subpath via `up` service)
- `client.v1.environments` — `create / list / get / update / delete / default`
- `client.v1.models` — `get / list / create / update / delete / list_providers / list_model_providers / get_model_provider / get_model_provider_credential_schema`
- `client.v1.prompts` — `create / list / update / delete`
- `client.v1.resources` — `create / list / update / delete / get_by_name / batch_get` (+ nested `client.v1.resources.directories`)
- `client.v1.mcps` — `create / list / get / update / delete / test_connection / resolve`
- `client.v1.skills` — `create / list / get / update / delete / list_versions / resolve_version`
- `client.v1.agents` — `create / list / get / batch_get / update / delete`
- `client.v1.sessions` — `create / list / get / get_by_key / archive / delete / list_messages / get_message / inject_message / chat / chat_streaming`

## Routing & versioning

| Domain         | Service (default)  | Version       |
| -------------- | ------------------ | ------------- |
| CRUD           | `hibot-server`     | `2026-04-23`  |
| Streaming chat | `hibot-gateway`    | `2026-05-11`  |
| Models         | `aigw`             | `2023-08-01`  |
| Uploads        | `up` (under `/up`) | `2022-01-01`  |

All four service identifiers can be overridden on `Config` for private
deployments (`server_service` / `gateway_service` / `model_service` /
`up_service`).

The SDK injects `WorkspaceID` only at the **top level** of each Action body
(never inside `Payload`), exactly mirroring the Go SDK.

## Stream events

`V1SessionChatStream` normalizes the gateway’s several event-name dialects
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

## Field alignment with Go SDK

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

Tests are completely offline — they use `httpx.MockTransport` to inspect
URL/Action/Version/Authorization headers and request bodies, plus simulated
SSE payloads to exercise the chat stream.

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
