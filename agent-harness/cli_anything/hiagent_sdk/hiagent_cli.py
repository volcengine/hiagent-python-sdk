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
from cli_anything.hiagent_sdk.core.session import SessionManager
from cli_anything.hiagent_sdk.core.services import ServiceManager
from cli_anything.hiagent_sdk.core.export import Exporter
from cli_anything.hiagent_sdk.utils.repl import repl as run_repl


class CLIContext:
    """CLI context object passed between commands."""

    def __init__(self, json_mode: bool = False, project_root: Optional[Path] = None):
        """Initialize CLI context."""
        self.json_mode = json_mode
        self.project_root = project_root or Path.cwd()
        self.project = Project(self.project_root)
        self.session_manager = SessionManager(self.project_root / ".hiagent" / "sessions")
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
@click.option(
    "--project",
    "-p",
    type=click.Path(exists=True, path_type=Path, file_okay=False),
    help="Project root directory",
)
@click.option("--version", is_flag=True, help="Show version")
@click.pass_context
def cli(ctx: click.Context, json: bool, project: Optional[Path], version: bool):
    """HiAgent SDK CLI - Command line interface for HiAgent Python SDK."""
    if version:
        click.echo("hiagent-sdk-cli 0.1.0")
        sys.exit(0)

    # Initialize context
    ctx.ensure_object(dict)
    ctx.obj = CLIContext(json_mode=json, project_root=project)

    # If no command is invoked, enter REPL
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


@cli.command()
@click.pass_obj
def repl(ctx: CLIContext):
    """Start interactive REPL mode."""
    run_repl(ctx)


@cli.group()
@click.pass_context
def config(ctx: click.Context):
    """Manage project configuration."""
    pass


@config.command("show")
@click.pass_obj
def config_show(ctx: CLIContext):
    """Show current configuration."""
    effective_config = ctx.project.get_effective_config()
    project_config = ctx.project.config.model_dump()

    result = {
        "effective": effective_config,
        "project": project_config,
    }

    ctx.exporter.print_result(result, True, "Configuration loaded")


@config.command("set")
@click.option("--app-key", help="HiAgent App Key")
@click.option("--workspace-id", help="HiAgent Workspace ID")
@click.option("--endpoint", help="HiAgent API endpoint")
@click.option("--region", help="HiAgent region")
@click.option("--app-base-url", help="HiAgent App Base URL")
@click.option("--user-id", help="Default user ID")
@click.pass_obj
def config_set(ctx: CLIContext, **kwargs):
    """Set configuration values."""
    # Filter out None values
    updates = {k: v for k, v in kwargs.items() if v is not None}

    if not updates:
        ctx.exporter.print_result(None, False, "No configuration values provided")
        sys.exit(1)

    ctx.project.update_config(**updates)
    ctx.exporter.print_result(updates, True, "Configuration updated")


@cli.group()
@click.pass_context
def session(ctx: click.Context):
    """Manage sessions for conversation/workflow/tool context."""
    pass


@session.command("create")
@click.argument("name")
@click.option("--conversation-id", help="Conversation ID to use")
@click.option("--workflow-id", help="Workflow ID to use")
@click.option("--tool-id", help="Tool ID to use")
@click.option(
    "--dataset-ids",
    help="Knowledge dataset IDs (comma-separated)",
    callback=lambda ctx, param, value: value.split(",") if value else [],
)
@click.pass_obj
def session_create(
    ctx: CLIContext,
    name: str,
    conversation_id: Optional[str],
    workflow_id: Optional[str],
    tool_id: Optional[str],
    dataset_ids: list,
):
    """Create a new session."""
    try:
        session = ctx.session_manager.create_session(
            name=name,
            conversation_id=conversation_id,
            workflow_id=workflow_id,
            tool_id=tool_id,
            dataset_ids=dataset_ids,
        )
        ctx.exporter.print_result(
            session.model_dump(),
            True,
            f"Session '{name}' created",
        )
    except ValueError as e:
        ctx.exporter.print_result(None, False, str(e))
        sys.exit(1)


@session.command("list")
@click.pass_obj
def session_list(ctx: CLIContext):
    """List all sessions."""
    sessions = ctx.session_manager.list_sessions()
    ctx.exporter.print_result(sessions, True, f"Found {len(sessions)} sessions")


@session.command("show")
@click.argument("name")
@click.pass_obj
def session_show(ctx: CLIContext, name: str):
    """Show session details."""
    session = ctx.session_manager.get_session(name)
    if not session:
        ctx.exporter.print_result(None, False, f"Session '{name}' not found")
        sys.exit(1)

    ctx.exporter.print_result(session.model_dump(), True, f"Session '{name}'")


