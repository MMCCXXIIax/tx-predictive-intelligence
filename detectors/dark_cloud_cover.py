# detectors/dark_cloud_cover.py

def is_dark_cloud_cover(candles):
    """
    Detects a Dark Cloud Cover pattern and returns detailed info.
    """
    if len(candles) < 2:
        return {
            "pattern": "Dark Cloud Cover",
            "detected": False,
            "confidence": 0.0,
            "explanation": "At least 2 candles are required to detect Dark Cloud Cover."
        }

    first = candles[-2]
    second = candles[-1]

    is_first_bullish = first['close'] > first['open']
    is_second_bearish = second['close'] < second['open']
    opens_above = second['open'] > first['high']
    closes_within = second['close'] < (first['open'] + first['close']) / 2
    closes_inside = second['close'] > first['open']

    if is_first_bullish and is_second_bearish and opens_above and closes_within and closes_inside:
        confidence = 0.88
        explanation = (
            "A bearish candle opens above the previous bullish high and closes below its midpoint. "
            "This shows strong bearish rejection and suggests a reversal."
        )
        return {
            "pattern": "Dark Cloud Cover",
            "detected": True,
            "confidence": confidence,
            "explanation": explanation
        }

    return {
        "pattern": "Dark Cloud Cover",
        "detected": False,
        "confidence": 0.0,
        "explanation": "Second candle does not meet the requirements for Dark Cloud Cover — either not bearish, not opening above previous high, or not closing below midpoint."
    }