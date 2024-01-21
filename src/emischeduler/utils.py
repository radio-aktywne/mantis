import asyncio
from functools import partial
from typing import Callable, ParamSpec, TypeVar

T = TypeVar("T")
P = ParamSpec("P")


async def background(f: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
    loop = asyncio.get_running_loop()
    f = partial(f, *args, **kwargs)
    return await loop.run_in_executor(None, f)
