# Backend

Small FastAPI service using CoinPaprika's public ticker API.

## Run

From the repository root:

```bash
python -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload
```

The root `.env` file contains the API base URL and filter/cache settings. The
default URL is `https://api.coinpaprika.com/v1`; no API key is required.

## Endpoints

- `GET /coins/filtered` returns projects from CoinPaprika that pass the filters.
- `GET /coins/filtered?refresh=true` fetches fresh data instead of using cache.
- `GET /health` is a health check.

Successful results are cached for 600 seconds by default. Each refresh fetches
the public ticker list once, then filters it locally.

## Filters and assumptions

- Market cap and 24h volume are USD values from the ticker response.
- FDV is estimated as USD price × max supply. Projects without finite market
  values, price, or supply data are excluded.
- Market cap must be above $0, estimated FDV below $100M, and 24h volume above
  $50K. Max supply and total supply must be available and exactly equal.
- CoinPaprika does not return CoinGecko's `preview_listing` or TVL fields in
  its public ticker response, so those two original filters are not applied.
- Thresholds and cache duration are configurable in `.env`.

## Tests

```bash
python -m unittest discover -s backend/tests -v
```
