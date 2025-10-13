"""
Pattern Heatmap Generator
Creates multi-timeframe pattern confidence matrix for visualization
"""

import logging
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class PatternHeatmapGenerator:
    """
    Generates pattern detection heatmap across multiple timeframes
    """
    
    TIMEFRAMES = ['15m', '1h', '4h', '1d']
    
    COMMON_PATTERNS = [
        'Bullish Engulfing',
        'Bearish Engulfing',
        'Hammer',
        'Shooting Star',
        'Morning Star',
        'Evening Star',
        'Doji',
        'Piercing Line',
        'Dark Cloud Cover',
        'Three White Soldiers',
        'Three Black Crows',
        'Harami'
    ]
    
    def __init__(self, pattern_detector):
        """
        Args:
            pattern_detector: Instance of pattern detection service
        """
        self.pattern_detector = pattern_detector
        self.logger = logger
    
    def generate_heatmap(
        self,
        symbol: str,
        patterns: Optional[List[str]] = None,
        timeframes: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate pattern confidence heatmap across timeframes
        
        Args:
            symbol: Stock symbol
            patterns: List of patterns to check (default: all common patterns)
            timeframes: List of timeframes (default: 15m, 1h, 4h, 1d)
        
        Returns:
            Dict with heatmap data
        """
        try:
            patterns_to_check = patterns or self.COMMON_PATTERNS
            timeframes_to_check = timeframes or self.TIMEFRAMES
            
            heatmap_data = []
            
            for pattern in patterns_to_check:
                row = {
                    'pattern': pattern,
                    'pattern_type': self._get_pattern_type(pattern),
                    'timeframes': {}
                }
                
                for tf in timeframes_to_check:
                    try:
                        # Detect pattern for this timeframe
                        confidence = self._detect_pattern_for_timeframe(
                            symbol, pattern, tf
                        )
                        
                        row['timeframes'][tf] = {
                            'confidence': round(confidence, 1),
                            'status': self._get_confidence_status(confidence),
                            'color': self._get_color_for_confidence(confidence)
                        }
                    except Exception as e:
                        self.logger.warning(f"Error detecting {pattern} on {tf}: {e}")
                        row['timeframes'][tf] = {
                            'confidence': 0,
                            'status': 'unavailable',
                            'color': 'gray'
                        }
                
                # Calculate average confidence across timeframes
                confidences = [
                    tf_data['confidence'] 
                    for tf_data in row['timeframes'].values() 
                    if tf_data['confidence'] > 0
                ]
                row['avg_confidence'] = round(sum(confidences) / len(confidences), 1) if confidences else 0
                
                heatmap_data.append(row)
            
            # Sort by average confidence (highest first)
            heatmap_data.sort(key=lambda x: x['avg_confidence'], reverse=True)
            
            # Calculate consensus patterns (high confidence across multiple TFs)
            consensus_patterns = [
                row for row in heatmap_data
                if row['avg_confidence'] >= 70 and
                sum(1 for tf in row['timeframes'].values() if tf['confidence'] >= 70) >= 2
            ]
            
            return {
                'success': True,
                'symbol': symbol,
                'timestamp': datetime.utcnow().isoformat(),
                'heatmap': heatmap_data,
                'consensus_patterns': [p['pattern'] for p in consensus_patterns],
                'timeframes': timeframes_to_check,
                'legend': {
                    'ELITE': {'range': '80-100', 'color': 'darkgreen'},
                    'HIGH': {'range': '70-80', 'color': 'green'},
                    'GOOD': {'range': '60-70', 'color': 'lightgreen'},
                    'MODERATE': {'range': '50-60', 'color': 'yellow'},
                    'WEAK': {'range': '<50', 'color': 'orange'},
                    'NONE': {'range': '0', 'color': 'red'}
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error generating heatmap: {e}")
            return {
                'success': False,
                'error': str(e),
                'symbol': symbol
            }
    
    def _detect_pattern_for_timeframe(
        self,
        symbol: str,
        pattern: str,
        timeframe: str
    ) -> float:
        """
        Detect pattern confidence for specific timeframe
        
        Returns:
            Confidence score (0-100)
        """
        # This would call your actual pattern detection logic
        # For now, using placeholder that integrates with existing detector
        
        try:
            # Map timeframe to period for data fetching
            period_map = {
                '15m': '5d',
                '1h': '1mo',
                '4h': '3mo',
                '1d': '1y'
            }
            
            period = period_map.get(timeframe, '1mo')
            
            # Use existing pattern detector
            result = self.pattern_detector.detect_pattern(
                symbol=symbol,
                pattern_name=pattern,
                timeframe=timeframe,
                period=period
            )
            
            if result and 'confidence' in result:
                return result['confidence']
            
            return 0
            
        except Exception as e:
            self.logger.warning(f"Pattern detection failed for {symbol} {pattern} {timeframe}: {e}")
            return 0
    
    def _get_pattern_type(self, pattern_name: str) -> str:
        """Determine pattern type"""
        bullish_keywords = ['bullish', 'hammer', 'morning', 'piercing', 'white', 'soldiers']
        bearish_keywords = ['bearish', 'shooting', 'evening', 'dark', 'black', 'crows']
        
        pattern_lower = pattern_name.lower()
        
        if any(kw in pattern_lower for kw in bullish_keywords):
            return 'bullish'
        elif any(kw in pattern_lower for kw in bearish_keywords):
            return 'bearish'
        else:
            return 'neutral'
    
    def _get_confidence_status(self, confidence: float) -> str:
        """Get status label for confidence"""
        if confidence >= 80:
            return 'ELITE'
        elif confidence >= 70:
            return 'HIGH'
        elif confidence >= 60:
            return 'GOOD'
        elif confidence >= 50:
            return 'MODERATE'
        elif confidence > 0:
            return 'WEAK'
        else:
            return 'NONE'
    
    def _get_color_for_confidence(self, confidence: float) -> str:
        """Get color code for confidence level"""
        if confidence >= 80:
            return 'darkgreen'
        elif confidence >= 70:
            return 'green'
        elif confidence >= 60:
            return 'lightgreen'
        elif confidence >= 50:
            return 'yellow'
        elif confidence > 0:
            return 'orange'
        else:
            return 'red'
