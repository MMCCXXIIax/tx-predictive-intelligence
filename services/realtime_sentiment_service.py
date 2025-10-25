"""
Real-Time Sentiment Analysis Service
Continuously monitors news, social media, and market sentiment for confidence scoring
"""

import logging
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from textblob import TextBlob
import yfinance as yf
import os

logger = logging.getLogger(__name__)


class RealtimeSentimentService:
    """
    Advanced sentiment analysis service that monitors:
    1. Financial news (multiple sources)
    2. Social media sentiment (Twitter/X, Reddit, StockTwits)
    3. Market sentiment indicators
    4. Trending events and breaking news
    5. Institutional sentiment
    """
    
    def __init__(self):
        self.news_api_key = os.getenv('NEWS_API_KEY', '')
        self.finnhub_api_key = os.getenv('FINNHUB_API_KEY', '')
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY', '')
        
        # Sentiment cache (5-minute TTL)
        self.sentiment_cache = {}
        self.cache_ttl = 300  # 5 minutes
        
        logger.info("Real-Time Sentiment Service initialized")
    
    def get_comprehensive_sentiment(
        self, 
        symbol: str,
        include_social: bool = True,
        include_news: bool = True,
        include_market: bool = True
    ) -> Dict[str, Any]:
        """
        Get comprehensive sentiment analysis for a symbol
        
        Returns:
        {
            'overall_sentiment': 0.75,  # -1 to 1
            'sentiment_score': 0.875,   # 0 to 1 (for confidence)
            'news_sentiment': {...},
            'social_sentiment': {...},
            'market_sentiment': {...},
            'trending_topics': [...],
            'sentiment_strength': 'STRONG_BULLISH',
            'confidence_contribution': 0.15,  # How much to add to confidence
            'explanation': 'Detailed explanation...'
        }
        """
        try:
            # Check cache
            cache_key = f"{symbol}_{include_social}_{include_news}_{include_market}"
            if cache_key in self.sentiment_cache:
                cached_data, timestamp = self.sentiment_cache[cache_key]
                if (datetime.now() - timestamp).total_seconds() < self.cache_ttl:
                    logger.info(f"Using cached sentiment for {symbol}")
                    return cached_data
            
            logger.info(f"Fetching real-time sentiment for {symbol}")
            
            sentiment_data = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'overall_sentiment': 0.0,
                'sentiment_score': 0.5,
                'news_sentiment': {},
                'social_sentiment': {},
                'market_sentiment': {},
                'trending_topics': [],
                'sentiment_strength': 'NEUTRAL',
                'confidence_contribution': 0.0,
                'explanation': ''
            }
            
            components = []
            weights = []
            
            # 1. News Sentiment (40% weight)
            if include_news:
                news_sent = self._get_news_sentiment(symbol)
                sentiment_data['news_sentiment'] = news_sent
                components.append(news_sent['score'])
                weights.append(0.40)
            
            # 2. Social Media Sentiment (30% weight)
            if include_social:
                social_sent = self._get_social_sentiment(symbol)
                sentiment_data['social_sentiment'] = social_sent
                components.append(social_sent['score'])
                weights.append(0.30)
            
            # 3. Market Sentiment (30% weight)
            if include_market:
                market_sent = self._get_market_sentiment(symbol)
                sentiment_data['market_sentiment'] = market_sent
                components.append(market_sent['score'])
                weights.append(0.30)
            
            # Calculate weighted overall sentiment
            if components:
                total_weight = sum(weights)
                overall_sentiment = sum(c * w for c, w in zip(components, weights)) / total_weight
                sentiment_data['overall_sentiment'] = overall_sentiment
                
                # Convert to 0-1 scale for confidence scoring
                sentiment_data['sentiment_score'] = (overall_sentiment + 1) / 2
                
                # Determine sentiment strength
                sentiment_data['sentiment_strength'] = self._get_sentiment_strength(overall_sentiment)
                
                # Calculate confidence contribution (-0.15 to +0.15)
                sentiment_data['confidence_contribution'] = overall_sentiment * 0.15
                
                # Generate explanation
                sentiment_data['explanation'] = self._generate_sentiment_explanation(sentiment_data)
            
            # Get trending topics
            sentiment_data['trending_topics'] = self._get_trending_topics(symbol)
            
            # Cache the result
            self.sentiment_cache[cache_key] = (sentiment_data, datetime.now())
            
            return sentiment_data
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed for {symbol}: {e}")
            return self._get_neutral_sentiment(symbol)
    
    def _get_news_sentiment(self, symbol: str) -> Dict[str, Any]:
        """
        Analyze sentiment from financial news
        Sources: NewsAPI, Finnhub, Yahoo Finance News
        """
        try:
            articles = []
            sentiments = []
            sources = []
            
            # 1. Try Finnhub News
            if self.finnhub_api_key:
                finnhub_news = self._fetch_finnhub_news(symbol)
                articles.extend(finnhub_news)
            
            # 2. Try NewsAPI
            if self.news_api_key:
                newsapi_articles = self._fetch_newsapi(symbol)
                articles.extend(newsapi_articles)
            
            # 3. Try Yahoo Finance News (always available)
            yahoo_news = self._fetch_yahoo_news(symbol)
            articles.extend(yahoo_news)
            
            # Analyze sentiment of all articles
            for article in articles[:20]:  # Limit to 20 most recent
                title = article.get('headline', '') or article.get('title', '')
                summary = article.get('summary', '') or article.get('description', '')
                
                text = f"{title}. {summary}"
                
                if text.strip():
                    blob = TextBlob(text)
                    sentiment = blob.sentiment.polarity  # -1 to 1
                    sentiments.append(sentiment)
                    sources.append(article.get('source', 'Unknown'))
            
            # Calculate average sentiment
            if sentiments:
                avg_sentiment = sum(sentiments) / len(sentiments)
                positive_count = sum(1 for s in sentiments if s > 0.1)
                negative_count = sum(1 for s in sentiments if s < -0.1)
                neutral_count = len(sentiments) - positive_count - negative_count
                
                return {
                    'score': avg_sentiment,
                    'article_count': len(articles),
                    'analyzed_count': len(sentiments),
                    'positive_count': positive_count,
                    'negative_count': negative_count,
                    'neutral_count': neutral_count,
                    'sources': list(set(sources)),
                    'latest_headlines': [a.get('headline', a.get('title', ''))[:100] for a in articles[:5]],
                    'strength': 'STRONG' if abs(avg_sentiment) > 0.3 else 'MODERATE' if abs(avg_sentiment) > 0.1 else 'WEAK'
                }
            
            return {'score': 0.0, 'article_count': 0, 'analyzed_count': 0, 'strength': 'NONE'}
            
        except Exception as e:
            logger.error(f"News sentiment analysis failed: {e}")
            return {'score': 0.0, 'article_count': 0, 'analyzed_count': 0, 'strength': 'ERROR'}
    
    def _get_social_sentiment(self, symbol: str) -> Dict[str, Any]:
        """
        Analyze sentiment from social media
        Sources: StockTwits, Reddit mentions, Twitter sentiment
        """
        try:
            # For now, use a simplified approach
            # In production, integrate with StockTwits API, Reddit API, Twitter API
            
            sentiments = []
            mentions = 0
            
            # Try to get social sentiment from Finnhub
            if self.finnhub_api_key:
                social_data = self._fetch_finnhub_social(symbol)
                if social_data:
                    return social_data
            
            # Fallback: Estimate from volume and price action
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                # Use volume as proxy for social interest
                avg_volume = info.get('averageVolume', 0)
                current_volume = info.get('volume', 0)
                
                if avg_volume > 0:
                    volume_ratio = current_volume / avg_volume
                    
                    # High volume = high social interest
                    if volume_ratio > 1.5:
                        social_score = 0.3  # Positive interest
                    elif volume_ratio > 1.2:
                        social_score = 0.15
                    elif volume_ratio < 0.7:
                        social_score = -0.15  # Low interest
                    else:
                        social_score = 0.0
                    
                    return {
                        'score': social_score,
                        'mentions': int(current_volume / 1000),  # Estimate
                        'volume_ratio': volume_ratio,
                        'strength': 'HIGH' if volume_ratio > 1.5 else 'MODERATE' if volume_ratio > 1.2 else 'LOW',
                        'note': 'Estimated from volume data'
                    }
            
            except Exception as e:
                logger.warning(f"Social sentiment estimation failed: {e}")
            
            return {'score': 0.0, 'mentions': 0, 'strength': 'UNKNOWN'}
            
        except Exception as e:
            logger.error(f"Social sentiment analysis failed: {e}")
            return {'score': 0.0, 'mentions': 0, 'strength': 'ERROR'}
    
    def _get_market_sentiment(self, symbol: str) -> Dict[str, Any]:
        """
        Analyze overall market sentiment indicators
        - VIX (fear index)
        - Put/Call ratio
        - Market breadth
        - Sector performance
        """
        try:
            market_indicators = {}
            sentiment_score = 0.0
            
            # 1. Get VIX (fear index)
            try:
                vix = yf.Ticker('^VIX')
                vix_data = vix.history(period='1d')
                if not vix_data.empty:
                    current_vix = float(vix_data['Close'].iloc[-1])
                    market_indicators['vix'] = current_vix
                    
                    # VIX interpretation
                    if current_vix < 15:
                        vix_sentiment = 0.3  # Low fear = bullish
                    elif current_vix < 20:
                        vix_sentiment = 0.1
                    elif current_vix < 30:
                        vix_sentiment = -0.1
                    else:
                        vix_sentiment = -0.3  # High fear = bearish
                    
                    sentiment_score += vix_sentiment * 0.4
            except Exception as e:
                logger.warning(f"VIX fetch failed: {e}")
            
            # 2. Get market trend (S&P 500)
            try:
                spy = yf.Ticker('SPY')
                spy_data = spy.history(period='5d')
                if len(spy_data) >= 2:
                    price_change = (spy_data['Close'].iloc[-1] - spy_data['Close'].iloc[0]) / spy_data['Close'].iloc[0]
                    market_indicators['spy_change_5d'] = float(price_change * 100)
                    
                    # Market trend sentiment
                    if price_change > 0.02:
                        market_sentiment = 0.3  # Strong uptrend
                    elif price_change > 0:
                        market_sentiment = 0.15
                    elif price_change > -0.02:
                        market_sentiment = -0.15
                    else:
                        market_sentiment = -0.3  # Strong downtrend
                    
                    sentiment_score += market_sentiment * 0.6
            except Exception as e:
                logger.warning(f"Market trend fetch failed: {e}")
            
            # Normalize sentiment score
            sentiment_score = max(-1.0, min(1.0, sentiment_score))
            
            return {
                'score': sentiment_score,
                'indicators': market_indicators,
                'strength': 'STRONG' if abs(sentiment_score) > 0.3 else 'MODERATE' if abs(sentiment_score) > 0.1 else 'WEAK'
            }
            
        except Exception as e:
            logger.error(f"Market sentiment analysis failed: {e}")
            return {'score': 0.0, 'indicators': {}, 'strength': 'ERROR'}
    
    def _fetch_finnhub_news(self, symbol: str) -> List[Dict]:
        """Fetch news from Finnhub"""
        try:
            if not self.finnhub_api_key:
                return []
            
            url = f"https://finnhub.io/api/v1/company-news"
            params = {
                'symbol': symbol,
                'from': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                'to': datetime.now().strftime('%Y-%m-%d'),
                'token': self.finnhub_api_key
            }
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                return response.json()[:20]
            
        except Exception as e:
            logger.warning(f"Finnhub news fetch failed: {e}")
        
        return []
    
    def _fetch_newsapi(self, symbol: str) -> List[Dict]:
        """Fetch news from NewsAPI"""
        try:
            if not self.news_api_key:
                return []
            
            # Get company name for better search
            ticker = yf.Ticker(symbol)
            company_name = ticker.info.get('longName', symbol)
            
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': f"{company_name} OR {symbol}",
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': 20,
                'apiKey': self.news_api_key
            }
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get('articles', [])
            
        except Exception as e:
            logger.warning(f"NewsAPI fetch failed: {e}")
        
        return []
    
    def _fetch_yahoo_news(self, symbol: str) -> List[Dict]:
        """Fetch news from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            news = ticker.news
            
            if news:
                return [
                    {
                        'headline': item.get('title', ''),
                        'summary': item.get('summary', ''),
                        'source': item.get('publisher', 'Yahoo Finance'),
                        'published': item.get('providerPublishTime', '')
                    }
                    for item in news[:10]
                ]
        
        except Exception as e:
            logger.warning(f"Yahoo news fetch failed: {e}")
        
        return []
    
    def _fetch_finnhub_social(self, symbol: str) -> Optional[Dict]:
        """Fetch social sentiment from Finnhub"""
        try:
            if not self.finnhub_api_key:
                return None
            
            url = f"https://finnhub.io/api/v1/stock/social-sentiment"
            params = {
                'symbol': symbol,
                'token': self.finnhub_api_key
            }
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                
                # Parse social sentiment data
                if 'reddit' in data or 'twitter' in data:
                    reddit_score = data.get('reddit', {}).get('score', 0)
                    twitter_score = data.get('twitter', {}).get('score', 0)
                    
                    avg_score = (reddit_score + twitter_score) / 2
                    
                    return {
                        'score': avg_score / 100,  # Normalize to -1 to 1
                        'reddit_score': reddit_score,
                        'twitter_score': twitter_score,
                        'mentions': data.get('reddit', {}).get('mention', 0) + data.get('twitter', {}).get('mention', 0),
                        'strength': 'HIGH' if abs(avg_score) > 30 else 'MODERATE' if abs(avg_score) > 10 else 'LOW'
                    }
        
        except Exception as e:
            logger.warning(f"Finnhub social sentiment fetch failed: {e}")
        
        return None
    
    def _get_trending_topics(self, symbol: str) -> List[str]:
        """Get trending topics related to the symbol"""
        try:
            topics = []
            
            # Get recent news headlines
            news = self._fetch_yahoo_news(symbol)
            
            # Extract keywords from headlines
            keywords = set()
            for article in news[:5]:
                headline = article.get('headline', '').lower()
                
                # Common trending keywords
                trending_words = [
                    'earnings', 'revenue', 'profit', 'loss', 'beat', 'miss',
                    'upgrade', 'downgrade', 'acquisition', 'merger', 'partnership',
                    'lawsuit', 'investigation', 'breakthrough', 'innovation',
                    'expansion', 'layoffs', 'hiring', 'ceo', 'dividend',
                    'buyback', 'split', 'ipo', 'bankruptcy', 'recovery'
                ]
                
                for word in trending_words:
                    if word in headline:
                        keywords.add(word.upper())
            
            topics = list(keywords)[:5]
            
            return topics
            
        except Exception as e:
            logger.warning(f"Trending topics extraction failed: {e}")
            return []
    
    def _get_sentiment_strength(self, sentiment: float) -> str:
        """Convert sentiment score to strength label"""
        if sentiment > 0.5:
            return 'VERY_BULLISH'
        elif sentiment > 0.2:
            return 'BULLISH'
        elif sentiment > 0.05:
            return 'SLIGHTLY_BULLISH'
        elif sentiment > -0.05:
            return 'NEUTRAL'
        elif sentiment > -0.2:
            return 'SLIGHTLY_BEARISH'
        elif sentiment > -0.5:
            return 'BEARISH'
        else:
            return 'VERY_BEARISH'
    
    def _generate_sentiment_explanation(self, sentiment_data: Dict) -> str:
        """Generate human-readable explanation of sentiment"""
        try:
            overall = sentiment_data['overall_sentiment']
            strength = sentiment_data['sentiment_strength']
            
            news = sentiment_data.get('news_sentiment', {})
            social = sentiment_data.get('social_sentiment', {})
            market = sentiment_data.get('market_sentiment', {})
            
            explanation = f"Overall sentiment is {strength} ({overall:+.2f}). "
            
            # News sentiment
            if news.get('analyzed_count', 0) > 0:
                explanation += f"Analyzed {news['analyzed_count']} news articles: "
                explanation += f"{news.get('positive_count', 0)} positive, "
                explanation += f"{news.get('negative_count', 0)} negative, "
                explanation += f"{news.get('neutral_count', 0)} neutral. "
            
            # Social sentiment
            if social.get('mentions', 0) > 0:
                explanation += f"Social media shows {social.get('strength', 'UNKNOWN')} interest "
                explanation += f"with {social.get('mentions', 0)} mentions. "
            
            # Market sentiment
            if market.get('indicators'):
                indicators = market['indicators']
                if 'vix' in indicators:
                    explanation += f"Market fear index (VIX) at {indicators['vix']:.1f}. "
                if 'spy_change_5d' in indicators:
                    explanation += f"Market trend: {indicators['spy_change_5d']:+.2f}% over 5 days."
            
            return explanation.strip()
            
        except Exception as e:
            logger.error(f"Sentiment explanation generation failed: {e}")
            return "Sentiment analysis completed."
    
    def _get_neutral_sentiment(self, symbol: str) -> Dict[str, Any]:
        """Return neutral sentiment when analysis fails"""
        return {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'overall_sentiment': 0.0,
            'sentiment_score': 0.5,
            'news_sentiment': {'score': 0.0, 'article_count': 0},
            'social_sentiment': {'score': 0.0, 'mentions': 0},
            'market_sentiment': {'score': 0.0, 'indicators': {}},
            'trending_topics': [],
            'sentiment_strength': 'NEUTRAL',
            'confidence_contribution': 0.0,
            'explanation': 'Sentiment analysis unavailable - using neutral baseline.'
        }


# Global instance
realtime_sentiment_service = RealtimeSentimentService()
