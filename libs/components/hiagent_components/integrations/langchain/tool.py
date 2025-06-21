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
from langchain_core.tools.structured import StructuredTool

from hiagent_components.tool.base import BaseTool


class LangChainTool(StructuredTool):
    @classmethod
    def from_tool(cls, tool: BaseTool) -> "LangChainTool":
        def invoke(**kwargs):
            return tool.invoke(input=kwargs)

        async def ainvoke(**kwargs):
            return await tool.ainvoke(input=kwargs)

        return LangChainTool(
            name=tool.name,
            description=tool.description,
            args_schema=tool.input_schema,
            func=invoke,
            coroutine=ainvoke,
        )
