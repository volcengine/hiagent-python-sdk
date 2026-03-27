"""REPL (Read-Eval-Print Loop) for HiAgent SDK CLI."""

import shlex

import click

from cli_anything.hiagent_sdk.utils.repl_skin import ReplSkin


_COMMANDS = {
    "config show": "Show effective and project config",
    "config set": "Update project config values",
    "session create <name>": "Create a new session",
    "session list": "List sessions",
    "session show <name>": "Show session details",
    "session delete <name>": "Delete a session",
    "chat create": "Create a conversation",
    "chat send": "Send a message",
    "tool execute": "Execute an archived tool",
    "workflow get": "Get workflow details",
    "workflow run": "Run a workflow",
    "workflow status": "Query workflow run status",
    "knowledge retrieve": "Retrieve knowledge from datasets",
    "file upload": "Upload a file via UP service",
    "file download": "Download a file via UP service",
    "observe token create": "Create an API token (observe service)",
    "observe trace list": "List trace spans (observe service)",
    "help": "Show this help",
    "quit / exit": "Exit the REPL",
}


def repl(ctx):
    from cli_anything.hiagent_sdk.hiagent_cli import cli as main_cli

    skin = ReplSkin("hiagent", version="0.1.0")
    if not ctx.json_mode:
        skin.print_banner()

    pt_session = None if ctx.json_mode else skin.create_prompt_session()
    project_name = getattr(getattr(ctx, "project_root", None), "name", "")

    while True:
        try:
            line = skin.get_input(pt_session, project_name=project_name, modified=False)
        except EOFError:
            break
        except KeyboardInterrupt:
            if not ctx.json_mode:
                skin.hint("Type quit to exit")
            continue

        if not line:
            continue

        cmd = line.strip()
        cmd_lower = cmd.lower()

        if cmd_lower in ("quit", "exit"):
            break

        if cmd_lower == "help":
            if ctx.json_mode:
                ctx.exporter.print_result(_COMMANDS, True, "Commands")
            else:
                skin.help(_COMMANDS)
            continue

        try:
            args = shlex.split(cmd)
            with main_cli.make_context(
                "cli-anything-hiagent",
                args,
                parent=click.Context(main_cli),
            ) as cmd_ctx:
                cmd_ctx.obj = ctx
                main_cli.invoke(cmd_ctx)
        except SystemExit:
            pass
        except click.ClickException as e:
            ctx.exporter.print_result(None, False, str(e))
        except Exception as e:
            ctx.exporter.print_result(None, False, f"Error: {str(e)}")

    if not ctx.json_mode:
        skin.print_goodbye()
