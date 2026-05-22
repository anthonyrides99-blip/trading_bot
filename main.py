"""
main.py — Entry point for the AI trading bot.

Runs a scheduled loop every TICK_INTERVAL_SECONDS during US market hours (Mon–Fri 09:30–16:00 ET).
Each tick: fetches bars → computes indicators → gets LLM decision → executes orders.
"""

import sys
import os
from datetime import datetime, timezone

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from alpaca.data.timeframe import TimeFrame

# Add the trading_bot directory to path so submodules resolve correctly
sys.path.insert(0, os.path.dirname(__file__))

import config
from utils.logger import logger
from data import market_data, indicators
from strategy import signals, llm_analyst
from execution import broker
from risk.risk_manager import RiskManager

risk = RiskManager()
_day_initialized = False
_last_day: str | None = None


def _today_et() -> str:
    from zoneinfo import ZoneInfo
    return datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d")


def _ensure_day_reset() -> None:
    global _day_initialized, _last_day
    today = _today_et()
    if _last_day != today:
        account = broker.get_account()
        equity = float(account.equity)
        risk.reset_for_new_day(equity)
        _last_day = today
        _day_initialized = True


def trading_tick() -> None:
    logger.info("=== Trading tick started ===")

    try:
        _ensure_day_reset()
    except Exception as exc:
        logger.error(f"Day reset failed: {exc}")
        return

    if not risk.can_trade():
        return

    # Fetch account state once per tick
    try:
        account = broker.get_account()
        equity = float(account.equity)
    except Exception as exc:
        logger.error(f"Failed to fetch account: {exc}")
        return

    if not risk.check_daily_loss(equity):
        return

    positions = broker.get_positions()

    for ticker in config.WATCHLIST:
        try:
            _process_ticker(ticker, equity, positions)
        except Exception as exc:
            logger.error(f"{ticker}: unhandled error — {exc}")

    logger.info("=== Trading tick complete ===")


def _process_ticker(ticker: str, equity: float, positions: dict) -> None:
    # Fetch market data
    df = market_data.get_bars(ticker, timeframe=TimeFrame.Minute, limit=120)
    if df.empty:
        logger.warning(f"{ticker}: no bar data returned")
        return

    # Compute indicators
    ind = indicators.compute(ticker, df)
    if ind is None:
        return

    price = market_data.get_latest_price(ticker)
    news = market_data.get_news_headlines(ticker, limit=5)

    # Build signal summary
    signal_summary = signals.summarize(ind)

    # LLM decision
    has_position = ticker in positions
    decision = llm_analyst.analyze(ticker, price, signal_summary, news, has_position)

    action = decision.get("action", "hold")
    confidence = decision.get("confidence", 0.0)

    # Only act on high-confidence decisions (>= 0.65)
    if confidence < 0.65:
        logger.info(f"{ticker}: confidence {confidence:.2f} too low — holding")
        return

    if action == "buy" and not has_position:
        qty = risk.position_size(equity, price)
        if qty > 0:
            broker.place_market_order(ticker, "buy", qty)

    elif action == "sell" and has_position:
        broker.close_position(ticker)

    elif action == "sell" and not has_position:
        logger.debug(f"{ticker}: sell signal but no position — skipping")

    elif action == "buy" and has_position:
        logger.debug(f"{ticker}: buy signal but already holding — skipping")


def main() -> None:
    mode = "PAPER" if config.PAPER_TRADING else "LIVE"
    logger.info(f"Starting AI trading bot | mode={mode} | watchlist={config.WATCHLIST}")
    logger.info(f"Tick interval: {config.TICK_INTERVAL_SECONDS}s | Max position: {config.MAX_POSITION_PCT:.0%} | Daily loss limit: {config.MAX_DAILY_LOSS_PCT:.0%}")

    # Run one tick immediately on startup so we don't wait for the first scheduled fire
    trading_tick()

    scheduler = BlockingScheduler(timezone="America/New_York")

    # Market hours: Mon–Fri 09:30–16:00 ET, tick every TICK_INTERVAL_SECONDS
    interval_minutes = max(1, config.TICK_INTERVAL_SECONDS // 60)
    scheduler.add_job(
        trading_tick,
        trigger=CronTrigger(
            day_of_week="mon-fri",
            hour="9-15",
            minute=f"*/{interval_minutes}",
            second="0",
            timezone="America/New_York",
        ),
        id="trading_tick",
        name="Trading tick",
        misfire_grace_time=60,
    )

    logger.info(f"Scheduler started — running every {interval_minutes} minute(s) during market hours (ET)")

    try:
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("Shutting down — KeyboardInterrupt received")
        scheduler.shutdown(wait=False)


if __name__ == "__main__":
    main()
