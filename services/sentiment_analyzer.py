"""
TX Sentiment Analysis Engine
Real-time sentiment analysis from Twitter, Reddit, and news feeds
"""

import json
import re
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
import requests
import time
import random
from threading import Lock
import logging

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
        
        # External API credentials (env-driven; set in Render as environment variables)
        self.twitter_bearer_token = os.getenv('TWITTER_BEARER_TOKEN')  # Provide via environment
        self.reddit_client_id = None      # Set via environment
        self.news_api_key = None          # Set via environment
        self.logger = logging.getLogger(__name__)
        
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
        
        # Twitter request metrics
        self.twitter_metrics = {
            'success': 0,
            'fail': 0,
            'skipped': 0,
            'last_status': None,
            'last_error': None,
            'last_ts': None
        }
    
    def analyze_symbol_sentiment(self, symbol: str, force_refresh: bool = False) -> SentimentScore:
        """
        Analyze sentiment for a specific symbol (crypto or equity)
        """
        # normalize key (crypto keywords are lowercase)
        key = (symbol or '').lower()
        
        # Check cache first (unless force refresh)
        if not force_refresh and self._is_cache_valid(key):
            return self.sentiment_cache[key]
        
        sentiment_score = SentimentScore(key)
        
        # Analyze sentiment from different sources
        twitter_sentiment = self._analyze_twitter_sentiment(key)
        reddit_sentiment = self._analyze_reddit_sentiment(key)
        news_sentiment = self._analyze_news_sentiment(key)
        
        # Combine sentiments with weights (only if data available)
        sentiment_score.sources = {}
        if twitter_sentiment:
            sentiment_score.sources['twitter'] = twitter_sentiment.get('sentiment', 0.0)
        if reddit_sentiment:
            sentiment_score.sources['reddit'] = reddit_sentiment.get('sentiment', 0.0)
        if news_sentiment:
            sentiment_score.sources['news'] = news_sentiment.get('sentiment', 0.0)
        
        # Calculate weighted overall sentiment
        weights = {'twitter': 0.4, 'reddit': 0.3, 'news': 0.3}
        total_sentiment = 0.0
        total_weight = 0.0
        for source, weight in weights.items():
            if source in sentiment_score.sources:
                total_sentiment += float(sentiment_score.sources[source]) * weight
                total_weight += weight
        sentiment_score.overall_sentiment = total_sentiment / total_weight if total_weight > 0 else 0.0
        
        # Calculate confidence based on volume and consistency (only from real sources)
        sentiment_score.volume = int(
            (twitter_sentiment.get('volume', 0) if twitter_sentiment else 0) +
            (reddit_sentiment.get('volume', 0) if reddit_sentiment else 0) +
            (news_sentiment.get('volume', 0) if news_sentiment else 0)
        )
        sentiment_score.confidence = self._calculate_confidence(
            sentiment_score.sources, sentiment_score.volume
        )
        
        # Trending score and key phrases
        sentiment_score.trending_score = self._calculate_trending_score(key)
        sentiment_score.key_phrases = self._extract_key_phrases(
            twitter_sentiment, reddit_sentiment, news_sentiment
        )
        
        # Cache the result
        with self.cache_lock:
            self.sentiment_cache[key] = sentiment_score
            self.last_update[key] = datetime.now(timezone.utc)
        
        return sentiment_score
    
    def _is_cache_valid(self, symbol: str, max_age_minutes: int = 15) -> bool:
        """Check if cached sentiment is still valid"""
        if symbol not in self.sentiment_cache or symbol not in self.last_update:
            return False
        age = datetime.now(timezone.utc) - self.last_update[symbol]
        return age.total_seconds() < (max_age_minutes * 60)
    
    def _analyze_twitter_sentiment(self, symbol: str) -> Dict:
        """Analyze Twitter sentiment using Recent Search if bearer token is set; fallback to simulated."""
        # If bearer token is not configured, fallback to simulation
        if not self.twitter_bearer_token:
            # Metrics: skipped (no token)
            self.twitter_metrics['skipped'] += 1
            self.twitter_metrics['last_status'] = 'no_token'
            self.twitter_metrics['last_error'] = None
            self.twitter_metrics['last_ts'] = datetime.now(timezone.utc).isoformat()
            self.logger.info("Twitter sentiment skipped: no TWITTER_BEARER_TOKEN configured")
            # Return None instead of fake data
            return None
        
        # Build query terms
        if symbol in self.crypto_keywords:
            terms = self.crypto_keywords.get(symbol, [symbol])
        else:
            s_up = symbol.upper()
            terms = [symbol, f"${s_up}"]
        # Deduplicate and sanitize
        terms = list(dict.fromkeys([t for t in terms if t]))
        terms = [re.sub(r"\s+", " ", t).strip() for t in terms]
        query = " OR ".join([f"(\"{t}\")" if ' ' in t else t for t in terms])
        
        url = "https://api.twitter.com/2/tweets/search/recent"
        headers = {"Authorization": f"Bearer {self.twitter_bearer_token}"}
        params = {
            "query": f"{query} lang:en -is:retweet",
            "max_results": 50,
            "tweet.fields": "created_at,lang,public_metrics"
        }
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=10)
            if resp.status_code != 200:
                # Record failure status before raising
                self.twitter_metrics['fail'] += 1
                self.twitter_metrics['last_status'] = resp.status_code
                self.twitter_metrics['last_error'] = resp.text[:200]
                self.twitter_metrics['last_ts'] = datetime.now(timezone.utc).isoformat()
                self.logger.warning(f"Twitter API error {resp.status_code}: {resp.text[:200]}")
                raise RuntimeError(f"Twitter API error {resp.status_code}: {resp.text[:200]}")
            data = resp.json() or {}
            tweets = data.get('data', [])
            if not tweets:
                # Successful call but empty data
                self.twitter_metrics['success'] += 1
                self.twitter_metrics['last_status'] = 200
                self.twitter_metrics['last_error'] = None
                self.twitter_metrics['last_ts'] = datetime.now(timezone.utc).isoformat()
                return {
                    'sentiment': 0.0,
                    'volume': 0,
                    'bullish': 0,
                    'bearish': 0,
                    'neutral': 0,
                    'source': 'twitter'
                }
            bullish = 0
            bearish = 0
            neutral = 0
            bull_set = set(self.bullish_keywords)
            bear_set = set(self.bearish_keywords)
            for t in tweets:
                text = (t.get('text') or '').lower()
                tokens = re.findall(r"[a-z$#]+", text)
                score = 0
                for tok in tokens:
                    if tok in bull_set:
                        score += 1
                    if tok in bear_set:
                        score -= 1
                if score > 0:
                    bullish += 1
                elif score < 0:
                    bearish += 1
                else:
                    neutral += 1
            total = bullish + bearish + neutral
            sentiment = ((bullish - bearish) / total) if total else 0.0
            # Metrics: success
            self.twitter_metrics['success'] += 1
            self.twitter_metrics['last_status'] = 200
            self.twitter_metrics['last_error'] = None
            self.twitter_metrics['last_ts'] = datetime.now(timezone.utc).isoformat()
            return {
                'sentiment': float(sentiment),
                'volume': int(total),
                'bullish': int(bullish),
                'bearish': int(bearish),
                'neutral': int(neutral),
                'source': 'twitter'
            }
        except Exception:
            # Fallback to simulated if API fails
            self.twitter_metrics['fail'] += 1
            self.twitter_metrics['last_status'] = 'exception'
            self.twitter_metrics['last_error'] = 'exception'
            self.twitter_metrics['last_ts'] = datetime.now(timezone.utc).isoformat()
            self.logger.exception("Twitter API request failed")
            # Return None instead of fake fallback data
            return None
    
    def _analyze_reddit_sentiment(self, symbol: str) -> Dict:
        """Analyze Reddit sentiment (not implemented - requires Reddit API)"""
        # TODO: Implement real Reddit API (PRAW, Pushshift, etc.)
        # Return None until real API is configured
        return None
    
    def _analyze_news_sentiment(self, symbol: str) -> Dict:
        """Analyze news sentiment (not implemented - requires News API)"""
        # TODO: Implement real News API (NewsAPI, CoinDesk, CryptoCompare, etc.)
        # Return None until real API is configured
        return None
    
    def _calculate_confidence(self, sources: Dict, volume: int) -> float:
        """Calculate confidence based on consistency and volume"""
        if not sources or volume == 0:
            return 0.0
        sentiments = list(sources.values())
        if len(sentiments) <= 1:
            consistency = 1.0
        else:
            avg_sentiment = sum(sentiments) / len(sentiments)
            variance = sum((s - avg_sentiment) ** 2 for s in sentiments) / len(sentiments)
            consistency = max(0.0, 1.0 - variance)  # Lower variance = higher consistency
        volume_score = min(1.0, volume / 1000.0)  # Normalize to 1000 mentions
        confidence = (consistency * 0.6) + (volume_score * 0.4)
        return min(1.0, confidence)
    
    def _calculate_trending_score(self, symbol: str) -> float:
        """Calculate how much the symbol is trending"""
        # TODO: Implement real trending calculation from social media APIs
        # Return 0.0 (neutral) until real data available
        return 0.0
    
    def _extract_key_phrases(self, twitter_data: Dict, reddit_data: Dict, news_data: Dict) -> List[str]:
        """Extract key phrases driving sentiment"""
        # TODO: Implement NLP key phrase extraction
        return []
    
    def enhance_pattern_confidence(self, pattern_detection: Dict, sentiment_score: SentimentScore) -> float:
        """Enhance pattern detection confidence using sentiment analysis"""
        original_confidence = float(pattern_detection.get('confidence', 0.5))
        pattern_name = (pattern_detection.get('pattern', '') or '').lower()
        bullish_patterns = [
            'hammer', 'bullish engulfing', 'morning star', 'piercing line',
            'marubozu', 'three white soldiers'
        ]
        is_bullish_pattern = any(bp in pattern_name for bp in bullish_patterns)
        sentiment_alignment = sentiment_score.overall_sentiment if is_bullish_pattern else -sentiment_score.overall_sentiment
        max_boost = 0.2  # Maximum 20% boost
        sentiment_multiplier = sentiment_alignment * sentiment_score.confidence
        confidence_adjustment = sentiment_multiplier * max_boost
        enhanced_confidence = original_confidence + confidence_adjustment
        return max(0.0, min(1.0, enhanced_confidence))
    
    def get_sentiment_alert_condition(self, symbol: str, pattern_name: str) -> Dict:
        """Check if sentiment conditions warrant an alert"""
        sentiment = self.analyze_symbol_sentiment(symbol)
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
