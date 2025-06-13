from concurrent.futures import Executor
from typing import Any, Dict, Optional

from typing_extensions import Self

from hiagent_components.base import Executable
from hiagent_components.tool.base import BaseTool


class ExecutableTool(BaseTool):
    def __init__(self, name: str, description: str, executable: Executable):
        self.name = name
        self.description = description
        self.executable = executable

    @property
    def input_schema(self) -> dict[str, Any]:
        return self.executable.input_schema

    @classmethod
    def from_executable(
        cls,
        executable: Executable,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Self:
        if name is None:
            name = executable.name
            if not name:
                name = executable.__class__.__name__

        if description is None:
            description = executable.description

        return cls(
            name=name,
            description=description,
            executable=executable,
        )

    def _invoke(self, input: Dict[str, Any], **kwargs: Any) -> Any:
        return self.executable.invoke(input, **kwargs)

    async def _ainvoke(
        self,
        input: Dict[str, Any],
        executor: Optional[Executor] = None,
        **kwargs: Any,
    ) -> Any:
        return await self.executable.ainvoke(input, executor, **kwargs)


class Tool(BaseTool):
    """
    Tool is a unified encapsulation of tools on the HiAgent platform. You can call a tool by providing the tool ID.
    """

    @classmethod
    def from_tool_service(cls): ...
