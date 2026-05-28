"""End-to-end tests for HiAgent CLI using subprocess."""

import json
import os
import shutil
import subprocess
import sys
import tempfile


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
        assert "observe" in result.stdout

    def test_version(self):
        result = self._run(["--version"])
        assert result.returncode == 0
        assert "hiagent-sdk-cli" in result.stdout

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
