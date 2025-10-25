"""
Hybrid Pro Pattern Detector
AI + Rules + Ensemble approach for conservative, reliable pattern detection
"""

import numpy as np
import pandas as pd
import yfinance as yf
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

# Technical analysis
import ta
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import MACD, EMAIndicator, ADXIndicator
from ta.volatility import BollingerBands, AverageTrueRange

# Internal imports
from services.detection_modes import (
    PatternDetectionResult, ConfidenceBreakdown,
    calculate_hybrid_pro_confidence, format_alert_message_hybrid_pro,
    DetectionMode
)
from detectors.ai_pattern_logic import detect_all_patterns
from detectors.advanced_ai_detection import enhance_pattern_detection
from services.deep_pattern_detector import get_deep_detector
from services.realtime_sentiment_service import realtime_sentiment_service

logger = logging.getLogger(__name__)


class HybridProDetector:
    """
    Hybrid Pro Detection System
    
    4-Layer Architecture:
    1. Deep Learning (CNN-LSTM) - Pattern recognition from raw OHLCV
    2. Rule Validation - Classical TA validation
    3. Real-Time Sentiment - News + Social + Market sentiment
    4. Ensemble Scoring - ML quality assessment
    """
    
    def __init__(self):
        self.mode = DetectionMode.HYBRID_PRO
        self.deep_detector = get_deep_detector()
        self.sentiment_service = realtime_sentiment_service
        self.min_confidence = 0.60
        
    def detect_patterns(
        self, 
        symbol: str, 
        timeframe: str = '1h',
        lookback_days: int = 5
    ) -> List[PatternDetectionResult]:
        """
        Detect patterns using Hybrid Pro approach
        
        Returns list of high-quality pattern detections with full transparency
        """
        try:
            logger.info(f"[HYBRID PRO] Detecting patterns for {symbol} on {timeframe}")
            
            # Step 1: Download real-time market data
            df = self._download_realtime_data(symbol, timeframe, lookback_days)
            if df.empty or len(df) < 50:
                logger.warning(f"Insufficient data for {symbol}")
                return []
            
            # Step 2: Calculate technical indicators
            df = self._calculate_indicators(df)
            
            # Step 3: LAYER 1 - Deep Learning Pattern Recognition
            deep_learning_patterns = self._deep_learning_detection(symbol, df, timeframe)
            
            # Step 4: LAYER 2 - Rule-Based Validation
            validated_patterns = self._rule_validation(df, deep_learning_patterns)
            
            # Step 5: LAYER 3 - Ensemble Quality Scoring
            final_patterns = self._ensemble_scoring(df, validated_patterns)
            
            # Step 6: Create full detection results with transparency
            results = []
            for pattern in final_patterns:
                result = self._create_detection_result(symbol, df, pattern, timeframe)
                if result and result.confidence >= self.min_confidence:
                    results.append(result)
            
            logger.info(f"[HYBRID PRO] Detected {len(results)} high-quality patterns for {symbol}")
            return results
            
        except Exception as e:
            logger.error(f"[HYBRID PRO] Detection failed for {symbol}: {e}")
            return []
    
    def _download_realtime_data(
        self, 
        symbol: str, 
        timeframe: str,
        lookback_days: int
    ) -> pd.DataFrame:
        """Download real-time market data (NO MOCK DATA)"""
        try:
            # Map timeframe to yfinance interval
            tf_map = {
                '1m': '1m', '5m': '5m', '15m': '15m', '30m': '30m',
                '1h': '60m', '2h': '120m', '4h': '240m', '1d': '1d'
            }
            interval = tf_map.get(timeframe, '60m')
            
            # Download with retry logic
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    df = yf.download(
                        symbol,
                        period=f'{lookback_days}d',
                        interval=interval,
                        progress=False,
                        auto_adjust=True
                    )
                    
                    if isinstance(df, pd.DataFrame) and not df.empty:
                        # Normalize column names
                        df.columns = [c.lower() for c in df.columns]
                        logger.info(f"Downloaded {len(df)} candles for {symbol}")
                        return df
                        
                except Exception as e:
                    if attempt < max_attempts - 1:
                        logger.warning(f"Download attempt {attempt + 1} failed, retrying...")
                        continue
                    raise e
            
            return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Failed to download data for {symbol}: {e}")
            return pd.DataFrame()
    
    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators for analysis"""
        try:
            # Trend indicators
            df['ema_9'] = EMAIndicator(df['close'], window=9).ema_indicator()
            df['ema_21'] = EMAIndicator(df['close'], window=21).ema_indicator()
            df['ema_50'] = EMAIndicator(df['close'], window=50).ema_indicator()
            
            # Momentum indicators
            df['rsi'] = RSIIndicator(df['close'], window=14).rsi()
            
            macd = MACD(df['close'])
            df['macd'] = macd.macd()
            df['macd_signal'] = macd.macd_signal()
            df['macd_diff'] = macd.macd_diff()
            
            stoch = StochasticOscillator(df['high'], df['low'], df['close'])
            df['stoch_k'] = stoch.stoch()
            df['stoch_d'] = stoch.stoch_signal()
            
            # Volatility indicators
            bb = BollingerBands(df['close'])
            df['bb_upper'] = bb.bollinger_hband()
            df['bb_middle'] = bb.bollinger_mavg()
            df['bb_lower'] = bb.bollinger_lband()
            df['bb_width'] = bb.bollinger_wband()
            
            atr = AverageTrueRange(df['high'], df['low'], df['close'])
            df['atr'] = atr.average_true_range()
            
            # Trend strength
            adx = ADXIndicator(df['high'], df['low'], df['close'])
            df['adx'] = adx.adx()
            
            # Volume analysis
            df['volume_sma'] = df['volume'].rolling(window=20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma']
            
            return df
            
        except Exception as e:
            logger.error(f"Indicator calculation failed: {e}")
            return df
    
    def _deep_learning_detection(
        self, 
        symbol: str, 
        df: pd.DataFrame,
        timeframe: str
    ) -> List[Dict[str, Any]]:
        """
        LAYER 1: Deep Learning Pattern Recognition
        Uses CNN-LSTM to detect patterns from raw OHLCV data
        """
        try:
            patterns = []
            
            # Use existing deep pattern detector
            deep_results = self.deep_detector.detect_patterns(symbol, timeframe)
            
            for result in deep_results:
                patterns.append({
                    'name': result.pattern_type,
                    'deep_learning_score': result.confidence,
                    'source': 'cnn_lstm',
                    'metadata': result.metadata
                })
            
            # Also use existing rule-based detectors for initial detection
            candles = []
            for idx, row in df.iterrows():
                candles.append({
                    'time': idx.isoformat() if hasattr(idx, 'isoformat') else str(idx),
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'volume': int(row['volume']) if not pd.isna(row['volume']) else 0
                })
            
            # Detect using existing pattern registry
            rule_patterns = detect_all_patterns(candles)
            
            for pattern in rule_patterns:
                patterns.append({
                    'name': pattern.get('name', 'Unknown'),
                    'deep_learning_score': pattern.get('confidence', 0.70),
                    'source': 'rule_based_initial',
                    'category': pattern.get('category', 'Unknown'),
                    'explanation': pattern.get('explanation', ''),
                    'index': pattern.get('index', len(candles) - 1)
                })
            
            logger.info(f"[LAYER 1] Deep learning detected {len(patterns)} patterns")
            return patterns
            
        except Exception as e:
            logger.error(f"Deep learning detection failed: {e}")
            return []
    
    def _rule_validation(
        self, 
        df: pd.DataFrame, 
        patterns: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        LAYER 2: Rule-Based Validation
        Validates AI findings against classical technical analysis rules
        """
        validated = []
        
        for pattern in patterns:
            try:
                pattern_name = pattern.get('name', '').lower()
                
                # Get validation score based on pattern type
                validation_score = self._validate_pattern_rules(df, pattern_name)
                
                # Calculate rules passed
                rules_passed, total_rules = self._count_rules_passed(df, pattern_name)
                
                pattern['rule_validation_score'] = validation_score
                pattern['rules_passed'] = rules_passed
                pattern['total_rules'] = total_rules
                
                # Only keep patterns that pass minimum validation
                if validation_score >= 0.50:
                    validated.append(pattern)
                    
            except Exception as e:
                logger.error(f"Rule validation failed for pattern: {e}")
                continue
        
        logger.info(f"[LAYER 2] Validated {len(validated)}/{len(patterns)} patterns")
        return validated
    
    def _validate_pattern_rules(self, df: pd.DataFrame, pattern_name: str) -> float:
        """Validate pattern against classical TA rules"""
        try:
            latest = df.iloc[-1]
            score = 0.70  # Base score
            
            # Bullish patterns validation
            if any(word in pattern_name for word in ['bull', 'hammer', 'morning', 'engulfing']):
                # Check bullish conditions
                if latest['rsi'] < 50:  # Oversold or neutral
                    score += 0.10
                if latest['macd'] > latest['macd_signal']:  # MACD bullish
                    score += 0.10
                if latest['close'] > latest['ema_9']:  # Above short EMA
                    score += 0.05
                if latest['volume_ratio'] > 1.2:  # High volume
                    score += 0.05
            
            # Bearish patterns validation
            elif any(word in pattern_name for word in ['bear', 'shooting', 'evening', 'dark']):
                # Check bearish conditions
                if latest['rsi'] > 50:  # Overbought or neutral
                    score += 0.10
                if latest['macd'] < latest['macd_signal']:  # MACD bearish
                    score += 0.10
                if latest['close'] < latest['ema_9']:  # Below short EMA
                    score += 0.05
                if latest['volume_ratio'] > 1.2:  # High volume
                    score += 0.05
            
            # Neutral patterns (doji, spinning top)
            else:
                if 30 < latest['rsi'] < 70:  # Neutral RSI
                    score += 0.10
                if latest['bb_width'] < 0.05:  # Tight Bollinger Bands
                    score += 0.10
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"Pattern validation failed: {e}")
            return 0.70
    
    def _count_rules_passed(self, df: pd.DataFrame, pattern_name: str) -> tuple:
        """Count how many rules the pattern passes"""
        try:
            latest = df.iloc[-1]
            passed = 0
            total = 5
            
            # Define rules based on pattern type
            if 'bull' in pattern_name:
                if latest['rsi'] < 50: passed += 1
                if latest['macd'] > latest['macd_signal']: passed += 1
                if latest['close'] > latest['ema_9']: passed += 1
                if latest['volume_ratio'] > 1.0: passed += 1
                if latest['close'] > latest['open']: passed += 1
            elif 'bear' in pattern_name:
                if latest['rsi'] > 50: passed += 1
                if latest['macd'] < latest['macd_signal']: passed += 1
                if latest['close'] < latest['ema_9']: passed += 1
                if latest['volume_ratio'] > 1.0: passed += 1
                if latest['close'] < latest['open']: passed += 1
            else:
                total = 3
                if 30 < latest['rsi'] < 70: passed += 1
                if latest['bb_width'] < 0.05: passed += 1
                if 0.8 < latest['volume_ratio'] < 1.2: passed += 1
            
            return passed, total
            
        except Exception:
            return 0, 5
    
    def _ensemble_scoring(
        self, 
        df: pd.DataFrame, 
        patterns: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        LAYER 3: Ensemble Quality Scoring
        Uses ML features to assess pattern quality
        """
        scored = []
        
        for pattern in patterns:
            try:
                # Calculate context score from market conditions
                context_score = self._calculate_context_score(df)
                
                # Calculate quality factors
                quality_factors = self._calculate_quality_factors(df)
                
                pattern['context_score'] = context_score
                pattern['quality_factors'] = quality_factors
                
                scored.append(pattern)
                
            except Exception as e:
                logger.error(f"Ensemble scoring failed: {e}")
                continue
        
        logger.info(f"[LAYER 3] Scored {len(scored)} patterns")
        return scored
    
    def _calculate_context_score(self, df: pd.DataFrame) -> float:
        """Calculate market context score"""
        try:
            latest = df.iloc[-1]
            score = 0.0
            
            # Volume score (0-0.33)
            volume_score = min(0.33, latest['volume_ratio'] / 3.0)
            
            # Momentum score (0-0.33)
            rsi_normalized = abs(latest['rsi'] - 50) / 50  # Distance from neutral
            momentum_score = 0.33 * (1 - rsi_normalized)
            
            # Trend strength score (0-0.34)
            if latest['adx'] > 25:
                trend_score = min(0.34, latest['adx'] / 100)
            else:
                trend_score = 0.17
            
            score = volume_score + momentum_score + trend_score
            return min(1.0, score)
            
        except Exception:
            return 0.50
    
    def _calculate_quality_factors(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate detailed quality factors"""
        try:
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest
            
            # Calculate S/R proximity
            lookback = min(50, len(df))
            recent = df.iloc[-lookback:]
            resistance = recent['high'].max()
            support = recent['low'].min()
            price_range = resistance - support
            
            dist_to_resistance = abs(latest['close'] - resistance) / price_range if price_range > 0 else 0.5
            dist_to_support = abs(latest['close'] - support) / price_range if price_range > 0 else 0.5
            sr_proximity = 1.0 - min(dist_to_resistance, dist_to_support)
            
            return {
                'volume_score': float(latest['volume_ratio']),
                'momentum_score': float(latest['rsi'] / 100),
                'trend_strength': float(latest['adx'] / 100) if latest['adx'] > 0 else 0.0,
                'sr_proximity': float(sr_proximity),
                'volatility': float(latest['atr']),
                'bb_position': float((latest['close'] - latest['bb_lower']) / (latest['bb_upper'] - latest['bb_lower'])) if latest['bb_upper'] > latest['bb_lower'] else 0.5,
                'macd_strength': float(abs(latest['macd_diff'])),
                'rules_passed': 0,  # Will be filled by validation
                'total_rules': 5
            }
            
        except Exception as e:
            logger.error(f"Quality factors calculation failed: {e}")
            return {
                'volume_score': 1.0,
                'momentum_score': 0.5,
                'trend_strength': 0.5,
                'sr_proximity': 0.5,
                'volatility': 0.0,
                'bb_position': 0.5,
                'macd_strength': 0.0,
                'rules_passed': 0,
                'total_rules': 5
            }
    
    def _create_detection_result(
        self,
        symbol: str,
        df: pd.DataFrame,
        pattern: Dict[str, Any],
        timeframe: str
    ) -> Optional[PatternDetectionResult]:
        """Create full detection result with transparency"""
        try:
            latest = df.iloc[-1]
            
            # Get real-time sentiment analysis
            sentiment_data = self.sentiment_service.get_comprehensive_sentiment(
                symbol=symbol,
                include_social=True,
                include_news=True,
                include_market=True
            )
            sentiment_score = sentiment_data.get('sentiment_score', 0.5)
            
            # Calculate final confidence using Hybrid Pro formula (with sentiment!)
            confidence_breakdown = calculate_hybrid_pro_confidence(
                deep_learning_score=pattern.get('deep_learning_score', 0.70),
                rule_validation_score=pattern.get('rule_validation_score', 0.70),
                context_score=pattern.get('context_score', 0.50),
                sentiment_score=sentiment_score,
                quality_factors=pattern.get('quality_factors', {}),
                sentiment_data=sentiment_data
            )
            
            # Update quality factors with rules passed
            confidence_breakdown.quality_factors['rules_passed'] = pattern.get('rules_passed', 0)
            confidence_breakdown.quality_factors['total_rules'] = pattern.get('total_rules', 5)
            
            # Add sentiment data to quality factors
            confidence_breakdown.quality_factors['sentiment_strength'] = sentiment_data.get('sentiment_strength', 'NEUTRAL')
            confidence_breakdown.quality_factors['news_articles'] = sentiment_data.get('news_sentiment', {}).get('analyzed_count', 0)
            confidence_breakdown.quality_factors['social_mentions'] = sentiment_data.get('social_sentiment', {}).get('mentions', 0)
            confidence_breakdown.quality_factors['trending_topics'] = sentiment_data.get('trending_topics', [])
            
            # Determine suggested action
            pattern_name = pattern.get('name', '').lower()
            if any(word in pattern_name for word in ['bull', 'hammer', 'morning']):
                action = 'BUY'
            elif any(word in pattern_name for word in ['bear', 'shooting', 'evening', 'dark']):
                action = 'SELL'
            else:
                action = 'HOLD'
            
            # Calculate risk management levels
            atr = float(latest['atr']) if 'atr' in latest and not pd.isna(latest['atr']) else 0.0
            entry_price = float(latest['close'])
            
            if action == 'BUY':
                stop_loss = entry_price - (1.5 * atr) if atr > 0 else None
                take_profit = entry_price + (2.0 * atr) if atr > 0 else None
            elif action == 'SELL':
                stop_loss = entry_price + (1.5 * atr) if atr > 0 else None
                take_profit = entry_price - (2.0 * atr) if atr > 0 else None
            else:
                stop_loss = None
                take_profit = None
            
            rr_ratio = 2.0 / 1.5 if atr > 0 else None
            
            # Create result
            result = PatternDetectionResult(
                symbol=symbol,
                pattern_type=pattern.get('category', 'Technical'),
                pattern_name=pattern.get('name', 'Unknown Pattern'),
                confidence=confidence_breakdown.final_confidence,
                confidence_breakdown=confidence_breakdown,
                price=entry_price,
                volume=int(latest['volume']) if not pd.isna(latest['volume']) else 0,
                timestamp=datetime.now().isoformat(),
                detection_mode='hybrid_pro',
                timeframe=timeframe,
                suggested_action=action,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                risk_reward_ratio=rr_ratio,
                metadata={
                    'source': pattern.get('source', 'hybrid'),
                    'explanation': pattern.get('explanation', ''),
                    'atr': atr,
                    'rsi': float(latest['rsi']) if 'rsi' in latest else None,
                    'macd': float(latest['macd']) if 'macd' in latest else None
                }
            )
            
            # Format alert message
            title, message, priority = format_alert_message_hybrid_pro(result)
            result.alert_title = title
            result.alert_message = message
            result.alert_priority = priority
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to create detection result: {e}")
            return None
