"""HTTP routes mapping cleanly onto Nepse client methods.

Handlers are intentionally thin: each delegates to ``call_nepse`` which runs
the blocking client call under a shared lock and normalises errors. They are
declared as synchronous ``def`` so Starlette runs them in its thread pool
rather than blocking the event loop on ``requests`` I/O.
"""

from typing import Optional

from fastapi import APIRouter, Query

from .deps import call_nepse

router = APIRouter()


# --- Market & indices -------------------------------------------------------

@router.get("/market/status", tags=["market"])
def market_status():
    """Market open/close status."""
    return call_nepse("get_market_status")


@router.get("/market/summary", tags=["market"])
def market_summary():
    """Overall market summary (turnover, transactions, total trades)."""
    return call_nepse("get_market_summary")


@router.get("/index/nepse", tags=["index"])
def nepse_index():
    """Main NEPSE index."""
    return call_nepse("get_nepse_index")


@router.get("/index/sub", tags=["index"])
def sub_indices():
    """All sector sub-indices with OHLCV data."""
    return call_nepse("get_sub_indices")


@router.get("/index/all", tags=["index"])
def all_indices():
    """All market indices in one call."""
    return call_nepse("get_all_indices")


# --- Stocks & trading -------------------------------------------------------

@router.get("/stocks", tags=["stocks"])
def stocks(date: Optional[str] = Query(None, description="Business date YYYY-MM-DD")):
    """Live (or historical, when ``date`` is given) prices for all stocks."""
    return call_nepse("get_stocks", date=date)


@router.get("/stocks/today-price", tags=["stocks"])
def today_price(
    size: int = Query(500, ge=1, le=2000),
    date: Optional[str] = Query(None, description="Business date YYYY-MM-DD"),
):
    """Today's price (OHLCV) via the POST today-price endpoint."""
    return call_nepse("get_today_price", size=size, date=date)


@router.get("/price-volume", tags=["stocks"])
def price_volume():
    """Daily price/volume stats for all securities."""
    return call_nepse("get_price_volume")


@router.get("/daily-trade", tags=["stocks"])
def daily_trade(
    date: str = Query(..., description="Business date YYYY-MM-DD"),
    size: int = Query(500, ge=1, le=2000),
):
    """Daily trade statistics for a specific business date."""
    return call_nepse("get_daily_trade", date, size=size)


@router.get("/marketcap", tags=["market"])
def marketcap(date: Optional[str] = Query(None, description="Business date YYYY-MM-DD")):
    """Market capitalisation, optionally for a specific business date."""
    return call_nepse("get_marcapbydate", date=date)


# --- Top performers ---------------------------------------------------------

@router.get("/top/gainers", tags=["top"])
def top_gainers(limit: Optional[int] = Query(None, ge=1)):
    """Top gaining stocks."""
    return call_nepse("get_top_gainers", limit=limit)


@router.get("/top/losers", tags=["top"])
def top_losers(limit: Optional[int] = Query(None, ge=1)):
    """Top losing stocks."""
    return call_nepse("get_top_losers", limit=limit)


@router.get("/top/turnover", tags=["top"])
def top_turnover():
    """Top 10 stocks by turnover."""
    return call_nepse("get_top_turnover")


@router.get("/top/trade", tags=["top"])
def top_trade():
    """Top 10 stocks by number of trades."""
    return call_nepse("get_top_trade")


@router.get("/top/transaction", tags=["top"])
def top_transaction():
    """Top 10 stocks by number of transactions."""
    return call_nepse("get_top_transaction")


# --- Per-security -----------------------------------------------------------

@router.get("/securities/{symbol}/depth", tags=["securities"])
def market_depth(symbol: str):
    """Live buy/sell order book for a stock symbol."""
    return call_nepse("get_market_depth", symbol)


@router.get("/securities/{symbol}/floorsheet", tags=["securities"])
def security_floorsheet(
    symbol: str,
    date: Optional[str] = Query(None, description="Business date YYYY-MM-DD"),
    size: int = Query(500, ge=1, le=2000),
    limit: Optional[int] = Query(None, description="Max pages to fetch (0 = all)"),
    page: int = Query(0, ge=0),
):
    """Floorsheet transactions for a specific symbol."""
    return call_nepse(
        "get_floorsheet", symbol=symbol, date=date, size=size, limit=limit, page=page
    )


@router.get("/securities/{symbol}/dividends", tags=["securities"])
def dividends(symbol: str):
    """Dividend history for a company."""
    return call_nepse("get_dividends", symbol)


@router.get("/securities/{symbol}/agm", tags=["securities"])
def agm(symbol: str):
    """AGM information for a company."""
    return call_nepse("get_agm", symbol)


@router.get("/securities/{symbol}/news", tags=["securities"])
def company_news(symbol: str):
    """News for a specific company."""
    return call_nepse("get_company_news", symbol)


@router.get("/securities/{security_id}/details", tags=["securities"])
def security_details(security_id: int):
    """Detailed info for a specific security by numeric ID."""
    return call_nepse("get_security_details", security_id)


@router.get("/securities/{security_id}/chart", tags=["securities"])
def historical_chart(
    security_id: int,
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
):
    """Historical OHLCV chart data (use ID 58 for the NEPSE index)."""
    return call_nepse(
        "get_historical_chart", security_id, start_date=start_date, end_date=end_date
    )


@router.get("/floorsheet", tags=["stocks"])
def market_floorsheet(
    date: Optional[str] = Query(None, description="Business date YYYY-MM-DD"),
    size: int = Query(500, ge=1, le=2000),
    limit: Optional[int] = Query(None, description="Max pages to fetch (default 1)"),
    page: int = Query(0, ge=0),
):
    """Whole-market floorsheet (latest trading session)."""
    return call_nepse(
        "get_floorsheet", date=date, size=size, limit=limit, page=page
    )


# --- Metadata & news --------------------------------------------------------

@router.get("/companies", tags=["metadata"])
def companies():
    """All listed companies."""
    return call_nepse("get_company_list")


@router.get("/securities", tags=["metadata"])
def securities():
    """All non-delisted securities."""
    return call_nepse("get_security_list")


@router.get("/promoters", tags=["metadata"])
def promoters():
    """Complete promoter securities list."""
    return call_nepse("get_promoter_list")


@router.get("/sectors", tags=["metadata"])
def sectors():
    """All market sectors."""
    return call_nepse("get_sector_list")


@router.get("/holidays", tags=["metadata"])
def holidays(year: int = Query(2026, ge=2000, le=2100)):
    """Market holidays for a given year."""
    return call_nepse("get_holiday_list", year=year)


@router.get("/news/alerts", tags=["news"])
def news_alerts():
    """General market news and alerts."""
    return call_nepse("get_news_alerts")


@router.get("/news/press-releases", tags=["news"])
def press_releases():
    """Official NEPSE press releases."""
    return call_nepse("get_press_releases")


# --- Admin ------------------------------------------------------------------

@router.post("/admin/refresh-token", tags=["admin"])
def refresh_token():
    """Manually refresh the authentication token."""
    return call_nepse("refresh_auth_token")


@router.post("/admin/clear-cache", tags=["admin"])
def clear_cache():
    """Clear the client's cached responses."""
    call_nepse("clear_cache")
    return {"status": "cache cleared"}
