from datetime import datetime, timedelta, timezone

import pandas as pd
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, StockLatestQuoteRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.enums import DataFeed

import config
from utils.logger import logger


_client = StockHistoricalDataClient(config.ALPACA_API_KEY, config.ALPACA_SECRET_KEY)

# News client — alpaca-py 0.43+ moved news to a separate client
try:
    from alpaca.data.historical.news import NewsClient
    from alpaca.data.requests import NewsRequest
    _news_client = NewsClient(config.ALPACA_API_KEY, config.ALPACA_SECRET_KEY)
    _NEWS_AVAILABLE = True
except ImportError:
    _NEWS_AVAILABLE = False


def get_bars(ticker: str, timeframe: TimeFrame = TimeFrame.Minute, limit: int = 100) -> pd.DataFrame:
    """Fetch OHLCV bars for a ticker. Returns a DataFrame indexed by timestamp."""
    end = datetime.now(timezone.utc)
    # Use 90 calendar days for daily bars (covers ~60 trading days for indicators)
    # Use 7 days for intraday bars (enough for 120 minute bars)
    if str(timeframe) == str(TimeFrame.Day):
        start = end - timedelta(days=90)
    else:
        start = end - timedelta(days=7)

    kwargs = dict(symbol_or_symbols=ticker, timeframe=timeframe, start=start, end=end, limit=limit, feed=DataFeed.IEX)

    request = StockBarsRequest(**kwargs)
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
    if not _NEWS_AVAILABLE:
        return []
    try:
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=2)
        request = NewsRequest(
            symbols=ticker,
            start=start,
            end=end,
            limit=limit,
        )
        news = _news_client.get_news(request)
        articles = getattr(news, "news", news)
        headlines = []
        for item in articles:
            # alpaca-py may yield (symbol, article) tuples or bare article objects
            article = item[-1] if isinstance(item, tuple) else item
            h = getattr(article, "headline", None)
            if h:
                headlines.append(h)
        return headlines[:limit]
    except Exception as exc:
        logger.warning(f"{ticker}: failed to fetch news — {exc}")
        return []
