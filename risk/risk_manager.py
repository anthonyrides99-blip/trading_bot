import math
from datetime import datetime, timezone

import config
from utils.logger import logger


class RiskManager:
    def __init__(self):
        self._halted = False
        self._start_equity: float | None = None
        self._halt_date: str | None = None

    def reset_for_new_day(self, equity: float) -> None:
        """Call at the start of each trading day to record opening equity."""
        today = _today()
        if self._halt_date != today:
            self._halted = False
        self._start_equity = equity
        logger.info(f"RiskManager: day reset — opening equity=${equity:,.2f} halt={self._halted}")

    def check_daily_loss(self, current_equity: float) -> bool:
        """
        Returns True if within loss limits, False (and halts) if limit breached.
        Loss threshold: equity has dropped >= MAX_DAILY_LOSS_PCT from start-of-day equity.
        """
        if self._start_equity is None:
            return True

        loss_pct = (self._start_equity - current_equity) / self._start_equity
        if loss_pct >= config.MAX_DAILY_LOSS_PCT:
            if not self._halted:
                logger.warning(
                    f"RiskManager: DAILY LOSS LIMIT HIT — "
                    f"loss={loss_pct:.2%} >= threshold={config.MAX_DAILY_LOSS_PCT:.2%}. "
                    f"Trading HALTED for the rest of the day."
                )
                self._halted = True
                self._halt_date = _today()
            return False

        return True

    def can_trade(self) -> bool:
        """Returns False if halted due to daily loss limit."""
        if self._halted:
            logger.debug("RiskManager: trading is halted — skipping tick")
            return False
        return True

    def position_size(self, equity: float, price: float) -> int:
        """
        Return number of whole shares to buy such that position value
        does not exceed MAX_POSITION_PCT of portfolio equity.
        """
        if price <= 0:
            return 0
        max_value = equity * config.MAX_POSITION_PCT
        qty = math.floor(max_value / price)
        logger.debug(
            f"RiskManager: position_size equity=${equity:,.2f} "
            f"price=${price:.2f} max_value=${max_value:.2f} qty={qty}"
        )
        return qty


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")
