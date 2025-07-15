# detectors/dragonfly_doji.py

def is_dragonfly_doji(candles):
    """
    Detects a Dragonfly Doji pattern and returns detailed info.
    """
    if not candles:
        return {
            "pattern": "Dragonfly Doji",
            "detected": False,
            "confidence": 0.0,
            "explanation": "No candles provided."
        }

    candle = candles[-1]
    body_size = abs(candle['open'] - candle['close'])
    total_range = candle['high'] - candle['low']
    lower_shadow = min(candle['open'], candle['close']) - candle['low']
    upper_shadow = candle['high'] - max(candle['open'], candle['close'])

    if total_range == 0:
        return {
            "pattern": "Dragonfly Doji",
            "detected": False,
            "confidence": 0.0,
            "explanation": "Invalid candle with zero range."
        }

    body_to_range_ratio = body_size / total_range

    if body_to_range_ratio <= 0.1 and upper_shadow <= body_size and lower_shadow >= total_range * 0.6:
        confidence = 0.9 if lower_shadow > total_range * 0.7 else 0.75
        explanation = (
            f"Long lower shadow ({lower_shadow}), very small body ({body_size}), minimal upper shadow. "
            f"This suggests a possible bullish reversal after sellers failed to hold lows."
        )
        return {
            "pattern": "Dragonfly Doji",
            "detected": True,
            "confidence": confidence,
            "explanation": explanation
        }

    return {
        "pattern": "Dragonfly Doji",
        "detected": False,
        "confidence": 0.0,
        "explanation": "Candle doesn't meet criteria for Dragonfly Doji (long lower shadow, small body, negligible upper shadow)."
    }