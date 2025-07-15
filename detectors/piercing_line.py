# detectors/piercing_line.py

def is_piercing_line(candles):
    """
    Detects a Piercing Line pattern and returns detailed info.
    """
    if len(candles) < 2:
        return {
            "pattern": "Piercing Line",
            "detected": False,
            "confidence": 0.0,
            "explanation": "At least 2 candles are required to detect a Piercing Line pattern."
        }

    first, second = candles[-2], candles[-1]

    first_body = abs(first['close'] - first['open'])
    second_body = abs(second['close'] - second['open'])

    # First candle: long bearish
    first_bearish = first['close'] < first['open'] and first_body > 0.6 * (first['high'] - first['low'])

    # Second candle: bullish, opens below low of previous and closes above midpoint of first
    second_bullish = second['close'] > second['open']
    opens_below_prev_low = second['open'] < first['low']
    closes_above_midpoint = second['close'] > (first['open'] + first['close']) / 2

    if first_bearish and second_bullish and opens_below_prev_low and closes_above_midpoint:
        confidence = 0.91
        explanation = (
            "Piercing Line detected — strong reversal signal: long bearish candle followed by a bullish candle that "
            "opens below the previous low and closes above the midpoint of the first candle."
        )
        return {
            "pattern": "Piercing Line",
            "detected": True,
            "confidence": confidence,
            "explanation": explanation
        }

    return {
        "pattern": "Piercing Line",
        "detected": False,
        "confidence": 0.0,
        "explanation": "Pattern conditions not met — likely due to candle directions, opening gap, or insufficient close above midpoint."
    }