"""
TX Sentiment Analysis Engine
Real-time sentiment analysis from Twitter, Reddit, and news feeds
"""

import json
import re
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
import requests
import time
from threading import Lock

class SentimentScore:
    """Represents sentiment analysis results"""
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.overall_sentiment = 0.0  # -1.0 (very bearish) to 1.0 (very bullish)
        self.confidence = 0.0  # 0.0 to 1.0
        self.sources = {}  # sentiment by source
        self.volume = 0  # number of mentions
        self.trending_score = 0.0  # how much it's trending
        self.key_phrases = []  # important phrases driving sentiment
        self.timestamp = datetime.now(timezone.utc)
        
    def to_dict(self) -> Dict:
        return {
            'symbol': self.symbol,
            'overall_sentiment': round(self.overall_sentiment, 3),
            'confidence': round(self.confidence, 3),
            'sources': {k: round(v, 3) for k, v in self.sources.items()},
            'volume': self.volume,
            'trending_score': round(self.trending_score, 3),
            'key_phrases': self.key_phrases,
            'timestamp': self.timestamp.isoformat(),
            'sentiment_label': self._get_sentiment_label()
        }
    
    def _get_sentiment_label(self) -> str:
        """Convert numerical sentiment to human-readable label"""
        if self.overall_sentiment >= 0.6:
            return "Very Bullish"
        elif self.overall_sentiment >= 0.2:
            return "Bullish"
        elif self.overall_sentiment >= -0.2:
            return "Neutral"
        elif self.overall_sentiment >= -0.6:
            return "Bearish"
        else:
            return "Very Bearish"

