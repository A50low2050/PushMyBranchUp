import time
from abc import ABC, abstractmethod

from pydantic import BaseModel


class CacheBucket(BaseModel):
    value: dict | str | int
    timestamp: float
    ttl: int


class AsyncCacheServiceBase(ABC):
    @abstractmethod
    async def get(self, key: str) -> dict | str | int | None: ...

    @abstractmethod
    async def setx(
        self,
        key: str,
        value: dict | str | int,
        ttl: int = 3600,
    ) -> dict | str | int | None: ...

    @abstractmethod
    async def exists(self, key: str) -> bool: ...

    @abstractmethod
    async def delete(self, key: str) -> bool: ...

    @abstractmethod
    async def clear(self): ...

    @abstractmethod
    async def ping(self) -> bool:
        """При неудачном соединении с кэшом
        должно возвращаться исключение
        src.utils.exceptions.CacheConnectionError"""
        ...


class InMemoryAsyncCacheService(AsyncCacheServiceBase):
    def __init__(self) -> None:
        self.storage: dict[str, CacheBucket] = {}

    def _check_ttl(self, key: str) -> None | CacheBucket:
        bucket = self.storage.get(key)
        if bucket is None:
            return None

        curr_timestamp = time.time()
        if curr_timestamp - bucket.timestamp >= bucket.ttl:
            del self.storage[key]
            return None

        return bucket

    async def get(self, key: str) -> dict | str | int | None:
        if key not in self.storage:
            return None

        bucket = self._check_ttl(key)
        if bucket is None:
            return None

        return bucket.value

    async def setx(
        self,
        key: str,
        value: dict | str | int,
        ttl: int = 3600,
    ) -> dict | str | int:
        bucket = CacheBucket(
            value=value,
            timestamp=time.time(),
            ttl=ttl,
        )
        self.storage[key] = bucket
        return bucket.value

    async def exists(self, key: str) -> bool:
        bucket = self._check_ttl(key)
        return bucket is not None

    async def delete(self, key: str) -> bool:
        if key in self.storage:
            del self.storage[key]
            return True
        return False

    async def clear(self) -> None:
        self.storage.clear()

    async def ping(self) -> bool:
        """Проверка соединения с кэшом.
        Так как это он в памяти, то всегда
        возвращает True."""
        return True
