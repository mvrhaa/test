from typing import Any

import httpx

from config import settings


class CoinGeckoAPIError(Exception):
    """Raised when CoinGecko returns a payload the screener cannot use."""


class CoinGeckoClient:
    MARKET_PAGE_SIZE = 250

    def __init__(self) -> None:
        self._client = httpx.AsyncClient(
            base_url=f"{settings.base_url.rstrip('/')}/",
            headers=settings.auth_header,
            timeout=httpx.Timeout(20.0),
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def markets_page(self, page: int) -> list[dict[str, Any]]:
        payload = await self._get_json(
            "coins/markets",
            params={
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": self.MARKET_PAGE_SIZE,
                "page": page,
                "sparkline": "false",
            },
        )
        if not isinstance(payload, list) or any(
            not isinstance(row, dict) for row in payload
        ):
            raise CoinGeckoAPIError("CoinGecko returned an invalid markets response")
        return payload

    async def coin_detail(self, coin_id: str) -> dict[str, Any]:
        payload = await self._get_json(
            f"coins/{coin_id}",
            params={
                "localization": "false",
                "tickers": "false",
                "market_data": "true",
                "community_data": "false",
                "developer_data": "false",
                "sparkline": "false",
            },
        )
        if not isinstance(payload, dict):
            raise CoinGeckoAPIError(
                f"CoinGecko returned an invalid detail response for {coin_id}"
            )
        return payload

    async def _get_json(self, path: str, params: dict[str, str | int]) -> Any:
        response = await self._client.get(path, params=params)
        response.raise_for_status()
        try:
            return response.json()
        except ValueError as exc:
            raise CoinGeckoAPIError(
                f"CoinGecko returned invalid JSON for {response.request.url.path}"
            ) from exc
