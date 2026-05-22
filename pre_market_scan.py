"""
pre_market_scan.py — Pre-market watchlist scoring (CCR routine).

Runs before market open (~9am ET). Scores each ticker as strong_buy / watch / avoid
using prior-day technical data + overnight news. No orders placed.
"""

import sys
import os
import json
from datetime import datetime, timezone

from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(__file__))

import config
from utils.logger import logger
from utils.clickup import create_task
from data import market_data, indicators
from strategy import signals
import anthropic
from alpaca.data.timeframe import TimeFrame

ET = ZoneInfo("America/New_York")
_client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

_SYSTEM_PROMPT = """You are a pre-market stock analyst. Your job is to score each stock for the upcoming trading day before the market opens.

For each ticker you receive: technical signals from the prior day's close and recent news headlines.

Score each ticker with one of:
- strong_buy: Multiple bullish signals align, good risk/reward for today
- watch: Mixed signals; wait for confirmation after open before trading
- avoid: Bearish signals, negative news, or high uncertainty — skip today

Respond ONLY with valid JSON in this exact format (no markdown):
{"ticker": "AAPL", "score": "strong_buy"|"watch"|"avoid", "reason": "<one sentence max>"}"""


def score_ticker(ticker: str) -> dict:
    try:
        df = market_data.get_bars(ticker, timeframe=TimeFrame.Day, limit=60)
        if df.empty or len(df) < 20:
            return {"ticker": ticker, "score": "watch", "reason": "Insufficient data for analysis"}

        ind = indicators.compute(ticker, df)
        if ind is None:
            return {"ticker": ticker, "score": "watch", "reason": "Could not compute indicators"}

        signal_summary = signals.summarize(ind)
        news = market_data.get_news_headlines(ticker, limit=5)
        news_text = "\n".join(f"- {h}" for h in news) if news else "No recent news."

        price = ind.current_price

        user_msg = f"""Ticker: {ticker}
Prior close: ${price:.2f}
Date: {datetime.now(ET).strftime('%A %Y-%m-%d')} (pre-market analysis)

Technical signals (daily timeframe):
{signal_summary}

Recent news:
{news_text}

Score this ticker for today's trading session."""

        response = _client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=128,
            system=[{"type": "text", "text": _SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": user_msg}],
        )
        raw = response.content[0].text.strip()
        result = json.loads(raw)
        return result
    except Exception as exc:
        logger.error(f"{ticker}: scan error — {exc}")
        return {"ticker": ticker, "score": "watch", "reason": f"Error: {exc}"}


def main() -> None:
    now = datetime.now(ET)
    logger.info(f"Pre-market scan | {now.strftime('%Y-%m-%d %H:%M ET')} | watchlist={config.WATCHLIST}")

    if now.weekday() >= 5:
        logger.info("Weekend — no scan needed")
        return

    results = []
    for ticker in config.WATCHLIST:
        result = score_ticker(ticker)
        results.append(result)
        icon = {"strong_buy": "BUY", "watch": "WATCH", "avoid": "AVOID"}.get(result["score"], "?")
        logger.info(f"  [{icon}] {result['ticker']}: {result['reason']}")

    strong_buys = [r["ticker"] for r in results if r["score"] == "strong_buy"]
    watches = [r["ticker"] for r in results if r["score"] == "watch"]
    avoids = [r["ticker"] for r in results if r["score"] == "avoid"]

    logger.info("--- Today's Game Plan ---")
    logger.info(f"  STRONG BUY : {strong_buys or 'none'}")
    logger.info(f"  WATCH      : {watches or 'none'}")
    logger.info(f"  AVOID      : {avoids or 'none'}")

    details = "\n".join(
        f"[{r['score'].upper()}] {r['ticker']}: {r['reason']}" for r in results
    )
    create_task(
        config.CLICKUP_API_TOKEN,
        config.CLICKUP_LIST_PREMARKET,
        name=f"Pre-Market Scan — {now.strftime('%Y-%m-%d')}",
        description=(
            f"Date: {now.strftime('%Y-%m-%d %H:%M ET')}\n\n"
            f"STRONG BUY: {strong_buys or 'none'}\n"
            f"WATCH: {watches or 'none'}\n"
            f"AVOID: {avoids or 'none'}\n\n"
            f"Ticker Details:\n{details}"
        ),
    )
    logger.info("Pre-market scan complete")


if __name__ == "__main__":
    main()
