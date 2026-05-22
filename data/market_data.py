from datetime import datetime, timedelta, timezone

import pandas as pd
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, StockLatestQuoteRequest, StockNewsRequest
from alpaca.data.timeframe import TimeFrame

import config
from utils.logger import logger


_client = StockHistoricalDataClient(config.ALPACA_API_KEY, config.ALPACA_SECRET_KEY)


def get_bars(ticker: str, timeframe: TimeFrame = TimeFrame.Minute, limit: int = 100) -> pd.DataFrame:
    """Fetch OHLCV bars for a ticker. Returns a DataFrame indexed by timestamp."""
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=5)  # enough history for all indicators

    request = StockBarsRequest(
        symbol_or_symbols=ticker,
        timeframe=timeframe,
        start=start,
        end=end,
        limit=limit,
    )
    bars = _client.get_stock_bars(request)
    df = bars.df

    if isinstance(df.index, pd.MultiIndex):
        df = df.xs(ticker, level="symbol")

    df = df.sort_index()
    logger.debug(f"{ticker}: fetched {len(df)} bars")
    return df


def get_latest_price(ticker: str) -> float:
    """Return the latest ask price for a ticker."""
    request = StockLatestQuoteRequest(symbol_or_symbols=ticker)
    quote = _client.get_stock_latest_quote(request)
    return float(quote[ticker].ask_price or quote[ticker].bid_price)


def get_news_headlines(ticker: str, limit: int = 5) -> list[str]:
    """Return recent news headlines for a ticker."""
    try:
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=2)
        request = StockNewsRequest(
            symbols=[ticker],
            start=start,
            end=end,
            limit=limit,
        )
        news = _client.get_stock_news(request)
        return [article.headline for article in news]
    except Exception as exc:
        logger.warning(f"{ticker}: failed to fetch news — {exc}")
        return []
