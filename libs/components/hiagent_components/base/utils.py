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
