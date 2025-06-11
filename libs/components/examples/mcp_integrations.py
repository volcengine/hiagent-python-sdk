import os

from dotenv import load_dotenv
from hiagent_api.knowledgebase import KnowledgebaseService
from hiagent_api.workflow import WorkflowService
from hiagent_components.integrations.mcp.tool import MCPTool
from hiagent_components.retriever.base import KnowledgeRetriever
from hiagent_components.workflow.base import Workflow
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.tools import Tool

load_dotenv()


def add(a: int, b: int) -> int:
    """add two numbers and return sum"""
    return a + b


def get_workflow_svc() -> WorkflowService:
    svc = WorkflowService(
        endpoint=os.getenv("HIAGENT_TOP_ENDPOINT") or "", region="cn-north-1"
    )

    svc.set_app_base_url(os.getenv("HIAGENT_APP_BASE_URL") or "")

    return svc


def get_knowledgebase_svc() -> KnowledgebaseService:
    svc = KnowledgebaseService(
        endpoint=os.getenv("HIAGENT_TOP_ENDPOINT") or "", region="cn-north-1"
    )

    return svc


def get_workflow_as_langchain_tool():
    app_key = os.getenv("HIAGENT_APP_KEY") or ""
    workflow = Workflow.init(
        svc=get_workflow_svc(),
        app_key=app_key,
        workflow_id="cvel84kg58epjrfkvtb0",
        workspace_id="cuq0pp9s7366bfl0cns0",
        user_id="test",
    )
    return workflow.as_tool()


def get_retriever_as_langchain_tool():
    retriever = KnowledgeRetriever(
        svc=get_knowledgebase_svc(),
        name="knowledge",
        description="知识库工具，用来检索大熊猫的相关知识",
        workspace_id="cuq0pp9s7366bfl0cns0",
        dataset_ids=["019613e3-f37b-7b80-8e0a-579435bb9870"],
        top_k=3,
        score_threshold=0.4,
        retrieval_search_method=0,
    )

    return retriever.as_tool()


def get_mcp_server() -> FastMCP:
    add_tool = Tool.from_function(add)
    workflow_tool = MCPTool.from_tool(get_workflow_as_langchain_tool())
    knowledge_tool = MCPTool.from_tool(get_retriever_as_langchain_tool())
    mcp = FastMCP(
        "hiagent-mcp-server",
        tools=[add_tool, workflow_tool, knowledge_tool],
    )
    return mcp


if __name__ == "__main__":
    mcp_server = get_mcp_server()

    mcp_server.run(transport="sse")
