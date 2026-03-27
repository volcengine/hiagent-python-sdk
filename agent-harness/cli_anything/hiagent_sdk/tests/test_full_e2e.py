"""End-to-end tests for HiAgent CLI using subprocess."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


def _resolve_cli(name: str) -> list[str]:
    force = os.environ.get("CLI_ANYTHING_FORCE_INSTALLED", "").strip() == "1"
    path = shutil.which(name)
    if path:
        print(f"[_resolve_cli] Using installed command: {path}")
        return [path]
    if force:
        raise RuntimeError(f"{name} not found in PATH. Install with: pip install -e .")
    if name == "cli-anything-hiagent":
        print(f"[_resolve_cli] Falling back to: {sys.executable} -m cli_anything.hiagent_sdk")
        return [sys.executable, "-m", "cli_anything.hiagent_sdk"]
    module = name.replace("cli-anything-", "cli_anything.") + "." + name.split("-")[-1] + "_cli"
    print(f"[_resolve_cli] Falling back to: {sys.executable} -m {module}")
    return [sys.executable, "-m", module]


class TestCLISubprocess:
    CLI_BASE = _resolve_cli("cli-anything-hiagent")

    def _run(self, args: list[str], check: bool = False, env: dict | None = None):
        return subprocess.run(
            self.CLI_BASE + args,
            capture_output=True,
            text=True,
            check=check,
            env={**os.environ, **(env or {})},
        )

    def test_help(self):
        result = self._run(["--help"])
        assert result.returncode == 0
        assert "HiAgent SDK CLI" in result.stdout

    def test_version(self):
        result = self._run(["--version"])
        assert result.returncode == 0
        assert "hiagent-sdk-cli" in result.stdout

    def test_config_set_and_show_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            result1 = self._run(
                [
                    "--json",
                    "--project",
                    str(project),
                    "config",
                    "set",
                    "--app-key",
                    "test-app-key",
                    "--workspace-id",
                    "ws-test",
                ]
            )
            assert result1.returncode == 0, result1.stderr
            data1 = json.loads(result1.stdout)
            assert data1["success"] is True

            result2 = self._run(["--json", "--project", str(project), "config", "show"])
            assert result2.returncode == 0, result2.stderr
            data2 = json.loads(result2.stdout)
            assert data2["success"] is True
            assert "effective" in data2["data"]
            assert "project" in data2["data"]
            assert data2["data"]["project"]["app_key"] == "test-app-key"

    def test_session_lifecycle_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            name = "test-session"

            result1 = self._run(
                [
                    "--json",
                    "--project",
                    str(project),
                    "session",
                    "create",
                    name,
                    "--conversation-id",
                    "conv-test-123",
                ]
            )
            assert result1.returncode == 0, result1.stderr
            data1 = json.loads(result1.stdout)
            assert data1["success"] is True

            result2 = self._run(["--json", "--project", str(project), "session", "list"])
            assert result2.returncode == 0, result2.stderr
            data2 = json.loads(result2.stdout)
            assert name in data2["data"]

            result3 = self._run(["--json", "--project", str(project), "session", "show", name])
            assert result3.returncode == 0, result3.stderr
            data3 = json.loads(result3.stdout)
            assert data3["data"]["name"] == name

            result4 = self._run(["--json", "--project", str(project), "session", "delete", name])
            assert result4.returncode == 0, result4.stderr
            data4 = json.loads(result4.stdout)
            assert data4["success"] is True

            result5 = self._run(["--json", "--project", str(project), "session", "show", name])
            assert result5.returncode != 0

    def test_observe_token_create_requires_credentials(self):
        with tempfile.TemporaryDirectory() as tmp_home:
            result = self._run(
                [
                    "--json",
                    "observe",
                    "token",
                    "create",
                    "--workspace-id",
                    "ws-test",
                    "--custom-app-id",
                    "app-test",
                ],
                env={"HOME": tmp_home, "VOLC_ACCESSKEY": "", "VOLC_SECRETKEY": ""},
            )
            assert result.returncode != 0
            data = json.loads(result.stdout)
            assert data["success"] is False
            assert "Volcengine credentials not found" in (data.get("message") or "")

    def test_observe_trace_list_requires_credentials(self):
        with tempfile.TemporaryDirectory() as tmp_home:
            result = self._run(
                [
                    "--json",
                    "observe",
                    "trace",
                    "list",
                    "--workspace-id",
                    "ws-test",
                ],
                env={"HOME": tmp_home, "VOLC_ACCESSKEY": "", "VOLC_SECRETKEY": ""},
            )
            assert result.returncode != 0
            data = json.loads(result.stdout)
            assert data["success"] is False
            assert "Volcengine credentials not found" in (data.get("message") or "")


@pytest.mark.e2e
class TestRealApiE2E:
    CLI_BASE = _resolve_cli("cli-anything-hiagent")

    def _run(self, args: list[str], check: bool = False):
        return subprocess.run(
            self.CLI_BASE + args,
            capture_output=True,
            text=True,
            check=check,
            env=os.environ.copy(),
        )

    def test_file_upload_download(self):
        if os.environ.get("CLI_ANYTHING_E2E_REAL_API", "").strip() != "1":
            pytest.skip("Set CLI_ANYTHING_E2E_REAL_API=1 to enable real API E2E tests")

        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            test_file = project / "test.txt"
            test_file.write_text("Hello, HiAgent!", encoding="utf-8")

            result1 = self._run(
                ["--json", "--project", str(project), "file", "upload", "--file", str(test_file)]
            )
            assert result1.returncode == 0, result1.stderr
            data1 = json.loads(result1.stdout)
            assert data1["success"] is True
            remote_path = data1["data"]["path"]

            out_file = project / "downloaded.txt"
            result2 = self._run(
                [
                    "--json",
                    "--project",
                    str(project),
                    "file",
                    "download",
                    "--path",
                    remote_path,
                    "--output",
                    str(out_file),
                ]
            )
            assert result2.returncode == 0, result2.stderr
            assert out_file.exists()
            assert out_file.read_text(encoding="utf-8") == "Hello, HiAgent!"
