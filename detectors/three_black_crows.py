# detectors/three_black_crows.py

def is_three_black_crows(candles):
    """
    Detects a Three Black Crows candlestick pattern and returns detailed info.
    """
    if len(candles) < 3:
        return {
            "pattern": "Three Black Crows",
            "detected": False,
            "confidence": 0.0,
            "explanation": "At least 3 candles are required to detect the Three Black Crows pattern."
        }

    c1, c2, c3 = candles[-3], candles[-2], candles[-1]

    def is_bearish(candle):
        return candle["close"] < candle["open"]

    def strong_body(candle):
        return abs(candle["close"] - candle["open"]) > 0.6 * (candle["high"] - candle["low"])

    all_bearish = is_bearish(c1) and is_bearish(c2) and is_bearish(c3)
    all_strong = strong_body(c1) and strong_body(c2) and strong_body(c3)

    falling_opens = c2["open"] < c1["open"] and c3["open"] < c2["open"]
    falling_closes = c2["close"] < c1["close"] and c3["close"] < c2["close"]

    if all_bearish and all_strong and falling_opens and falling_closes:
        confidence = 0.94
        explanation = (
            "Three Black Crows detected — three consecutive bearish candles with strong bodies and falling opens/closes. "
            "Indicates strong bearish reversal momentum after an uptrend."
        )
        return {
            "pattern": "Three Black Crows",
            "detected": True,
            "confidence": confidence,
            "explanation": explanation
        }

    return {
        "pattern": "Three Black Crows",
        "detected": False,
        "confidence": 0.0,
        "explanation": (
            "Pattern conditions not met — "
            f"bearish={all_bearish}, strong_body={all_strong}, falling_opens={falling_opens}, falling_closes={falling_closes}."
        )
    }