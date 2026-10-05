import math
import unittest

from filters import passes_detail_filters, passes_market_filters


class MarketFilterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.market = {
            "market_cap": 1_000_000,
            "fully_diluted_valuation": 99_000_000,
            "total_volume": 51_000,
            "max_supply": 1_000_000,
            "total_supply": 1_000_000,
        }

    def test_accepts_coin_meeting_all_market_criteria(self) -> None:
        self.assertTrue(passes_market_filters(self.market))

    def test_market_thresholds_are_strict(self) -> None:
        for field, value in (
            ("market_cap", 0),
            ("fully_diluted_valuation", 100_000_000),
            ("total_volume", 50_000),
        ):
            with self.subTest(field=field):
                market = self.market | {field: value}
                self.assertFalse(passes_market_filters(market))

    def test_supply_must_be_present_and_exactly_equal(self) -> None:
        self.assertFalse(
            passes_market_filters(self.market | {"total_supply": 999_999.9999})
        )
        self.assertFalse(passes_market_filters(self.market | {"max_supply": None}))

    def test_rejects_non_finite_market_values(self) -> None:
        self.assertFalse(
            passes_market_filters(self.market | {"market_cap": math.nan})
        )


class DetailFilterTests(unittest.TestCase):
    def test_accepts_preview_listing_with_tvl_above_threshold(self) -> None:
        detail = {
            "preview_listing": True,
            "market_data": {"total_value_locked": {"usd": 50_001}},
        }
        self.assertTrue(passes_detail_filters(detail))

    def test_tvl_threshold_is_strict(self) -> None:
        detail = {
            "preview_listing": True,
            "market_data": {"total_value_locked": 50_000},
        }
        self.assertFalse(passes_detail_filters(detail))

    def test_requires_preview_listing_and_valid_tvl(self) -> None:
        no_preview = {
            "preview_listing": False,
            "market_data": {"total_value_locked": 100_000},
        }
        no_tvl = {"preview_listing": True, "market_data": {"total_value_locked": None}}
        self.assertFalse(passes_detail_filters(no_preview))
        self.assertFalse(passes_detail_filters(no_tvl))
        malformed_market_data = {"preview_listing": True, "market_data": []}
        self.assertFalse(passes_detail_filters(malformed_market_data))


if __name__ == "__main__":
    unittest.main()
