from __future__ import annotations

from abc import abstractmethod
from concurrent.futures import Executor
from typing import (
    Any,
    Dict,
    Optional,
    TypeVar,
)

from hiagent_components.base import Executable
from hiagent_components.base.utils import (
    run_in_executor,
)

Input = TypeVar("Input", contravariant=True)
Output = TypeVar("Output", covariant=True)


class BaseTool(Executable):
    name: str
    description: str

    def invoke(
        self,
        input: Dict[str, Any],
        **kwargs: Any,
    ) -> Any:
        return self._invoke(input, **kwargs)

    async def ainvoke(
        self,
        input: Dict[str, Any],
        executor: Optional[Executor] = None,
        **kwargs: Any,
    ) -> Any:
        return await self._ainvoke(input, executor, **kwargs)

    @abstractmethod
    def _invoke(
        self,
        input: Dict[str, Any],
        **kwargs: Any,
    ) -> Any: ...

    async def _ainvoke(
        self,
        input: Dict[str, Any],
        executor: Optional[Executor] = None,
        **kwargs: Any,
    ) -> Any:
        return await run_in_executor(executor, self._invoke, input, **kwargs)
