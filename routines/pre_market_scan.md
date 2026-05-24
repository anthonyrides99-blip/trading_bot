---
name: "Trading Bot — Pre-Market Scan"
routine_id: "trig_01DWCtSrSSCDsvNykrsoMJ1x"
cron: "0 13 * * 1-5"
schedule_human: "9am ET Mon–Fri (before market open)"
enabled: true
model: claude-opus-4-7
repo: https://github.com/anthonyrides99-blip/trading_bot
---

You are running a pre-market watchlist scan before the US stock market opens. Follow these steps exactly and report the results.

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

3. Run the pre-market scan:
.venv/bin/python pre_market_scan.py

4. Report: the score (strong_buy / watch / avoid) and one-line reason for each ticker, and a summary of today's game plan.

Note: This routine does NOT place any orders. It is analysis only.
