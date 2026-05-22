---
name: "Trading Bot — Post-Market Summary"
routine_id: "trig_012ERzvaCtxCDLBR47vhtGsc"
cron: "0 21 * * 1-5"
schedule_human: "5pm ET Mon–Fri (after market close)"
enabled: true
model: claude-opus-4-7
repo: https://github.com/anthonyrides99-blip/trading_bot
---

You are running an end-of-day performance summary after the US stock market has closed. Follow these steps exactly and report the results.

1. Create a .env file in the current directory with the following content (exactly as shown):

ALPACA_API_KEY=${ALPACA_API_KEY}
ALPACA_SECRET_KEY=${ALPACA_SECRET_KEY}
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
PAPER_TRADING=true
WATCHLIST=AAPL,MSFT,NVDA,GOOGL,AMZN
MAX_POSITION_PCT=0.05
MAX_DAILY_LOSS_PCT=0.02
TICK_INTERVAL_SECONDS=300
CLICKUP_API_TOKEN=${CLICKUP_API_TOKEN}
CLICKUP_LIST_TRADES=${CLICKUP_LIST_TRADES}
CLICKUP_LIST_DAILY=${CLICKUP_LIST_DAILY}
CLICKUP_LIST_WEEKLY=${CLICKUP_LIST_WEEKLY}
CLICKUP_LIST_PREMARKET=${CLICKUP_LIST_PREMARKET}

2. Install dependencies:
pip install -r requirements.txt -q

3. Run the post-market summary:
python post_market_summary.py

4. Report: number of trades today, today's P&L (dollar and percent), any positions held overnight, and the biggest winner/loser of the day.

Note: This routine does NOT place any orders. It is reporting only.
