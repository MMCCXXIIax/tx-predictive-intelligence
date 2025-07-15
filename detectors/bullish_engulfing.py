# detectors/bullish_engulfing.py

def is_bullish_engulfing(candles):
    """
    Detects a Bullish Engulfing pattern and returns detailed info.
    """
    if len(candles) < 2:
        return {
            "pattern": "Bullish Engulfing",
            "detected": False,
            "confidence": 0.0,
            "explanation": "Not enough candles to evaluate pattern."
        }

    prev = candles[-2]
    curr = candles[-1]

    prev_body = abs(prev['close'] - prev['open'])
    curr_body = abs(curr['close'] - curr['open'])

    # Conditions for bullish engulfing
    is_prev_bearish = prev['close'] < prev['open']
    is_curr_bullish = curr['close'] > curr['open']
    engulfs = curr['open'] < prev['close'] and curr['close'] > prev['open']

    if is_prev_bearish and is_curr_bullish and engulfs:
        confidence = 0.9 if curr_body > prev_body else 0.75
        explanation = (
            f"Previous candle was bearish and current candle is bullish. "
            f"Current body ({curr_body:.2f}) engulfs previous body ({prev_body:.2f})."
        )
        return {
            "pattern": "Bullish Engulfing",
            "detected": True,
            "confidence": confidence,
            "explanation": explanation
        }

    return {
        "pattern": "Bullish Engulfing",
        "detected": False,
        "confidence": 0.0,
        "explanation": "Conditions for Bullish Engulfing not met."
    }