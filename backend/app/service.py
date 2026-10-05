import asyncio
import time
from typing import Any

from .coinpaprika import CoinPaprikaClient
from .config import settings
from .filters import coin_from_ticker


class ScreenerService:
    def __init__(self, client: CoinPaprikaClient) -> None:
        self._client = client
        self._lock = asyncio.Lock()
        self._cache: list[dict[str, Any]] | None = None
        self._cached_at = 0.0

    @property
    def cached_at(self) -> float:
        return self._cached_at

    async def get_filtered(self, refresh: bool = False) -> list[dict[str, Any]]:
        async with self._lock:  # one scan at a time
            fresh = time.time() - self._cached_at < settings.cache_ttl_seconds
            if self._cache is not None and fresh and not refresh:
                return self._cache
            self._cache = await self._scan()
            self._cached_at = time.time()
            return self._cache

    async def _scan(self) -> list[dict[str, Any]]:
        tickers = await self._client.tickers()
        return [coin for ticker in tickers if (coin := coin_from_ticker(ticker))]