class TXSentimentAnalyzer:
    """Real-time sentiment analysis engine"""
    
    def __init__(self):
        self.sentiment_cache = {}
        self.cache_lock = Lock()
        self.last_update = {}
        
        # Initialize with simulated API credentials
        # In production, these would come from environment variables
        self.twitter_bearer_token = None  # Set via environment
        self.reddit_client_id = None      # Set via environment
        self.news_api_key = None          # Set via environment
        
        # Crypto-specific keywords for better filtering
        self.crypto_keywords = {
            'bitcoin': ['bitcoin', 'btc', '$btc', '#bitcoin'],
            'ethereum': ['ethereum', 'eth', '$eth', '#ethereum'],
            'solana': ['solana', 'sol', '$sol', '#solana'],
        }
        
        # Sentiment keywords
        self.bullish_keywords = [
            'moon', 'bullish', 'pump', 'rally', 'breakout', 'surge', 'rocket',
            'buy', 'long', 'hodl', 'bull', 'green', 'up', 'rise', 'gains'
        ]
        
        self.bearish_keywords = [
            'bear', 'bearish', 'dump', 'crash', 'drop', 'fall', 'red', 'sell',
            'short', 'down', 'decline', 'dip', 'correction', 'loss', 'blood'
        ]
    
    def analyze_symbol_sentiment(self, symbol: str, force_refresh: bool = False) -> SentimentScore:
        """
        Analyze sentiment for a specific cryptocurrency
        
        Args:
            symbol: Crypto symbol (bitcoin, ethereum, etc.)
            force_refresh: Force new analysis instead of using cache
        """
        
        # Check cache first (unless force refresh)
        if not force_refresh and self._is_cache_valid(symbol):
            return self.sentiment_cache[symbol]
        
        sentiment_score = SentimentScore(symbol)
        
        # Analyze sentiment from different sources
        twitter_sentiment = self._analyze_twitter_sentiment(symbol)
        reddit_sentiment = self._analyze_reddit_sentiment(symbol)
        news_sentiment = self._analyze_news_sentiment(symbol)
        
        # Combine sentiments with weights
        sentiment_score.sources = {
            'twitter': twitter_sentiment['sentiment'],
            'reddit': reddit_sentiment['sentiment'],
            'news': news_sentiment['sentiment']
        }
        
        # Calculate weighted overall sentiment
        weights = {'twitter': 0.4, 'reddit': 0.3, 'news': 0.3}
        total_sentiment = 0
        total_weight = 0
        
        for source, weight in weights.items():
            if source in sentiment_score.sources:
                total_sentiment += sentiment_score.sources[source] * weight
                total_weight += weight
        
        sentiment_score.overall_sentiment = total_sentiment / total_weight if total_weight > 0 else 0
        
        # Calculate confidence based on volume and consistency
        sentiment_score.volume = (
            twitter_sentiment.get('volume', 0) +
            reddit_sentiment.get('volume', 0) +
            news_sentiment.get('volume', 0)
        )
        
        sentiment_score.confidence = self._calculate_confidence(
            sentiment_score.sources, sentiment_score.volume
        )
        
        # Calculate trending score
        sentiment_score.trending_score = self._calculate_trending_score(symbol)
        
        # Extract key phrases
        sentiment_score.key_phrases = self._extract_key_phrases(
            twitter_sentiment, reddit_sentiment, news_sentiment
        )
        
        # Cache the result
        with self.cache_lock:
            self.sentiment_cache[symbol] = sentiment_score
            self.last_update[symbol] = datetime.now(timezone.utc)
        
        return sentiment_score
    
    def _is_cache_valid(self, symbol: str, max_age_minutes: int = 15) -> bool:
        """Check if cached sentiment is still valid"""
        if symbol not in self.sentiment_cache or symbol not in self.last_update:
            return False
        
        age = datetime.now(timezone.utc) - self.last_update[symbol]
        return age.total_seconds() < (max_age_minutes * 60)
    
    def _analyze_twitter_sentiment(self, symbol: str) -> Dict:
        """Analyze Twitter sentiment (simulated for now)"""
        
        # In production, this would use Twitter API v2
        # For now, we'll simulate realistic sentiment data
        
        import random
        
        # Simulate Twitter API call
        keywords = self.crypto_keywords.get(symbol, [symbol])
        
        # Simulate tweets analysis
        tweet_count = random.randint(500, 2000)
        bullish_mentions = sum(1 for _ in range(tweet_count) if random.random() < 0.4)
        bearish_mentions = sum(1 for _ in range(tweet_count) if random.random() < 0.3)
        neutral_mentions = tweet_count - bullish_mentions - bearish_mentions
        
        # Calculate sentiment score
        if tweet_count > 0:
            sentiment = (bullish_mentions - bearish_mentions) / tweet_count
        else:
            sentiment = 0
        
        return {
            'sentiment': sentiment,
            'volume': tweet_count,
            'bullish': bullish_mentions,
            'bearish': bearish_mentions,
            'neutral': neutral_mentions,
            'source': 'twitter'
        }
    
    def _analyze_reddit_sentiment(self, symbol: str) -> Dict:
        """Analyze Reddit sentiment (simulated for now)"""
        
        # In production, this would use Reddit API (PRAW)
        # Analyzing r/cryptocurrency, r/bitcoin, r/ethereum, etc.
        
        import random
        
        # Simulate Reddit API call
        post_count = random.randint(50, 200)
        comment_count = random.randint(200, 1000)
        
        total_interactions = post_count + comment_count
        bullish_score = random.uniform(-0.5, 0.8)  # Reddit tends to be more bullish
        
        return {
            'sentiment': bullish_score,
            'volume': total_interactions,
            'posts': post_count,
            'comments': comment_count,
            'source': 'reddit'
        }
    
    def _analyze_news_sentiment(self, symbol: str) -> Dict:
        """Analyze news sentiment (simulated for now)"""
        
        # In production, this would use news APIs like:
        # - NewsAPI
        # - CoinDesk API  
        # - CryptoCompare News
        # - Alpha Vantage News
        
        import random
        
        # Simulate news analysis
        article_count = random.randint(10, 50)
        
        # News tends to be more neutral/bearish
        news_sentiment = random.uniform(-0.3, 0.5)
        
        return {
            'sentiment': news_sentiment,
            'volume': article_count,
            'articles': article_count,
            'source': 'news'
        }
    
    def _calculate_confidence(self, sources: Dict, volume: int) -> float:
        """Calculate confidence based on consistency and volume"""
        
        if not sources or volume == 0:
            return 0.0
        
        # Consistency score (how similar are the sentiments across sources)
        sentiments = list(sources.values())
        if len(sentiments) <= 1:
            consistency = 1.0
        else:
            avg_sentiment = sum(sentiments) / len(sentiments)
            variance = sum((s - avg_sentiment) ** 2 for s in sentiments) / len(sentiments)
            consistency = max(0, 1.0 - variance)  # Lower variance = higher consistency
        
        # Volume score (more mentions = higher confidence)
        volume_score = min(1.0, volume / 1000.0)  # Normalize to 1000 mentions
        
        # Combined confidence
        confidence = (consistency * 0.6) + (volume_score * 0.4)
        
        return min(1.0, confidence)
    
    def _calculate_trending_score(self, symbol: str) -> float:
        """Calculate how much the symbol is trending"""
        
        # In production, this would compare current mention volume
        # to historical average to determine if it's trending
        
        import random
        return random.uniform(0.1, 0.9)
    
    def _extract_key_phrases(self, twitter_data: Dict, reddit_data: Dict, 
                           news_data: Dict) -> List[str]:
        """Extract key phrases driving sentiment"""
        
        # In production, this would use NLP to extract actual phrases
        # For now, simulate common crypto phrases
        
        import random
        
        possible_phrases = [
            "breaking resistance", "bullish momentum", "whale accumulation",
            "institutional adoption", "regulatory clarity", "technical breakout",
            "strong support level", "bearish divergence", "profit taking",
            "market correction", "oversold conditions", "bullish reversal"
        ]
        
        return random.sample(possible_phrases, k=random.randint(2, 5))
    
    def enhance_pattern_confidence(self, pattern_detection: Dict, 
                                 sentiment_score: SentimentScore) -> float:
        """
        Enhance pattern detection confidence using sentiment analysis
        
        Args:
            pattern_detection: Original pattern detection data
            sentiment_score: Sentiment analysis results
            
        Returns:
            Enhanced confidence score
        """
        
        original_confidence = pattern_detection.get('confidence', 0.5)
        pattern_name = pattern_detection.get('pattern', '').lower()
        
        # Determine if pattern is bullish or bearish
        bullish_patterns = [
            'hammer', 'bullish engulfing', 'morning star', 'piercing line',
            'marubozu', 'three white soldiers'
        ]
        
        is_bullish_pattern = any(bp in pattern_name for bp in bullish_patterns)
        
        # Calculate sentiment alignment
        if is_bullish_pattern:
            # Bullish pattern + bullish sentiment = boost confidence
            sentiment_alignment = sentiment_score.overall_sentiment
        else:
            # Bearish pattern + bearish sentiment = boost confidence
            sentiment_alignment = -sentiment_score.overall_sentiment
        
        # Calculate confidence boost/penalty
        max_boost = 0.2  # Maximum 20% boost
        sentiment_multiplier = sentiment_alignment * sentiment_score.confidence
        confidence_adjustment = sentiment_multiplier * max_boost
        
        # Apply the adjustment
        enhanced_confidence = original_confidence + confidence_adjustment
        
        # Ensure confidence stays within bounds [0, 1]
        enhanced_confidence = max(0.0, min(1.0, enhanced_confidence))
        
        return enhanced_confidence
    
    def get_sentiment_alert_condition(self, symbol: str, pattern_name: str) -> Dict:
        """
        Check if sentiment conditions warrant an alert
        
        Returns:
            Alert condition data including whether to trigger alert
        """
        
        sentiment = self.analyze_symbol_sentiment(symbol)
        
        # Define alert thresholds
        high_confidence_threshold = 0.7
        strong_sentiment_threshold = 0.5
        high_volume_threshold = 1000
        
        should_alert = (
            sentiment.confidence >= high_confidence_threshold and
            abs(sentiment.overall_sentiment) >= strong_sentiment_threshold and
            sentiment.volume >= high_volume_threshold
        )
        
        return {
            'should_alert': should_alert,
            'sentiment_data': sentiment.to_dict(),
            'alert_reason': self._generate_alert_reason(sentiment, pattern_name),
            'priority': 'high' if should_alert else 'normal'
        }
    
    def _generate_alert_reason(self, sentiment: SentimentScore, pattern_name: str) -> str:
        """Generate human-readable alert reason"""
        
        sentiment_label = sentiment._get_sentiment_label()
        
        return (f"{pattern_name} detected with {sentiment_label.lower()} market sentiment "
                f"({sentiment.volume} mentions, {sentiment.confidence:.0%} confidence)")

# Global sentiment analyzer
sentiment_analyzer = TXSentimentAnalyzer()