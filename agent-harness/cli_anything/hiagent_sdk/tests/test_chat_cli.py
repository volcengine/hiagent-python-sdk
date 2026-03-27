"""Unit tests for chat CLI commands."""

import json

from click.testing import CliRunner

from cli_anything.hiagent_sdk.core.services import ServiceManager
from cli_anything.hiagent_sdk.hiagent_cli import cli


class _Event:
    def __init__(self, i: int):
        self.i = i

    def model_dump(self):
        return {"i": self.i}


class _Resp:
    def model_dump(self):
        return {"ok": True}


class _ChatSvc:
    def __init__(self):
        self.blocking_called = False
        self.streaming_called = False
        self.last_app_key = None
        self.last_chat = None

    def chat_blocking(self, app_key, chat):
        self.blocking_called = True
        self.last_app_key = app_key
        self.last_chat = chat
        return _Resp()

    def chat_streaming(self, app_key, chat):
        self.streaming_called = True
        self.last_app_key = app_key
        self.last_chat = chat
        yield _Event(1)
        yield _Event(2)


def test_chat_send_blocking_json(monkeypatch):
    svc = _ChatSvc()
    monkeypatch.setattr(ServiceManager, "get_chat_service", lambda self: svc)

    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "--json",
                "--project",
                ".",
                "chat",
                "send",
                "--app-key",
                "ak",
                "--conversation-id",
                "cid",
                "-q",
                "Hello",
                "--user-id",
                "uid",
            ],
        )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["success"] is True
    assert data["message"] == "Message sent"
    assert svc.blocking_called is True
    assert svc.streaming_called is False
    assert svc.last_app_key == "ak"


def test_chat_send_streaming_json(monkeypatch):
    svc = _ChatSvc()
    monkeypatch.setattr(ServiceManager, "get_chat_service", lambda self: svc)

    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "--json",
                "--project",
                ".",
                "chat",
                "send",
                "--app-key",
                "ak",
                "--conversation-id",
                "cid",
                "-q",
                "Hello",
                "--user-id",
                "uid",
                "--stream",
            ],
        )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["success"] is True
    assert data["message"] == "Sent message (streamed 2 events)"
    assert data["data"] == [{"i": 1}, {"i": 2}]
    assert svc.streaming_called is True
    assert svc.blocking_called is False
    assert svc.last_app_key == "ak"

