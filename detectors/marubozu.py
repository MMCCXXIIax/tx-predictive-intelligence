# detectors/marubozu.py

def is_marubozu(candles):
    """
    Detects a Marubozu pattern and returns detailed info.
    """
    if len(candles) < 1:
        return {
            "pattern": "Marubozu",
            "detected": False,
            "confidence": 0.0,
            "explanation": "At least 1 candle is required to detect Marubozu."
        }

    last = candles[-1]
    body_size = abs(last['close'] - last['open'])
    candle_range = last['high'] - last['low']

    # Avoid division by zero
    if candle_range == 0:
        return {
            "pattern": "Marubozu",
            "detected": False,
            "confidence": 0.0,
            "explanation": "Invalid candle with no price range."
        }

    body_ratio = body_size / candle_range
    upper_shadow = last['high'] - max(last['open'], last['close'])
    lower_shadow = min(last['open'], last['close']) - last['low']

    small_shadow_threshold = 0.01 * candle_range  # Small wicks

    if body_ratio >= 0.95 and upper_shadow <= small_shadow_threshold and lower_shadow <= small_shadow_threshold:
        direction = "Bullish" if last['close'] > last['open'] else "Bearish"
        confidence = 0.90
        explanation = (
            f"{direction} Marubozu detected — candle body covers almost entire range with minimal shadows, "
            "indicating strong directional momentum."
        )
        return {
            "pattern": "Marubozu",
            "detected": True,
            "confidence": confidence,
            "explanation": explanation
        }

    return {
        "pattern": "Marubozu",
        "detected": False,
        "confidence": 0.0,
        "explanation": "Candle does not meet strict body-to-range ratio or has significant shadows, so not a Marubozu."
    }