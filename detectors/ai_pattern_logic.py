"""
ai_pattern_logic.py

AI-Enhanced pattern detection with advanced quality scoring.
Combines rule-based detection with 10+ AI features for superior accuracy.
"""

from pattern_registry import pattern_registry
import pandas as pd
import logging

logger = logging.getLogger(__name__)

# Optional ML scorer
try:
    from services.ml_patterns import score_symbol as _ml_score_symbol
except Exception:
    _ml_score_symbol = None  # type: ignore

# Import advanced AI detection
try:
    from detectors.advanced_ai_detection import enhance_pattern_detection
    AI_ENHANCEMENT_AVAILABLE = True
except Exception as e:
    logger.warning(f"Advanced AI detection not available: {e}")
    AI_ENHANCEMENT_AVAILABLE = False


def detect_all_patterns(candles):
    """
    AI-Enhanced pattern detection via registry callbacks.
    Now includes advanced quality scoring with 10+ features.
    """
    results = []

    # Enhanced pattern detection logic
    for detect in pattern_registry:
        try:
            result = detect(candles)

            if result and result.get("detected", False):
                pattern_name = (
                    result.get("pattern") or
                    result.get("pattern_name") or
                    result.get("pattern_type") or
                    "Unknown Pattern"
                )
                category = result.get("pattern_category", "Unknown")
                index = result.get("index", len(candles) - 1)
                confidence = result.get("confidence", 0.70)
                explanation = result.get("explanation", "No explanation provided.")
                candle_time = (
                    candles[index]["time"]
                    if 0 <= index < len(candles) and "time" in candles[index]
                    else None
                )

                results.append({
                    "name": pattern_name,
                    "category": category,
                    "index": index,
                    "confidence": confidence,
                    "explanation": explanation,
                    "candle_time": candle_time
                })

        except Exception:
            # Best-effort; skip failing detectors
            continue
    
    # Apply AI enhancement if available
    if AI_ENHANCEMENT_AVAILABLE and results and len(candles) > 0:
        try:
            # Convert candles to DataFrame for AI analysis
            df = pd.DataFrame(candles)
            
            # Ensure required columns
            required_cols = ['open', 'high', 'low', 'close', 'volume']
            if all(col in df.columns for col in required_cols):
                # Get last candle index
                idx = len(df) - 1
                
                # Enhance all detected patterns with AI features
                results = enhance_pattern_detection(results, df, idx)
                
                logger.info(f"AI-enhanced {len(results)} patterns with advanced features")
            else:
                logger.warning("Missing required columns for AI enhancement")
                
        except Exception as e:
            logger.error(f"AI enhancement failed, using base detection: {e}")
            # Continue with base results if enhancement fails

    return results


def ml_score(symbol: str, timeframe: str = "1h"):
    """Return ML score for a symbol/timeframe using trained model.
    Expected return: {'success': True/False, 'score': float, ...}
    """
    if _ml_score_symbol is None:
        return {"success": False, "error": "ml_not_available"}
    try:
        res = _ml_score_symbol(symbol, timeframe=timeframe)
        return res
    except Exception as e:
        return {"success": False, "error": str(e)}


def detect_with_ml(symbol: str, timeframe: str = "1h", threshold: float = 0.7):
    """Binary detection using ML score and threshold (no heuristics).
    Returns a list with one detection dict if score >= threshold; otherwise empty list.
    """
    res = ml_score(symbol, timeframe)
    if not res.get("success"):
        return []
    score = float(res.get("score", 0.0))
    if score >= float(threshold):
        return [{
            "name": "ML SCORE",
            "category": "ML",
            "index": -1,
            "confidence": score,
            "explanation": f"Model score {score:.3f} >= threshold {threshold}",
            "candle_time": None,
            "symbol": symbol,
            "timeframe": timeframe,
            "detected": True
        }]
    return []


def orchestrate_ml(symbols, timeframes=("1h",), threshold: float = 0.7):
    """Orchestrate ML scoring across multiple symbols/timeframes and return detections.
    Example usage:
        alerts = orchestrate_ml(["AAPL","MSFT"], ("1h","1d"), threshold=0.72)
    """
    results = []
    if not symbols:
        return results
    for s in symbols:
        for tf in timeframes:
            try:
                results.extend(detect_with_ml(s, tf, threshold=threshold))
            except Exception:
                continue
    return results