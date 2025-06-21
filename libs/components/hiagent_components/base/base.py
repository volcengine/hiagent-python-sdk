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
from __future__ import annotations

from abc import ABC, abstractmethod
from concurrent.futures import Executor
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncIterator,
    Dict,
    Generic,
    Iterator,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)

from tenacity import (
    AsyncRetrying,
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
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
        retry_exception_types: Tuple[Type[BaseException]] = (Exception,),
        wait_exponential_jitter: bool = True,
        max_attempts: int = 3,
    ) -> Executable[Input, Output]:
        return RetryableExecutable(self, retry_exception_types, wait_exponential_jitter, max_attempts)

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

class RetryableExecutable(Executable[Input, Output]):
    def __init__(
        self,
        executable: Executable[Input, Output],
        retry_exception_types: Tuple[Type[BaseException], ...] = (Exception,),
        wait_exponential_jitter: bool = True,
        max_attempts: int = 3,
    ):
        self.max_attempts = max_attempts
        self.retry_exception_types = retry_exception_types
        self.wait_exponential_jitter = wait_exponential_jitter
        self.executable = executable

    @property
    def _retrying_kwargs(self) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = dict()

        if self.max_attempts:
            kwargs["stop"] = stop_after_attempt(self.max_attempts)

        if self.wait_exponential_jitter:
            kwargs["wait"] = wait_exponential_jitter()

        if self.retry_exception_types:
            kwargs["retry"] = retry_if_exception_type(self.retry_exception_types)

        return kwargs

    def _sync_retrying(self, **kwargs: Any) -> Retrying:
        return Retrying(**self._retrying_kwargs, **kwargs)

    def _async_retrying(self, **kwargs: Any) -> AsyncRetrying:
        return AsyncRetrying(**self._retrying_kwargs, **kwargs)

    def invoke(self, input: Input, **kwargs: Any) -> Output:
        result = None
        for attempt in self._sync_retrying(reraise=True):
            with attempt:
                result = self.executable.invoke(
                    input,
                    **kwargs,
                )
            if attempt.retry_state.outcome and not attempt.retry_state.outcome.failed:
                attempt.retry_state.set_result(result)
        return result

    async def ainvoke(
        self,
        input: Input,
        executor: Optional[Executor] = None,
        **kwargs: Any
    ) -> Output:
        result = None
        async for attempt in self._async_retrying(reraise=True):
            with attempt:
                result = await self.executable.ainvoke(
                    input,
                    executor,
                    **kwargs,
                )
            if attempt.retry_state.outcome and not attempt.retry_state.outcome.failed:
                attempt.retry_state.set_result(result)
        return result
