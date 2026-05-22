from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

import config
from utils.logger import logger

_client = TradingClient(
    api_key=config.ALPACA_API_KEY,
    secret_key=config.ALPACA_SECRET_KEY,
    paper=config.PAPER_TRADING,
)


def get_account():
    """Return the Alpaca account object."""
    return _client.get_account()


def get_positions() -> dict[str, float]:
    """Return {ticker: qty} for all open positions."""
    positions = _client.get_all_positions()
    return {p.symbol: float(p.qty) for p in positions}


def place_market_order(ticker: str, side: str, qty: int) -> bool:
    """Place a market order. side='buy' or 'sell'. Returns True on success."""
    if qty <= 0:
        logger.warning(f"{ticker}: skipping order — qty={qty}")
        return False

    order_side = OrderSide.BUY if side == "buy" else OrderSide.SELL
    request = MarketOrderRequest(
        symbol=ticker,
        qty=qty,
        side=order_side,
        time_in_force=TimeInForce.DAY,
    )
    try:
        order = _client.submit_order(request)
        mode = "PAPER" if config.PAPER_TRADING else "LIVE"
        logger.info(f"[{mode}] {ticker}: {side.upper()} {qty} shares — order_id={order.id}")
        return True
    except Exception as exc:
        logger.error(f"{ticker}: order failed — {exc}")
        return False


def close_position(ticker: str) -> bool:
    """Close the entire position for a ticker. Returns True on success."""
    try:
        _client.close_position(ticker)
        mode = "PAPER" if config.PAPER_TRADING else "LIVE"
        logger.info(f"[{mode}] {ticker}: CLOSE position")
        return True
    except Exception as exc:
        logger.error(f"{ticker}: close position failed — {exc}")
        return False
