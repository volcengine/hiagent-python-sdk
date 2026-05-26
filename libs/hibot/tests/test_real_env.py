"""Real-environment e2e — mirrors go/examples/e2e runRealEnvJourney + TestRealEnvResourceSkillLoop.

Both tests are skipped unless ``HIBOT_E2E_TOP_HOST`` is set (and the AK/SK/
WORKSPACE trio is provided). They hit a real Hibot cluster — fixture content
under ``testdata/`` is shared with this package's real-environment tests.
"""

from __future__ import annotations

import os
import time
import zipfile
from pathlib import Path

import hibot
import pytest
from hibot import (
    V1AgentDeleteParams,
    V1AgentListParams,
    V1AgentNewParams,
    V1AgentNewParamsToolUnion,
    V1ManagedAgentModelConfigParams,
    V1ManagedAgentResourceRefParams,
    V1ManagedAgentSkillToolParams,
    V1Model,
    V1ModelGetParams,
    V1ResourceDeleteParams,
    V1ResourceNewParams,
    V1SessionChatParams,
    V1SessionNewParams,
    V1SkillDeleteParams,
    V1SkillNewParams,
    V1UploadBlobParams,
)

_V1_MANAGED_AGENT_MODEL_DOUBAO_SEED_PRO = "doubao-seed-2.0-pro-260215"
_E2E_SKILL_PULSE_TOKEN = "PULSE_OK_E2E"

_TESTDATA_DIR = Path(__file__).resolve().parents[1] / "testdata"
_E2E_RESOURCE_FIXTURE = _TESTDATA_DIR / "runbook.md"
_E2E_SKILL_FIXTURE_DIR = _TESTDATA_DIR / "skill"


def _trim_env(key: str) -> str:
    """Mirror Go ``trimEnv``: strip whitespace, backticks, and quotes."""
    v = os.environ.get(key, "").strip()
    return v.strip("`'\" ")


def _require_real_env_or_skip() -> str:
    host = _trim_env("HIBOT_E2E_TOP_HOST")
    if not host:
        pytest.skip(
            "real-env tests require HIBOT_E2E_TOP_HOST; skipping in offline-only run"
        )
    return host


def _require_credentials() -> tuple[str, str, str]:
    ak = _trim_env("HIBOT_E2E_AK")
    sk = _trim_env("HIBOT_E2E_SK")
    workspace = _trim_env("HIBOT_E2E_WORKSPACE")
    if not ak or not sk or not workspace:
        pytest.fail(
            "real-env tests require HIBOT_E2E_AK / HIBOT_E2E_SK / HIBOT_E2E_WORKSPACE"
        )
    return ak, sk, workspace


def _new_real_client() -> tuple[hibot.Client, str, str]:
    host = _require_real_env_or_skip()
    ak, sk, workspace = _require_credentials()
    print(f"\nreal-env: host={host} workspace={workspace}")
    cfg = hibot.Config(
        endpoint=host,
        access_key=ak,
        secret_key=sk,
        workspace_id=workspace,
        timeout=120.0,
    )
    return hibot.Hibot(cfg), host, workspace


def _run_streaming_and_collect_events(
    client: hibot.Client,
    session_id: str,
    agent_id: str,
    prompt: str,
):
    """Mirror go runStreamingChat: drain the stream, return (final_msg, event_names)."""
    event_names: list[str] = []
    saw_completed = False
    saw_delta = False
    with client.v1.sessions.chat_streaming(
        session_id, V1SessionChatParams(agent_id=agent_id, input=prompt)
    ) as stream:
        for event in stream:
            event_names.append(event.type)
            if event.type == "delta":
                saw_delta = True
            elif event.type == "completed":
                saw_completed = True
            elif event.type == "failed":
                pytest.fail(
                    f"streaming chat failed: {event.error.message} (events={event_names})"
                )
        if stream.err is not None:
            pytest.fail(
                f"streaming chat err: {stream.err} (events={event_names})"
            )
        if not saw_completed:
            pytest.fail(
                f"streaming chat: no completed event observed (events={event_names})"
            )
        if not saw_delta:
            print(
                f"streaming chat: no delta event (short reply); events={event_names}"
            )
        final_msg = stream.final_message()
    return final_msg, event_names


