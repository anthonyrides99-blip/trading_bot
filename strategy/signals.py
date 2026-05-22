from data.indicators import Indicators


def summarize(ind: Indicators) -> str:
    """Convert indicator values into a human-readable signal summary for the LLM."""
    lines = []

    # RSI
    if ind.rsi >= 70:
        lines.append(f"RSI={ind.rsi:.1f} (overbought)")
    elif ind.rsi <= 30:
        lines.append(f"RSI={ind.rsi:.1f} (oversold)")
    else:
        lines.append(f"RSI={ind.rsi:.1f} (neutral)")

    # MACD
    if ind.macd_hist > 0 and ind.macd > ind.macd_signal:
        lines.append("MACD: bullish crossover, histogram positive")
    elif ind.macd_hist < 0 and ind.macd < ind.macd_signal:
        lines.append("MACD: bearish crossover, histogram negative")
    else:
        lines.append(f"MACD hist={ind.macd_hist:.4f} (no clear crossover)")

    # Price vs EMAs
    price = ind.current_price
    if price > ind.ema20 > ind.ema50:
        lines.append(f"Price ${price:.2f} above EMA20 (${ind.ema20:.2f}) and EMA50 (${ind.ema50:.2f}) — bullish trend")
    elif price < ind.ema20 < ind.ema50:
        lines.append(f"Price ${price:.2f} below EMA20 (${ind.ema20:.2f}) and EMA50 (${ind.ema50:.2f}) — bearish trend")
    else:
        lines.append(f"Price ${price:.2f} | EMA20=${ind.ema20:.2f} | EMA50=${ind.ema50:.2f} — mixed trend")

    # Bollinger Bands
    if price > ind.bb_upper:
        lines.append(f"Price above upper Bollinger Band (${ind.bb_upper:.2f}) — potentially extended")
    elif price < ind.bb_lower:
        lines.append(f"Price below lower Bollinger Band (${ind.bb_lower:.2f}) — potentially oversold")
    else:
        bb_pct = (price - ind.bb_lower) / (ind.bb_upper - ind.bb_lower) * 100 if ind.bb_upper != ind.bb_lower else 50
        lines.append(f"Price within Bollinger Bands ({bb_pct:.0f}% of band width)")

    # Volume
    if ind.volume_ratio >= 2.0:
        lines.append(f"Volume {ind.volume_ratio:.1f}x above 20-period average — strong interest")
    elif ind.volume_ratio <= 0.5:
        lines.append(f"Volume {ind.volume_ratio:.1f}x below 20-period average — low interest")
    else:
        lines.append(f"Volume ratio {ind.volume_ratio:.1f}x (normal)")

    return "\n".join(lines)
