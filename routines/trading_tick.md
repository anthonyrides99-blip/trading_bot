---
name: "Trading Bot — Market Hours Tick"
routine_id: "trig_01RC4WJ4Y5tFTPj1h1WevQpi"
cron: "0 14-20 * * 1-5"
schedule_human: "Hourly Mon–Fri 10am–4pm ET"
enabled: true
model: claude-sonnet-4-6
repo: https://github.com/anthonyrides99-blip/trading_bot
---

You are running a scheduled trading bot tick. Follow these steps exactly and report the results.

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

3. Run the trading bot single-tick:
python run_once.py

4. Report: what time it ran, whether the market was open, what decision Claude made for each ticker (buy/sell/hold + confidence), and any orders placed on the Alpaca paper account.
