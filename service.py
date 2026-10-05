import asyncio
import logging
import time
from typing import Any

from coingecko import CoinGeckoClient
from config import settings
from filters import extract_tvl_usd, passes_detail_filters, passes_market_filters

log = logging.getLogger(__name__)


class ScreenerService:
    def __init__(self, client: CoinGeckoClient) -> None:
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
        # Stage 1: cheap bulk filter on /coins/markets
        candidates: list[dict[str, Any]] = []
        page = 1
        while True:
            rows = await self._client.markets_page(page)
            if not rows:
                break
            candidates.extend(r for r in rows if passes_market_filters(r))
            if len(rows) < self._client.MARKET_PAGE_SIZE:
                break
            page += 1
        log.info("Stage 1 candidates: %d", len(candidates))

        # Stage 2: per-coin check for preview_listing + TVL
        sem = asyncio.Semaphore(settings.detail_concurrency)

        async def check(m: dict[str, Any]) -> dict[str, Any] | None:
            async with sem:
                detail = await self._client.coin_detail(m["id"])
            if not passes_detail_filters(detail):
                return None
            return {
                "id": m["id"],
                "symbol": m["symbol"],
                "name": m["name"],
                "market_cap": m["market_cap"],
                "fdv": m["fully_diluted_valuation"],
                "volume_24h": m["total_volume"],
                "tvl": extract_tvl_usd(detail),
                "max_supply": m["max_supply"],
                "total_supply": m["total_supply"],
                "preview_listing": detail["preview_listing"],
            }

        results = await asyncio.gather(*(check(m) for m in candidates))
        return [r for r in results if r]