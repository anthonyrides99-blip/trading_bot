from dataclasses import dataclass

import pandas as pd
import ta

from utils.logger import logger


@dataclass
class Indicators:
    ticker: str
    rsi: float
    macd: float
    macd_signal: float
    macd_hist: float
    ema20: float
    ema50: float
    bb_upper: float
    bb_mid: float
    bb_lower: float
    current_price: float
    volume_ratio: float  # current vol / 20-period average vol


def compute(ticker: str, df: pd.DataFrame) -> Indicators | None:
    """Compute technical indicators from an OHLCV DataFrame."""
    if len(df) < 52:
        logger.warning(f"{ticker}: insufficient bars ({len(df)}) to compute indicators — need 52+")
        return None

    close = df["close"]
    volume = df["volume"]

    rsi_series = ta.momentum.RSIIndicator(close=close, window=14).rsi()

    macd_ind = ta.trend.MACD(close=close, window_slow=26, window_fast=12, window_sign=9)
    macd_series = macd_ind.macd()
    macd_signal_series = macd_ind.macd_signal()
    macd_hist_series = macd_ind.macd_diff()

    ema20_series = ta.trend.EMAIndicator(close=close, window=20).ema_indicator()
    ema50_series = ta.trend.EMAIndicator(close=close, window=50).ema_indicator()

    bb = ta.volatility.BollingerBands(close=close, window=20, window_dev=2)
    bb_upper_series = bb.bollinger_hband()
    bb_mid_series = bb.bollinger_mavg()
    bb_lower_series = bb.bollinger_lband()

    avg_vol = volume.rolling(20).mean().iloc[-1]
    vol_ratio = float(volume.iloc[-1] / avg_vol) if avg_vol else 1.0

    ind = Indicators(
        ticker=ticker,
        rsi=_last(rsi_series),
        macd=_last(macd_series),
        macd_signal=_last(macd_signal_series),
        macd_hist=_last(macd_hist_series),
        ema20=_last(ema20_series),
        ema50=_last(ema50_series),
        bb_upper=_last(bb_upper_series),
        bb_mid=_last(bb_mid_series),
        bb_lower=_last(bb_lower_series),
        current_price=float(close.iloc[-1]),
        volume_ratio=round(vol_ratio, 2),
    )
    logger.debug(f"{ticker}: RSI={ind.rsi:.1f} MACD_hist={ind.macd_hist:.3f} EMA20={ind.ema20:.2f}")
    return ind


def _last(series: pd.Series) -> float:
    return float(series.dropna().iloc[-1]) if not series.dropna().empty else 0.0
