"""HiAgent SDK CLI - Main entry point with Click."""

import sys
from pathlib import Path
from typing import Optional

import click

def _ensure_local_hiagent_api_on_path() -> None:
    candidates = []
    try:
        candidates.append(Path(__file__).resolve().parents[3] / "libs" / "api")
    except Exception:
        pass
    candidates.append(Path.cwd() / "libs" / "api")

    for p in candidates:
        if (p / "hiagent_api").is_dir():
            sys.path.insert(0, str(p))
            return


_ensure_local_hiagent_api_on_path()

from cli_anything.hiagent_sdk.core.project import Project
from cli_anything.hiagent_sdk.core.services import ServiceManager
from cli_anything.hiagent_sdk.core.export import Exporter


class CLIContext:
    """CLI context object passed between commands."""

    def __init__(self, json_mode: bool = False, project_root: Optional[Path] = None):
        """Initialize CLI context."""
        self.json_mode = json_mode
        self.project_root = project_root or Path.cwd()
        self.project = Project(self.project_root)
        self.exporter = Exporter(json_mode=json_mode)
        self._service_manager: Optional[ServiceManager] = None

    @property
    def service_manager(self) -> ServiceManager:
        """Get service manager with effective configuration."""
        if self._service_manager is None:
            config = self.project.get_effective_config()
            self._service_manager = ServiceManager(config)
        return self._service_manager


@click.group(invoke_without_command=True)
@click.option("--json", is_flag=True, help="Output in JSON format")
@click.option("--version", is_flag=True, help="Show version")
@click.pass_context
def cli(ctx: click.Context, json: bool, version: bool):
    """HiAgent SDK CLI - Observe service commands."""
    if version:
        click.echo("hiagent-sdk-cli 0.1.0")
        sys.exit(0)

    # Initialize context
    ctx.ensure_object(dict)
    ctx.obj = CLIContext(json_mode=json)


@cli.group()
@click.pass_context
def observe(ctx: click.Context):
    """Observe service commands (API Token, Trace Spans)."""
    pass


@observe.group()
@click.pass_context
def token(ctx: click.Context):
    """API Token management commands."""
    pass


@token.command("create")
@click.option("--workspace-id", required=True, help="Workspace ID")
@click.option("--custom-app-id", required=True, help="Custom App ID")
@click.pass_obj
def observe_token_create(
    ctx: CLIContext,
    workspace_id: str,
    custom_app_id: str,
):
    """Create an API Token for observe service."""
    try:
        from cli_anything.hiagent_sdk.utils.hiagent_backend import ensure_volc_credentials
        from hiagent_api.observe_types import CreateApiTokenRequest

        ensure_volc_credentials()
        req = CreateApiTokenRequest(
            WorkspaceID=workspace_id,
            CustomAppID=custom_app_id,
        )

        resp = ctx.service_manager.get_observe_service().CreateApiToken(req)

        ctx.exporter.print_result(
            resp.model_dump(),
            True,
            f"API Token created (expires in {resp.ExpiresIn}s)",
        )

    except Exception as e:
        ctx.exporter.print_result(None, False, f"Error: {str(e)}")
        sys.exit(1)


@observe.group()
@click.pass_context
def trace(ctx: click.Context):
    """Trace span management commands."""
    pass


@trace.command("list")
@click.option("--workspace-id", required=True, help="Workspace ID")
@click.option("--page-size", type=int, default=10, help="Page size")
@click.option("--last-id", default="", help="Last ID for pagination")
@click.option(
    "--sort-by",
    type=click.Choice(["StartTime", "Latency", "LatencyFirstResp", "TotalTokens"]),
    default="StartTime",
    help="Sort by field",
)
@click.option(
    "--sort-order",
    type=click.Choice(["Asc", "Desc"]),
    default="Desc",
    help="Sort order",
)
@click.pass_obj
def observe_trace_list(
    ctx: CLIContext,
    workspace_id: str,
    page_size: int,
    last_id: str,
    sort_by: str,
    sort_order: str,
):
    """List trace spans."""
    try:
        from cli_anything.hiagent_sdk.utils.hiagent_backend import ensure_volc_credentials
        from hiagent_api.observe_types import (
            ListTraceSpansRequest,
            ListTraceSpansRequestSort,
            ListTraceSpansRequestSortBy,
            SortOrderType,
        )

        ensure_volc_credentials()
        req = ListTraceSpansRequest(
            WorkspaceID=workspace_id,
            PageSize=page_size,
            LastID=last_id,
            Sort=[
                ListTraceSpansRequestSort(
                    SortBy=ListTraceSpansRequestSortBy(sort_by),
                    SortOrder=SortOrderType(sort_order),
                )
            ],
        )

        resp = ctx.service_manager.get_observe_service().ListTraceSpans(req)

        items = [item.model_dump() for item in resp.Items]
        result = {
            "total": resp.Total,
            "has_more": resp.HasMore,
            "items": items,
        }

        ctx.exporter.print_result(
            result,
            True,
            f"Found {len(items)} trace spans (total: {resp.Total})",
        )

    except Exception as e:
        ctx.exporter.print_result(None, False, f"Error: {str(e)}")
        sys.exit(1)


