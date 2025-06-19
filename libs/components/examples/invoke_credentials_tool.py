import asyncio
import os

from dotenv import load_dotenv
from hiagent_api.tool import ToolService
from hiagent_components.tool.tool import Tool

load_dotenv()

ak = os.getenv("AIPPT_AK")
sk = os.getenv("AIPPT_SK")

def get_tool_svc() -> ToolService:
    svc = ToolService(
        endpoint=os.getenv("HIAGENT_TOP_ENDPOINT") or "", region="cn-north-1"
    )
    return svc


def invoke_aippt_tool():
    tool = Tool.init(
        svc=get_tool_svc(),
        workspace_id="cuq0pp9s7366bfl0cns0",
        tool_id="5tg2e381qs08vmoh7ft0",
        # credentials={
        #     "api_key": ak,
        #     "secret_key": sk,
        # }
    )

    resp = tool.invoke(input={"ppt_title": "健康生活一百年"})
    print("invoke tool:", resp)

async def get_tool_input_schema():
    tool = await Tool.ainit(
        svc=get_tool_svc(),
        workspace_id="cuq0pp9s7366bfl0cns0",
        tool_id="5tg2e381qs08vmoh7ft0",
    )
    print(tool.name)
    print(tool.description)
    print(tool.input_schema)


if __name__ == "__main__":
    asyncio.run(get_tool_input_schema())
    invoke_aippt_tool()