@session.command("delete")
@click.argument("name")
@click.pass_obj
def session_delete(ctx: CLIContext, name: str):
    """Delete a session."""
    success = ctx.session_manager.delete_session(name)
    if success:
        ctx.exporter.print_result(None, True, f"Session '{name}' deleted")
    else:
        ctx.exporter.print_result(None, False, f"Session '{name}' not found")
        sys.exit(1)


@cli.group()
@click.pass_context
def chat(ctx: click.Context):
    """Chat conversation commands."""
    pass


@chat.command("create")
@click.option("--app-key", required=True, help="App key")
@click.option("--user-id", help="User ID (defaults to config)")
@click.option(
    "--variable", "-v",
    multiple=True,
    help="Variables as key=value",
    callback=lambda ctx, param, values: dict(v.split("=", 1) for v in values),
)
@click.option("--app-base-url", help="App base URL")
@click.pass_obj
def chat_create(ctx: CLIContext, app_key: str, user_id: Optional[str], variable: dict, app_base_url: Optional[str]):
    """Create a new conversation."""
    try:
        from hiagent_api.chat_types import CreateConversationRequest

        user_id = user_id or ctx.project.config.user_id or "cli-user"

        req = CreateConversationRequest(
            app_key=app_key,
            inputs=variable or {},
            user_id=user_id,
        )

        resp = ctx.service_manager.get_chat_service().create_conversation(
            app_key=app_key, conversation=req
        )

        # Check if error
        if hasattr(resp, "ResponseMetadata"):
            ctx.exporter.print_result(
                resp.model_dump() if hasattr(resp, "model_dump") else str(resp),
                False,
                "Failed to create conversation",
            )
            sys.exit(1)

        ctx.exporter.print_result(
            resp.model_dump(),
            True,
            f"Conversation created: {resp.conversation.app_conversation_id}",
        )
    except Exception as e:
        ctx.exporter.print_result(None, False, f"Error: {str(e)}")
        sys.exit(1)


@chat.command("send")
@click.option("--app-key", required=True, help="App key")
@click.option("--conversation-id", required=True, help="Conversation ID")
@click.option("--query", "-q", required=True, help="Query/message to send")
@click.option("--user-id", help="User ID (defaults to config)")
@click.option("--stream", is_flag=True, help="Stream response")
@click.pass_obj
def chat_send(
    ctx: CLIContext,
    app_key: str,
    conversation_id: str,
    query: str,
    user_id: Optional[str],
    stream: bool,
):
    """Send a message to a conversation."""
    try:
        from hiagent_api.chat_types import ChatRequest

        user_id = user_id or ctx.project.config.user_id or "cli-user"

        req = ChatRequest(
            app_key=app_key,
            app_conversation_id=conversation_id,
            query=query,
            user_id=user_id,
            response_mode="streaming" if stream else "blocking",
        )

        if stream:
            # Handle streaming
            events = []
            for event in ctx.service_manager.get_chat_service().chat_streaming(
                app_key=app_key, chat=req
            ):
                events.append(event.model_dump() if hasattr(event, "model_dump") else str(event))

            ctx.exporter.print_result(
                events, True, f"Sent message (streamed {len(events)} events)"
            )
        else:
            # Non-streaming
            resp = ctx.service_manager.get_chat_service().chat_blocking(app_key=app_key, chat=req)
            ctx.exporter.print_result(
                resp.model_dump() if hasattr(resp, "model_dump") else resp,
                True,
                "Message sent",
            )

    except Exception as e:
        ctx.exporter.print_result(None, False, f"Error: {str(e)}")
        sys.exit(1)


@cli.group()
@click.pass_context
def tool(ctx: click.Context):
    """Tool execution commands."""
    pass


@tool.command("execute")
@click.option("--workspace-id", required=True, help="Workspace ID")
@click.option("--tool-id", required=True, help="Tool ID")
@click.option("--input", "input_data", help="Input JSON string or @file.json")
@click.option("--plugin-id", help="Plugin ID (fetched if not provided)")
@click.option("--name", help="Tool name (fetched if not provided)")
@click.pass_obj
def tool_execute(
    ctx: CLIContext,
    workspace_id: str,
    tool_id: str,
    input_data: Optional[str],
    plugin_id: Optional[str],
    name: Optional[str],
):
    """Execute a tool."""
    try:
        from hiagent_api.tool_types import ExecArchivedToolRequest
        import json

        # Parse input data
        input_dict = {}
        if input_data:
            if input_data.startswith("@"):
                # Read from file
                file_path = Path(input_data[1:])
                with open(file_path) as f:
                    input_dict = json.load(f)
            else:
                input_dict = json.loads(input_data)

        # Get tool details if needed
        if not plugin_id or not name:
            from hiagent_api.tool_types import GetArchivedToolRequest

            tool_resp = ctx.service_manager.get_tool_service().get_archived_tool(
                GetArchivedToolRequest(workspace_id=workspace_id, id=tool_id)
            )
            plugin_id = plugin_id or tool_resp.plugin_id
            name = name or tool_resp.name

        req = ExecArchivedToolRequest(
            workspace_id=workspace_id,
            plugin_id=plugin_id,
            tool_id=tool_id,
            config="",  # Use default config
            input_data=json.dumps(input_dict),
        )

        resp = ctx.service_manager.get_tool_service().exec_archived_tool(req)
        ctx.exporter.print_result(
            resp.model_dump(), True, f"Tool '{name}' executed"
        )

    except Exception as e:
        ctx.exporter.print_result(None, False, f"Error: {str(e)}")
        sys.exit(1)


