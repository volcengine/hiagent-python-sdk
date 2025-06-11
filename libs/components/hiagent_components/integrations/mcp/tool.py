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
