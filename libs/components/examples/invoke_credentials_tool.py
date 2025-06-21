# Copyright (c) 2024 Bytedance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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
        credentials={
            "api_key": ak,
            "secret_key": sk,
        }
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
