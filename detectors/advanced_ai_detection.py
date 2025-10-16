"""
Advanced AI-Enhanced Rule-Based Pattern Detection
Combines traditional technical analysis with machine learning features
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class PatternFeatures:
    """Advanced features for pattern quality assessment"""
    body_ratio: float
    wick_ratio: float
    volume_surge: float
    momentum_score: float
    volatility_score: float
    trend_strength: float
    support_resistance_proximity: float
    fibonacci_alignment: float
    volume_profile_score: float
    order_flow_imbalance: float


class AdvancedPatternDetector:
    """
    AI-Enhanced Pattern Detection with Quality Scoring
    Uses 10+ features to assess pattern quality beyond basic rules
    """
    
    def __init__(self):
        self.min_confidence = 0.60
        self.feature_weights = {
            'body_ratio': 0.15,
            'wick_ratio': 0.10,
            'volume_surge': 0.15,
            'momentum_score': 0.12,
            'volatility_score': 0.08,
            'trend_strength': 0.12,
            'support_resistance': 0.10,
            'fibonacci': 0.08,
            'volume_profile': 0.05,
            'order_flow': 0.05
        }
    
    def calculate_advanced_features(self, df: pd.DataFrame, idx: int) -> PatternFeatures:
        """Calculate advanced features for pattern quality"""
        
        try:
            # Get candle data
            current = df.iloc[idx]
            prev = df.iloc[idx - 1] if idx > 0 else current
            
            # 1. Body Ratio (how strong is the candle body)
            body_size = abs(current['close'] - current['open'])
            total_range = current['high'] - current['low']
            body_ratio = body_size / total_range if total_range > 0 else 0
            
            # 2. Wick Ratio (rejection strength)
            upper_wick = current['high'] - max(current['open'], current['close'])
            lower_wick = min(current['open'], current['close']) - current['low']
            wick_ratio = (upper_wick + lower_wick) / total_range if total_range > 0 else 0
            
            # 3. Volume Surge (institutional interest)
            avg_volume = df['volume'].iloc[max(0, idx-20):idx].mean()
            volume_surge = current['volume'] / avg_volume if avg_volume > 0 else 1.0
            volume_surge = min(volume_surge, 3.0)  # Cap at 3x
            
            # 4. Momentum Score (RSI + MACD alignment)
            momentum_score = self._calculate_momentum(df, idx)
            
            # 5. Volatility Score (ATR-based)
            volatility_score = self._calculate_volatility(df, idx)
            
            # 6. Trend Strength (EMA alignment)
            trend_strength = self._calculate_trend_strength(df, idx)
            
            # 7. Support/Resistance Proximity
            sr_proximity = self._calculate_sr_proximity(df, idx)
            
            # 8. Fibonacci Alignment
            fib_alignment = self._calculate_fibonacci_alignment(df, idx)
            
            # 9. Volume Profile Score
            volume_profile = self._calculate_volume_profile(df, idx)
            
            # 10. Order Flow Imbalance
            order_flow = self._calculate_order_flow(df, idx)
            
            return PatternFeatures(
                body_ratio=body_ratio,
                wick_ratio=wick_ratio,
                volume_surge=volume_surge,
                momentum_score=momentum_score,
                volatility_score=volatility_score,
                trend_strength=trend_strength,
                support_resistance_proximity=sr_proximity,
                fibonacci_alignment=fib_alignment,
                volume_profile_score=volume_profile,
                order_flow_imbalance=order_flow
            )
            
        except Exception as e:
            logger.error(f"Error calculating features: {e}")
            # Return neutral features
            return PatternFeatures(0.5, 0.5, 1.0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5)
    
    def _calculate_momentum(self, df: pd.DataFrame, idx: int) -> float:
        """Calculate momentum score from RSI and MACD"""
        try:
            # RSI
            if 'rsi' in df.columns:
                rsi = df['rsi'].iloc[idx]
                rsi_score = 1.0 if 30 < rsi < 70 else 0.5
            else:
                rsi_score = 0.5
            
            # MACD
            if 'macd' in df.columns and 'macd_signal' in df.columns:
                macd = df['macd'].iloc[idx]
                signal = df['macd_signal'].iloc[idx]
                macd_score = 1.0 if macd > signal else 0.3
            else:
                macd_score = 0.5
            
            return (rsi_score + macd_score) / 2
            
        except Exception:
            return 0.5
    
    def _calculate_volatility(self, df: pd.DataFrame, idx: int) -> float:
        """Calculate volatility score (lower is better for patterns)"""
        try:
            # ATR-based volatility
            lookback = min(14, idx)
            if lookback < 2:
                return 0.5
            
            high_low = df['high'].iloc[idx-lookback:idx] - df['low'].iloc[idx-lookback:idx]
            atr = high_low.mean()
            current_range = df['high'].iloc[idx] - df['low'].iloc[idx]
            
            # Lower volatility = better pattern quality
            volatility_ratio = current_range / atr if atr > 0 else 1.0
            
            # Score: 1.0 for normal volatility, lower for high volatility
            if volatility_ratio < 1.2:
                return 1.0
            elif volatility_ratio < 1.5:
                return 0.7
            else:
                return 0.4
                
        except Exception:
            return 0.5
    
    def _calculate_trend_strength(self, df: pd.DataFrame, idx: int) -> float:
        """Calculate trend strength from EMA alignment"""
        try:
            # Check if EMAs are available
            if 'ema_9' not in df.columns:
                return 0.5
            
            ema_9 = df['ema_9'].iloc[idx]
            ema_21 = df['ema_21'].iloc[idx] if 'ema_21' in df.columns else ema_9
            ema_50 = df['ema_50'].iloc[idx] if 'ema_50' in df.columns else ema_21
            
            # Bullish alignment: EMA9 > EMA21 > EMA50
            if ema_9 > ema_21 > ema_50:
                return 1.0
            # Bearish alignment: EMA9 < EMA21 < EMA50
            elif ema_9 < ema_21 < ema_50:
                return 1.0
            # Partial alignment
            elif ema_9 > ema_21 or ema_21 > ema_50:
                return 0.7
            else:
                return 0.4
                
        except Exception:
            return 0.5
    
    def _calculate_sr_proximity(self, df: pd.DataFrame, idx: int) -> float:
        """Calculate proximity to support/resistance levels"""
        try:
            lookback = min(50, idx)
            if lookback < 10:
                return 0.5
            
            # Find recent highs and lows (support/resistance)
            recent_data = df.iloc[max(0, idx-lookback):idx]
            resistance = recent_data['high'].max()
            support = recent_data['low'].min()
            
            current_price = df['close'].iloc[idx]
            price_range = resistance - support
            
            if price_range == 0:
                return 0.5
            
            # Distance to nearest S/R level
            dist_to_resistance = abs(current_price - resistance) / price_range
            dist_to_support = abs(current_price - support) / price_range
            
            min_distance = min(dist_to_resistance, dist_to_support)
            
            # Closer to S/R = higher score (more significant)
            if min_distance < 0.02:  # Within 2%
                return 1.0
            elif min_distance < 0.05:  # Within 5%
                return 0.8
            else:
                return 0.5
                
        except Exception:
            return 0.5
    
    def _calculate_fibonacci_alignment(self, df: pd.DataFrame, idx: int) -> float:
        """Check if price is near Fibonacci retracement levels"""
        try:
            lookback = min(50, idx)
            if lookback < 10:
                return 0.5
            
            # Find swing high and low
            recent_data = df.iloc[max(0, idx-lookback):idx]
            swing_high = recent_data['high'].max()
            swing_low = recent_data['low'].min()
            
            current_price = df['close'].iloc[idx]
            price_range = swing_high - swing_low
            
            if price_range == 0:
                return 0.5
            
            # Calculate Fibonacci levels
            fib_levels = {
                0.236: swing_low + 0.236 * price_range,
                0.382: swing_low + 0.382 * price_range,
                0.500: swing_low + 0.500 * price_range,
                0.618: swing_low + 0.618 * price_range,
                0.786: swing_low + 0.786 * price_range,
            }
            
            # Check proximity to any Fibonacci level
            for level, price in fib_levels.items():
                distance = abs(current_price - price) / price_range
                if distance < 0.02:  # Within 2% of Fib level
                    return 1.0
            
            return 0.5
            
        except Exception:
            return 0.5
    
    def _calculate_volume_profile(self, df: pd.DataFrame, idx: int) -> float:
        """Calculate volume profile score"""
        try:
            lookback = min(20, idx)
            if lookback < 5:
                return 0.5
            
            # Compare current volume to recent volume distribution
            recent_volumes = df['volume'].iloc[max(0, idx-lookback):idx]
            current_volume = df['volume'].iloc[idx]
            
            # Percentile rank
            percentile = (recent_volumes < current_volume).sum() / len(recent_volumes)
            
            # Higher volume = better pattern confirmation
            if percentile > 0.8:  # Top 20% volume
                return 1.0
            elif percentile > 0.6:  # Top 40% volume
                return 0.8
            else:
                return 0.5
                
        except Exception:
            return 0.5
    
    def _calculate_order_flow(self, df: pd.DataFrame, idx: int) -> float:
        """Estimate order flow imbalance from price action"""
        try:
            current = df.iloc[idx]
            
            # Buying pressure: close near high
            close_position = (current['close'] - current['low']) / (current['high'] - current['low'])
            
            # Strong buying pressure
            if close_position > 0.8:
                return 1.0
            # Strong selling pressure
            elif close_position < 0.2:
                return 0.3
            else:
                return 0.6
                
        except Exception:
            return 0.5
    
    def calculate_pattern_quality_score(self, features: PatternFeatures) -> float:
        """
        Calculate overall pattern quality score using weighted features
        Returns: 0.0 to 1.0 confidence score
        """
        
        # Convert features to dict
        feature_dict = {
            'body_ratio': features.body_ratio,
            'wick_ratio': 1.0 - features.wick_ratio,  # Invert (less wick = better)
            'volume_surge': min(features.volume_surge / 2.0, 1.0),  # Normalize
            'momentum_score': features.momentum_score,
            'volatility_score': features.volatility_score,
            'trend_strength': features.trend_strength,
            'support_resistance': features.support_resistance_proximity,
            'fibonacci': features.fibonacci_alignment,
            'volume_profile': features.volume_profile_score,
            'order_flow': features.order_flow_imbalance
        }
        
        # Calculate weighted score
        total_score = 0.0
        for feature_name, weight in self.feature_weights.items():
            feature_value = feature_dict.get(feature_name, 0.5)
            total_score += feature_value * weight
        
        return total_score
    
    def enhance_pattern_confidence(
        self, 
        base_confidence: float, 
        df: pd.DataFrame, 
        idx: int,
        pattern_name: str
    ) -> Tuple[float, Dict[str, float]]:
        """
        Enhance base rule-based confidence with AI features
        
        Returns:
            - Enhanced confidence (0.0 to 1.0)
            - Feature breakdown dict
        """
        
        try:
            # Calculate advanced features
            features = self.calculate_advanced_features(df, idx)
            
            # Calculate quality score
            quality_score = self.calculate_pattern_quality_score(features)
            
            # Combine base confidence with quality score
            # Base confidence: 60% weight
            # Quality score: 40% weight
            enhanced_confidence = (base_confidence * 0.60) + (quality_score * 0.40)
            
            # Feature breakdown for transparency
            breakdown = {
                'base_confidence': base_confidence,
                'quality_score': quality_score,
                'body_ratio': features.body_ratio,
                'volume_surge': features.volume_surge,
                'momentum': features.momentum_score,
                'trend_strength': features.trend_strength,
                'sr_proximity': features.support_resistance_proximity,
                'enhanced_confidence': enhanced_confidence
            }
            
            logger.info(f"Enhanced {pattern_name}: {base_confidence:.2f} → {enhanced_confidence:.2f}")
            
            return enhanced_confidence, breakdown
            
        except Exception as e:
            logger.error(f"Error enhancing confidence: {e}")
            return base_confidence, {'base_confidence': base_confidence}


# Global instance
advanced_detector = AdvancedPatternDetector()


def enhance_pattern_detection(
    base_patterns: List[Dict],
    df: pd.DataFrame,
    idx: int
) -> List[Dict]:
    """
    Enhance list of detected patterns with AI quality scoring
    
    Args:
        base_patterns: List of patterns from rule-based detection
        df: DataFrame with OHLCV data
        idx: Current candle index
    
    Returns:
        Enhanced patterns with improved confidence scores
    """
    
    enhanced_patterns = []
    
    for pattern in base_patterns:
        try:
            # Get base confidence
            base_conf = pattern.get('confidence', 0.70)
            pattern_name = pattern.get('name', 'Unknown')
            
            # Enhance with AI features
            enhanced_conf, breakdown = advanced_detector.enhance_pattern_confidence(
                base_conf, df, idx, pattern_name
            )
            
            # Update pattern
            pattern['confidence'] = enhanced_conf
            pattern['ai_enhanced'] = True
            pattern['feature_breakdown'] = breakdown
            
            # Only include high-quality patterns
            if enhanced_conf >= advanced_detector.min_confidence:
                enhanced_patterns.append(pattern)
            else:
                logger.debug(f"Filtered out low-quality {pattern_name}: {enhanced_conf:.2f}")
                
        except Exception as e:
            logger.error(f"Error enhancing pattern: {e}")
            # Keep original pattern if enhancement fails
            enhanced_patterns.append(pattern)
    
    return enhanced_patterns
