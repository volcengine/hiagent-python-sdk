"""CLI tests for observe AI commands using Click's CliRunner."""
import json
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from cli_anything.hiagent_sdk.hiagent_cli import cli


@pytest.fixture
def fake_ai_payload():
    return {
        "content": "AI report",
        "reasoning_content": "thinking...",
        "usage": {"InputTokens": 1, "OutputTokens": 2, "TotalTokens": 3},
        "latency": 1234,
        "trace_id": "tid-1",
    }


def _patch_observe(svc_mock):
    """Patch ServiceManager.get_observe_service to return svc_mock."""
    return patch(
        "cli_anything.hiagent_sdk.core.services.ServiceManager.get_observe_service",
        return_value=svc_mock,
    )


def test_trace_ai_process_json_mode_outputs_single_json(fake_ai_payload):
    svc = MagicMock()
    svc.TraceAIProcess.return_value = fake_ai_payload
    runner = CliRunner()
    with patch(
        "cli_anything.hiagent_sdk.utils.hiagent_backend.ensure_volc_credentials",
        return_value=None,
    ), _patch_observe(svc):
        result = runner.invoke(
            cli,
            [
                "--json",
                "observe", "trace-ai-process",
                "--workspace-id", "ws-1",
                "--trace-id", "t-1",
            ],
        )

    assert result.exit_code == 0, result.output
    parsed = json.loads(result.output)  # 必须是单一 JSON 块
    assert parsed["success"] is True
    assert parsed["data"]["content"] == "AI report"
    # IsStream 默认 True
    args, kwargs = svc.TraceAIProcess.call_args
    assert args[0]["IsStream"] is True
    assert args[0]["TraceIDs"] == ["t-1"]


def test_trace_ai_process_rejects_no_stream_option():
    svc = MagicMock()
    svc.TraceAIProcess.return_value = {"content": "unexpected"}
    runner = CliRunner()
    with patch(
        "cli_anything.hiagent_sdk.utils.hiagent_backend.ensure_volc_credentials",
        return_value=None,
    ), _patch_observe(svc):
        result = runner.invoke(
            cli,
            [
                "--json",
                "observe", "trace-ai-process",
                "--workspace-id", "ws-1",
                "--trace-id", "t-1",
                "--no-stream",
            ],
        )

    assert result.exit_code != 0
    assert "No such option: --no-stream" in result.output


def test_trace_ai_process_human_mode_streams_to_stdout(fake_ai_payload):
    svc = MagicMock()

    def fake_call(params, on_event=None):
        if on_event is not None:
            on_event("reasoning", {"reasoning_content": "step1"})
            on_event("content", {"content": "answer"})
            on_event("done", fake_ai_payload)
        return fake_ai_payload

    svc.TraceAIProcess.side_effect = fake_call
    runner = CliRunner()
    with patch(
        "cli_anything.hiagent_sdk.utils.hiagent_backend.ensure_volc_credentials",
        return_value=None,
    ), _patch_observe(svc):
        result = runner.invoke(
            cli,
            [
                "observe", "trace-ai-process",
                "--workspace-id", "ws-1",
                "--trace-id", "t-1",
            ],
        )
    assert result.exit_code == 0, result.output
    assert "Reasoning" in result.output
    assert "Content" in result.output
    assert "step1" in result.output
    assert "answer" in result.output
    assert "TraceAIProcess completed" in result.output


def test_trace_ai_process_multiple_trace_ids(fake_ai_payload):
    svc = MagicMock()
    svc.TraceAIProcess.return_value = fake_ai_payload
    runner = CliRunner()
    with patch(
        "cli_anything.hiagent_sdk.utils.hiagent_backend.ensure_volc_credentials",
        return_value=None,
    ), _patch_observe(svc):
        result = runner.invoke(
            cli,
            [
                "--json",
                "observe", "trace-ai-process",
                "--workspace-id", "ws-1",
                "--trace-id", "a",
                "--trace-id", "b",
            ],
        )
    assert result.exit_code == 0, result.output
    args, _ = svc.TraceAIProcess.call_args
    assert args[0]["TraceIDs"] == ["a", "b"]


