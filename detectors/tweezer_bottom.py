# detectors/tweezer_bottom.py

def is_tweezer_bottom(candles):
    """
    Detects a Tweezer Bottom candlestick pattern and returns detailed info.
    """
    if len(candles) < 2:
        return {
            "pattern": "Tweezer Bottom",
            "detected": False,
            "confidence": 0.0,
            "explanation": "At least 2 candles are required to detect a Tweezer Bottom pattern."
        }

    first = candles[-2]
    second = candles[-1]

    first_bearish = first["close"] < first["open"]
    second_bullish = second["close"] > second["open"]

    # Lows should be approximately equal (within 0.1% of range)
    low_diff = abs(first["low"] - second["low"])
    total_range = max(first["high"] - first["low"], second["high"] - second["low"])
    low_match = low_diff <= 0.001 * total_range

    if first_bearish and second_bullish and low_match:
        confidence = round(1.0 - (low_diff / (total_range + 1e-6)), 2)
        explanation = (
            f"Tweezer Bottom detected — first candle is bearish, second is bullish, and lows are nearly equal "
            f"(diff: {low_diff:.4f}). Suggests bullish reversal after a downtrend."
        )
        return {
            "pattern": "Tweezer Bottom",
            "detected": True,
            "confidence": confidence,
            "explanation": explanation
        }

    return {
        "pattern": "Tweezer Bottom",
        "detected": False,
        "confidence": 0.0,
        "explanation": (
            f"Pattern conditions not met — bearish then bullish: {first_bearish}->{second_bullish}, "
            f"low_diff={low_diff:.4f}, required ≤ {0.001 * total_range:.4f}."
        )
    }