def test_real_env_journey():
    """Mirrors Go runRealEnvJourney — discover agent, chat streaming + batch."""
    client, _host, workspace = _new_real_client()

    # Step 1: discover an existing agent.
    agents = client.v1.agents.list(V1AgentListParams())
    if not agents:
        pytest.fail(
            f"real-env workspace {workspace!r} has no agents; please pre-create one before running this test"
        )
    agent = agents[0]
    print(f"using agent: id={agent.id} name={agent.name}")

    # Step 2: create a session with no Peer — webchat default path.
    session = client.v1.sessions.create(V1SessionNewParams(agent_id=agent.id))
    if not session.id:
        pytest.fail(f"real-env CreateSession returned empty ID: {session!r}")
    print(f"created session: {session.id}")

    # Step 3: streaming chat — must observe completed.
    streaming_final, streaming_events = _run_streaming_and_collect_events(
        client,
        session.id,
        agent.id,
        "流式真实环境冒烟：请用一句话介绍你自己。",
    )
    if not streaming_final.id or not streaming_final.content:
        pytest.fail(
            f"real-env streaming final message incomplete: {streaming_final!r}"
        )
    print(
        f"streaming final: id={streaming_final.id} content={streaming_final.content!r} events={streaming_events}"
    )

    # Step 4: batch (non-streaming) chat reuses the same session.
    batch_final = client.v1.sessions.chat(
        session.id,
        V1SessionChatParams(
            agent_id=agent.id, input="批量真实环境冒烟：再回答一次同样的问题。"
        ),
    )
    if not batch_final.id or not batch_final.content:
        pytest.fail(f"real-env batch final message incomplete: {batch_final!r}")
    print(f"batch final: id={batch_final.id} content={batch_final.content!r}")


def _build_skill_zip_from_dir(src_dir: Path, out_path: Path) -> Path:
    """Pack ``src_dir`` into a zip placing files at the archive root."""
    if not (src_dir / "SKILL.md").exists():
        pytest.fail(f"skill fixture missing SKILL.md: {src_dir}")
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in src_dir.rglob("*"):
            if path.is_file():
                rel = path.relative_to(src_dir).as_posix()
                zf.write(path, arcname=rel)
    if not out_path.exists() or out_path.stat().st_size == 0:
        pytest.fail(f"skill zip is empty: {out_path}")
    # Defensive: ensure SKILL.md was packed.
    with zipfile.ZipFile(out_path) as zf:
        names = zf.namelist()
    if not any(n == "SKILL.md" or n.endswith("/SKILL.md") for n in names):
        pytest.fail(f"skill zip does not reference SKILL.md: names={names}")
    return out_path


def _resolve_real_env_model(client: hibot.Client) -> V1Model:
    """Mirror Go: prefer HIBOT_E2E_MODEL_ID, then models.get by ModelName, then list[0]."""
    preset = _trim_env("HIBOT_E2E_MODEL_ID")
    if preset:
        print(f"using preset model id={preset} (HIBOT_E2E_MODEL_ID)")
        return V1Model(id=preset)
    try:
        got = client.v1.models.get(
            V1ModelGetParams(model_name=_V1_MANAGED_AGENT_MODEL_DOUBAO_SEED_PRO)
        )
    except Exception as exc:  # noqa: BLE001
        print(
            f"get default model by ModelName={_V1_MANAGED_AGENT_MODEL_DOUBAO_SEED_PRO!r} failed: {exc}; falling back to ListModels"
        )
        listing = client.v1.models.list()
        if not listing.items:
            pytest.fail(
                "real-env workspace has no models; please pre-create one before running this test"
            )
        got = listing.items[0]
        print(
            f"fallback model picked: id={got.id} name={got.name} modelName={got.model_name} type={got.type}"
        )
    else:
        print(
            f"matched model by ModelName: id={got.id} name={got.name} modelName={got.model_name}"
        )
    return got


