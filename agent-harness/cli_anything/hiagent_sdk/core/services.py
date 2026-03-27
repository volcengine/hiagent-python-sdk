"""Service initialization and management for HiAgent SDK CLI."""

import os
from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from hiagent_api.chat import ChatService
    from hiagent_api.tool import ToolService
    from hiagent_api.workflow import WorkflowService
    from hiagent_api.knowledgebase import KnowledgebaseService
    from hiagent_api.eva import EvaService
    from hiagent_api.observe import ObserveService
    from hiagent_api.up import UpService
    from hiagent_components.agent import Agent
    from hiagent_components.tool import Tool
    from hiagent_components.workflow import Workflow
    from hiagent_components.retriever import KnowledgeRetriever


def _missing_dep_error(missing: str) -> RuntimeError:
    return RuntimeError(
        f"Missing dependency: {missing}\n\n"
        "If you are in the hiagent-python-sdk monorepo, install from source:\n"
        "  pip install -e /path/to/hiagent-python-sdk/libs/api\n"
        "  pip install -e /path/to/hiagent-python-sdk/libs/components\n"
        "  pip install -e /path/to/hiagent-python-sdk/agent-harness\n\n"
        "Or using uv from repo root:\n"
        "  uv sync --dev\n"
        "  uv pip install -e agent-harness\n"
    )


Agent = None
Tool = None
Workflow = None
KnowledgeRetriever = None


class ServiceManager:
    """Manages HiAgent service initialization and caching."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize service manager with configuration."""
        self.config = config
        self._services = {}

    def get_endpoint(self) -> str:
        """Get the endpoint URL."""
        return self.config.get("endpoint", "https://open.volcengineapi.com")

    def get_region(self) -> str:
        """Get the region."""
        return self.config.get("region", "cn-north-1")

    def get_chat_service(self):
        """Get or create ChatService."""
        try:
            from hiagent_api.chat import ChatService
        except ModuleNotFoundError as e:
            raise _missing_dep_error("hiagent-api") from e

        if "chat" not in self._services:
            self._services["chat"] = ChatService(
                endpoint=self.get_endpoint(),
                region=self.get_region()
            )
        return self._services["chat"]

    def get_tool_service(self):
        """Get or create ToolService."""
        try:
            from hiagent_api.tool import ToolService
        except ModuleNotFoundError as e:
            raise _missing_dep_error("hiagent-api") from e

        if "tool" not in self._services:
            self._services["tool"] = ToolService(
                endpoint=self.get_endpoint(),
                region=self.get_region()
            )
        return self._services["tool"]

    def get_workflow_service(self):
        """Get or create WorkflowService."""
        try:
            from hiagent_api.workflow import WorkflowService
        except ModuleNotFoundError as e:
            raise _missing_dep_error("hiagent-api") from e

        if "workflow" not in self._services:
            self._services["workflow"] = WorkflowService(
                endpoint=self.get_endpoint(),
                region=self.get_region()
            )
        return self._services["workflow"]

    def get_knowledgebase_service(self):
        """Get or create KnowledgebaseService."""
        try:
            from hiagent_api.knowledgebase import KnowledgebaseService
        except ModuleNotFoundError as e:
            raise _missing_dep_error("hiagent-api") from e

        if "knowledgebase" not in self._services:
            self._services["knowledgebase"] = KnowledgebaseService(
                endpoint=self.get_endpoint(),
                region=self.get_region()
            )
        return self._services["knowledgebase"]

    def get_eva_service(self):
        """Get or create EvaService."""
        try:
            from hiagent_api.eva import EvaService
        except ModuleNotFoundError as e:
            raise _missing_dep_error("hiagent-api") from e

        if "eva" not in self._services:
            self._services["eva"] = EvaService(
                endpoint=self.get_endpoint(),
                region=self.get_region()
            )
        return self._services["eva"]

    def get_observe_service(self):
        """Get or create ObserveService."""
        try:
            from hiagent_api.observe import ObserveService
        except ModuleNotFoundError as e:
            raise _missing_dep_error("hiagent-api") from e

        if "observe" not in self._services:
            self._services["observe"] = ObserveService(
                endpoint=self.get_endpoint(),
                region=self.get_region()
            )
        return self._services["observe"]

    def get_up_service(self):
        """Get or create UpService."""
        try:
            from hiagent_api.up import UpService
        except ModuleNotFoundError as e:
            raise _missing_dep_error("hiagent-api") from e

        if "up" not in self._services:
            self._services["up"] = UpService(
                endpoint=self.get_endpoint(),
                region=self.get_region()
            )
        return self._services["up"]

    def init_agent(
        self,
        app_key: str,
        user_id: str,
        variables: Dict[str, Any],
        conversation_id: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ):
        """Initialize an Agent component."""
        global Agent
        if Agent is None:
            try:
                from hiagent_components.agent import Agent as _Agent
            except ModuleNotFoundError as e:
                raise _missing_dep_error("hiagent-components") from e
            Agent = _Agent

        return Agent.init(
            svc=self.get_chat_service(),
            app_key=app_key,
            user_id=user_id,
            variables=variables,
            conversation_id=conversation_id,
            name=name,
            description=description,
        )

    def init_tool(
        self,
        workspace_id: str,
        tool_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ):
        """Initialize a Tool component."""
        global Tool
        if Tool is None:
            try:
                from hiagent_components.tool import Tool as _Tool
            except ModuleNotFoundError as e:
                raise _missing_dep_error("hiagent-components") from e
            Tool = _Tool

        return Tool.init(
            svc=self.get_tool_service(),
            workspace_id=workspace_id,
            tool_id=tool_id,
            name=name,
            description=description,
        )

    def init_workflow(
        self,
        app_key: str,
        workspace_id: str,
        workflow_id: str,
        user_id: str,
    ):
        """Initialize a Workflow component."""
        global Workflow
        if Workflow is None:
            try:
                from hiagent_components.workflow import Workflow as _Workflow
            except ModuleNotFoundError as e:
                raise _missing_dep_error("hiagent-components") from e
            Workflow = _Workflow

        return Workflow.init(
            svc=self.get_workflow_service(),
            app_key=app_key,
            workspace_id=workspace_id,
            workflow_id=workflow_id,
            user_id=user_id,
        )

    def init_retriever(
        self,
        workspace_id: str,
        dataset_ids: list,
        name: str,
        description: Optional[str] = None,
        top_k: int = 3,
        score_threshold: float = 0.4,
    ):
        """Initialize a KnowledgeRetriever component."""
        global KnowledgeRetriever
        if KnowledgeRetriever is None:
            try:
                from hiagent_components.retriever import KnowledgeRetriever as _KnowledgeRetriever
            except ModuleNotFoundError as e:
                raise _missing_dep_error("hiagent-components") from e
            KnowledgeRetriever = _KnowledgeRetriever

        return KnowledgeRetriever(
            svc=self.get_knowledgebase_service(),
            name=name,
            description=description or "",
            workspace_id=workspace_id,
            dataset_ids=dataset_ids,
            top_k=top_k,
            score_threshold=score_threshold,
        )