@cli.group()
@click.pass_context
def workflow(ctx: click.Context):
    """Workflow execution commands."""
    pass


@workflow.command("get")
@click.option("--workspace-id", required=True, help="Workspace ID")
@click.option("--workflow-id", required=True, help="Workflow ID")
@click.pass_obj
def workflow_get(
    ctx: CLIContext,
    workspace_id: str,
    workflow_id: str,
):
    """Get workflow details."""
    try:
        from hiagent_api.workflow_types import GetWorkflowRequest

        req = GetWorkflowRequest(
            id=workflow_id,
            workspace_id=workspace_id,
        )

        resp = ctx.service_manager.get_workflow_service().get_workflow(req)

        # Check if error
        if hasattr(resp, "ResponseMetadata") and hasattr(resp.ResponseMetadata, "Error"):
            ctx.exporter.print_result(
                resp.model_dump() if hasattr(resp, "model_dump") else str(resp),
                False,
                "Failed to get workflow",
            )
            sys.exit(1)

        ctx.exporter.print_result(
            resp.model_dump() if hasattr(resp, "model_dump") else resp,
            True,
            f"Workflow retrieved: {workflow_id}",
        )

    except Exception as e:
        ctx.exporter.print_result(None, False, f"Error: {str(e)}")
        sys.exit(1)


@workflow.command("status")
@click.option("--app-key", required=True, help="App key")
@click.option("--run-id", required=True, help="Workflow run ID")
@click.option("--user-id", help="User ID (defaults to config)")
@click.pass_obj
def workflow_status(
    ctx: CLIContext,
    app_key: str,
    run_id: str,
    user_id: Optional[str],
):
    """Query workflow run status."""
    try:
        from hiagent_api.workflow_types import QueryWorkflowStatusRequest

        user_id = user_id or ctx.project.config.user_id or "cli-user"

        req = QueryWorkflowStatusRequest(
            app_key=app_key,
            run_id=run_id,
            user_id=user_id,
        )

        resp = ctx.service_manager.get_workflow_service().query_workflow_status(app_key, req)

        # Check if error
        if hasattr(resp, "ResponseMetadata") and hasattr(resp.ResponseMetadata, "Error"):
            ctx.exporter.print_result(
                resp.model_dump() if hasattr(resp, "model_dump") else str(resp),
                False,
                "Failed to query workflow status",
            )
            sys.exit(1)

        ctx.exporter.print_result(
            resp.model_dump() if hasattr(resp, "model_dump") else resp,
            True,
            f"Status for run: {run_id}",
        )

    except Exception as e:
        ctx.exporter.print_result(None, False, f"Error: {str(e)}")
        sys.exit(1)


@workflow.command("run")
@click.option("--app-key", required=True, help="App key")
@click.option("--workspace-id", required=True, help="Workspace ID")
@click.option("--workflow-id", required=True, help="Workflow ID")
@click.option("--user-id", help="User ID (defaults to config)")
@click.option("--async", "async_mode", is_flag=True, help="Run workflow asynchronously")
@click.option("--input", "input_data", help="Input JSON string or @file.json")
@click.option("--stream", is_flag=True, help="Stream workflow events")
@click.pass_obj
def workflow_run(
    ctx: CLIContext,
    app_key: str,
    workspace_id: str,
    workflow_id: str,
    user_id: Optional[str],
    async_mode: bool,
    input_data: Optional[str],
    stream: bool,
):
    """Run a workflow."""
    try:
        from hiagent_api.workflow_types import RunWorkflowRequest
        import json

        user_id = user_id or ctx.project.config.user_id or "cli-user"

        # Parse input data
        input_dict = {}
        if input_data:
            if input_data.startswith("@"):
                # Read from file
                file_path = Path(input_data[1:])
                with open(file_path) as f:
                    input_dict = json.load(f)
            else:
                input_dict = json.loads(input_data)

        req = RunWorkflowRequest(
            app_key=app_key,
            workspace_id=workspace_id,
            workflow_id=workflow_id,
            user_id=user_id,
            inputs=input_dict,
        )

        if stream:
            # Handle streaming
            events = []
            for event in ctx.service_manager.get_workflow_service().run_workflow(req):
                events.append(event.model_dump() if hasattr(event, "model_dump") else str(event))

            ctx.exporter.print_result(
                events, True, f"Workflow executed (streamed {len(events)} events)"
            )
        elif async_mode:
            # Async execution
            resp = ctx.service_manager.get_workflow_service().run_workflow_async(req)
            ctx.exporter.print_result(
                resp.model_dump() if hasattr(resp, "model_dump") else resp,
                True,
                f"Workflow started asynchronously: {resp.run_id}",
            )
        else:
            # Non-streaming sync execution
            resp = ctx.service_manager.get_workflow_service().run_workflow(req)
            ctx.exporter.print_result(
                resp.model_dump() if hasattr(resp, "model_dump") else resp,
                True,
                "Workflow executed",
            )

    except Exception as e:
        ctx.exporter.print_result(None, False, f"Error: {str(e)}")
        sys.exit(1)


