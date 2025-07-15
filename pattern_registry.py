# pattern_registry.py

from detectors.hammer import is_hammer
from detectors.inverted_hammer import is_inverted_hammer
from detectors.hanging_man import is_hanging_man
from detectors.shooting_star import is_shooting_star
from detectors.marubozu import is_marubozu
from detectors.doji import is_doji
from detectors.spinning_top import is_spinning_top
from detectors.evening_star import is_evening_star
from detectors.piercing_line import is_piercing_line
from detectors.three_black_crows import is_three_black_crows
from detectors.three_white_soldiers import is_three_white_soldiers
from detectors.bullish_engulfing import is_bullish_engulfing
from detectors.bearish_engulfing import is_bearish_engulfing
from detectors.dragonfly_doji import is_dragonfly_doji 
from detectors.harami_bearish import is_harami_bearish
from detectors.tweezer_top import is_tweezer_top
from detectors.tweezer_bottom import is_tweezer_bottom
from detectors.dark_cloud_cover import is_dark_cloud_cover

# Centralized registry for all candlestick pattern detection functions
pattern_registry = [
    is_hammer,
    is_inverted_hammer,
    is_hanging_man,
    is_shooting_star,
    is_marubozu,
    is_doji,
    is_spinning_top,
    is_evening_star,
    is_piercing_line,
    is_dark_cloud_cover,
    is_three_black_crows,
    is_three_white_soldiers,
    is_bullish_engulfing,
    is_bearish_engulfing,
    is_dragonfly_doji,
    is_harami_bearish,
    is_tweezer_top,
    is_tweezer_bottom
]