# detectors/bearish_engulfing.py

def format_body(value):
    """
    Formats the candle body size to 4 decimal places.
    Clamps very small values to <0.0001 to avoid displaying 0.0000.
    """
    return f"{value:.4f}" if value >= 0.0001 else "<0.0001"


def is_bearish_engulfing(candles):
    """
    Detects a Bearish Engulfing pattern and returns detailed info.
    """
    if len(candles) < 2:
        return {
            "pattern": "Bearish Engulfing",
            "detected": False,
            "confidence": 0.0,
            "explanation": "Not enough candles to evaluate pattern."
        }

    prev = candles[-2]
    curr = candles[-1]

    prev_body = abs(prev['close'] - prev['open'])
    curr_body = abs(curr['close'] - curr['open'])

    # Conditions for bearish engulfing
    is_prev_bullish = prev['close'] > prev['open']
    is_curr_bearish = curr['close'] < curr['open']
    engulfs = curr['open'] > prev['close'] and curr['close'] < prev['open']

    if is_prev_bullish and is_curr_bearish and engulfs:
        confidence = 0.9 if curr_body > prev_body else 0.75
        explanation = (
            f"Previous candle was bullish and current candle is bearish. "
            f"Current body ({format_body(curr_body)}) engulfs previous body ({format_body(prev_body)})."
        )
        return {
            "pattern": "Bearish Engulfing",
            "detected": True,
            "confidence": confidence,
            "explanation": explanation
        }

    return {
        "pattern": "Bearish Engulfing",
        "detected": False,
        "confidence": 0.0,
        "explanation": "Conditions for Bearish Engulfing not met."
    }