"""
Sentiment-ML Integration Module
Integrates sentiment analysis features into ML model feature engineering
"""

import logging
from typing import Dict, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)


class SentimentFeatureEngineer:
    """
    Converts sentiment analysis results into ML-ready features
    """
    
    def __init__(self, sentiment_analyzer):
        """
        Args:
            sentiment_analyzer: Instance of TXSentimentAnalyzer
        """
        self.sentiment_analyzer = sentiment_analyzer
    
    def extract_sentiment_features(self, symbol: str) -> Dict[str, float]:
        """
        Extract sentiment features for a symbol
        
        Returns dict of features:
        - sentiment_score: Overall sentiment (-1 to 1)
        - sentiment_confidence: Confidence in sentiment (0 to 1)
        - sentiment_volume: Normalized mention volume
        - sentiment_trending: Trending score
        - sentiment_bullish_ratio: Ratio of bullish to total mentions
        - sentiment_momentum: Change in sentiment over time
        - sentiment_volatility: Volatility of sentiment scores
        """
        try:
            # Get current sentiment
            sentiment = self.sentiment_analyzer.analyze_symbol_sentiment(symbol)
            
            if sentiment is None:
                return self._get_default_features()
            
            # Extract base features
            features = {
                'sentiment_score': float(sentiment.overall_sentiment),
                'sentiment_confidence': float(sentiment.confidence),
                'sentiment_volume': self._normalize_volume(sentiment.volume),
                'sentiment_trending': float(sentiment.trending_score),
            }
            
            # Calculate derived features
            features['sentiment_bullish_ratio'] = self._calculate_bullish_ratio(sentiment)
            features['sentiment_momentum'] = self._calculate_momentum(symbol, sentiment)
            features['sentiment_volatility'] = self._calculate_volatility(symbol)
            
            # Source-specific features
            if sentiment.sources:
                features['sentiment_twitter'] = sentiment.sources.get('twitter', 0.0)
                features['sentiment_reddit'] = sentiment.sources.get('reddit', 0.0)
                features['sentiment_news'] = sentiment.sources.get('news', 0.0)
            else:
                features['sentiment_twitter'] = 0.0
                features['sentiment_reddit'] = 0.0
                features['sentiment_news'] = 0.0
            
            # Interaction features
            features['sentiment_volume_x_score'] = features['sentiment_volume'] * features['sentiment_score']
            features['sentiment_confidence_x_score'] = features['sentiment_confidence'] * abs(features['sentiment_score'])
            
            return features
        
        except Exception as e:
            logger.warning(f"Failed to extract sentiment features for {symbol}: {e}")
            return self._get_default_features()
    
    def _get_default_features(self) -> Dict[str, float]:
        """Return neutral default features when sentiment unavailable"""
        return {
            'sentiment_score': 0.0,
            'sentiment_confidence': 0.0,
            'sentiment_volume': 0.0,
            'sentiment_trending': 0.0,
            'sentiment_bullish_ratio': 0.5,
            'sentiment_momentum': 0.0,
            'sentiment_volatility': 0.0,
            'sentiment_twitter': 0.0,
            'sentiment_reddit': 0.0,
            'sentiment_news': 0.0,
            'sentiment_volume_x_score': 0.0,
            'sentiment_confidence_x_score': 0.0,
        }
    
    def _normalize_volume(self, volume: int) -> float:
        """Normalize volume to 0-1 range using log scale"""
        if volume <= 0:
            return 0.0
        # Log scale normalization (assumes max ~10000 mentions)
        normalized = np.log1p(volume) / np.log1p(10000)
        return min(1.0, normalized)
    
    def _calculate_bullish_ratio(self, sentiment) -> float:
        """Calculate ratio of bullish sentiment"""
        if sentiment.overall_sentiment == 0:
            return 0.5
        # Map -1 to 1 range to 0 to 1 range
        return (sentiment.overall_sentiment + 1.0) / 2.0
    
    def _calculate_momentum(self, symbol: str, current_sentiment) -> float:
        """
        Calculate sentiment momentum (change over time)
        Requires historical sentiment tracking
        """
        try:
            # Get historical sentiment from cache if available
            cache = getattr(self.sentiment_analyzer, 'sentiment_cache', {})
            if symbol not in cache:
                return 0.0
            
            cached = cache[symbol]
            if hasattr(cached, 'overall_sentiment'):
                prev_sentiment = cached.overall_sentiment
                momentum = current_sentiment.overall_sentiment - prev_sentiment
                # Normalize to -1 to 1
                return np.clip(momentum, -1.0, 1.0)
            
            return 0.0
        except:
            return 0.0
    
    def _calculate_volatility(self, symbol: str) -> float:
        """
        Calculate sentiment volatility (how much it fluctuates)
        Requires historical tracking
        """
        # Placeholder: would need historical sentiment data
        # For now, return neutral
        return 0.0


def integrate_sentiment_into_features(base_features: Dict[str, float], 
                                     sentiment_features: Dict[str, float]) -> Dict[str, float]:
    """
    Merge sentiment features with existing technical features
    
    Args:
        base_features: Technical indicator features
        sentiment_features: Sentiment-derived features
    
    Returns:
        Combined feature dict
    """
    combined = base_features.copy()
    combined.update(sentiment_features)
    return combined


def get_sentiment_feature_names() -> list:
    """Return list of sentiment feature names for model training"""
    return [
        'sentiment_score',
        'sentiment_confidence',
        'sentiment_volume',
        'sentiment_trending',
        'sentiment_bullish_ratio',
        'sentiment_momentum',
        'sentiment_volatility',
        'sentiment_twitter',
        'sentiment_reddit',
        'sentiment_news',
        'sentiment_volume_x_score',
        'sentiment_confidence_x_score',
    ]
