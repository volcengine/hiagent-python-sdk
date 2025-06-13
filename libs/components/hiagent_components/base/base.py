from __future__ import annotations

from abc import ABC, abstractmethod
from concurrent.futures import Executor
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncIterator,
    Generic,
    Iterator,
    Optional,
    TypeVar,
    Union,
    cast,
)

from hiagent_components.base.utils import (
    gather_with_concurrency,
    get_executor,
    run_in_executor,
)

if TYPE_CHECKING:
    from hiagent_components.tool.base import BaseTool


Input = TypeVar("Input", contravariant=True)
Output = TypeVar("Output", covariant=True)


class Executable(Generic[Input, Output], ABC):
    name: str

    description: str

    @property
    def input_schema(self) -> dict[str, Any]: ...

    def stream(
        self,
        input: Input,
        **kwargs: Optional[Any],
    ) -> Iterator[Output]:
        yield self.invoke(input, **kwargs)

    async def astream(
        self,
        input: Input,
        **kwargs: Optional[Any],
    ) -> AsyncIterator[Output]:
        yield await self.ainvoke(input, None, **kwargs)

    def batch(
        self,
        inputs: list[Input],
        max_parallel: int,
        return_exceptions: bool = False,
        **kwargs: Optional[Any],
    ) -> list[Output]:
        if not inputs:
            return []

        def invoke(input: Input) -> Union[Output, Exception]:
            if return_exceptions:
                try:
                    return self.invoke(input, **kwargs)
                except Exception as e:
                    return e
            else:
                return self.invoke(input, **kwargs)

        if len(inputs) == 1:
            return cast("list[Output]", [invoke(inputs[0])])

        with get_executor(max_parallel) as executor:
            return cast("list[Output]", list[executor.map(invoke, inputs)])

    async def abatch(
        self,
        inputs: list[Input],
        max_parallel: int,
        return_exceptions: bool = False,
        **kwargs: Optional[Any],
    ) -> list[Output]:
        if not inputs:
            return []

        with get_executor(max_parallel) as executor:

            async def ainvoke(
                input: Input,
            ) -> Union[Output, Exception]:
                if return_exceptions:
                    try:
                        return await self.ainvoke(input, executor, **kwargs)
                    except Exception as e:
                        return e
                else:
                    return await self.ainvoke(input, executor, **kwargs)

            coros = map(ainvoke, inputs)
            return await gather_with_concurrency(max_parallel, *coros)

    def with_retry(
        self,
        retry_if_exceptions: list[type[BaseException]] = [Exception],
        wait_exponential_jitter: bool = True,
        stop_after_attempt: int = 3,
    ) -> Executable[Input, Output]: ...

    def as_tool(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> BaseTool:
        from hiagent_components.tool.tool import ExecutableTool

        return ExecutableTool.from_executable(self, name, description)

    @abstractmethod
    def invoke(self, input: Input, **kwargs: Any) -> Output: ...

    async def ainvoke(
        self,
        input: Input,
        executor: Optional[Executor] = None,
        **kwargs: Any,
    ) -> Output:
        return await run_in_executor(executor, self.invoke, input, **kwargs)
