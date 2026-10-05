import math
import unittest

from backend.app.filters import coin_from_ticker


class CoinPaprikaFilterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.ticker = {
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

    def test_estimates_fdv_and_returns_project_data(self) -> None:
        coin = coin_from_ticker(self.ticker)
        self.assertIsNotNone(coin)
        assert coin is not None
        self.assertEqual(coin["fdv"], 20_000_000)
        self.assertEqual(coin["market_cap"], 1_000_000)
        self.assertEqual(coin["volume_24h"], 60_000)

    def test_excludes_values_at_strict_thresholds(self) -> None:
        for changes in (
            {"quotes": {"USD": {"price": 2, "market_cap": 0, "volume_24h": 60_000}}},
            {"quotes": {"USD": {"price": 2, "market_cap": 1, "volume_24h": 50_000}}},
        ):
            with self.subTest(changes=changes):
                self.assertIsNone(coin_from_ticker(self.ticker | changes))
        too_expensive = self.ticker | {
            "quotes": {
                "USD": {
                    "price": 10,
                    "market_cap": 1_000_000,
                    "volume_24h": 60_000,
                }
            }
        }
        self.assertIsNone(coin_from_ticker(too_expensive))

    def test_requires_equal_supply_and_complete_numeric_data(self) -> None:
        self.assertIsNone(
            coin_from_ticker(self.ticker | {"total_supply": 9_999_999})
        )
        self.assertIsNone(coin_from_ticker(self.ticker | {"max_supply": None}))
        self.assertIsNone(
            coin_from_ticker(self.ticker | {"max_supply": 0, "total_supply": 0})
        )
        bad_price = self.ticker | {
            "quotes": {
                "USD": {
                    "price": math.nan,
                    "market_cap": 1_000_000,
                    "volume_24h": 60_000,
                }
            }
        }
        self.assertIsNone(coin_from_ticker(bad_price))

    def test_requires_usd_quote_and_project_identity(self) -> None:
        self.assertIsNone(coin_from_ticker(self.ticker | {"quotes": {}}))
        self.assertIsNone(coin_from_ticker(self.ticker | {"name": ""}))
        self.assertIsNone(
            coin_from_ticker(
                self.ticker
                | {
                    "quotes": {
                        "USD": {
                            "price": 2,
                            "market_cap": 1_000_000,
                            "volume_24h": 60_000,
                        }
                    }
                }
                | {"id": ""}
            )
        )


if __name__ == "__main__":
    unittest.main()