def _make_human_on_event():
    """Stream printer for human mode.

    Writes reasoning/content deltas to stdout incrementally. Server-side payload
    fields are `reasoning_content` (for `reasoning` events) and `content`
    (for `content` events). A section header (🤔 Reasoning / ✨ Content) is
    printed once per section transition to avoid per-delta prefix noise.
    """
    import sys

    state = {"section": None}

    def on_event(name, payload):
        if name not in ("reasoning", "content"):
            return  # done / error 由主流程处理
        if not isinstance(payload, dict):
            return
        field = "reasoning_content" if name == "reasoning" else "content"
        text = payload.get(field, "")
        if not text:
            return
        if state["section"] != name:
            header = "\n🤔 Reasoning:\n" if name == "reasoning" else "\n✨ Content:\n"
            sys.stdout.write(header)
            state["section"] = name
        sys.stdout.write(text)
        sys.stdout.flush()

    return on_event


@observe.command("trace-ai-process")
@click.option("--workspace-id", required=True, help="Workspace ID")
@click.option("--trace-id", "trace_ids", required=True, multiple=True,
              help="Trace ID (repeatable)")
@click.option("--tenant-id", default=None, help="Optional Tenant ID")
@click.pass_obj
def observe_trace_ai_process(
    ctx: CLIContext,
    workspace_id: str,
    trace_ids: tuple,
    tenant_id,
):
    """Run AI analysis over one or more trace IDs."""
    try:
        from cli_anything.hiagent_sdk.utils.hiagent_backend import ensure_volc_credentials

        ensure_volc_credentials()
        params = {
            "WorkspaceID": workspace_id,
            "TraceIDs": list(trace_ids),
            "IsStream": True,
        }
        if tenant_id:
            params["TenantID"] = tenant_id

        on_event = None if ctx.json_mode else _make_human_on_event()
        resp = ctx.service_manager.get_observe_service().TraceAIProcess(
            params, on_event=on_event
        )

        latency = (resp or {}).get("latency")
        trace_id = (resp or {}).get("trace_id")
        ctx.exporter.print_result(
            resp,
            True,
            f"TraceAIProcess completed (latency={latency}ms, trace_id={trace_id})",
        )
    except Exception as e:
        ctx.exporter.print_result(None, False, f"Error: {str(e)}")
        sys.exit(1)


@observe.command("trace-ai-history")
@click.option("--workspace-id", required=True, help="Workspace ID")
@click.option("--trace-id", required=True, help="Trace ID")
@click.option("--page-size", type=int, default=10, help="Page size")
@click.pass_obj
def observe_trace_ai_history(
    ctx: CLIContext,
    workspace_id: str,
    trace_id: str,
    page_size: int,
):
    """List historical AI analyses for a trace."""
    try:
        from cli_anything.hiagent_sdk.utils.hiagent_backend import ensure_volc_credentials

        ensure_volc_credentials()
        params = {
            "WorkspaceID": workspace_id,
            "TraceID": trace_id,
            "PageSize": page_size,
        }
        resp = ctx.service_manager.get_observe_service().GetTraceAIProcessHistory(params)
        items = [item.model_dump() for item in (resp.Items or [])]
        ctx.exporter.print_result(
            {"items": items},
            True,
            f"Found {len(items)} AI history records",
        )
    except Exception as e:
        ctx.exporter.print_result(None, False, f"Error: {str(e)}")
        sys.exit(1)


@observe.command("alert-ai-process")
@click.option("--workspace-id", required=True, help="Workspace ID")
@click.option("--rule-id", required=True, help="Alert Rule ID")
@click.option("--tenant-id", default=None, help="Optional Tenant ID")
@click.pass_obj
def observe_alert_ai_process(
    ctx: CLIContext,
    workspace_id: str,
    rule_id: str,
    tenant_id,
):
    """Run AI analysis over an alert rule."""
    try:
        from cli_anything.hiagent_sdk.utils.hiagent_backend import ensure_volc_credentials

        ensure_volc_credentials()
        params = {
            "WorkspaceID": workspace_id,
            "RuleID": rule_id,
            "IsStream": True,
        }
        if tenant_id:
            params["TenantID"] = tenant_id

        on_event = None if ctx.json_mode else _make_human_on_event()
        resp = ctx.service_manager.get_observe_service().AlertAIProcess(
            params, on_event=on_event
        )

        latency = (resp or {}).get("latency")
        trace_id = (resp or {}).get("trace_id")
        ctx.exporter.print_result(
            resp,
            True,
            f"AlertAIProcess completed (latency={latency}ms, trace_id={trace_id})",
        )
    except Exception as e:
        ctx.exporter.print_result(None, False, f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
