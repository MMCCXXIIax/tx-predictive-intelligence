"""
Enhanced Pattern Detection with Layer-by-Layer Breakdown
Provides detailed AI confidence breakdown for frontend visualization
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)


class EnhancedPatternDetector:
    """
    Provides enhanced pattern detection with detailed layer breakdown
    for frontend AI confidence visualization
    """
    
    def __init__(self):
        self.logger = logger
    
    def detect_with_layers(
        self,
        symbol: str,
        pattern_name: str,
        rule_based_score: float,
        deep_learning_score: Optional[float] = None,
        multi_tf_scores: Optional[Dict[str, float]] = None,
        sentiment_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Detect pattern with detailed layer-by-layer breakdown
        
        Args:
            symbol: Stock symbol
            pattern_name: Pattern name
            rule_based_score: Traditional pattern detection score (0-100)
            deep_learning_score: CNN-LSTM confidence (0-100)
            multi_tf_scores: Dict of timeframe scores {'1h': 75, '4h': 82, '1d': 80}
            sentiment_data: Sentiment breakdown from sentiment analyzer
        
        Returns:
            Dict with composite score and detailed layer breakdown
        """
        try:
            # Layer 1: Rule-Based Detection (40% weight)
            rule_weight = 40
            rule_contribution = rule_based_score * (rule_weight / 100)
            
            # Layer 2: Deep Learning (15% weight + boost)
            dl_weight = 15
            dl_boost = 0
            dl_contribution = 0
            
            if deep_learning_score is not None and deep_learning_score >= 85:
                dl_contribution = deep_learning_score * (dl_weight / 100)
                # Boost if DL confidence is very high
                if deep_learning_score >= 90:
                    dl_boost = 15
                elif deep_learning_score >= 85:
                    dl_boost = 10
            
            # Layer 3: Multi-Timeframe Fusion (60% weight)
            mtf_weight = 60
            mtf_contribution = 0
            alignment_score = 0
            
            if multi_tf_scores:
                # Weighted average of timeframes
                tf_weights = {'1h': 25, '4h': 35, '1d': 40}
                weighted_sum = 0
                total_weight = 0
                
                for tf, score in multi_tf_scores.items():
                    weight = tf_weights.get(tf, 33.33)
                    weighted_sum += score * weight
                    total_weight += weight
                
                mtf_avg = weighted_sum / total_weight if total_weight > 0 else 0
                mtf_contribution = mtf_avg * (mtf_weight / 100)
                
                # Calculate alignment (how close scores are to each other)
                if len(multi_tf_scores) > 1:
                    scores_list = list(multi_tf_scores.values())
                    std_dev = np.std(scores_list)
                    # Lower std = higher alignment
                    alignment_score = max(0, 1 - (std_dev / 50))
            
            # Layer 4: Sentiment (10% weight + boost)
            sent_weight = 10
            sent_boost = 0
            sent_contribution = 0
            
            if sentiment_data:
                overall_sent = sentiment_data.get('overall_sentiment', 0.5)
                # Convert 0-1 sentiment to 0-100 score
                sent_score = overall_sent * 100
                sent_contribution = sent_score * (sent_weight / 100)
                
                # Boost if sentiment strongly aligns with pattern direction
                pattern_type = self._get_pattern_type(pattern_name)
                if pattern_type == 'bullish' and overall_sent >= 0.75:
                    sent_boost = 10
                elif pattern_type == 'bearish' and overall_sent <= 0.25:
                    sent_boost = 10
            
            # Calculate composite score
            base_score = rule_contribution + dl_contribution + mtf_contribution + sent_contribution
            total_boost = dl_boost + sent_boost
            composite_score = min(100, base_score + total_boost)
            
            # Determine quality badge
            quality_badge = self._get_quality_badge(composite_score)
            
            # Build detailed response
            response = {
                'pattern_name': pattern_name,
                'symbol': symbol,
                'composite_score': round(composite_score, 2),
                'quality_badge': quality_badge,
                'timestamp': datetime.utcnow().isoformat(),
                'layers': {
                    'rule_based': {
                        'score': round(rule_based_score, 1),
                        'weight': rule_weight,
                        'contribution': round(rule_contribution, 2),
                        'status': self._get_status(rule_based_score),
                        'details': f'Traditional technical analysis detected {pattern_name}'
                    },
                    'deep_learning': {
                        'score': round(deep_learning_score, 1) if deep_learning_score else None,
                        'weight': dl_weight,
                        'contribution': round(dl_contribution, 2),
                        'boost': dl_boost,
                        'status': self._get_status(deep_learning_score) if deep_learning_score else 'unavailable',
                        'model_version': 'v2.1',
                        'details': f'CNN-LSTM neural network confirms pattern with {deep_learning_score:.1f}% confidence' if deep_learning_score else 'Deep learning model not available'
                    },
                    'multi_timeframe': {
                        'score': round(mtf_avg, 1) if multi_tf_scores else None,
                        'weight': mtf_weight,
                        'contribution': round(mtf_contribution, 2),
                        'alignment': round(alignment_score, 3),
                        'status': self._get_status(mtf_avg) if multi_tf_scores else 'unavailable',
                        'timeframes': {
                            tf: {
                                'score': round(score, 1),
                                'weight': tf_weights.get(tf, 33.33),
                                'status': self._get_status(score)
                            }
                            for tf, score in (multi_tf_scores or {}).items()
                        },
                        'details': f'Pattern confirmed across {len(multi_tf_scores or {})} timeframes with {alignment_score:.2f} alignment' if multi_tf_scores else 'Multi-timeframe analysis not available'
                    },
                    'sentiment': {
                        'score': round(sent_score, 1) if sentiment_data else None,
                        'weight': sent_weight,
                        'contribution': round(sent_contribution, 2),
                        'boost': sent_boost,
                        'status': self._get_status(sent_score) if sentiment_data else 'unavailable',
                        'sources': self._format_sentiment_sources(sentiment_data) if sentiment_data else None,
                        'details': self._get_sentiment_details(sentiment_data, pattern_name) if sentiment_data else 'Sentiment analysis not available'
                    }
                }
            }
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error in enhanced detection: {e}")
            return self._fallback_response(symbol, pattern_name, rule_based_score)
    
    def _get_pattern_type(self, pattern_name: str) -> str:
        """Determine if pattern is bullish, bearish, or neutral"""
        bullish_patterns = [
            'bullish engulfing', 'hammer', 'morning star', 'piercing line',
            'three white soldiers', 'inverse head and shoulders', 'double bottom',
            'ascending triangle', 'cup and handle'
        ]
        bearish_patterns = [
            'bearish engulfing', 'shooting star', 'evening star', 'dark cloud cover',
            'three black crows', 'head and shoulders', 'double top',
            'descending triangle', 'rising wedge'
        ]
        
        pattern_lower = pattern_name.lower()
        
        if any(p in pattern_lower for p in bullish_patterns):
            return 'bullish'
        elif any(p in pattern_lower for p in bearish_patterns):
            return 'bearish'
        else:
            return 'neutral'
    
    def _get_status(self, score: Optional[float]) -> str:
        """Get status label based on score"""
        if score is None:
            return 'unavailable'
        elif score >= 80:
            return 'strong'
        elif score >= 60:
            return 'moderate'
        else:
            return 'weak'
    
    def _get_quality_badge(self, score: float) -> str:
        """Get quality badge based on composite score"""
        if score >= 85:
            return 'ELITE'
        elif score >= 75:
            return 'HIGH'
        elif score >= 65:
            return 'GOOD'
        else:
            return 'MODERATE'
    
    def _format_sentiment_sources(self, sentiment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format sentiment sources for frontend"""
        sources = sentiment_data.get('sources', {})
        
        return {
            'news': {
                'score': round(sources.get('news', 0.5) * 100, 1),
                'reliability': 85,
                'count': sentiment_data.get('metrics', {}).get('news_articles', 0)
            },
            'social': {
                'score': round(sources.get('social', 0.5) * 100, 1),
                'reliability': 65,
                'count': sentiment_data.get('metrics', {}).get('social_mentions', 0)
            },
            'technical': {
                'score': round(sources.get('technical', 0.5) * 100, 1),
                'reliability': 90,
                'count': None
            }
        }
    
    def _get_sentiment_details(self, sentiment_data: Dict[str, Any], pattern_name: str) -> str:
        """Generate sentiment details text"""
        overall = sentiment_data.get('overall_sentiment', 0.5)
        label = sentiment_data.get('sentiment_label', 'NEUTRAL')
        news_count = sentiment_data.get('metrics', {}).get('news_articles', 0)
        social_count = sentiment_data.get('metrics', {}).get('social_mentions', 0)
        
        pattern_type = self._get_pattern_type(pattern_name)
        
        if pattern_type == 'bullish' and overall >= 0.7:
            alignment = 'strongly supports'
        elif pattern_type == 'bearish' and overall <= 0.3:
            alignment = 'strongly supports'
        elif pattern_type == 'bullish' and overall >= 0.5:
            alignment = 'supports'
        elif pattern_type == 'bearish' and overall <= 0.5:
            alignment = 'supports'
        else:
            alignment = 'is neutral towards'
        
        return f'Market sentiment is {label} ({overall*100:.0f}%). {news_count} news articles and {social_count} social mentions {alignment} this {pattern_type} pattern.'
    
    def _fallback_response(self, symbol: str, pattern_name: str, score: float) -> Dict[str, Any]:
        """Fallback response if enhanced detection fails"""
        return {
            'pattern_name': pattern_name,
            'symbol': symbol,
            'composite_score': round(score, 2),
            'quality_badge': self._get_quality_badge(score),
            'timestamp': datetime.utcnow().isoformat(),
            'layers': {
                'rule_based': {
                    'score': round(score, 1),
                    'weight': 100,
                    'contribution': round(score, 2),
                    'status': self._get_status(score),
                    'details': 'Basic pattern detection'
                }
            }
        }


# Global instance
enhanced_detector = EnhancedPatternDetector()
