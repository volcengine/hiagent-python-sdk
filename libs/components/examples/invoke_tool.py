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


def invoke_tool():
    tool = Tool.init(
        svc=get_tool_svc(),
        workspace_id="cuq0pp9s7366bfl0cns0",
        tool_id="rgnadh3poolns0v5sa10",
    )

    resp = tool.invoke(input={"query": "llm"})
    print("invoke tool:", resp)


async def ainvoke_tool():
    tool = await Tool.ainit(
        svc=get_tool_svc(),
        workspace_id="cuq0pp9s7366bfl0cns0",
        tool_id="rgnadh3poolns0v5sa10",
    )

    resp = await tool.ainvoke(input={"query": "llm"})
    print("ainvoke tool:", resp)


async def get_tool_input_schema():
    tool = await Tool.ainit(
        svc=get_tool_svc(),
        workspace_id="cuq0pp9s7366bfl0cns0",
        tool_id="rgnadh3poolns0v5sa10",
    )
    print(tool.name)
    print(tool.description)
    print(tool.input_schema)


if __name__ == "__main__":
    asyncio.run(get_tool_input_schema())

    asyncio.run(ainvoke_tool())

    invoke_tool()