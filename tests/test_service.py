import unittest
from typing import Any

from coingecko import CoinGeckoClient
from service import ScreenerService


class FakeCoinGeckoClient(CoinGeckoClient):
    MARKET_PAGE_SIZE = 250

    def __init__(self) -> None:
        self.requested_pages: list[int] = []
        self.requested_details: list[str] = []

    async def markets_page(self, page: int) -> list[dict[str, Any]]:
        self.requested_pages.append(page)
        if page == 1:
            return [
                {
                    "market_cap": 0,
                    "fully_diluted_valuation": 1,
                    "total_volume": 100_000,
                    "max_supply": 1,
                    "total_supply": 1,
                }
                for _ in range(self.MARKET_PAGE_SIZE)
            ]
        if page == 2:
            return [
                {
                    "id": "test-coin",
                    "symbol": "tst",
                    "name": "Test Coin",
                    "market_cap": 1_000_000,
                    "fully_diluted_valuation": 90_000_000,
                    "total_volume": 60_000,
                    "max_supply": 1_000_000,
                    "total_supply": 1_000_000,
                }
            ]
        return []

    async def coin_detail(self, coin_id: str) -> dict[str, Any]:
        self.requested_details.append(coin_id)
        return {
            "preview_listing": True,
            "market_data": {"total_value_locked": 70_000},
        }


class ScreenerServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_scans_market_pages_and_returns_matching_details(self) -> None:
        client = FakeCoinGeckoClient()
        service = ScreenerService(client)

        coins = await service.get_filtered(refresh=True)

        self.assertEqual(client.requested_pages, [1, 2])
        self.assertEqual(client.requested_details, ["test-coin"])
        self.assertEqual(
            coins,
            [
                {
                    "id": "test-coin",
                    "symbol": "tst",
                    "name": "Test Coin",
                    "market_cap": 1_000_000,
                    "fdv": 90_000_000,
                    "volume_24h": 60_000,
                    "tvl": 70_000,
                    "max_supply": 1_000_000,
                    "total_supply": 1_000_000,
                    "preview_listing": True,
                }
            ],
        )


if __name__ == "__main__":
    unittest.main()
