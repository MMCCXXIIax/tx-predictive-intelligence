# detectors/spinning_top.py

def is_spinning_top(candles):
    """
    Detects a Spinning Top candlestick pattern and returns detailed info.
    """
    if len(candles) < 1:
        return {
            "pattern": "Spinning Top",
            "detected": False,
            "confidence": 0.0,
            "explanation": "At least 1 candle is required to detect a Spinning Top pattern."
        }

    c = candles[-1]
    open_price = c["open"]
    close_price = c["close"]
    high = c["high"]
    low = c["low"]

    body = abs(close_price - open_price)
    upper_shadow = high - max(open_price, close_price)
    lower_shadow = min(open_price, close_price) - low
    total_range = high - low

    body_ratio = body / total_range if total_range else 0
    upper_shadow_ratio = upper_shadow / total_range if total_range else 0
    lower_shadow_ratio = lower_shadow / total_range if total_range else 0

    is_small_body = 0.1 <= body_ratio <= 0.3
    is_balanced_shadows = abs(upper_shadow - lower_shadow) <= total_range * 0.2

    if is_small_body and is_balanced_shadows:
        confidence = round(1.0 - abs(upper_shadow - lower_shadow) / (total_range + 1e-6), 2)
        explanation = (
            f"Spinning Top detected — small body ({body:.2f}) with nearly equal upper ({upper_shadow:.2f}) "
            f"and lower ({lower_shadow:.2f}) shadows. Indicates market indecision."
        )
        return {
            "pattern": "Spinning Top",
            "detected": True,
            "confidence": confidence,
            "explanation": explanation
        }

    return {
        "pattern": "Spinning Top",
        "detected": False,
        "confidence": 0.0,
        "explanation": (
            f"Pattern conditions not met — body_ratio={body_ratio:.2f}, upper_shadow={upper_shadow:.2f}, "
            f"lower_shadow={lower_shadow:.2f}, balance_difference={abs(upper_shadow - lower_shadow):.2f}."
        )
    }