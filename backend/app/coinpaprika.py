from typing import Any

import httpx

from .config import settings


class CoinPaprikaClient:
    def __init__(self) -> None:
        self._client = httpx.AsyncClient(
            base_url=f"{settings.coinpaprika_base_url.rstrip('/')}/",
            timeout=20.0,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def tickers(self) -> list[dict[str, Any]]:
        response = await self._client.get("tickers")
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, list) or any(not isinstance(row, dict) for row in data):
            raise ValueError("Market-data API returned an invalid ticker list")
        return data
