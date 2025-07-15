# detectors/evening_star.py

def is_evening_star(candles):
    """
    Detects an Evening Star pattern and returns detailed info.
    """
    if len(candles) < 3:
        return {
            "pattern": "Evening Star",
            "detected": False,
            "confidence": 0.0,
            "explanation": "Less than 3 candles provided."
        }

    c1, c2, c3 = candles[-3], candles[-2], candles[-1]

    c1_bullish = c1['close'] > c1['open']
    c3_bearish = c3['close'] < c3['open']
    small_body = abs(c2['close'] - c2['open']) <= abs(c1['close'] - c1['open']) * 0.5

    gap_up = c2['open'] > c1['close']
    gap_down = c3['open'] < c2['close']
    c3_close_below_mid_c1 = c3['close'] < (c1['open'] + c1['close']) / 2

    if c1_bullish and small_body and c3_bearish and gap_up and gap_down and c3_close_below_mid_c1:
        confidence = 0.92
        explanation = (
            "First candle is bullish, second has a small body with a gap up, third is bearish with a gap down "
            "and closes below midpoint of the first candle, forming a strong Evening Star reversal signal."
        )
        return {
            "pattern": "Evening Star",
            "detected": True,
            "confidence": confidence,
            "explanation": explanation
        }

    return {
        "pattern": "Evening Star",
        "detected": False,
        "confidence": 0.0,
        "explanation": "Candle sequence doesn't match Evening Star pattern (bullish > indecision > bearish reversal with gaps)."
    }