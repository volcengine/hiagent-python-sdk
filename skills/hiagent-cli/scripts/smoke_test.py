import argparse
import json
import os
import shutil
import subprocess
import sys
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
    if "observe" not in p_help.stdout:
        raise RuntimeError(f"unexpected help output (missing observe):\n{p_help.stdout}")

    no_cred_env = {"VOLC_ACCESSKEY": "", "VOLC_SECRETKEY": "", "HOME": str(repo_root / "_no_home_for_smoke")}

    p_token = _run(
        base_cmd,
        cwd,
        ["--json", "observe", "token", "create", "--workspace-id", "ws-test", "--custom-app-id", "app-test"],
        env=no_cred_env,
    )
    if p_token.returncode == 0:
        raise RuntimeError(f"observe token create unexpectedly succeeded without credentials:\n{p_token.stdout}")
    try:
        data = json.loads(p_token.stdout)
    except Exception as e:
        raise RuntimeError(f"observe token create json parse failed: {e}\nraw:\n{p_token.stdout}") from e
    if data.get("success") is not False or "Volcengine credentials not found" not in (data.get("message") or ""):
        raise RuntimeError(f"observe token create unexpected payload: {data}")

    p_trace = _run(
        base_cmd,
        cwd,
        ["--json", "observe", "trace", "list", "--workspace-id", "ws-test"],
        env=no_cred_env,
    )
    if p_trace.returncode == 0:
        raise RuntimeError(f"observe trace list unexpectedly succeeded without credentials:\n{p_trace.stdout}")
    try:
        data = json.loads(p_trace.stdout)
    except Exception as e:
        raise RuntimeError(f"observe trace list json parse failed: {e}\nraw:\n{p_trace.stdout}") from e
    if data.get("success") is not False or "Volcengine credentials not found" not in (data.get("message") or ""):
        raise RuntimeError(f"observe trace list unexpected payload: {data}")

    for sub_args in [
        [
            "--json", "observe", "trace-ai-process",
            "--workspace-id", "ws-test", "--trace-id", "t-1",
        ],
        [
            "--json", "observe", "trace-ai-history",
            "--workspace-id", "ws-test", "--trace-id", "t-1",
        ],
        [
            "--json", "observe", "alert-ai-process",
            "--workspace-id", "ws-test", "--rule-id", "r-1",
        ],
    ]:
        p = _run(base_cmd, cwd, sub_args, env=no_cred_env)
        if p.returncode == 0:
            raise RuntimeError(
                f"{sub_args} unexpectedly succeeded without credentials:\n{p.stdout}"
            )
        try:
            data = json.loads(p.stdout)
        except Exception as e:
            raise RuntimeError(
                f"{sub_args} json parse failed: {e}\nraw:\n{p.stdout}"
            ) from e
        if data.get("success") is not False or "Volcengine credentials not found" not in (data.get("message") or ""):
            raise RuntimeError(
                f"{sub_args} unexpected payload: {data}"
            )

    sys.stdout.write("OK\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
