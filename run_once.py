"""
run_once.py — Single-tick entry point for CCR (Claude Code Routines).

Runs one full trading pass: fetch → indicators → LLM decision → execute.
Daily loss is computed statelessly from Alpaca's portfolio history API.
No scheduler — CCR fires this on its own cron schedule.
"""

import sys
import os
import math
from datetime import datetime, timezone, timedelta

from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(__file__))

import config
from utils.logger import logger
from utils.clickup import create_task
from data import market_data, indicators
from strategy import signals, llm_analyst
from execution import broker

ET = ZoneInfo("America/New_York")


def is_market_hours() -> bool:
    now = datetime.now(ET)
    if now.weekday() >= 5:
        return False
    market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
    return market_open <= now <= market_close


def get_today_open_equity() -> float | None:
    """Fetch start-of-day equity from Alpaca portfolio history."""
    try:
        from alpaca.trading.client import TradingClient
        from alpaca.trading.requests import GetPortfolioHistoryRequest

        client = TradingClient(
            api_key=config.ALPACA_API_KEY,
            secret_key=config.ALPACA_SECRET_KEY,
            paper=config.PAPER_TRADING,
        )
        request = GetPortfolioHistoryRequest(period="1D", timeframe="1H")
        history = client.get_portfolio_history(request)
        if history.equity and len(history.equity) > 0:
            return float(history.equity[0])
    except Exception as exc:
        logger.warning(f"Could not fetch portfolio history: {exc}")
    return None


def is_daily_loss_exceeded(current_equity: float) -> bool:
    open_equity = get_today_open_equity()
    if open_equity is None or open_equity == 0:
        return False
    loss_pct = (open_equity - current_equity) / open_equity
    if loss_pct >= config.MAX_DAILY_LOSS_PCT:
        logger.warning(
            f"Daily loss limit hit: {loss_pct:.2%} >= {config.MAX_DAILY_LOSS_PCT:.2%} — skipping all trades"
        )
        return True
    logger.info(f"Daily P&L: {-loss_pct:.2%} (limit: -{config.MAX_DAILY_LOSS_PCT:.2%})")
    return False


def position_size(equity: float, price: float) -> int:
    if price <= 0:
        return 0
    return math.floor((equity * config.MAX_POSITION_PCT) / price)


def main() -> None:
    mode = "PAPER" if config.PAPER_TRADING else "LIVE"
    logger.info(f"CCR single-tick run | mode={mode} | {datetime.now(ET).strftime('%Y-%m-%d %H:%M ET')}")
    logger.info(f"Watchlist: {config.WATCHLIST}")

    if not is_market_hours():
        logger.info("Outside market hours — no trades placed")
        return

    try:
        account = broker.get_account()
        equity = float(account.equity)
        logger.info(f"Account equity: ${equity:,.2f}")
    except Exception as exc:
        logger.error(f"Failed to fetch account: {exc}")
        return

    if is_daily_loss_exceeded(equity):
        return

    positions = broker.get_positions()
    logger.info(f"Open positions: {list(positions.keys()) or 'none'}")

    from alpaca.data.timeframe import TimeFrame

    for ticker in config.WATCHLIST:
        try:
            logger.info(f"--- {ticker} ---")
            df = market_data.get_bars(ticker, timeframe=TimeFrame.Minute, limit=120)
            if df.empty:
                logger.warning(f"{ticker}: no data")
                continue

            ind = indicators.compute(ticker, df)
            if ind is None:
                continue

            price = market_data.get_latest_price(ticker)
            news = market_data.get_news_headlines(ticker, limit=5)
            signal_summary = signals.summarize(ind)

            has_position = ticker in positions
            decision = llm_analyst.analyze(ticker, price, signal_summary, news, has_position)

            action = decision.get("action", "hold")
            confidence = decision.get("confidence", 0.0)

            if confidence < 0.65:
                logger.info(f"{ticker}: confidence {confidence:.2f} < 0.65 — hold")
                continue

            reason = decision.get("reason", "")
            mode_tag = "PAPER" if config.PAPER_TRADING else "LIVE"
            timestamp = datetime.now(ET).strftime("%Y-%m-%d %H:%M ET")

            if action == "buy" and not has_position:
                qty = position_size(equity, price)
                if qty > 0:
                    success = broker.place_market_order(ticker, "buy", qty)
                    if success:
                        create_task(
                            config.CLICKUP_API_TOKEN,
                            config.CLICKUP_LIST_TRADES,
                            name=f"BUY {qty}x {ticker} @ ${price:.2f} [{mode_tag}]",
                            description=(
                                f"Ticker: {ticker}\n"
                                f"Side: BUY\n"
                                f"Qty: {qty} shares\n"
                                f"Price: ${price:.2f}\n"
                                f"Confidence: {confidence:.0%}\n"
                                f"Reason: {reason}\n\n"
                                f"Technical Signals:\n{signal_summary}\n\n"
                                f"Time: {timestamp}\nMode: {mode_tag}"
                            ),
                            priority=2,
                        )
            elif action == "sell" and has_position:
                success = broker.close_position(ticker)
                if success:
                    create_task(
                        config.CLICKUP_API_TOKEN,
                        config.CLICKUP_LIST_TRADES,
                        name=f"SELL {ticker} (close position) [{mode_tag}]",
                        description=(
                            f"Ticker: {ticker}\n"
                            f"Side: SELL (close)\n"
                            f"Price: ${price:.2f}\n"
                            f"Confidence: {confidence:.0%}\n"
                            f"Reason: {reason}\n\n"
                            f"Technical Signals:\n{signal_summary}\n\n"
                            f"Time: {timestamp}\nMode: {mode_tag}"
                        ),
                        priority=2,
                    )
            else:
                logger.info(f"{ticker}: {action} — no action needed")

        except Exception as exc:
            logger.error(f"{ticker}: error — {exc}")

    logger.info("CCR tick complete")


if __name__ == "__main__":
    main()