@cli.group()
@click.pass_context
def knowledge(ctx: click.Context):
    """Knowledge base commands."""
    pass


@knowledge.command("retrieve")
@click.option("--workspace-id", required=True, help="Workspace ID")
@click.option("--dataset-ids", required=True, help="Dataset IDs (comma-separated)")
@click.option("--query", "-q", required=True, help="Query to search")
@click.option("--top-k", type=int, default=3, help="Number of results to return")
@click.option("--score-threshold", type=float, default=0.4, help="Minimum score threshold")
@click.pass_obj
def knowledge_retrieve(
    ctx: CLIContext,
    workspace_id: str,
    dataset_ids: str,
    query: str,
    top_k: int,
    score_threshold: float,
):
    """Retrieve knowledge from datasets."""
    try:
        dataset_ids_list = dataset_ids.split(",")

        retriever = ctx.service_manager.init_retriever(
            workspace_id=workspace_id,
            dataset_ids=dataset_ids_list,
            name="knowledge_retriever",
            description="Knowledge retriever",
            top_k=top_k,
            score_threshold=score_threshold,
        )

        result = retriever.invoke({"query": query})
        ctx.exporter.print_result(result, True, f"Retrieved knowledge for: {query}")

    except Exception as e:
        ctx.exporter.print_result(None, False, f"Error: {str(e)}")
        sys.exit(1)


@cli.group()
@click.pass_context
def file(ctx: click.Context):
    """File upload/download commands (UP service)."""
    pass


@file.command("upload")
@click.option("--file", "file_path", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--id", "file_id", help="File ID (defaults to a random cli-* id)")
@click.option("--expire", default="15h", show_default=True, help="Expire duration, e.g. 15h")
@click.option("--content-type", default="application/octet-stream", show_default=True, help="Content type")
@click.pass_obj
def file_upload(
    ctx: CLIContext,
    file_path: Path,
    file_id: Optional[str],
    expire: str,
    content_type: str,
):
    """Upload a file."""
    try:
        from cli_anything.hiagent_sdk.utils.hiagent_backend import upload_raw_file

        result = upload_raw_file(
            ctx.service_manager.get_up_service(),
            file_path=file_path,
            file_id=file_id,
            expire=expire,
            content_type=content_type,
        )
        ctx.exporter.print_result(result, True, f"File uploaded: {file_path.name}")

    except Exception as e:
        ctx.exporter.print_result(None, False, f"Error: {str(e)}")
        sys.exit(1)


@file.command("download")
@click.option("--path", "remote_path", required=True, help="Remote file path returned by upload")
@click.option("--key", help="Download key (auto-fetched if omitted)")
@click.option(
    "--output",
    "output_path",
    required=True,
    type=click.Path(path_type=Path),
    help="Output file path",
)
@click.pass_obj
def file_download(ctx: CLIContext, remote_path: str, key: Optional[str], output_path: Path):
    """Download a file."""
    try:
        from cli_anything.hiagent_sdk.utils.hiagent_backend import download_file

        result = download_file(
            ctx.service_manager.get_up_service(),
            path=remote_path,
            save_to=output_path,
            key=key,
        )
        ctx.exporter.print_result(result, True, f"File downloaded to: {output_path}")

    except Exception as e:
        ctx.exporter.print_result(None, False, f"Error: {str(e)}")
        sys.exit(1)


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


# Load and register plugin commands if available
try:
    from cli_anything.hiagent_sdk.plugins import register_plugin_commands

    register_plugin_commands(cli)
except ImportError:
    # No plugins available
    pass


if __name__ == "__main__":
    cli()
