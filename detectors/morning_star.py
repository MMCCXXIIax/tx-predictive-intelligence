# detectors/morning_star.py

def is_morning_star(candles):
    """
    Detects a Morning Star pattern and returns detailed info.
    """
    if len(candles) < 3:
        return {
            "pattern": "Morning Star",
            "detected": False,
            "confidence": 0.0,
            "explanation": "At least 3 candles are required to detect a Morning Star pattern."
        }

    first, second, third = candles[-3], candles[-2], candles[-1]

    # First candle: long bearish
    first_body = abs(first['close'] - first['open'])
    first_range = first['high'] - first['low']
    first_bearish = first['close'] < first['open'] and first_body > 0.6 * first_range

    # Second candle: small real body (indecision)
    second_body = abs(second['close'] - second['open'])
    second_range = second['high'] - second['low']
    second_small = second_body < 0.3 * second_range

    # Third candle: long bullish closing above midpoint of first candle
    third_body = abs(third['close'] - third['open'])
    third_range = third['high'] - third['low']
    third_bullish = third['close'] > third['open'] and third_body > 0.6 * third_range
    closes_above_midpoint = third['close'] > (first['open'] + first['close']) / 2

    if first_bearish and second_small and third_bullish and closes_above_midpoint:
        confidence = 0.93
        explanation = (
            "Morning Star detected — strong reversal pattern: large bearish candle, small-bodied candle of indecision, "
            "followed by strong bullish candle closing above the midpoint of the first candle."
        )
        return {
            "pattern": "Morning Star",
            "detected": True,
            "confidence": confidence,
            "explanation": explanation
        }

    return {
        "pattern": "Morning Star",
        "detected": False,
        "confidence": 0.0,
        "explanation": "Pattern conditions not met — may be due to candle sizes, directions, or third candle not closing above midpoint."
    }