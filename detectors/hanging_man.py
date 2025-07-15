# detectors/hanging_man.py

def is_hanging_man(candles):
    """
    Detects a Hanging Man pattern and returns detailed info.
    """
    if len(candles) < 1:
        return {
            "pattern": "Hanging Man",
            "detected": False,
            "confidence": 0.0,
            "explanation": "No candles provided."
        }

    candle = candles[-1]
    body_size = abs(candle['close'] - candle['open'])
    lower_shadow = min(candle['open'], candle['close']) - candle['low']
    upper_shadow = candle['high'] - max(candle['open'], candle['close'])

    lower_shadow_condition = lower_shadow >= 2 * body_size
    upper_shadow_condition = upper_shadow <= 0.1 * body_size
    small_body = body_size <= (candle['high'] - candle['low']) * 0.3
    close_near_high = abs(candle['close'] - candle['high']) <= (candle['high'] - candle['low']) * 0.1

    if lower_shadow_condition and upper_shadow_condition and small_body and close_near_high:
        confidence = 0.86
        explanation = (
            "Small body near the high with a long lower shadow and little to no upper shadow, "
            "indicates potential bearish reversal in uptrend, matching Hanging Man pattern."
        )
        return {
            "pattern": "Hanging Man",
            "detected": True,
            "confidence": confidence,
            "explanation": explanation
        }

    return {
        "pattern": "Hanging Man",
        "detected": False,
        "confidence": 0.0,
        "explanation": "Candle does not match Hanging Man structure (long lower shadow, small body near top, tiny upper shadow)."
    }