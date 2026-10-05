import unittest
from typing import Any

from backend.app.service import ScreenerService


class FakeCoinPaprikaClient:
    def __init__(self) -> None:
        self.calls = 0

    async def tickers(self) -> list[dict[str, Any]]:
        self.calls += 1
        return [
            {
                "id": "sample-coin",
                "name": "Sample Coin",
                "symbol": "SMP",
                "max_supply": 10_000_000,
                "total_supply": 10_000_000,
                "quotes": {
                    "USD": {
                        "price": 2,
                        "market_cap": 1_000_000,
                        "volume_24h": 60_000,
                    }
                },
            }
        ]


class ScreenerServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_maps_ticker_and_uses_cached_response(self) -> None:
        client = FakeCoinPaprikaClient()
        service = ScreenerService(client)

        first = await service.get_filtered()
        second = await service.get_filtered()

        self.assertEqual(client.calls, 1)
        self.assertEqual(first, second)
        self.assertEqual(len(first), 1)
        self.assertEqual(first[0]["name"], "Sample Coin")
        self.assertEqual(first[0]["fdv"], 20_000_000)

    async def test_refresh_reads_live_api_again(self) -> None:
        client = FakeCoinPaprikaClient()
        service = ScreenerService(client)

        await service.get_filtered()
        await service.get_filtered(refresh=True)

        self.assertEqual(client.calls, 2)


if __name__ == "__main__":
    unittest.main()
