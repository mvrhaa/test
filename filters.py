import math
from typing import Any

from config import settings


def passes_market_filters(m: dict[str, Any]) -> bool:
    mcap = m.get("market_cap")
    fdv = m.get("fully_diluted_valuation")
    volume = m.get("total_volume")
    max_supply = m.get("max_supply")
    total_supply = m.get("total_supply")

    values = (mcap, fdv, volume, max_supply, total_supply)
    if any(
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or not math.isfinite(value)
        for value in values
    ):
        return False
    return (
        mcap > 0
        and fdv < settings.max_fdv
        and volume > settings.min_volume_24h
        and max_supply == total_supply
    )


def extract_tvl_usd(detail: dict[str, Any]) -> float | None:
    market_data = detail.get("market_data")
    if not isinstance(market_data, dict):
        return None
    tvl = market_data.get("total_value_locked")
    if isinstance(tvl, dict):
        tvl = tvl.get("usd")
    if (
        isinstance(tvl, (int, float))
        and not isinstance(tvl, bool)
        and math.isfinite(tvl)
    ):
        return float(tvl)
    return None


def passes_detail_filters(detail: dict[str, Any]) -> bool:
    """Check listing preview status and TVL in a /coins/{id} payload."""
    if detail.get("preview_listing") is not True:
        return False
    tvl = extract_tvl_usd(detail)
    return tvl is not None and tvl > settings.min_tvl