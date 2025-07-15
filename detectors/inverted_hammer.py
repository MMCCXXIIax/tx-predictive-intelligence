from typing import List, Dict

def is_inverted_hammer(candle: Dict) -> bool:
    """
    Determines if a single candlestick is an Inverted Hammer pattern.

    Conditions:
    - Small real body near the bottom of the candle.
    - Long upper wick (at least twice the real body).
    - Little to no lower wick.
    - Can be bullish or bearish in color.

    Returns:
        bool: True if the candlestick matches the Inverted Hammer pattern.
    """
    open_price = candle["open"]
    close_price = candle["close"]
    high = candle["high"]
    low = candle["low"]

    body = abs(close_price - open_price)
    upper_wick = high - max(open_price, close_price)
    lower_wick = min(open_price, close_price) - low

    # Avoid division by zero and unrealistic candles
    if body == 0:
        return False

    return (
        upper_wick >= 2 * body and       # long upper wick
        lower_wick <= 0.3 * body and     # small lower wick
        body / (high - low) <= 0.4       # small real body relative to range
    )

def detect_inverted_hammer(candles: List[Dict]) -> List[int]:
    """
    Detects Inverted Hammer patterns in a list of candlesticks.

    Args:
        candles (List[Dict]): List of candlestick data.

    Returns:
        List[int]: Indices of candles that match the Inverted Hammer pattern.
    """
    inverted_hammer_indices = []

    for i in range(len(candles)):
        if is_inverted_hammer(candles[i]):
            inverted_hammer_indices.append(i)

    return inverted_hammer_indices