def test_trace_ai_history_basic():
    svc = MagicMock()
    fake_item = MagicMock()
    fake_item.model_dump.return_value = {"DocID": "d1"}
    fake_resp = MagicMock(Items=[fake_item])
    svc.GetTraceAIProcessHistory.return_value = fake_resp
    runner = CliRunner()
    with patch(
        "cli_anything.hiagent_sdk.utils.hiagent_backend.ensure_volc_credentials",
        return_value=None,
    ), _patch_observe(svc):
        result = runner.invoke(
            cli,
            [
                "--json",
                "observe", "trace-ai-history",
                "--workspace-id", "ws-1",
                "--trace-id", "t-1",
                "--page-size", "5",
            ],
        )
    assert result.exit_code == 0, result.output
    parsed = json.loads(result.output)
    assert parsed["success"] is True
    assert parsed["data"]["items"] == [{"DocID": "d1"}]
    args, _ = svc.GetTraceAIProcessHistory.call_args
    assert args[0]["TraceID"] == "t-1"
    assert args[0]["PageSize"] == 5


def test_alert_ai_process_json_mode_default_stream(fake_ai_payload):
    svc = MagicMock()
    svc.AlertAIProcess.return_value = fake_ai_payload
    runner = CliRunner()
    with patch(
        "cli_anything.hiagent_sdk.utils.hiagent_backend.ensure_volc_credentials",
        return_value=None,
    ), _patch_observe(svc):
        result = runner.invoke(
            cli,
            [
                "--json",
                "observe", "alert-ai-process",
                "--workspace-id", "ws-1",
                "--rule-id", "r-1",
            ],
        )
    assert result.exit_code == 0, result.output
    parsed = json.loads(result.output)
    assert parsed["success"] is True
    assert parsed["data"]["content"] == "AI report"
    args, _ = svc.AlertAIProcess.call_args
    assert args[0]["RuleID"] == "r-1"
    assert args[0]["IsStream"] is True


def test_alert_ai_process_rejects_no_stream_option():
    svc = MagicMock()
    svc.AlertAIProcess.return_value = {"content": "unexpected"}
    runner = CliRunner()
    with patch(
        "cli_anything.hiagent_sdk.utils.hiagent_backend.ensure_volc_credentials",
        return_value=None,
    ), _patch_observe(svc):
        result = runner.invoke(
            cli,
            [
                "--json",
                "observe", "alert-ai-process",
                "--workspace-id", "ws-1",
                "--rule-id", "r-1",
                "--no-stream",
            ],
        )

    assert result.exit_code != 0
    assert "No such option: --no-stream" in result.output


def test_alert_ai_process_human_mode_streams(fake_ai_payload):
    svc = MagicMock()

    def fake_call(params, on_event=None):
        if on_event is not None:
            on_event("content", {"content": "alert!"})
            on_event("done", fake_ai_payload)
        return fake_ai_payload

    svc.AlertAIProcess.side_effect = fake_call
    runner = CliRunner()
    with patch(
        "cli_anything.hiagent_sdk.utils.hiagent_backend.ensure_volc_credentials",
        return_value=None,
    ), _patch_observe(svc):
        result = runner.invoke(
            cli,
            [
                "observe", "alert-ai-process",
                "--workspace-id", "ws-1",
                "--rule-id", "r-1",
            ],
        )
    assert result.exit_code == 0, result.output
    assert "alert!" in result.output
    assert "AlertAIProcess completed" in result.output


def test_human_on_event_uses_reasoning_content_and_content_fields(fake_ai_payload):
    """Regression: server-side payload uses `reasoning_content` and `content`,
    NOT `text`. The human-mode streamer must read the correct fields and
    print a section header per transition (not per delta)."""
    svc = MagicMock()

    def fake_call(params, on_event=None):
        if on_event is not None:
            # Multiple deltas in the same section must NOT repeat the header.
            on_event("reasoning", {"reasoning_content": "delta-r1 "})
            on_event("reasoning", {"reasoning_content": "delta-r2"})
            on_event("content", {"content": "delta-c1 "})
            on_event("content", {"content": "delta-c2"})
            # Wrong-field events must be silently ignored (defensive).
            on_event("reasoning", {"text": "ignored"})
            on_event("done", fake_ai_payload)
        return fake_ai_payload

    svc.TraceAIProcess.side_effect = fake_call
    runner = CliRunner()
    with patch(
        "cli_anything.hiagent_sdk.utils.hiagent_backend.ensure_volc_credentials",
        return_value=None,
    ), _patch_observe(svc):
        result = runner.invoke(
            cli,
            [
                "observe", "trace-ai-process",
                "--workspace-id", "ws-1",
                "--trace-id", "t-1",
            ],
        )
    assert result.exit_code == 0, result.output
    out = result.output
    # Headers appear exactly once per section
    assert out.count("🤔 Reasoning:") == 1
    assert out.count("✨ Content:") == 1
    # Deltas are concatenated under each section
    assert "delta-r1 delta-r2" in out
    assert "delta-c1 delta-c2" in out
    # Unknown payload field never leaks
    assert "ignored" not in out
