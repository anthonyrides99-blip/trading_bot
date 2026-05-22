import json

import anthropic

import config
from utils.logger import logger

_client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

_SYSTEM_PROMPT = """You are a disciplined, risk-aware stock trading agent. Your role is to analyze technical signals and recent news for a given stock and decide whether to buy, sell, or hold.

Rules you must follow:
- Never chase momentum blindly; confirm signals with at least 2 agreeing indicators.
- Prioritize capital preservation. When signals conflict, choose hold.
- If news is strongly negative (earnings miss, lawsuit, CEO departure), lean toward sell or hold.
- Do not recommend buy if RSI is above 75 (overbought) unless volume strongly confirms.
- Do not recommend sell if RSI is below 25 (oversold) and MACD is turning up.

Respond ONLY with a JSON object in this exact format (no markdown, no extra text):
{"action": "buy" | "sell" | "hold", "confidence": <float 0.0-1.0>, "reason": "<one sentence>"}"""


def analyze(
    ticker: str,
    price: float,
    signal_summary: str,
    news_headlines: list[str],
    has_position: bool,
) -> dict:
    """Call Claude to decide buy/sell/hold. Returns dict with action, confidence, reason."""
    position_context = (
        f"You currently HOLD a position in {ticker}."
        if has_position
        else f"You have NO position in {ticker}."
    )
    news_text = (
        "\n".join(f"- {h}" for h in news_headlines)
        if news_headlines
        else "No recent news available."
    )

    user_message = f"""Ticker: {ticker}
Current price: ${price:.2f}
{position_context}

Technical signals:
{signal_summary}

Recent news headlines:
{news_text}

What is your trading decision?"""

    try:
        response = _client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=256,
            system=[
                {
                    "type": "text",
                    "text": _SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": user_message}],
        )
        raw = response.content[0].text.strip()
        decision = json.loads(raw)
        logger.info(
            f"{ticker}: LLM → action={decision['action']} confidence={decision['confidence']:.2f} | {decision['reason']}"
        )
        return decision
    except json.JSONDecodeError as exc:
        logger.error(f"{ticker}: LLM returned invalid JSON — {exc}. Raw: {raw!r}")
        return {"action": "hold", "confidence": 0.0, "reason": "LLM parse error"}
    except Exception as exc:
        logger.error(f"{ticker}: LLM call failed — {exc}")
        return {"action": "hold", "confidence": 0.0, "reason": f"LLM error: {exc}"}
