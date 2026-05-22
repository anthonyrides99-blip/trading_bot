from dataclasses import dataclass

import pandas as pd
import pandas_ta as ta

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

    rsi_series = ta.rsi(close, length=14)
    macd_df = ta.macd(close, fast=12, slow=26, signal=9)
    ema20_series = ta.ema(close, length=20)
    ema50_series = ta.ema(close, length=50)
    bb_df = ta.bbands(close, length=20, std=2)

    avg_vol = volume.rolling(20).mean().iloc[-1]
    vol_ratio = float(volume.iloc[-1] / avg_vol) if avg_vol else 1.0

    macd_col = [c for c in macd_df.columns if c.startswith("MACD_") and "Signal" not in c and "Hist" not in c]
    signal_col = [c for c in macd_df.columns if "MACDs" in c]
    hist_col = [c for c in macd_df.columns if "MACDh" in c]

    ind = Indicators(
        ticker=ticker,
        rsi=_last(rsi_series),
        macd=_last(macd_df[macd_col[0]]) if macd_col else 0.0,
        macd_signal=_last(macd_df[signal_col[0]]) if signal_col else 0.0,
        macd_hist=_last(macd_df[hist_col[0]]) if hist_col else 0.0,
        ema20=_last(ema20_series),
        ema50=_last(ema50_series),
        bb_upper=_last(bb_df[[c for c in bb_df.columns if "BBU" in c][0]]),
        bb_mid=_last(bb_df[[c for c in bb_df.columns if "BBM" in c][0]]),
        bb_lower=_last(bb_df[[c for c in bb_df.columns if "BBL" in c][0]]),
        current_price=float(close.iloc[-1]),
        volume_ratio=round(vol_ratio, 2),
    )
    logger.debug(f"{ticker}: RSI={ind.rsi:.1f} MACD_hist={ind.macd_hist:.3f} EMA20={ind.ema20:.2f}")
    return ind


def _last(series: pd.Series) -> float:
    return float(series.dropna().iloc[-1]) if not series.dropna().empty else 0.0
