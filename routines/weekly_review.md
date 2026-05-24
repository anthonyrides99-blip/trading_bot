---
name: "Trading Bot — Weekly Performance Review"
routine_id: "trig_01TUeVkic1a2docVEpd9PH8F"
cron: "0 22 * * 0"
schedule_human: "6pm ET every Sunday"
enabled: true
model: claude-opus-4-7
repo: https://github.com/anthonyrides99-blip/trading_bot
---

You are running a weekly trading performance review. Follow these steps exactly and report the results.

1. Create a .env file in the current directory with the following content (exactly as shown):

ALPACA_API_KEY=${ALPACA_API_KEY}
ALPACA_SECRET_KEY=${ALPACA_SECRET_KEY}
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
PAPER_TRADING=true
WATCHLIST=AAPL,MSFT,NVDA,GOOGL,AMZN,META
MAX_POSITION_PCT=0.05
MAX_DAILY_LOSS_PCT=0.02
TICK_INTERVAL_SECONDS=300
CLICKUP_API_TOKEN=${CLICKUP_API_TOKEN}
CLICKUP_LIST_TRADES=${CLICKUP_LIST_TRADES}
CLICKUP_LIST_DAILY=${CLICKUP_LIST_DAILY}
CLICKUP_LIST_WEEKLY=${CLICKUP_LIST_WEEKLY}
CLICKUP_LIST_PREMARKET=${CLICKUP_LIST_PREMARKET}

2. Create a venv and install dependencies:
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt -q

3. Run the weekly review:
.venv/bin/python weekly_review.py

4. Report: weekly P&L, number of winning vs losing days, most active tickers, the LLM's performance assessment, and any watchlist adjustment suggestions.

Note: This routine does NOT place any orders. It is analysis and review only.
