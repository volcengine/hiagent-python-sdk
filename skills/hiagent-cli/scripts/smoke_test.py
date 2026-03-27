import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def _resolve_cmd(repo_root: Path) -> tuple[list[str], Path]:
    installed = shutil.which("cli-anything-hiagent")
    if installed:
        return ["cli-anything-hiagent"], repo_root

    agent_harness = repo_root / "agent-harness"
    if not agent_harness.is_dir():
        raise RuntimeError(f"agent-harness not found under repo root: {agent_harness}")
    return [sys.executable, "-m", "cli_anything.hiagent_sdk"], agent_harness


def _run(
    base_cmd: list[str],
    cwd: Path,
    args: list[str],
    *,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    merged_env = dict(os.environ)
    if env:
        merged_env.update(env)
    return subprocess.run(
        [*base_cmd, *args],
        cwd=str(cwd),
        env=merged_env,
        text=True,
        capture_output=True,
        check=False,
    )


def _run_json(
    base_cmd: list[str],
    cwd: Path,
    project_root: Path,
    args: list[str],
) -> dict:
    p = _run(
        base_cmd,
        cwd,
        ["--json", "--project", str(project_root), *args],
    )
    if p.returncode != 0:
        raise RuntimeError(
            f"command failed ({p.returncode}): {' '.join([*base_cmd, *args])}\nstdout:\n{p.stdout}\nstderr:\n{p.stderr}"
        )
    try:
        return json.loads(p.stdout)
    except Exception as e:
        raise RuntimeError(f"json parse failed: {e}\nraw:\n{p.stdout}") from e


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--repo-root",
        default=str(Path(__file__).resolve().parents[3]),
        help="Repository root path (default: auto-detected)",
    )
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    base_cmd, cwd = _resolve_cmd(repo_root)

    p_version = _run(base_cmd, cwd, ["--version"])
    if p_version.returncode != 0:
        raise RuntimeError(f"--version failed\nstdout:\n{p_version.stdout}\nstderr:\n{p_version.stderr}")
    if "hiagent-sdk-cli" not in p_version.stdout:
        raise RuntimeError(f"unexpected version output:\n{p_version.stdout}")

    p_help = _run(base_cmd, cwd, ["--help"])
    if p_help.returncode != 0:
        raise RuntimeError(f"--help failed\nstdout:\n{p_help.stdout}\nstderr:\n{p_help.stderr}")
    if "config" not in p_help.stdout or "session" not in p_help.stdout:
        raise RuntimeError(f"unexpected help output:\n{p_help.stdout}")

    with tempfile.TemporaryDirectory(prefix="hiagent-cli-skill-") as td:
        project_root = Path(td)

        app_key = "test-app-key"
        workspace_id = "test-workspace-id"

        _run_json(
            base_cmd,
            cwd,
            project_root,
            ["config", "set", "--app-key", app_key, "--workspace-id", workspace_id],
        )

        cfg_path = project_root / ".hiagent" / "config.json"
        if not cfg_path.is_file():
            raise RuntimeError(f"expected config file not found: {cfg_path}")
        cfg = json.loads(cfg_path.read_text())
        if cfg.get("app_key") != app_key or cfg.get("workspace_id") != workspace_id:
            raise RuntimeError(f"unexpected config file content: {cfg}")

        show = _run_json(base_cmd, cwd, project_root, ["config", "show"])
        if not show.get("success"):
            raise RuntimeError(f"config show not success: {show}")
        if not isinstance(show.get("data"), dict):
            raise RuntimeError(f"config show missing data: {show}")
        if "effective" not in show["data"] or "project" not in show["data"]:
            raise RuntimeError(f"config show missing effective/project: {show}")

        name = "smoke-session"
        create = _run_json(
            base_cmd,
            cwd,
            project_root,
            ["session", "create", name, "--conversation-id", "conv-123", "--tool-id", "tool-456"],
        )
        if not create.get("success"):
            raise RuntimeError(f"session create not success: {create}")

        listed = _run_json(base_cmd, cwd, project_root, ["session", "list"])
        if not listed.get("success"):
            raise RuntimeError(f"session list not success: {listed}")
        sessions = listed.get("data")
        if not isinstance(sessions, list) or name not in sessions:
            raise RuntimeError(f"session list missing {name}: {listed}")

        shown = _run_json(base_cmd, cwd, project_root, ["session", "show", name])
        if not shown.get("success") or not isinstance(shown.get("data"), dict):
            raise RuntimeError(f"session show unexpected: {shown}")

        deleted = _run_json(base_cmd, cwd, project_root, ["session", "delete", name])
        if not deleted.get("success"):
            raise RuntimeError(f"session delete not success: {deleted}")

        after = _run_json(base_cmd, cwd, project_root, ["session", "list"])
        if name in (after.get("data") or []):
            raise RuntimeError(f"session still present after delete: {after}")

    sys.stdout.write("OK\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
