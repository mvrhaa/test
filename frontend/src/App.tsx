import { useEffect, useMemo, useState } from "react";

type Coin = {
  id: string;
  symbol: string;
  name: string;
  market_cap: number;
  fdv: number;
  volume_24h: number;
  max_supply: number;
  total_supply: number;
};

type FilteredResponse = {
  count: number;
  cached_age_seconds: number;
  coins: Coin[];
};

type SortField = "market_cap" | "volume_24h";

function isCoin(value: unknown): value is Coin {
  if (typeof value !== "object" || value === null) return false;
  const coin = value as Record<string, unknown>;
  return (
    typeof coin.id === "string" &&
    typeof coin.symbol === "string" &&
    typeof coin.name === "string" &&
    typeof coin.market_cap === "number" &&
    typeof coin.fdv === "number" &&
    typeof coin.volume_24h === "number" &&
    typeof coin.max_supply === "number" &&
    typeof coin.total_supply === "number"
  );
}

function isFilteredResponse(value: unknown): value is FilteredResponse {
  if (typeof value !== "object" || value === null) return false;
  const response = value as Record<string, unknown>;
  return (
    typeof response.count === "number" &&
    typeof response.cached_age_seconds === "number" &&
    Array.isArray(response.coins) &&
    response.coins.every(isCoin)
  );
}

const fullCurrency = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});
const compactCurrency = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  notation: "compact",
  maximumFractionDigits: 2,
});

function errorMessage(status: number, detail: unknown): string {
  const detailText = typeof detail === "string" ? detail : "";
  if (/429|too many requests|rate.?limit/i.test(detailText)) {
    return "The market-data API is temporarily rate-limiting requests. Wait a moment, then try again.";
  }
  if (status === 502 || status === 503 || status === 504) {
    return "The market-data service is temporarily unavailable. Check that the backend is running, then try again.";
  }
  return `The request failed (HTTP ${status}). Try again in a moment.`;
}

function formatSupply(value: number): string {
  return new Intl.NumberFormat("en-US", {
    notation: "compact",
    maximumFractionDigits: 2,
  }).format(value);
}

