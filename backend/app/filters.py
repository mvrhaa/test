import math
from typing import Any

from .config import settings


def coin_from_ticker(ticker: dict[str, Any]) -> dict[str, Any] | None:
    quotes = ticker.get("quotes")
    usd_quote = quotes.get("USD") if isinstance(quotes, dict) else None
    if not isinstance(usd_quote, dict):
        return None

    price = usd_quote.get("price")
    market_cap = usd_quote.get("market_cap")
    volume = usd_quote.get("volume_24h")
    max_supply = ticker.get("max_supply")
    total_supply = ticker.get("total_supply")
    values = (price, market_cap, volume, max_supply, total_supply)
    if any(
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or not math.isfinite(value)
        for value in values
    ):
        return None

    fdv = price * max_supply
    name = ticker.get("name")
    coin_id = ticker.get("id")
    symbol = ticker.get("symbol")
    if (
        not isinstance(name, str)
        or not name
        or not isinstance(coin_id, str)
        or not coin_id
        or not isinstance(symbol, str)
        or not symbol
        or market_cap <= 0
        or price <= 0
        or fdv >= settings.max_fdv
        or volume <= settings.min_volume_24h
        or max_supply <= 0
        or total_supply <= 0
        or max_supply != total_supply
    ):
        return None

    return {
        "id": coin_id,
        "name": name,
        "symbol": symbol,
        "market_cap": float(market_cap),
        "fdv": float(fdv),
        "volume_24h": float(volume),
        "max_supply": float(max_supply),
        "total_supply": float(total_supply),
    }
