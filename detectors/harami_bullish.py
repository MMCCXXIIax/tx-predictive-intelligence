# detectors/harami_bullish.py

def is_harami_bullish(candles):
    """
    Detects a Bullish Harami pattern and returns detailed info.
    """
    if len(candles) < 2:
        return {
            "pattern": "Bullish Harami",
            "detected": False,
            "confidence": 0.0,
            "explanation": "At least 2 candles are required to detect Bullish Harami."
        }

    first = candles[-2]
    second = candles[-1]

    is_first_bearish = first['close'] < first['open']
    is_second_bullish = second['close'] > second['open']

    first_body_low = min(first['open'], first['close'])
    first_body_high = max(first['open'], first['close'])
    second_body_low = min(second['open'], second['close'])
    second_body_high = max(second['open'], second['close'])

    is_second_inside_first = second_body_low > first_body_low and second_body_high < first_body_high

    if is_first_bearish and is_second_bullish and is_second_inside_first:
        confidence = 0.84
        explanation = (
            "First candle is bearish, followed by a bullish candle completely inside the previous body. "
            "This indicates weakening bearish pressure and a potential bullish reversal."
        )
        return {
            "pattern": "Bullish Harami",
            "detected": True,
            "confidence": confidence,
            "explanation": explanation
        }

    return {
        "pattern": "Bullish Harami",
        "detected": False,
        "confidence": 0.0,
        "explanation": "Second bullish candle is not fully engulfed within the body of the previous bearish candle."
    }