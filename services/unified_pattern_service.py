"""
Unified Pattern Detection Service
Manages both Hybrid Pro and AI Elite detection modes
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from services.detection_modes import (
    DetectionMode, PatternDetectionResult,
    HYBRID_PRO_CONFIG, AI_ELITE_CONFIG, get_mode_config
)
from services.hybrid_pro_detector import HybridProDetector
from services.ai_elite_detector import AIEliteDetector

logger = logging.getLogger(__name__)


class UnifiedPatternDetectionService:
    """
    Unified service managing both detection modes
    
    Modes:
    - HYBRID_PRO: AI + Rules + Ensemble (Conservative, 75-85% accuracy)
    - AI_ELITE: Pure AI + RL + Multi-Modal (Aggressive, 65-95% accuracy)
    """
    
    def __init__(self):
        self.hybrid_detector = HybridProDetector()
        self.ai_elite_detector = AIEliteDetector()
        self.default_mode = DetectionMode.HYBRID_PRO
        
        logger.info("Unified Pattern Detection Service initialized")
        logger.info(f"  - Hybrid Pro: {HYBRID_PRO_CONFIG.name}")
        logger.info(f"  - AI Elite: {AI_ELITE_CONFIG.name}")
    
    def detect_patterns(
        self,
        symbol: str,
        mode: DetectionMode = None,
        timeframe: str = '1h',
        lookback_days: int = 5
    ) -> List[PatternDetectionResult]:
        """
        Detect patterns using specified mode
        
        Args:
            symbol: Trading symbol (e.g., 'AAPL', 'BTC-USD')
            mode: Detection mode (HYBRID_PRO or AI_ELITE)
            timeframe: Chart timeframe ('1m', '5m', '15m', '30m', '1h', '4h', '1d')
            lookback_days: Days of historical data to analyze
            
        Returns:
            List of detected patterns with full transparency
        """
        mode = mode or self.default_mode
        
        try:
            logger.info(f"Detecting patterns for {symbol} using {mode.value} mode")
            
            if mode == DetectionMode.HYBRID_PRO:
                results = self.hybrid_detector.detect_patterns(
                    symbol, timeframe, lookback_days
                )
            elif mode == DetectionMode.AI_ELITE:
                results = self.ai_elite_detector.detect_patterns(
                    symbol, timeframe, lookback_days
                )
            else:
                raise ValueError(f"Unknown detection mode: {mode}")
            
            logger.info(f"Detected {len(results)} patterns for {symbol}")
            return results
            
        except Exception as e:
            logger.error(f"Pattern detection failed for {symbol}: {e}")
            return []
    
    def detect_patterns_both_modes(
        self,
        symbol: str,
        timeframe: str = '1h',
        lookback_days: int = 5
    ) -> Dict[str, List[PatternDetectionResult]]:
        """
        Detect patterns using BOTH modes for comparison
        
        Returns:
            {
                'hybrid_pro': [patterns],
                'ai_elite': [patterns],
                'comparison': {comparison metrics}
            }
        """
        try:
            logger.info(f"Running dual-mode detection for {symbol}")
            
            # Run both detectors
            hybrid_results = self.hybrid_detector.detect_patterns(
                symbol, timeframe, lookback_days
            )
            
            ai_elite_results = self.ai_elite_detector.detect_patterns(
                symbol, timeframe, lookback_days
            )
            
            # Generate comparison
            comparison = self._compare_results(hybrid_results, ai_elite_results)
            
            return {
                'hybrid_pro': hybrid_results,
                'ai_elite': ai_elite_results,
                'comparison': comparison,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Dual-mode detection failed: {e}")
            return {
                'hybrid_pro': [],
                'ai_elite': [],
                'comparison': {},
                'error': str(e)
            }
    
    def _compare_results(
        self,
        hybrid_results: List[PatternDetectionResult],
        ai_elite_results: List[PatternDetectionResult]
    ) -> Dict[str, Any]:
        """Compare results from both modes"""
        try:
            # Count patterns
            hybrid_count = len(hybrid_results)
            ai_elite_count = len(ai_elite_results)
            
            # Average confidence
            hybrid_avg_conf = (
                sum(r.confidence for r in hybrid_results) / hybrid_count
                if hybrid_count > 0 else 0
            )
            ai_elite_avg_conf = (
                sum(r.confidence for r in ai_elite_results) / ai_elite_count
                if ai_elite_count > 0 else 0
            )
            
            # Find common patterns
            hybrid_patterns = set(r.pattern_name for r in hybrid_results)
            ai_elite_patterns = set(r.pattern_name for r in ai_elite_results)
            common_patterns = hybrid_patterns.intersection(ai_elite_patterns)
            unique_hybrid = hybrid_patterns - ai_elite_patterns
            unique_ai_elite = ai_elite_patterns - hybrid_patterns
            
            # Priority distribution
            hybrid_priorities = {}
            for r in hybrid_results:
                hybrid_priorities[r.alert_priority] = hybrid_priorities.get(r.alert_priority, 0) + 1
            
            ai_elite_priorities = {}
            for r in ai_elite_results:
                ai_elite_priorities[r.alert_priority] = ai_elite_priorities.get(r.alert_priority, 0) + 1
            
            return {
                'pattern_counts': {
                    'hybrid_pro': hybrid_count,
                    'ai_elite': ai_elite_count,
                    'difference': ai_elite_count - hybrid_count
                },
                'average_confidence': {
                    'hybrid_pro': round(hybrid_avg_conf, 4),
                    'ai_elite': round(ai_elite_avg_conf, 4),
                    'difference': round(ai_elite_avg_conf - hybrid_avg_conf, 4)
                },
                'pattern_overlap': {
                    'common': list(common_patterns),
                    'unique_to_hybrid': list(unique_hybrid),
                    'unique_to_ai_elite': list(unique_ai_elite),
                    'overlap_percentage': round(
                        len(common_patterns) / max(len(hybrid_patterns), 1) * 100, 1
                    )
                },
                'priority_distribution': {
                    'hybrid_pro': hybrid_priorities,
                    'ai_elite': ai_elite_priorities
                },
                'recommendation': self._generate_recommendation(
                    hybrid_count, ai_elite_count,
                    hybrid_avg_conf, ai_elite_avg_conf
                )
            }
            
        except Exception as e:
            logger.error(f"Comparison failed: {e}")
            return {'error': str(e)}
    
    def _generate_recommendation(
        self,
        hybrid_count: int,
        ai_elite_count: int,
        hybrid_conf: float,
        ai_elite_conf: float
    ) -> str:
        """Generate recommendation based on comparison"""
        if hybrid_conf > ai_elite_conf + 0.10:
            return "Hybrid Pro showing stronger signals - consider conservative approach"
        elif ai_elite_conf > hybrid_conf + 0.10:
            return "AI Elite showing stronger signals - consider aggressive approach"
        elif ai_elite_count > hybrid_count * 1.5:
            return "AI Elite finding more patterns - good for discovery"
        elif hybrid_count > ai_elite_count * 1.5:
            return "Hybrid Pro more selective - good for quality over quantity"
        else:
            return "Both modes performing similarly - use based on preference"
    
    def get_mode_info(self, mode: DetectionMode) -> Dict[str, Any]:
        """Get information about a detection mode"""
        config = get_mode_config(mode)
        return config.to_dict()
    
    def get_all_modes_info(self) -> Dict[str, Any]:
        """Get information about all detection modes"""
        return {
            'hybrid_pro': HYBRID_PRO_CONFIG.to_dict(),
            'ai_elite': AI_ELITE_CONFIG.to_dict(),
            'default_mode': self.default_mode.value
        }
    
    def set_default_mode(self, mode: DetectionMode):
        """Set default detection mode"""
        self.default_mode = mode
        logger.info(f"Default detection mode set to: {mode.value}")
    
    def format_results_for_api(
        self,
        results: List[PatternDetectionResult]
    ) -> List[Dict[str, Any]]:
        """Format results for API response"""
        return [result.to_dict() for result in results]
