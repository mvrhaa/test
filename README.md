# CoinGecko Screener API

A small FastAPI service that retrieves CoinGecko market data, applies the requested
filters, and returns matching projects.

## What was completed

The existing backend starter code was reviewed and helped along with fixes to its
CoinGecko client, module imports, pagination, filtering, and REST endpoint wiring.
Setup instructions, assumptions, and focused tests were also added.

## Setup

1. Use Python 3.11 or newer and install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Optionally set a CoinGecko API key and plan in the environment:

   ```bash
   export COINGECKO_API_KEY="your-api-key"
   export COINGECKO_PLAN="demo"  # use "pro" for a Pro API key
   ```

   The demo API is used by default. CoinGecko rate limits and endpoint availability
   depend on the API plan.

3. Start the server from this directory:

   ```bash
   uvicorn main:app --reload
   ```

## API

- `GET /coins/filtered` returns matching coins.
- `GET /coins/filtered?refresh=true` bypasses the in-memory cache.
- `GET /health` is a simple health check.

The filtered response contains `count`, `cached_age_seconds`, and `coins`.
CoinGecko request failures return HTTP 502 rather than an incomplete success
response.

## Filter and data assumptions

- Market capitalization, fully diluted valuation, and 24-hour volume come from
  `/coins/markets` in USD.
- `preview_listing` and TVL come from `/coins/{id}`. TVL is read from
  `market_data.total_value_locked`; when it is an object, its `usd` value is used.
- Max supply and total supply must both be present and exactly equal. Missing,
  non-finite, or non-numeric data is excluded.
- All thresholds are strict: market cap > 0, FDV < $100M, volume > $50K, and
  TVL > $50K.
- The service paginates the market endpoint until CoinGecko returns a partial or
  empty page. API-plan limits may restrict accessible data.
- Successful scans are cached in memory for 600 seconds by default; restarting
  the service clears the cache. `CACHE_TTL_SECONDS` and
  `DETAIL_CONCURRENCY` can be set through environment variables.

## AI workflow

- **Tool used:** Claude Code.
- **How it was used:** As a coding assistant to inspect and fix gaps in the
  existing backend, clarify CoinGecko response usage, and help add tests and
  setup documentation(README).
- **Where it helped most:** Identifying missing backend pieces and checking
  that market and coin-detail data were used for the appropriate filters.
