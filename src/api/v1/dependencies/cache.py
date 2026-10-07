import asyncio
from collections.abc import AsyncGenerator
from typing import Annotated, Any

from fastapi import Depends, Request

from src.utils.cacheserv import AsyncCacheServiceBase
from src.utils.exceptions import CacheConnectionError


async def get_cache(request: Request) -> AsyncGenerator[AsyncCacheServiceBase, Any]:
    cache: AsyncCacheServiceBase = request.app.state.cache
    try:
        async with asyncio.timeout(3):
            await cache.ping()
    except asyncio.TimeoutError as exc:
        raise CacheConnectionError(detail="Не удалось подключиться к кэшу") from exc

    yield cache


CacheDep = Annotated[AsyncCacheServiceBase, Depends(get_cache)]
