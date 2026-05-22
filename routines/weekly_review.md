---
name: "Trading Bot — Weekly Performance Review"
routine_id: ""
cron: "0 22 * * 0"
schedule_human: "6pm ET every Sunday"
enabled: true
model: claude-sonnet-4-6
repo: https://github.com/anthonyrides99-blip/trading_bot
---

You are running a weekly trading performance review. Follow these steps exactly and report the results.

1. Create a .env file in the current directory with the following content (exactly as shown):

ALPACA_API_KEY=${ALPACA_API_KEY}
ALPACA_SECRET_KEY=${ALPACA_SECRET_KEY}
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
PAPER_TRADING=true
WATCHLIST=AAPL,MSFT,NVDA,GOOGL,AMZN
MAX_POSITION_PCT=0.05
MAX_DAILY_LOSS_PCT=0.02
TICK_INTERVAL_SECONDS=300

2. Install dependencies:
pip install -r requirements.txt -q

3. Run the weekly review:
python weekly_review.py

4. Report: weekly P&L, number of winning vs losing days, most active tickers, the LLM's performance assessment, and any watchlist adjustment suggestions.

Note: This routine does NOT place any orders. It is analysis and review only.
