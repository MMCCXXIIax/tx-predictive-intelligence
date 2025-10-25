"""
Market Regime Detection System - Adaptive Trading
- Real-time regime classification (trending/ranging/volatile)
- Strategy auto-switcher
- Edge probability scoring
- Volatility regime detection
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
import statistics

logger = logging.getLogger(__name__)


@dataclass
class MarketRegime:
    """Market regime classification"""
    regime_type: str  # 'trending_up', 'trending_down', 'ranging', 'volatile', 'breakout'
    confidence: float  # 0-1
    volatility_level: str  # 'low', 'medium', 'high', 'extreme'
    recommended_strategy: str  # 'trend_following', 'mean_reversion', 'breakout', 'stay_out'
    edge_probability: float  # 0-100, probability of having edge in this regime
    risk_on_off: str  # 'risk_on', 'risk_off', 'neutral'
    market_phase: str  # 'accumulation', 'markup', 'distribution', 'markdown'
    optimal_timeframe: str  # Best timeframe for current regime
    should_trade: bool  # Whether to trade in this regime
    regime_strength: float  # 0-100, how strong the regime is
    expected_duration: str  # 'short', 'medium', 'long'
    metrics: Dict[str, float]
    timestamp: str


class MarketRegimeDetector:
    """
    World-Class Market Regime Detection
    - Identifies market conditions in real-time
    - Recommends optimal strategies per regime
    - Calculates edge probability
    - Prevents trading in unfavorable conditions
    """
    
    def __init__(self):
        self.regime_history = []
        self.strategy_performance = {}
        
    def detect_regime(self, symbol: str, timeframe: str = '1h') -> MarketRegime:
        """
        Detect current market regime
        """
        try:
            from main import market_data_service
            data = market_data_service.get_ohlcv(symbol, timeframe, limit=200)
            
            if not data or len(data) < 100:
                raise Exception("Insufficient data for regime detection")
            
            df = pd.DataFrame(data)
            
            # Calculate regime indicators
            trend_strength = self._calculate_trend_strength(df)
            volatility = self._calculate_volatility_regime(df)
            range_bound = self._check_range_bound(df)
            breakout_potential = self._check_breakout_potential(df)
            
            # Classify regime
            regime_type, confidence = self._classify_regime(
                trend_strength,
                volatility,
                range_bound,
                breakout_potential
            )
            
            # Determine volatility level
            vol_level = self._classify_volatility(volatility)
            
            # Recommend strategy
            strategy = self._recommend_strategy(regime_type, vol_level)
            
            # Calculate edge probability
            edge_prob = self._calculate_edge_probability(
                regime_type,
                vol_level,
                trend_strength
            )
            
            # Detect risk-on/risk-off
            risk_sentiment = self._detect_risk_sentiment(df)
            
            # Identify market phase
            market_phase = self._identify_market_phase(df)
            
            # Determine optimal timeframe
            optimal_tf = self._determine_optimal_timeframe(regime_type, vol_level)
            
            # Should trade?
            should_trade = edge_prob > 60 and vol_level != 'extreme'
            
            # Regime strength
            regime_strength = self._calculate_regime_strength(
                confidence,
                trend_strength,
                volatility
            )
            
            # Expected duration
            duration = self._estimate_regime_duration(regime_type, df)
            
            # Compile metrics
            metrics = {
                'trend_strength': round(trend_strength, 3),
                'volatility': round(volatility, 3),
                'range_bound_score': round(range_bound, 3),
                'breakout_score': round(breakout_potential, 3),
                'adx': round(self._calculate_adx(df), 2),
                'atr_ratio': round(self._calculate_atr_ratio(df), 2)
            }
            
            regime = MarketRegime(
                regime_type=regime_type,
                confidence=round(confidence, 3),
                volatility_level=vol_level,
                recommended_strategy=strategy,
                edge_probability=round(edge_prob, 2),
                risk_on_off=risk_sentiment,
                market_phase=market_phase,
                optimal_timeframe=optimal_tf,
                should_trade=should_trade,
                regime_strength=round(regime_strength, 2),
                expected_duration=duration,
                metrics=metrics,
                timestamp=datetime.now().isoformat()
            )
            
            # Store in history
            self.regime_history.append(regime)
            if len(self.regime_history) > 1000:
                self.regime_history = self.regime_history[-1000:]
            
            return regime
            
        except Exception as e:
            logger.error(f"Regime detection error for {symbol}: {e}")
            raise
    
    def _calculate_trend_strength(self, df: pd.DataFrame) -> float:
        """
        Calculate trend strength using ADX-like logic
        Returns 0-1 (0 = no trend, 1 = strong trend)
        """
        try:
            # Calculate moving averages
            sma_20 = df.iloc[-20:]['close'].mean()
            sma_50 = df.iloc[-50:]['close'].mean()
            sma_100 = df.iloc[-100:]['close'].mean()
            
            current_price = df.iloc[-1]['close']
            
            # Check alignment
            if current_price > sma_20 > sma_50 > sma_100:
                alignment_score = 1.0  # Perfect bullish alignment
            elif current_price < sma_20 < sma_50 < sma_100:
                alignment_score = 1.0  # Perfect bearish alignment
            elif current_price > sma_20 > sma_50:
                alignment_score = 0.7
            elif current_price < sma_20 < sma_50:
                alignment_score = 0.7
            elif current_price > sma_20:
                alignment_score = 0.4
            elif current_price < sma_20:
                alignment_score = 0.4
            else:
                alignment_score = 0.1
            
            # Calculate slope consistency
            slopes = []
            for i in range(10, 50, 10):
                slope = (df.iloc[-1]['close'] - df.iloc[-i]['close']) / i
                slopes.append(slope)
            
            # Consistent slopes = strong trend
            slope_std = statistics.stdev(slopes) if len(slopes) > 1 else 1.0
            slope_consistency = 1.0 / (1.0 + slope_std)
            
            # Combine scores
            trend_strength = (alignment_score * 0.7) + (slope_consistency * 0.3)
            
            return min(1.0, trend_strength)
            
        except Exception as e:
            logger.error(f"Trend strength calculation error: {e}")
            return 0.5
    
    def _calculate_volatility_regime(self, df: pd.DataFrame) -> float:
        """
        Calculate volatility (ATR-based)
        Returns normalized volatility score
        """
        try:
            high = df['high'].values
            low = df['low'].values
            close = df['close'].values
            
            tr_list = []
            for i in range(1, min(20, len(df))):
                tr = max(
                    high[i] - low[i],
                    abs(high[i] - close[i-1]),
                    abs(low[i] - close[i-1])
                )
                tr_list.append(tr)
            
            atr = statistics.mean(tr_list)
            normalized_atr = atr / close[-1]
            
            return normalized_atr
            
        except:
            return 0.02
    
    def _check_range_bound(self, df: pd.DataFrame) -> float:
        """
        Check if market is range-bound
        Returns 0-1 (0 = trending, 1 = ranging)
        """
        try:
            # Calculate price range over last 50 candles
            high_50 = df.iloc[-50:]['high'].max()
            low_50 = df.iloc[-50:]['low'].min()
            range_50 = high_50 - low_50
            
            # Calculate how much price oscillates within range
            closes = df.iloc[-50:]['close'].values
            
            # Count touches of upper/lower range
            upper_threshold = low_50 + (range_50 * 0.8)
            lower_threshold = low_50 + (range_50 * 0.2)
            
            upper_touches = sum(1 for c in closes if c > upper_threshold)
            lower_touches = sum(1 for c in closes if c < lower_threshold)
            
            # More touches = more range-bound
            total_touches = upper_touches + lower_touches
            range_score = min(1.0, total_touches / 20)
            
            return range_score
            
        except:
            return 0.5
    
    def _check_breakout_potential(self, df: pd.DataFrame) -> float:
        """
        Check breakout potential
        Returns 0-1 (0 = no breakout, 1 = imminent breakout)
        """
        try:
            # Check for consolidation followed by volume spike
            recent_range = df.iloc[-10:]['high'].max() - df.iloc[-10:]['low'].min()
            avg_range = (df.iloc[-50:-10]['high'].max() - df.iloc[-50:-10]['low'].min()) / 4
            
            # Tight consolidation
            consolidation_score = 1.0 - (recent_range / avg_range) if avg_range > 0 else 0
            consolidation_score = max(0, min(1, consolidation_score))
            
            # Volume increase
            recent_volume = df.iloc[-5:]['volume'].mean()
            avg_volume = df.iloc[-50:]['volume'].mean()
            volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
            volume_score = min(1.0, (volume_ratio - 1) / 2)
            
            # Combine
            breakout_score = (consolidation_score * 0.6) + (volume_score * 0.4)
            
            return max(0, breakout_score)
            
        except:
            return 0.0
    
    def _classify_regime(self, trend_strength: float, volatility: float, 
                        range_bound: float, breakout: float) -> Tuple[str, float]:
        """
        Classify market regime
        Returns (regime_type, confidence)
        """
        # Breakout regime
        if breakout > 0.7:
            return 'breakout', breakout
        
        # Ranging regime
        if range_bound > 0.6 and trend_strength < 0.4:
            return 'ranging', range_bound
        
        # Volatile regime
        if volatility > 0.04:  # 4% ATR
            return 'volatile', min(1.0, volatility / 0.04)
        
        # Trending regimes
        if trend_strength > 0.6:
            # Determine direction from recent price action
            # (simplified - would use more sophisticated logic)
            return 'trending_up', trend_strength  # or 'trending_down'
        
        # Default to ranging
        return 'ranging', 0.5
    
    def _classify_volatility(self, volatility: float) -> str:
        """Classify volatility level"""
        if volatility < 0.015:
            return 'low'
        elif volatility < 0.03:
            return 'medium'
        elif volatility < 0.05:
            return 'high'
        else:
            return 'extreme'
    
    def _recommend_strategy(self, regime_type: str, vol_level: str) -> str:
        """Recommend trading strategy based on regime"""
        strategy_map = {
            'trending_up': 'trend_following',
            'trending_down': 'trend_following',
            'ranging': 'mean_reversion',
            'breakout': 'breakout',
            'volatile': 'stay_out'
        }
        
        strategy = strategy_map.get(regime_type, 'stay_out')
        
        # Adjust for extreme volatility
        if vol_level == 'extreme':
            strategy = 'stay_out'
        
        return strategy
    
    def _calculate_edge_probability(self, regime_type: str, vol_level: str, 
                                   trend_strength: float) -> float:
        """
        Calculate probability of having edge in current regime
        Returns 0-100
        """
        base_edges = {
            'trending_up': 75,
            'trending_down': 75,
            'ranging': 60,
            'breakout': 70,
            'volatile': 40
        }
        
        base_edge = base_edges.get(regime_type, 50)
        
        # Adjust for volatility
        vol_adjustments = {
            'low': 5,
            'medium': 0,
            'high': -10,
            'extreme': -30
        }
        
        vol_adj = vol_adjustments.get(vol_level, 0)
        
        # Adjust for trend strength
        trend_adj = (trend_strength - 0.5) * 20  # -10 to +10
        
        edge_prob = base_edge + vol_adj + trend_adj
        
        return max(0, min(100, edge_prob))
    
    def _detect_risk_sentiment(self, df: pd.DataFrame) -> str:
        """Detect risk-on or risk-off sentiment"""
        try:
            # Simple: rising prices + volume = risk-on
            price_change = (df.iloc[-1]['close'] - df.iloc[-20]['close']) / df.iloc[-20]['close']
            volume_ratio = df.iloc[-5:]['volume'].mean() / df.iloc[-50:]['volume'].mean()
            
            if price_change > 0.05 and volume_ratio > 1.2:
                return 'risk_on'
            elif price_change < -0.05 and volume_ratio > 1.2:
                return 'risk_off'
            else:
                return 'neutral'
        except:
            return 'neutral'
    
    def _identify_market_phase(self, df: pd.DataFrame) -> str:
        """Identify Wyckoff market phase"""
        try:
            # Simplified Wyckoff phase detection
            sma_50 = df.iloc[-50:]['close'].mean()
            current_price = df.iloc[-1]['close']
            volume_trend = df.iloc[-10:]['volume'].mean() / df.iloc[-50:]['volume'].mean()
            
            if current_price < sma_50 * 0.95 and volume_trend < 0.8:
                return 'accumulation'
            elif current_price > sma_50 and volume_trend > 1.2:
                return 'markup'
            elif current_price > sma_50 * 1.05 and volume_trend < 0.8:
                return 'distribution'
            elif current_price < sma_50 and volume_trend > 1.2:
                return 'markdown'
            else:
                return 'transition'
        except:
            return 'unknown'
    
    def _determine_optimal_timeframe(self, regime_type: str, vol_level: str) -> str:
        """Determine optimal timeframe for current regime"""
        if regime_type in ['trending_up', 'trending_down']:
            if vol_level == 'low':
                return '1h'
            else:
                return '4h'
        elif regime_type == 'ranging':
            return '15m'
        elif regime_type == 'breakout':
            return '5m'
        elif regime_type == 'volatile':
            return '1d'  # Stay on higher TF
        else:
            return '1h'
    
    def _calculate_regime_strength(self, confidence: float, trend_strength: float, 
                                  volatility: float) -> float:
        """Calculate overall regime strength (0-100)"""
        # Strong regime = high confidence + appropriate volatility
        strength = confidence * 50  # 0-50 from confidence
        strength += trend_strength * 30  # 0-30 from trend
        
        # Moderate volatility is good
        if 0.02 < volatility < 0.04:
            strength += 20
        elif 0.015 < volatility < 0.05:
            strength += 10
        
        return min(100, strength)
    
    def _estimate_regime_duration(self, regime_type: str, df: pd.DataFrame) -> str:
        """Estimate how long regime will last"""
        # Simplified estimation
        if regime_type in ['trending_up', 'trending_down']:
            return 'medium'  # Trends last weeks
        elif regime_type == 'ranging':
            return 'long'  # Ranges can last months
        elif regime_type == 'breakout':
            return 'short'  # Breakouts are quick
        elif regime_type == 'volatile':
            return 'short'  # Volatility spikes are temporary
        else:
            return 'unknown'
    
    def _calculate_adx(self, df: pd.DataFrame, period: int = 14) -> float:
        """Calculate ADX (Average Directional Index)"""
        try:
            # Simplified ADX calculation
            high = df['high'].values
            low = df['low'].values
            close = df['close'].values
            
            # Calculate +DM and -DM
            dm_plus = []
            dm_minus = []
            
            for i in range(1, len(df)):
                high_diff = high[i] - high[i-1]
                low_diff = low[i-1] - low[i]
                
                if high_diff > low_diff and high_diff > 0:
                    dm_plus.append(high_diff)
                else:
                    dm_plus.append(0)
                
                if low_diff > high_diff and low_diff > 0:
                    dm_minus.append(low_diff)
                else:
                    dm_minus.append(0)
            
            # Simplified ADX (just average of DMs)
            adx = (statistics.mean(dm_plus[-period:]) + statistics.mean(dm_minus[-period:])) / 2
            
            return adx
        except:
            return 20.0
    
    def _calculate_atr_ratio(self, df: pd.DataFrame) -> float:
        """Calculate ATR ratio (current ATR / average ATR)"""
        try:
            current_atr = self._calculate_volatility_regime(df)
            
            # Calculate historical ATR
            historical_atrs = []
            for i in range(50, len(df), 10):
                hist_df = df.iloc[i-50:i]
                hist_atr = self._calculate_volatility_regime(hist_df)
                historical_atrs.append(hist_atr)
            
            avg_atr = statistics.mean(historical_atrs) if historical_atrs else current_atr
            
            ratio = current_atr / avg_atr if avg_atr > 0 else 1.0
            
            return ratio
        except:
            return 1.0


# Singleton instance
_regime_detector = None

def get_regime_detector() -> MarketRegimeDetector:
    """Get or create regime detector instance"""
    global _regime_detector
    if _regime_detector is None:
        _regime_detector = MarketRegimeDetector()
    return _regime_detector
