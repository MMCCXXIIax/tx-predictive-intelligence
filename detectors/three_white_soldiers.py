# detectors/three_white_soldiers.py

def is_three_white_soldiers(candles):
    """
    Detects a Three White Soldiers candlestick pattern and returns detailed info.
    """
    if len(candles) < 3:
        return {
            "pattern": "Three White Soldiers",
            "detected": False,
            "confidence": 0.0,
            "explanation": "At least 3 candles are required to detect the Three White Soldiers pattern."
        }

    c1, c2, c3 = candles[-3], candles[-2], candles[-1]

    def is_bullish(candle):
        return candle["close"] > candle["open"]

    def strong_body(candle):
        return abs(candle["close"] - candle["open"]) > 0.6 * (candle["high"] - candle["low"])

    all_bullish = is_bullish(c1) and is_bullish(c2) and is_bullish(c3)
    all_strong = strong_body(c1) and strong_body(c2) and strong_body(c3)

    rising_opens = c2["open"] > c1["open"] and c3["open"] > c2["open"]
    rising_closes = c2["close"] > c1["close"] and c3["close"] > c2["close"]

    if all_bullish and all_strong and rising_opens and rising_closes:
        confidence = 0.95
        explanation = (
            "Three White Soldiers detected — three consecutive bullish candles with strong bodies and rising opens/closes. "
            "Suggests strong bullish reversal momentum."
        )
        return {
            "pattern": "Three White Soldiers",
            "detected": True,
            "confidence": confidence,
            "explanation": explanation
        }

    return {
        "pattern": "Three White Soldiers",
        "detected": False,
        "confidence": 0.0,
        "explanation": (
            "Pattern conditions not met — "
            f"bullish={all_bullish}, strong_body={all_strong}, rising_opens={rising_opens}, rising_closes={rising_closes}."
        )
    }