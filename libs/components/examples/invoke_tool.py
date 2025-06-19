import asyncio
import os

from dotenv import load_dotenv
from hiagent_api.tool import ToolService
from hiagent_components.tool.tool import Tool

load_dotenv()


def get_tool_svc() -> ToolService:
    svc = ToolService(
        endpoint=os.getenv("HIAGENT_TOP_ENDPOINT") or "", region="cn-north-1"
    )
    return svc


def invoke_tool(tool_id: str, input: dict):
    tool = Tool.init(
        svc=get_tool_svc(),
        workspace_id="cuq0pp9s7366bfl0cns0",
        tool_id=tool_id
    )

    resp = tool.invoke(input=input)
    print("invoke tool:", resp)


async def ainvoke_tool(tool_id: str, input: dict):
    tool = await Tool.ainit(
        svc=get_tool_svc(),
        workspace_id="cuq0pp9s7366bfl0cns0",
        tool_id=tool_id,
    )

    resp = await tool.ainvoke(input=input)
    print("ainvoke tool:", resp)


async def get_tool_input_schema(tool_id: str):
    tool = await Tool.ainit(
        svc=get_tool_svc(),
        workspace_id="cuq0pp9s7366bfl0cns0",
        tool_id=tool_id,
    )
    print(tool.name)
    print(tool.description)
    print(tool.input_schema)


if __name__ == "__main__":
    print("=====================invoke arxiv tool=======================")
    arxiv = "rgnadh3poolns0v5sa10"
    arxiv_input = {"query": "llm"}
    asyncio.run(get_tool_input_schema(arxiv))
    asyncio.run(ainvoke_tool(arxiv, arxiv_input))
    invoke_tool(arxiv, arxiv_input)

    print("=====================invoke mcp time tool=======================")
    tool_id = "d13b7huckn3ivh361hj0"
    tool_input = {"timezone": "America/New_York"}
    asyncio.run(get_tool_input_schema(tool_id))
    asyncio.run(ainvoke_tool(tool_id, tool_input))
    invoke_tool(tool_id, tool_input)