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
from concurrent.futures import Executor, ThreadPoolExecutor
from contextlib import contextmanager
from typing import Any, Callable, Coroutine, Optional, ParamSpec, TypeVar

P = ParamSpec("P")
T = TypeVar("T")


async def run_in_executor(
    executor: Optional[Executor],
    func: Callable[P, T],
    *args: P.args,
    **kwargs: P.kwargs,
) -> T:
    def wrapper() -> T:
        try:
            return func(*args, **kwargs)
        except StopIteration as exc:
            raise RuntimeError from exc

    return await asyncio.get_running_loop().run_in_executor(executor, wrapper)


@contextmanager
def get_executor(max_parallel: int):
    with ThreadPoolExecutor(
        max_workers=max_parallel,
    ) as executor:
        yield executor


async def gated_coro(
    semaphore: asyncio.Semaphore, coro: Coroutine[Any, Any, Any]
) -> Any:
    async with semaphore:
        return await coro


async def gather_with_concurrency(
    max_parallel: Optional[int], *coros: Coroutine[Any, Any, Any]
) -> list[Any]:
    if max_parallel is None:
        return await asyncio.gather(*coros)

    semaphore = asyncio.Semaphore(max_parallel)

    return await asyncio.gather(*(gated_coro(semaphore, c) for c in coros))
