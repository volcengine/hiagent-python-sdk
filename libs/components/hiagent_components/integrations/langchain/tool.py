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
