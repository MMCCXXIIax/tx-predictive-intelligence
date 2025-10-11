"""
Loader shim for services.ml_patterns that avoids importing the file directly
when it contains trailing demo/merge artifact code that breaks parsing.

This module:
- Reads services/ml_patterns.py as text
- Truncates everything starting from "if __name__ == '__main__':" (inclusive)
- Executes the sanitized source in an isolated module namespace
- Exposes the public wrapper functions used by the backend:
  - train_from_outcomes(lookback='180d')
  - score_symbol(symbol, timeframe='1h')
  - score_symbol_with_pattern(symbol, timeframe, pattern)

Note: The original ML file on disk is NEVER modified.
"""
from __future__ import annotations

import os
import sys
import types
import traceback
from typing import Any, Dict

# Absolute path to the ML file
_BASE_DIR = os.path.dirname(os.path.dirname(__file__))
_ML_PATH = os.path.join(_BASE_DIR, 'services', 'ml_patterns.py')

# Cached module namespace to avoid re-loading per import
_ml_mod: types.ModuleType | None = None


def _sanitize_source(src: str) -> str:
    """Remove trailing demo/duplicate code and any __main__ block.
    Strategy:
    - If we find a top-level line starting with: if __name__ == "__main__":
      we truncate the source at that point to avoid executing demo code.
    - Additionally, if the file has accidental duplicated tail content,
      truncating at __main__ will discard it.
    """
    sentinel = "if __name__ == \"__main__\":"
    idx = src.find(sentinel)
    if idx != -1:
        return src[:idx]
    # If not found, attempt to cut at a known bad artifact token observed in the file
    artifact_token = "MODEL_TYPE.value,"
    art_idx = src.find(artifact_token)
    if art_idx != -1:
        # Cut a bit earlier on a safe line boundary
        # Find previous newline preceding artifact
        nl = src.rfind('\n', 0, art_idx)
        return src[:nl if nl != -1 else art_idx]
    return src


def _load_ml_module() -> types.ModuleType:
    global _ml_mod
    if _ml_mod is not None:
        return _ml_mod

    if not os.path.exists(_ML_PATH):
        raise FileNotFoundError(f"ML file not found at {_ML_PATH}")

    with open(_ML_PATH, 'r', encoding='utf-8') as f:
        raw_src = f.read()

    sanitized = _sanitize_source(raw_src)

    mod = types.ModuleType('services.ml_patterns_sanitized')
    mod.__file__ = _ML_PATH
    # Provide builtins and minimal globals expected by the ML file
    g: Dict[str, Any] = mod.__dict__

    try:
        exec(compile(sanitized, _ML_PATH, 'exec'), g, g)
    except Exception as e:
        # Surface useful debugging info, but do not modify original file
        tb = traceback.format_exc()
        raise ImportError(f"Failed to dynamically load sanitized ml_patterns.py: {e}\n{tb}")

    _ml_mod = mod
    return mod


# Public API wrappers expected by main.py

def train_from_outcomes(lookback: str = '180d') -> Dict[str, Any]:
    mod = _load_ml_module()
    return mod.train_from_outcomes(lookback=lookback)  # type: ignore[attr-defined]


def score_symbol(symbol: str, timeframe: str = '1h') -> Dict[str, Any]:
    mod = _load_ml_module()
    return mod.score_symbol(symbol, timeframe=timeframe)  # type: ignore[attr-defined]


def score_symbol_with_pattern(symbol: str, timeframe: str, pattern: str) -> Dict[str, Any]:
    mod = _load_ml_module()
    return mod.score_symbol_with_pattern(symbol, timeframe, pattern)  # type: ignore[attr-defined]


# Additional utilities exposed via instance methods
def get_model_info(asset_class: str, timeframe: str, regime: str = 'all', version: str = 'latest') -> Dict[str, Any]:
    mod = _load_ml_module()
    system = mod.TradingMLSystem()  # type: ignore[attr-defined]
    return system.get_model_info(asset_class, timeframe, regime, version)


def list_available_models() -> Dict[str, Any]:
    mod = _load_ml_module()
    system = mod.TradingMLSystem()  # type: ignore[attr-defined]
    return system.list_available_models()


def get_feature_contributions(symbol: str, timeframe: str = '1h') -> Dict[str, Any]:
    mod = _load_ml_module()
    system = mod.TradingMLSystem()  # type: ignore[attr-defined]
    return system.get_feature_contributions(symbol, timeframe)


def promote_model(asset_class: str, timeframe: str, regime: str, to_version: str, pattern: str | None = None) -> Dict[str, Any]:
    mod = _load_ml_module()
    system = mod.TradingMLSystem()  # type: ignore[attr-defined]
    return system.promote_model(asset_class, timeframe, regime, to_version, pattern=pattern)


def get_active_version(asset_class: str, timeframe: str, regime: str, pattern: str | None = None) -> Dict[str, Any]:
    mod = _load_ml_module()
    system = mod.TradingMLSystem()  # type: ignore[attr-defined]
    v = system.get_active_version(asset_class, timeframe, regime, pattern=pattern)
    return {'success': True, 'active_version': v}
