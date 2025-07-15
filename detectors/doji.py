# detectors/doji.py

def is_doji(candles):
    """
    Detects a Doji pattern and returns detailed info.
    """
    if not candles:
        return {
            "pattern": "Doji",
            "detected": False,
            "confidence": 0.0,
            "explanation": "No candles provided."
        }

    candle = candles[-1]
    body_size = abs(candle['close'] - candle['open'])
    total_range = candle['high'] - candle['low']

    if total_range == 0:
        return {
            "pattern": "Doji",
            "detected": False,
            "confidence": 0.0,
            "explanation": "Invalid candle with zero range."
        }

    body_to_range_ratio = body_size / total_range

    if body_to_range_ratio <= 0.1:
        confidence = 0.9 if body_to_range_ratio < 0.05 else 0.75
        explanation = (
            f"Small real body ({body_size}) compared to total range ({total_range}). "
            f"Market shows indecision — typical of a Doji candle."
        )
        return {
            "pattern": "Doji",
            "detected": True,
            "confidence": confidence,
            "explanation": explanation
        }

    return {
        "pattern": "Doji",
        "detected": False,
        "confidence": 0.0,
        "explanation": "Candle body is too large relative to range to be a Doji."
    }