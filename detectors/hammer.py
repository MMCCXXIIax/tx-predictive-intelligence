# detectors/hammer.py

def is_hammer(candles):
    """
    Detects a Hammer pattern and returns detailed info.
    """
    if len(candles) < 1:
        return {
            "pattern": "Hammer",
            "detected": False,
            "confidence": 0.0,
            "explanation": "Not enough candles to evaluate pattern."
        }

    c = candles[-1]
    body_size = abs(c['close'] - c['open'])
    upper_shadow = c['high'] - max(c['close'], c['open'])
    lower_shadow = min(c['close'], c['open']) - c['low']

    has_small_body = body_size < (c['high'] - c['low']) * 0.3
    has_long_lower_shadow = lower_shadow > body_size * 2
    minimal_upper_shadow = upper_shadow <= body_size * 0.25

    if has_small_body and has_long_lower_shadow and minimal_upper_shadow:
        confidence = 0.85 if lower_shadow > body_size * 3 else 0.7
        explanation = (
            f"Small real body with long lower shadow ({lower_shadow:.2f}) and small upper shadow ({upper_shadow:.2f}). "
            f"Suggests potential bullish reversal after downtrend."
        )
        return {
            "pattern": "Hammer",
            "detected": True,
            "confidence": confidence,
            "explanation": explanation
        }

    return {
        "pattern": "Hammer",
        "detected": False,
        "confidence": 0.0,
        "explanation": "Conditions for Hammer not met."
    }