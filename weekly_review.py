"""
weekly_review.py — Weekly performance review (CCR routine).

Runs Sunday evening. Fetches the past week of trades and portfolio history from Alpaca.
LLM analyzes performance and suggests watchlist adjustments. No orders placed.
"""

import sys
import os
import json
from datetime import datetime, timezone, timedelta

from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(__file__))

import config
from utils.logger import logger
import anthropic
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest, GetPortfolioHistoryRequest
from alpaca.trading.enums import QueryOrderStatus

ET = ZoneInfo("America/New_York")
_client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
_trading = TradingClient(
    api_key=config.ALPACA_API_KEY,
    secret_key=config.ALPACA_SECRET_KEY,
    paper=config.PAPER_TRADING,
)


def main() -> None:
    now = datetime.now(ET)
    week_end = now.strftime("%Y-%m-%d")
    week_start = (now - timedelta(days=7)).strftime("%Y-%m-%d")
    mode = "PAPER" if config.PAPER_TRADING else "LIVE"
    logger.info(f"Weekly review | {week_start} → {week_end} | mode={mode}")

    # Account
    account = _trading.get_account()
    equity = float(account.equity)
    logger.info(f"Current equity: ${equity:,.2f}")

    # Orders for the week
    try:
        after = datetime.now(timezone.utc) - timedelta(days=7)
        orders_req = GetOrdersRequest(
            status=QueryOrderStatus.CLOSED,
            after=after,
            limit=200,
        )
        orders = _trading.get_orders(orders_req)
        filled = [o for o in orders if str(o.status) == "filled"]
    except Exception as exc:
        logger.error(f"Failed to fetch weekly orders: {exc}")
        filled = []

    total_trades = len(filled)
    tickers_traded = list({o.symbol for o in filled})
    logger.info(f"Total trades this week: {total_trades} across {tickers_traded}")

    # Portfolio history for the week
    pnl_summary = "Portfolio history unavailable."
    week_pnl = 0.0
    try:
        hist_req = GetPortfolioHistoryRequest(period="1W", timeframe="1D")
        history = _trading.get_portfolio_history(hist_req)
        if history.equity and len(history.equity) >= 2:
            open_eq = float(history.equity[0])
            close_eq = float(history.equity[-1])
            week_pnl = close_eq - open_eq
            week_pnl_pct = (week_pnl / open_eq * 100) if open_eq else 0
            sign = "+" if week_pnl >= 0 else ""
            pnl_summary = f"Week P&L: {sign}${week_pnl:,.2f} ({sign}{week_pnl_pct:.2f}%)"
            logger.info(pnl_summary)

            daily_pnls = []
            for i in range(1, len(history.equity)):
                prev = float(history.equity[i - 1])
                curr = float(history.equity[i])
                daily_pnls.append(curr - prev)
            if daily_pnls:
                winning_days = sum(1 for p in daily_pnls if p > 0)
                logger.info(f"Winning days: {winning_days}/{len(daily_pnls)}")
    except Exception as exc:
        logger.warning(f"Portfolio history error: {exc}")

    # Ticker breakdown
    ticker_counts: dict[str, int] = {}
    for o in filled:
        ticker_counts[o.symbol] = ticker_counts.get(o.symbol, 0) + 1
    most_active = sorted(ticker_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    logger.info(f"Most active tickers: {most_active}")

    # LLM analysis
    trades_text = "\n".join(
        f"- {o.side.upper()} {float(o.filled_qty or 0):.0f}x {o.symbol} @ ${float(o.filled_avg_price or 0):.2f}"
        for o in filled[:30]
    ) or "No trades this week."

    prompt = f"""Weekly trading performance review for the week ending {week_end}.

Portfolio:
- Current equity: ${equity:,.2f}
- {pnl_summary}
- Total trades: {total_trades}
- Tickers traded: {tickers_traded}
- Most active: {most_active}
- Current watchlist: {config.WATCHLIST}

Trades (up to 30 shown):
{trades_text}

Please provide:
1. A brief performance assessment (2-3 sentences)
2. What's working well
3. What to improve
4. Watchlist suggestions: which tickers to add, remove, or keep based on activity and implied performance

Be concise and actionable."""

    try:
        response = _client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        review = response.content[0].text.strip()
        logger.info("\n--- LLM Weekly Review ---")
        for line in review.split("\n"):
            logger.info(line)
        logger.info("--- End of Review ---")
    except Exception as exc:
        logger.error(f"LLM review failed: {exc}")

    logger.info("Weekly review complete")


if __name__ == "__main__":
    main()
