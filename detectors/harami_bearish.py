# detectors/harami_bearish.py

def is_harami_bearish(candles):
    """
    Detects a Bearish Harami pattern and returns detailed info.
    """
    if len(candles) < 2:
        return {
            "pattern": "Bearish Harami",
            "detected": False,
            "confidence": 0.0,
            "explanation": "At least 2 candles are required to detect Bearish Harami."
        }

    first = candles[-2]
    second = candles[-1]

    is_first_bullish = first['close'] > first['open']
    is_second_bearish = second['close'] < second['open']

    first_body_low = min(first['open'], first['close'])
    first_body_high = max(first['open'], first['close'])
    second_body_low = min(second['open'], second['close'])
    second_body_high = max(second['open'], second['close'])

    is_second_inside_first = second_body_low > first_body_low and second_body_high < first_body_high

    if is_first_bullish and is_second_bearish and is_second_inside_first:
        confidence = 0.84
        explanation = (
            "First candle is bullish, followed by a bearish candle completely inside the previous body. "
            "This indicates weakening bullish momentum and a possible bearish reversal."
        )
        return {
            "pattern": "Bearish Harami",
            "detected": True,
            "confidence": confidence,
            "explanation": explanation
        }

    return {
        "pattern": "Bearish Harami",
        "detected": False,
        "confidence": 0.0,
        "explanation": "Second bearish candle is not fully engulfed within the body of the previous bullish candle."
    }