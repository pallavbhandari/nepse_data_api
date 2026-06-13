# Changelog

All notable changes to **nepse-data-api** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.0.0.4] - 2026-06-13

### Fixed
- `get_security_details(security_id)` returned an empty `{}` because the GET
  form of `/api/nots/security/{id}` is no longer accepted by NEPSE. It now
  POSTs with the computed payload `id` (the same scheme used by today-price /
  floorsheet), with a GET fallback for compatibility.

---

## [1.0.0.3] - 2026-06-13

### Added
- Automatic token freshness on every API call. `_get_auth_headers()` now
  refreshes a stale access token before each request via the lightweight
  refresh-token endpoint, falling back to a full re-authentication when the
  refresh token itself is stale or the refresh fails. Configurable through new
  `Nepse(token_validity=45, refresh_validity=600)` parameters (set
  `token_validity=0` to force a refresh ahead of every request).

---

## [1.0.0.2] - 2026-04-27

### Added
- `get_marcapbydate(date=None)` — Fetch market capitalization data (total, sensitive, float, sensitive float) from `/api/nots/nepse-data/marcapbydate/`. Supports optional `date` query parameter (YYYY-MM-DD) to retrieve historical market cap for a specific business date. Results cached for 1 hour.

---

## [1.0.0.1] - Initial Release

### Added
- `get_market_status()` — Market open/close status
- `get_market_summary()` — Overall market summary (turnover, transactions, total trades)
- `get_nepse_index()` — Main NEPSE index data
- `get_sub_indices()` — All sector sub-indices with OHLCV data
- `get_stocks(date=None)` — Live or historical stock prices for all listed companies
- `get_today_price(size, date)` — Today's price with OHLCV via POST endpoint
- `get_top_gainers(limit)` — Top gaining stocks
- `get_top_losers(limit)` — Top losing stocks
- `get_top_turnover()` — Top 10 stocks by turnover
- `get_top_trade()` — Top 10 stocks by number of trades
- `get_top_transaction()` — Top 10 stocks by number of transactions
- `get_market_depth(symbol)` — Live buy/sell order book for a specific stock
- `get_floorsheet(symbol, date, size, limit, page)` — Transaction floorsheet data with full pagination support
- `get_daily_trade(date, size)` — Daily trade statistics for a specific business date
- `get_price_volume()` — Daily price/volume stats for all securities
- `get_company_list()` — All listed companies
- `get_security_list()` — All non-delisted securities
- `get_security_details(security_id)` — Detailed info for a specific security
- `get_historical_chart(security_id, start_date, end_date)` — Historical OHLCV chart data
- `get_promoter_list()` — Complete promoter securities list with pagination
- `get_holiday_list(year)` — Market holidays for a given year
- `get_sector_list()` — All market sectors
- `get_all_indices()` — All market indices in one call
- `get_news_alerts()` — General market news and alerts
- `get_company_news(symbol)` — News for a specific company
- `get_press_releases()` — Official NEPSE press releases
- `get_dividends(symbol)` — Dividend history for a company
- `get_agm(symbol)` — AGM information for a company
- `refresh_auth_token()` — Manual authentication token refresh
- WASM-based token authentication (`NepseTokenParser`)
- Built-in `CacheManager` with configurable TTL
- Full `AsyncNepse` class for async/await support
