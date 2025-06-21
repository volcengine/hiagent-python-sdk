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
        raise_exception: bool = True,
        **kwargs: Any,
    ) -> Any:
        return self._invoke(input, **kwargs)

    async def ainvoke(
        self,
        input: Dict[str, Any],
        raise_exception: bool = True,
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