function formatAge(seconds: number): string {
  if (seconds < 60) return "under a minute ago";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes} min ago`;
  const hours = Math.floor(minutes / 60);
  return `${hours} hr ${minutes % 60} min ago`;
}

function App() {
  const [coins, setCoins] = useState<Coin[]>([]);
  const [sourceCount, setSourceCount] = useState(0);
  const [loaded, setLoaded] = useState(false);
  const [lastUpdatedAt, setLastUpdatedAt] = useState<number | null>(null);
  const [now, setNow] = useState(Date.now());
  const [search, setSearch] = useState("");
  const [maxFdv, setMaxFdv] = useState("100000000");
  const [sortBy, setSortBy] = useState<SortField>("market_cap");
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [requestKey, setRequestKey] = useState(0);
  const [refresh, setRefresh] = useState(false);

  useEffect(() => {
    const interval = window.setInterval(() => setNow(Date.now()), 30_000);
    return () => window.clearInterval(interval);
  }, []);

  useEffect(() => {
    const controller = new AbortController();

    async function loadCoins() {
      setLoading(true);
      setError(null);
      const path = `/coins/filtered${refresh ? "?refresh=true" : ""}`;
      try {
        const response = await fetch(path, {
          signal: controller.signal,
        });
        let data: FilteredResponse | undefined;
        let detail: unknown;
        try {
          const payload: unknown = await response.json();
          if (typeof payload === "object" && payload !== null && "detail" in payload) {
            detail = payload.detail;
          }
          if (isFilteredResponse(payload)) data = payload;
        } catch (parseError) {
          if (!(parseError instanceof SyntaxError)) throw parseError;
        }

        if (!response.ok) {
          throw new Error(errorMessage(response.status, detail));
        }
        if (!data) {
          throw new Error("The backend returned an unexpected response. Try again.");
        }

        setCoins(data.coins);
        setSourceCount(data.count);
        setLastUpdatedAt(Date.now() - data.cached_age_seconds * 1000);
        setLoaded(true);
      } catch (reason) {
        if (reason instanceof Error && reason.name === "AbortError") return;
        if (reason instanceof TypeError) {
          setError("The backend could not be reached. Check that it is running, then try again.");
        } else {
          setError(
            reason instanceof Error
              ? reason.message
              : "The market-data service is temporarily unavailable. Try again.",
          );
        }
      } finally {
        if (!controller.signal.aborted) setLoading(false);
      }
    }

    void loadCoins();
    return () => controller.abort();
  }, [requestKey, refresh]);

  const fdvNumber = Number(maxFdv);
  const fdvIsValid =
    maxFdv.trim() === "" || (Number.isFinite(fdvNumber) && fdvNumber > 0);

  const visibleCoins = useMemo(() => {
    const query = search.trim().toLocaleLowerCase();
    const threshold = maxFdv.trim() === "" ? null : Number(maxFdv);
    return coins
      .filter((coin) => !query || coin.name.toLocaleLowerCase().includes(query))
      .filter(
        (coin) =>
          threshold === null ||
          !Number.isFinite(threshold) ||
          threshold <= 0 ||
          coin.fdv < threshold,
      )
      .sort((left, right) => right[sortBy] - left[sortBy]);
  }, [coins, maxFdv, search, sortBy]);

  const pageCount = Math.max(1, Math.ceil(visibleCoins.length / pageSize));
  const currentPage = Math.min(page, pageCount);
  const pageCoins = visibleCoins.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize,
  );
  const hasActiveFilters = search.trim() !== "" || maxFdv !== "100000000";
  const ageSeconds =
    lastUpdatedAt === null
      ? null
      : Math.max(0, Math.floor((now - lastUpdatedAt) / 1000));

  function refreshData(): void {
    setRefresh(true);
    setRequestKey((key) => key + 1);
  }

  function resetFilters(): void {
    setSearch("");
    setMaxFdv("100000000");
    setPage(1);
  }

  return (
    <div className="app-frame">
      <header className="app-header">
        <a className="wordmark" href="/" aria-label="Screener home">
          <span className="wordmark-symbol" aria-hidden="true">S</span>
          <span>Market<span className="wordmark-muted">screen</span></span>
        </a>
        <div className={`connection-state ${error ? "is-unavailable" : ""}`}>
          <span className="connection-dot" />
          <span>
            {error
              ? "CoinGecko unavailable"
              : loading
                ? "Connecting"
                : "CoinGecko"}
          </span>
        </div>
      </header>

      <main className="main-content">
        <div className="page-heading">
          <div>
            <div className="breadcrumb">MARKETS <span>/</span> SCREENER</div>
            <h1>Project screener</h1>
            <p>Screen projects by market activity, valuation, and token supply.</p>
          </div>
          <div className="update-info" aria-live="polite">
            <span className="update-label">DATA UPDATED</span>
            <span className="update-value">
              {ageSeconds === null ? "—" : formatAge(ageSeconds)}
            </span>
          </div>
        </div>

        <section className="criteria-bar" aria-label="Backend screening criteria">
          <span className="criteria-title">BASE SCREEN</span>
          <span className="criteria-item">Market cap <b>&gt; $0</b></span>
          <span className="criteria-divider" />
          <span className="criteria-item">Est. FDV <b>&lt; $100M</b></span>
          <span className="criteria-divider" />
          <span className="criteria-item">24h volume <b>&gt; $50K</b></span>
          <span className="criteria-divider" />
          <span className="criteria-item">Max supply = total supply</span>
        </section>

        <section className="results-panel" aria-label="Screened projects">
          <div className="toolbar">
            <label className="search-control">
              <SearchIcon />
              <input
                type="search"
                value={search}
                onChange={(event) => {
                  setSearch(event.target.value);
                  setPage(1);
                }}
                placeholder="Search by project name"
                aria-label="Search by project name"
              />
              {search && (
                <button
                  type="button"
                  className="clear-search"
                  onClick={() => {
                    setSearch("");
                    setPage(1);
                  }}
                  aria-label="Clear search"
                >
                  ×
                </button>
              )}
            </label>

            <label className="control-group fdv-control">
              <span>MAX FDV <span className="unit-label">USD</span></span>
              <span className={`number-control ${!fdvIsValid ? "invalid" : ""}`}>
                <span aria-hidden="true">$</span>
                <input
                  aria-label="Maximum fully diluted valuation in USD"
                  aria-invalid={!fdvIsValid}
                  type="number"
                  min="1"
                  step="1000000"
                  value={maxFdv}
                  onChange={(event) => {
                    setMaxFdv(event.target.value);
                    setPage(1);
                  }}
                />
              </span>
            </label>

            <label className="control-group sort-control">
              <span>ORDER BY</span>
              <select
                aria-label="Sort projects by"
                value={sortBy}
                onChange={(event) => {
                  setSortBy(event.target.value as SortField);
                  setPage(1);
                }}
              >
                <option value="market_cap">Market capitalization</option>
                <option value="volume_24h">24h trading volume</option>
              </select>
            </label>

            <button
              type="button"
              className="refresh-button"
              onClick={refreshData}
              disabled={loading}
            >
              <RefreshIcon />
              <span>{loading ? "Refreshing…" : "Refresh data"}</span>
            </button>
            {hasActiveFilters && (
              <button type="button" className="clear-filters" onClick={resetFilters}>
                Clear filters
              </button>
            )}
          </div>

          {!fdvIsValid && (
            <p className="validation-message" role="alert">
              Enter a maximum FDV greater than zero, or clear the field to remove this filter.
            </p>
          )}

          {error && (
            <div className="data-notice" role="status">
              <span className="notice-mark" aria-hidden="true">!</span>
              <div className="notice-copy">
                <strong>
                  {loaded
                    ? "Showing the last successful results"
                    : "Market data is unavailable"}
                </strong>
                <span>
                  {loaded
                    ? `The latest refresh failed. ${error}`
                    : error}
                </span>
              </div>
              <button type="button" onClick={refreshData} disabled={loading}>
                Try again
              </button>
            </div>
          )}

          <div className="table-heading">
            <div className="result-count" aria-live="polite">
              <strong>{loaded ? visibleCoins.length : "—"}</strong>
              <span>{visibleCoins.length === 1 ? "project" : "projects"}</span>
              {loaded && visibleCoins.length !== sourceCount && (
                <span className="of-count">of {sourceCount} screened</span>
              )}
            </div>
            <label className="page-size-control">
              <span>Rows</span>
              <select
                aria-label="Rows per page"
                value={pageSize}
                onChange={(event) => {
                  setPageSize(Number(event.target.value));
                  setPage(1);
                }}
              >
                <option value={25}>25</option>
                <option value={50}>50</option>
                <option value={100}>100</option>
              </select>
              <span>per page</span>
            </label>
          </div>

          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th className="asset-header">PROJECT</th>
                  <th className="number-header">MARKET CAP</th>
                  <th className="number-header">EST. FDV</th>
                  <th className="number-header">VOLUME (24H)</th>
                  <th className="number-header">MAX / TOTAL SUPPLY</th>
                </tr>
              </thead>
              <tbody>
                {loading && !loaded &&
                  Array.from({ length: 8 }, (_, index) => (
                    <tr className="loading-row" key={index} aria-hidden="true">
                      <td><span className="loading-line asset-loading" /></td>
                      <td><span className="loading-line value-loading" /></td>
                      <td><span className="loading-line value-loading" /></td>
                      <td><span className="loading-line value-loading" /></td>
                      <td><span className="loading-line value-loading" /></td>
                    </tr>
                  ))}
                {loaded && pageCoins.map((coin) => (
                  <tr key={coin.id}>
                    <td>
                      <div className="asset-cell">
                        <span className="asset-name">{coin.name}</span>
                        <span className="asset-symbol">{coin.symbol.toUpperCase()}</span>
                      </div>
                    </td>
                    <td className="number-cell" title={fullCurrency.format(coin.market_cap)}>
                      {compactCurrency.format(coin.market_cap)}
                    </td>
                    <td className="number-cell" title={fullCurrency.format(coin.fdv)}>
                      {compactCurrency.format(coin.fdv)}
                    </td>
                    <td className="number-cell" title={fullCurrency.format(coin.volume_24h)}>
                      {compactCurrency.format(coin.volume_24h)}
                    </td>
                    <td
                      className="number-cell"
                      title={`${coin.max_supply.toLocaleString()} / ${coin.total_supply.toLocaleString()}`}
                    >
                      {formatSupply(coin.max_supply)} / {formatSupply(coin.total_supply)}
                    </td>
                  </tr>
                ))}
                {!loading && !error && loaded && pageCoins.length === 0 && (
                  <tr>
                    <td colSpan={5}>
                      <div className="empty-results">
                        <strong>No projects match these filters</strong>
                        <span>Try a different name or increase the maximum FDV.</span>
                        {hasActiveFilters && (
                          <button type="button" onClick={resetFilters}>Clear filters</button>
                        )}
                      </div>
                    </td>
                  </tr>
                )}
                {!loading && !loaded && error && (
                  <tr>
                    <td colSpan={5}>
                      <div className="empty-results">
                        <strong>No current results to display</strong>
                        <span>Existing filters will be applied when market data is available.</span>
                      </div>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          {loaded && (
            <footer className="table-footer">
              <span>
                Showing {visibleCoins.length === 0 ? 0 : (currentPage - 1) * pageSize + 1}–{Math.min(currentPage * pageSize, visibleCoins.length)} of {visibleCoins.length}
              </span>
              {pageCount > 1 && (
                <nav className="pagination" aria-label="Project pages">
                  <button
                    type="button"
                    onClick={() => setPage((current) => Math.max(1, current - 1))}
                    disabled={currentPage === 1}
                    aria-label="Previous page"
                  >
                    <ChevronIcon direction="left" />
                  </button>
                  <span>Page {currentPage} of {pageCount}</span>
                  <button
                    type="button"
                    onClick={() => setPage((current) => Math.min(pageCount, current + 1))}
                    disabled={currentPage === pageCount}
                    aria-label="Next page"
                  >
                    <ChevronIcon direction="right" />
                  </button>
                </nav>
              )}
            </footer>
          )}
        </section>
      </main>
    </div>
  );
}

function SearchIcon() {
  return (
    <svg viewBox="0 0 20 20" fill="none" aria-hidden="true">
      <circle cx="8.8" cy="8.8" r="5.8" />
      <path d="m13.2 13.2 4 4" />
    </svg>
  );
}

function RefreshIcon() {
  return (
    <svg viewBox="0 0 20 20" fill="none" aria-hidden="true">
      <path d="M16.5 6.5v4h-4M3.5 13.5v-4h4" />
      <path d="M5.2 7.8a5.5 5.5 0 0 1 9.3-1.7l2 2.4M3.5 10.5l2 2.4a5.5 5.5 0 0 0 9.3-1.7" />
    </svg>
  );
}

function ChevronIcon({ direction }: { direction: "left" | "right" }) {
  return (
    <svg
      viewBox="0 0 16 16"
      fill="none"
      aria-hidden="true"
      className={direction === "left" ? "chevron-left" : undefined}
    >
      <path d="m6 3 5 5-5 5" />
    </svg>
  );
}

export default App;
