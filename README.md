# Crypto Project Screener

This repository was already in progress; I helped fix and connect its backend
and frontend to meet the screener requirements.

This repository has two packages:

- [`backend/`](./backend/) — Python API that loads public market data from
  CoinPaprika and applies the available screener filters.
- [`frontend/`](./frontend/) — React UI that talks only to the backend.

## Run

From the repository root, start the backend:

```bash
python -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload
```

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend proxies API requests to `http://127.0.0.1:8000`. The backend reads
settings from the root `.env` file. It uses CoinPaprika's public ticker API and
does not require an API key.

## Data notes

The frontend is branded as a CoinGecko screener, while the backend uses
CoinPaprika to provide live data without a key. It filters market cap above $0,
estimated FDV below $100M (USD price × max supply), 24-hour volume above $50K,
and exact equality of available max and total supply. The public ticker API
does not provide CoinGecko's `preview_listing` or TVL fields, so those two
filters cannot be applied. Results cover the active assets returned by that API,
not every listed cryptocurrency.

The backend caches successful results for 10 minutes by default. Refresh in the
UI bypasses the cache. Tests can be run with:

```bash
python -m unittest discover -s backend/tests -v
```
