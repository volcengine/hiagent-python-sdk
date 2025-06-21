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
from hiagent_components.tool import BaseTool
from json_schema_to_pydantic import create_model
from mcp.server.fastmcp.tools.base import Tool
from mcp.server.fastmcp.utilities.func_metadata import ArgModelBase, FuncMetadata


class MCPTool(Tool):
    @classmethod
    def from_tool(cls, tool: BaseTool) -> "MCPTool":
        arg_model = create_model(tool.input_schema, base_model_type=ArgModelBase)

        func_arg_metadata = FuncMetadata(
            arg_model=arg_model,
        )

        async def ainvoke(**kwargs):
            return await tool.ainvoke(input=kwargs)

        mcp_tool = cls(
            fn=ainvoke,
            name=tool.name,
            description=tool.description,
            parameters=tool.input_schema,
            is_async=True,
            fn_metadata=func_arg_metadata,
            context_kwarg=None,
            annotations=None,
        )

        return mcp_tool
