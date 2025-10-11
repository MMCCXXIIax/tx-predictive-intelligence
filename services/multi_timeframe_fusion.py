"""
Multi-Timeframe Fusion System
Scores symbols across multiple timeframes (1h, 4h, 1D) and combines predictions
using weighted ensemble for more robust signals.
"""

import logging
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TimeframeScore:
    """Individual timeframe scoring result"""
    timeframe: str
    prediction: float
    confidence: str
    features_used: int
    model_version: str
    success: bool
    error: Optional[str] = None


@dataclass
class FusionResult:
    """Multi-timeframe fusion result"""
    symbol: str
    fused_score: float
    confidence_level: str
    timeframe_scores: Dict[str, TimeframeScore]
    weights_used: Dict[str, float]
    recommendation: str
    metadata: Dict[str, Any]


class MultiTimeframeFusion:
    """
    Scores a symbol across multiple timeframes and fuses predictions
    using configurable weighting strategies
    """
    
    def __init__(self, score_function):
        """
        Args:
            score_function: Function that takes (symbol, timeframe) and returns score dict
        """
        self.score_function = score_function
        
        # Default timeframes and weights
        self.timeframes = ['1h', '4h', '1d']
        self.default_weights = {
            '1h': 0.25,   # Short-term: lower weight
            '4h': 0.35,   # Medium-term: higher weight
            '1d': 0.40    # Long-term: highest weight (trend is king)
        }
        
        # Adaptive weighting based on market regime
        self.regime_weights = {
            'trending': {'1h': 0.20, '4h': 0.30, '1d': 0.50},  # Favor longer TF in trends
            'ranging': {'1h': 0.40, '4h': 0.35, '1d': 0.25},   # Favor shorter TF in ranges
            'volatile': {'1h': 0.35, '4h': 0.35, '1d': 0.30},  # Balanced
            'default': {'1h': 0.25, '4h': 0.35, '1d': 0.40}
        }
    
    def score_multi_timeframe(self, symbol: str, regime: str = 'default',
                             custom_weights: Optional[Dict[str, float]] = None) -> FusionResult:
        """
        Score symbol across multiple timeframes and fuse results
        
        Args:
            symbol: Trading symbol
            regime: Market regime for adaptive weighting
            custom_weights: Optional custom weights per timeframe
        
        Returns:
            FusionResult with fused score and individual timeframe results
        """
        try:
            # Determine weights
            if custom_weights:
                weights = custom_weights
            else:
                weights = self.regime_weights.get(regime, self.default_weights)
            
            # Score each timeframe in parallel
            timeframe_scores = {}
            
            with ThreadPoolExecutor(max_workers=3) as executor:
                future_to_tf = {
                    executor.submit(self._score_timeframe, symbol, tf): tf
                    for tf in self.timeframes
                }
                
                for future in as_completed(future_to_tf):
                    tf = future_to_tf[future]
                    try:
                        score_result = future.result(timeout=10)
                        timeframe_scores[tf] = score_result
                    except Exception as e:
                        logger.warning(f"Timeframe {tf} scoring failed: {e}")
                        timeframe_scores[tf] = TimeframeScore(
                            timeframe=tf,
                            prediction=0.5,
                            confidence='unknown',
                            features_used=0,
                            model_version='error',
                            success=False,
                            error=str(e)
                        )
            
            # Fuse predictions using weighted average
            fused_score = self._fuse_predictions(timeframe_scores, weights)
            
            # Determine confidence level
            confidence_level = self._determine_confidence(timeframe_scores, fused_score)
            
            # Generate recommendation
            recommendation = self._generate_recommendation(fused_score, confidence_level, timeframe_scores)
            
            # Build metadata
            metadata = {
                'regime': regime,
                'weights_applied': weights,
                'timeframes_scored': len([s for s in timeframe_scores.values() if s.success]),
                'alignment_score': self._calculate_alignment(timeframe_scores),
                'divergence_detected': self._detect_divergence(timeframe_scores)
            }
            
            return FusionResult(
                symbol=symbol,
                fused_score=fused_score,
                confidence_level=confidence_level,
                timeframe_scores=timeframe_scores,
                weights_used=weights,
                recommendation=recommendation,
                metadata=metadata
            )
        
        except Exception as e:
            logger.error(f"Multi-timeframe fusion failed for {symbol}: {e}")
            # Return safe default
            return FusionResult(
                symbol=symbol,
                fused_score=0.5,
                confidence_level='error',
                timeframe_scores={},
                weights_used={},
                recommendation='SKIP - scoring error',
                metadata={'error': str(e)}
            )
    
    def _score_timeframe(self, symbol: str, timeframe: str) -> TimeframeScore:
        """Score a single timeframe"""
        try:
            result = self.score_function(symbol, timeframe=timeframe)
            
            if not result.get('success'):
                return TimeframeScore(
                    timeframe=timeframe,
                    prediction=0.5,
                    confidence='unknown',
                    features_used=0,
                    model_version='error',
                    success=False,
                    error=result.get('error', 'Unknown error')
                )
            
            prediction = result.get('prediction') or result.get('score') or result.get('probability') or 0.5
            
            return TimeframeScore(
                timeframe=timeframe,
                prediction=float(prediction),
                confidence=result.get('confidence', 'medium'),
                features_used=result.get('features_used', 0),
                model_version=result.get('model_version', 'unknown'),
                success=True
            )
        
        except Exception as e:
            return TimeframeScore(
                timeframe=timeframe,
                prediction=0.5,
                confidence='error',
                features_used=0,
                model_version='error',
                success=False,
                error=str(e)
            )
    
    def _fuse_predictions(self, timeframe_scores: Dict[str, TimeframeScore],
                         weights: Dict[str, float]) -> float:
        """Weighted average fusion of timeframe predictions"""
        total_weight = 0.0
        weighted_sum = 0.0
        
        for tf, score in timeframe_scores.items():
            if score.success:
                weight = weights.get(tf, 0.0)
                weighted_sum += score.prediction * weight
                total_weight += weight
        
        if total_weight == 0:
            return 0.5  # Neutral if no successful scores
        
        return weighted_sum / total_weight
    
    def _determine_confidence(self, timeframe_scores: Dict[str, TimeframeScore],
                            fused_score: float) -> str:
        """Determine overall confidence based on agreement and individual confidences"""
        successful_scores = [s for s in timeframe_scores.values() if s.success]
        
        if len(successful_scores) == 0:
            return 'none'
        
        # Check alignment (all pointing same direction)
        predictions = [s.prediction for s in successful_scores]
        std_dev = self._std(predictions)
        
        # High confidence: low divergence + extreme fused score
        if std_dev < 0.1 and (fused_score > 0.7 or fused_score < 0.3):
            return 'very_high'
        elif std_dev < 0.15 and (fused_score > 0.65 or fused_score < 0.35):
            return 'high'
        elif std_dev < 0.2:
            return 'medium'
        else:
            return 'low'
    
    def _generate_recommendation(self, fused_score: float, confidence: str,
                                timeframe_scores: Dict[str, TimeframeScore]) -> str:
        """Generate trading recommendation"""
        if confidence in ['none', 'error']:
            return 'SKIP - insufficient data'
        
        # Strong signals
        if fused_score >= 0.75 and confidence in ['high', 'very_high']:
            return 'STRONG BUY'
        elif fused_score <= 0.25 and confidence in ['high', 'very_high']:
            return 'STRONG SELL'
        
        # Moderate signals
        elif fused_score >= 0.65:
            return 'BUY'
        elif fused_score <= 0.35:
            return 'SELL'
        
        # Weak/neutral
        elif 0.45 <= fused_score <= 0.55:
            return 'NEUTRAL - wait for clarity'
        else:
            return 'HOLD - monitor'
    
    def _calculate_alignment(self, timeframe_scores: Dict[str, TimeframeScore]) -> float:
        """Calculate alignment score (0-1) across timeframes"""
        successful = [s.prediction for s in timeframe_scores.values() if s.success]
        if len(successful) < 2:
            return 0.0
        
        # Alignment = 1 - normalized standard deviation
        std_dev = self._std(successful)
        max_std = 0.5  # Max possible std for [0,1] range
        alignment = max(0.0, 1.0 - (std_dev / max_std))
        return alignment
    
    def _detect_divergence(self, timeframe_scores: Dict[str, TimeframeScore]) -> bool:
        """Detect if timeframes are diverging (conflicting signals)"""
        successful = [s for s in timeframe_scores.values() if s.success]
        if len(successful) < 2:
            return False
        
        predictions = [s.prediction for s in successful]
        
        # Divergence: some > 0.6 and some < 0.4
        has_bullish = any(p > 0.6 for p in predictions)
        has_bearish = any(p < 0.4 for p in predictions)
        
        return has_bullish and has_bearish
    
    @staticmethod
    def _std(values: List[float]) -> float:
        """Calculate standard deviation"""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5


# Wrapper function for API
def score_multi_timeframe(symbol: str, score_function, regime: str = 'default',
                         custom_weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    """
    Score symbol across multiple timeframes
    
    Args:
        symbol: Trading symbol
        score_function: Function(symbol, timeframe) -> score dict
        regime: Market regime for adaptive weighting
        custom_weights: Optional custom weights
    
    Returns:
        Dict with fused score and breakdown
    """
    try:
        fusion = MultiTimeframeFusion(score_function)
        result = fusion.score_multi_timeframe(symbol, regime, custom_weights)
        
        return {
            'success': True,
            'symbol': result.symbol,
            'fused_score': result.fused_score,
            'confidence': result.confidence_level,
            'recommendation': result.recommendation,
            'timeframe_breakdown': {
                tf: {
                    'prediction': score.prediction,
                    'confidence': score.confidence,
                    'success': score.success,
                    'weight': result.weights_used.get(tf, 0.0)
                }
                for tf, score in result.timeframe_scores.items()
            },
            'metadata': result.metadata
        }
    
    except Exception as e:
        logger.error(f"Multi-timeframe scoring failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }
