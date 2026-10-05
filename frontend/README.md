# Frontend

React and Vite user interface for the crypto project screener.

## Run

Start the Python backend first, then run from this directory:

```bash
npm install
npm run dev
```

Open the local URL printed by Vite. The dev server proxies `/coins` requests to
`http://127.0.0.1:8000` by default. Set `BACKEND_URL` if the API is running
elsewhere:

```bash
BACKEND_URL=http://localhost:9000 npm run dev
```

## Features

- Displays project data from the backend's `GET /coins/filtered` endpoint.
- Searches project names with partial, case-insensitive matches.
- Filters using a user-defined maximum FDV.
- Sorts by market capitalization or 24-hour trading volume.
- Paginates the backend result set locally, with 25, 50, or 100 rows per page.
- Provides a manual refresh that bypasses the backend cache.

The browser calls only the backend. The page is branded as a CoinGecko screener;
the backend currently returns public CoinPaprika market data. FDV is estimated
by the backend as USD price multiplied by max supply. TVL and preview-listing
filters are not available from that feed.
