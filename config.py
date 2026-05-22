import os
from dotenv import load_dotenv

load_dotenv()


def _require(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(f"Missing required environment variable: {key}")
    return value


ALPACA_API_KEY = _require("ALPACA_API_KEY")
ALPACA_SECRET_KEY = _require("ALPACA_SECRET_KEY")
ANTHROPIC_API_KEY = _require("ANTHROPIC_API_KEY")

PAPER_TRADING: bool = os.getenv("PAPER_TRADING", "true").lower() == "true"

WATCHLIST: list[str] = [
    t.strip().upper()
    for t in os.getenv("WATCHLIST", "AAPL,MSFT,NVDA").split(",")
    if t.strip()
]

MAX_POSITION_PCT: float = float(os.getenv("MAX_POSITION_PCT", "0.05"))
MAX_DAILY_LOSS_PCT: float = float(os.getenv("MAX_DAILY_LOSS_PCT", "0.02"))
TICK_INTERVAL_SECONDS: int = int(os.getenv("TICK_INTERVAL_SECONDS", "300"))

ALPACA_BASE_URL = (
    "https://paper-api.alpaca.markets"
    if PAPER_TRADING
    else "https://api.alpaca.markets"
)
ALPACA_DATA_URL = "https://data.alpaca.markets"
