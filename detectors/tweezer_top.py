# detectors/tweezer_top.py

def is_tweezer_top(candles):
    """
    Detects a Tweezer Top candlestick pattern and returns detailed info.
    """
    if len(candles) < 2:
        return {
            "pattern": "Tweezer Top",
            "detected": False,
            "confidence": 0.0,
            "explanation": "At least 2 candles are required to detect a Tweezer Top pattern."
        }

    first = candles[-2]
    second = candles[-1]

    first_bullish = first["close"] > first["open"]
    second_bearish = second["close"] < second["open"]

    # Highs should be approximately equal (within 0.1% of range)
    high_diff = abs(first["high"] - second["high"])
    total_range = max(first["high"] - first["low"], second["high"] - second["low"])
    high_match = high_diff <= 0.001 * total_range

    if first_bullish and second_bearish and high_match:
        confidence = round(1.0 - (high_diff / (total_range + 1e-6)), 2)
        explanation = (
            f"Tweezer Top detected — first candle is bullish, second is bearish, and highs are nearly equal "
            f"(diff: {high_diff:.4f}). Suggests bearish reversal after an uptrend."
        )
        return {
            "pattern": "Tweezer Top",
            "detected": True,
            "confidence": confidence,
            "explanation": explanation
        }

    return {
        "pattern": "Tweezer Top",
        "detected": False,
        "confidence": 0.0,
        "explanation": (
            f"Pattern conditions not met — bullish then bearish: {first_bullish}->{second_bearish}, "
            f"high_diff={high_diff:.4f}, required ≤ {0.001 * total_range:.4f}."
        )
    }