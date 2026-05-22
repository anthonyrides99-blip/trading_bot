"""
post_market_summary.py — End-of-day performance report (CCR routine).

Runs after market close (~5pm ET). Fetches today's trades and P&L from Alpaca.
No orders placed.
"""

import sys
import os
from datetime import datetime, date, timezone, timedelta

from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(__file__))

import config
from utils.logger import logger
from utils.clickup import create_task
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest, GetPortfolioHistoryRequest
from alpaca.trading.enums import QueryOrderStatus

ET = ZoneInfo("America/New_York")

_trading_client = TradingClient(
    api_key=config.ALPACA_API_KEY,
    secret_key=config.ALPACA_SECRET_KEY,
    paper=config.PAPER_TRADING,
)


def main() -> None:
    now = datetime.now(ET)
    today = now.strftime("%Y-%m-%d")
    mode = "PAPER" if config.PAPER_TRADING else "LIVE"
    logger.info(f"Post-market summary | {today} | mode={mode}")

    if now.weekday() >= 5:
        logger.info("Weekend — no summary needed")
        return

    # Account state
    account = _trading_client.get_account()
    equity = float(account.equity)
    cash = float(account.cash)
    logger.info(f"Account equity: ${equity:,.2f} | Cash: ${cash:,.2f}")

    # Today's filled orders
    try:
        start_of_day = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        orders_req = GetOrdersRequest(
            status=QueryOrderStatus.CLOSED,
            after=start_of_day,
            limit=50,
        )
        orders = _trading_client.get_orders(orders_req)
        filled = [o for o in orders if str(o.status) == "filled"]
    except Exception as exc:
        logger.error(f"Failed to fetch orders: {exc}")
        filled = []

    logger.info(f"Trades today: {len(filled)}")
    buys = [o for o in filled if str(o.side) == "buy"]
    sells = [o for o in filled if str(o.side) == "sell"]
    logger.info(f"  Buys: {len(buys)}  |  Sells/Closes: {len(sells)}")

    for o in filled:
        qty = float(o.filled_qty or 0)
        price = float(o.filled_avg_price or 0)
        logger.info(f"  {o.side.upper()} {qty:.0f}x {o.symbol} @ ${price:.2f}")

    # Portfolio history for today's P&L
    pnl_summary = "P&L unavailable"
    try:
        hist_req = GetPortfolioHistoryRequest(period="1D", timeframe="1H")
        history = _trading_client.get_portfolio_history(hist_req)
        if history.equity and len(history.equity) >= 2:
            open_eq = float(history.equity[0])
            close_eq = float(history.equity[-1])
            pnl = close_eq - open_eq
            pnl_pct = (pnl / open_eq * 100) if open_eq else 0
            sign = "+" if pnl >= 0 else ""
            pnl_summary = f"Today's P&L: {sign}${pnl:,.2f} ({sign}{pnl_pct:.2f}%)"
            logger.info(pnl_summary)
        else:
            logger.info("P&L: portfolio history unavailable")
    except Exception as exc:
        logger.warning(f"Portfolio history error: {exc}")

    # Open positions (held overnight)
    try:
        positions = _trading_client.get_all_positions()
        if positions:
            logger.info(f"Positions held overnight ({len(positions)}):")
            for p in positions:
                unreal = float(p.unrealized_pl or 0)
                sign = "+" if unreal >= 0 else ""
                logger.info(f"  {p.symbol}: {float(p.qty):.0f} shares @ avg ${float(p.avg_entry_price):.2f} | unrealized {sign}${unreal:.2f}")
        else:
            logger.info("No positions held overnight — flat into close")
    except Exception as exc:
        logger.warning(f"Positions error: {exc}")

    # Build ClickUp task description from everything logged
    trades_detail = "\n".join(
        f"  {o.side.upper()} {float(o.filled_qty or 0):.0f}x {o.symbol} @ ${float(o.filled_avg_price or 0):.2f}"
        for o in filled
    ) or "No trades today."

    try:
        overnight = _trading_client.get_all_positions()
        overnight_detail = "\n".join(
            f"  {p.symbol}: {float(p.qty):.0f} shares, unrealized ${float(p.unrealized_pl or 0):+.2f}"
            for p in overnight
        ) or "None — flat."
    except Exception:
        overnight_detail = "Could not fetch."

    pnl_line = pnl_summary

    create_task(
        config.CLICKUP_API_TOKEN,
        config.CLICKUP_LIST_DAILY,
        name=f"Daily Summary — {today} | {pnl_line}",
        description=(
            f"Date: {today}\nMode: {'PAPER' if config.PAPER_TRADING else 'LIVE'}\n\n"
            f"Account equity: ${equity:,.2f}\n"
            f"{pnl_line}\n\n"
            f"Trades ({len(filled)}):\n{trades_detail}\n\n"
            f"Overnight positions:\n{overnight_detail}"
        ),
    )
    logger.info("Post-market summary complete")


if __name__ == "__main__":
    main()