def test_real_env_resource_skill_loop(tmp_path):
    """Mirrors Go TestRealEnvResourceSkillLoop — full closed loop with cleanup."""
    client, _host, _workspace = _new_real_client()

    # Step 1: pick a usable model.
    model = _resolve_real_env_model(client)

    # Step 2: upload Resource fixture.
    resource_filename = _E2E_RESOURCE_FIXTURE.name
    with open(_E2E_RESOURCE_FIXTURE, "rb") as f:
        runbook_bytes = f.read()
    resource_blob = client.v1.uploads.upload_blob(
        V1UploadBlobParams(filename=resource_filename, content_type="text/markdown"),
        runbook_bytes,
    )
    if not resource_blob.blob_id:
        pytest.fail(f"upload {resource_filename}: empty BlobID")
    resource = client.v1.resources.create(
        V1ResourceNewParams(
            name=f"e2e-runbook-{time.time_ns()}",
            type="document_collection",
            blob_id=resource_blob.blob_id,
        )
    )
    print(f"created resource: id={resource.id} name={resource.name}")

    keep_agent = bool(_trim_env("HIBOT_E2E_KEEP_AGENT"))
    cleanup_records: list[tuple[str, callable]] = []

    def _cleanup():
        if keep_agent:
            return
        for label, fn in reversed(cleanup_records):
            try:
                fn()
            except Exception as exc:  # noqa: BLE001
                print(f"cleanup {label}: {exc}")

    try:
        cleanup_records.append(
            (
                f"resource {resource.id}",
                lambda: client.v1.resources.delete(
                    V1ResourceDeleteParams(resource_id=resource.id)
                ),
            )
        )

        # Step 3: package skill dir into zip and upload.
        skill_zip_path = _build_skill_zip_from_dir(
            _E2E_SKILL_FIXTURE_DIR, tmp_path / "skill.zip"
        )
        with open(skill_zip_path, "rb") as f:
            skill_zip_bytes = f.read()
        skill_blob = client.v1.uploads.upload_blob(
            V1UploadBlobParams(
                filename=skill_zip_path.name, content_type="application/zip"
            ),
            skill_zip_bytes,
        )
        if not skill_blob.blob_id:
            pytest.fail("upload skill zip: empty BlobID")
        skill = client.v1.skills.create(
            V1SkillNewParams(
                name=f"e2e-runbook-skill-{time.time_ns()}",
                description="Skill uploaded by hibot python e2e closed-loop test.",
                blob_id=skill_blob.blob_id,
                enabled=True,
                version="1.0.0",
            )
        )
        if not skill.id:
            pytest.fail("create skill: empty ID")
        print(f"created skill version: id={skill.id}")
        cleanup_records.append(
            (
                f"skill {skill.id}",
                lambda: client.v1.skills.delete(V1SkillDeleteParams(id=skill.id)),
            )
        )

        # Step 4: create temp Agent — bind Skill (Resource attached but not asserted).
        system_prompt = (
            "你是 hibot 端到端测试助手。"
            "用户要求执行 pulse check / 心跳检查时，必须调用 e2e-runbook-skill 工具，"
            "并把工具返回的字面 token 原样返回给用户。"
        )
        agent = client.v1.agents.create(
            V1AgentNewParams(
                name=f"e2e-loop-agent-{time.time_ns()}",
                model=V1ManagedAgentModelConfigParams(id=model.id),
                system=system_prompt,
                tools=[
                    V1AgentNewParamsToolUnion(
                        of_skill=V1ManagedAgentSkillToolParams(
                            skill_version_id=skill.id
                        )
                    )
                ],
                resources=[V1ManagedAgentResourceRefParams(id=resource.id)],
            )
        )
        if not agent.id:
            pytest.fail("create agent: empty ID")
        print(f"created agent: id={agent.id}")
        cleanup_records.append(
            (
                f"agent {agent.id}",
                lambda: client.v1.agents.delete(
                    V1AgentDeleteParams(agent_id=agent.id)
                ),
            )
        )

        # Step 5: create session.
        session = client.v1.sessions.create(V1SessionNewParams(agent_id=agent.id))
        if not session.id:
            pytest.fail("create session: empty ID")
        print(f"created session: {session.id}")

        # Step 6: skill closed loop — trigger pulse check, must observe tool events.
        skill_final, skill_events = _run_streaming_and_collect_events(
            client,
            session.id,
            agent.id,
            "请执行一次 pulse check（按照 e2e-runbook-skill 的契约调用工具），并把工具返回的 token 原样告诉我。",
        )
        print(
            f"skill loop events={skill_events} final={skill_final.content!r}"
        )
        content = skill_final.content or ""
        if _E2E_SKILL_PULSE_TOKEN not in content:
            pytest.fail(
                f"skill loop: agent did not return pulse token {_E2E_SKILL_PULSE_TOKEN!r}; "
                f"system prompt no longer leaks the token, so this proves the skill was NOT invoked. "
                f"got={content!r}"
            )
        if not any(
            ev in ("tool_start", "tool_complete") for ev in skill_events
        ):
            pytest.fail(
                "skill loop: no tool_start/tool_complete event observed on SSE stream; "
                "the model likely answered without actually invoking e2e-runbook-skill. "
                f"events={skill_events}"
            )
        print(
            f"skill loop ok: pulse token {_E2E_SKILL_PULSE_TOKEN!r} returned via real skill invocation (events={skill_events})"
        )
    finally:
        _cleanup()
