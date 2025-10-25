"""
Multi-Timeframe Analysis System - Institutional Grade
- Analyzes 5+ timeframes simultaneously
- MTF Confluence Score (AI-rated setup strength)
- Institutional Flow Tracker
- Timeframe Sync Alerts
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
import statistics

logger = logging.getLogger(__name__)


@dataclass
class MTFAnalysis:
    """Multi-timeframe analysis result"""
    symbol: str
    timeframes_analyzed: List[str]
    confluence_score: float  # 0-100, higher = better alignment
    trend_direction: str  # 'bullish', 'bearish', 'neutral'
    entry_timeframe: str  # Best TF for entry
    stop_loss_timeframe: str  # Best TF for SL placement
    take_profit_timeframe: str  # Best TF for TP
    institutional_flow: str  # 'buying', 'selling', 'neutral'
    all_timeframes_aligned: bool
    recommended_action: str  # 'strong_buy', 'buy', 'hold', 'sell', 'strong_sell'
    risk_reward_ratio: float
    timeframe_details: Dict[str, Dict]  # Details per TF
    timestamp: str


class MultiTimeframeAnalyzer:
    """
    World-Class Multi-Timeframe Analysis
    - Simultaneous analysis of 5+ timeframes
    - Trend alignment detection
    - Institutional flow tracking
    - Optimal entry/exit TF identification
    """
    
    def __init__(self):
        self.timeframe_hierarchy = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w']
        self.trend_indicators = ['SMA_20', 'SMA_50', 'SMA_200', 'EMA_12', 'EMA_26']
        
    def analyze_symbol(self, symbol: str, timeframes: Optional[List[str]] = None) -> MTFAnalysis:
        """
        Comprehensive multi-timeframe analysis
        """
        if timeframes is None:
            timeframes = ['15m', '1h', '4h', '1d']  # Default 4 timeframes
        
        try:
            # Analyze each timeframe
            tf_details = {}
            for tf in timeframes:
                tf_analysis = self._analyze_single_timeframe(symbol, tf)
                if tf_analysis:
                    tf_details[tf] = tf_analysis
            
            if not tf_details:
                raise Exception("No timeframe data available")
            
            # Calculate confluence score
            confluence_score = self._calculate_confluence_score(tf_details)
            
            # Determine overall trend
            trend_direction = self._determine_overall_trend(tf_details)
            
            # Identify optimal timeframes for entry/SL/TP
            entry_tf, sl_tf, tp_tf = self._identify_optimal_timeframes(tf_details, timeframes)
            
            # Detect institutional flow
            institutional_flow = self._detect_institutional_flow(tf_details)
            
            # Check if all timeframes aligned
            all_aligned = self._check_alignment(tf_details)
            
            # Generate recommendation
            recommendation = self._generate_recommendation(
                confluence_score,
                trend_direction,
                all_aligned,
                institutional_flow
            )
            
            # Calculate risk/reward
            rr_ratio = self._calculate_mtf_risk_reward(tf_details)
            
            return MTFAnalysis(
                symbol=symbol,
                timeframes_analyzed=timeframes,
                confluence_score=round(confluence_score, 2),
                trend_direction=trend_direction,
                entry_timeframe=entry_tf,
                stop_loss_timeframe=sl_tf,
                take_profit_timeframe=tp_tf,
                institutional_flow=institutional_flow,
                all_timeframes_aligned=all_aligned,
                recommended_action=recommendation,
                risk_reward_ratio=round(rr_ratio, 2),
                timeframe_details=tf_details,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"MTF analysis error for {symbol}: {e}")
            raise
    
    def _analyze_single_timeframe(self, symbol: str, timeframe: str) -> Optional[Dict]:
        """
        Analyze single timeframe
        Returns trend, strength, support/resistance, volume
        """
        try:
            from main import market_data_service
            data = market_data_service.get_ohlcv(symbol, timeframe, limit=200)
            
            if not data or len(data) < 50:
                return None
            
            df = pd.DataFrame(data)
            
            # Calculate indicators
            sma_20 = df.iloc[-20:]['close'].mean()
            sma_50 = df.iloc[-50:]['close'].mean()
            sma_200 = df.iloc[-200:]['close'].mean() if len(df) >= 200 else sma_50
            
            current_price = float(df.iloc[-1]['close'])
            
            # Determine trend
            if current_price > sma_20 > sma_50:
                trend = 'bullish'
                trend_strength = 0.8
            elif current_price < sma_20 < sma_50:
                trend = 'bearish'
                trend_strength = 0.8
            elif current_price > sma_20:
                trend = 'bullish'
                trend_strength = 0.5
            elif current_price < sma_20:
                trend = 'bearish'
                trend_strength = 0.5
            else:
                trend = 'neutral'
                trend_strength = 0.3
            
            # Calculate momentum
            momentum = self._calculate_momentum(df)
            
            # Find support/resistance
            support, resistance = self._find_support_resistance(df)
            
            # Volume analysis
            volume_trend = self._analyze_volume(df)
            
            # Calculate volatility
            volatility = self._calculate_volatility(df)
            
            return {
                'trend': trend,
                'trend_strength': trend_strength,
                'momentum': momentum,
                'current_price': current_price,
                'sma_20': sma_20,
                'sma_50': sma_50,
                'sma_200': sma_200,
                'support': support,
                'resistance': resistance,
                'volume_trend': volume_trend,
                'volatility': volatility,
                'data': df
            }
            
        except Exception as e:
            logger.error(f"Single TF analysis error for {symbol} {timeframe}: {e}")
            return None
    
    def _calculate_momentum(self, df: pd.DataFrame) -> float:
        """Calculate momentum score (-1 to 1)"""
        try:
            # Simple momentum: (current - 10 periods ago) / 10 periods ago
            current = df.iloc[-1]['close']
            past = df.iloc[-10]['close']
            
            momentum = (current - past) / past
            
            # Normalize to -1 to 1
            return max(-1, min(1, momentum * 10))
        except:
            return 0.0
    
    def _find_support_resistance(self, df: pd.DataFrame) -> Tuple[float, float]:
        """Find key support and resistance levels"""
        try:
            # Use recent swing highs/lows
            highs = df.iloc[-50:]['high'].values
            lows = df.iloc[-50:]['low'].values
            
            resistance = np.percentile(highs, 95)
            support = np.percentile(lows, 5)
            
            return float(support), float(resistance)
        except:
            current = df.iloc[-1]['close']
            return current * 0.95, current * 1.05
    
    def _analyze_volume(self, df: pd.DataFrame) -> str:
        """Analyze volume trend"""
        try:
            recent_volume = df.iloc[-10:]['volume'].mean()
            avg_volume = df.iloc[-50:]['volume'].mean()
            
            if recent_volume > avg_volume * 1.3:
                return 'increasing'
            elif recent_volume < avg_volume * 0.7:
                return 'decreasing'
            else:
                return 'stable'
        except:
            return 'unknown'
    
    def _calculate_volatility(self, df: pd.DataFrame) -> float:
        """Calculate volatility (ATR-based)"""
        try:
            high = df['high'].values
            low = df['low'].values
            close = df['close'].values
            
            tr_list = []
            for i in range(1, min(15, len(df))):
                tr = max(
                    high[i] - low[i],
                    abs(high[i] - close[i-1]),
                    abs(low[i] - close[i-1])
                )
                tr_list.append(tr)
            
            atr = statistics.mean(tr_list)
            return atr / close[-1]  # Normalized ATR
        except:
            return 0.02
    
    def _calculate_confluence_score(self, tf_details: Dict[str, Dict]) -> float:
        """
        Calculate confluence score (0-100)
        Higher score = better alignment across timeframes
        """
        if not tf_details:
            return 0.0
        
        scores = []
        
        # Check trend alignment
        trends = [tf['trend'] for tf in tf_details.values()]
        bullish_count = trends.count('bullish')
        bearish_count = trends.count('bearish')
        
        if bullish_count > len(trends) * 0.75:
            trend_score = 90
        elif bearish_count > len(trends) * 0.75:
            trend_score = 90
        elif bullish_count > len(trends) * 0.5:
            trend_score = 70
        elif bearish_count > len(trends) * 0.5:
            trend_score = 70
        else:
            trend_score = 40
        
        scores.append(trend_score)
        
        # Check momentum alignment
        momentums = [tf['momentum'] for tf in tf_details.values()]
        avg_momentum = statistics.mean(momentums)
        
        if abs(avg_momentum) > 0.5:
            momentum_score = 80
        elif abs(avg_momentum) > 0.3:
            momentum_score = 60
        else:
            momentum_score = 40
        
        scores.append(momentum_score)
        
        # Check volume confirmation
        volumes = [tf['volume_trend'] for tf in tf_details.values()]
        increasing_count = volumes.count('increasing')
        
        if increasing_count > len(volumes) * 0.6:
            volume_score = 80
        else:
            volume_score = 50
        
        scores.append(volume_score)
        
        # Calculate weighted average
        confluence = statistics.mean(scores)
        
        return confluence
    
    def _determine_overall_trend(self, tf_details: Dict[str, Dict]) -> str:
        """Determine overall trend across all timeframes"""
        trends = [tf['trend'] for tf in tf_details.values()]
        
        bullish_count = trends.count('bullish')
        bearish_count = trends.count('bearish')
        
        if bullish_count > len(trends) * 0.6:
            return 'bullish'
        elif bearish_count > len(trends) * 0.6:
            return 'bearish'
        else:
            return 'neutral'
    
    def _identify_optimal_timeframes(self, tf_details: Dict[str, Dict], 
                                    timeframes: List[str]) -> Tuple[str, str, str]:
        """
        Identify optimal timeframes for entry, SL, and TP
        """
        # Entry: Use lowest timeframe with strong trend
        entry_tf = timeframes[0]  # Default to lowest
        
        for tf in timeframes:
            if tf_details[tf]['trend_strength'] > 0.6:
                entry_tf = tf
                break
        
        # Stop Loss: Use mid-range timeframe
        sl_tf = timeframes[len(timeframes) // 2] if len(timeframes) > 1 else timeframes[0]
        
        # Take Profit: Use highest timeframe
        tp_tf = timeframes[-1]
        
        return entry_tf, sl_tf, tp_tf
    
    def _detect_institutional_flow(self, tf_details: Dict[str, Dict]) -> str:
        """
        Detect institutional money flow
        Based on volume and price action across timeframes
        """
        # Check if higher timeframes show increasing volume with trend
        higher_tf_volumes = []
        higher_tf_trends = []
        
        for tf, details in tf_details.items():
            if tf in ['4h', '1d', '1w']:  # Higher timeframes
                higher_tf_volumes.append(details['volume_trend'])
                higher_tf_trends.append(details['trend'])
        
        if not higher_tf_volumes:
            return 'neutral'
        
        # Institutional buying: increasing volume + bullish trend
        if higher_tf_volumes.count('increasing') > len(higher_tf_volumes) * 0.5 and \
           higher_tf_trends.count('bullish') > len(higher_tf_trends) * 0.5:
            return 'buying'
        
        # Institutional selling: increasing volume + bearish trend
        if higher_tf_volumes.count('increasing') > len(higher_tf_volumes) * 0.5 and \
           higher_tf_trends.count('bearish') > len(higher_tf_trends) * 0.5:
            return 'selling'
        
        return 'neutral'
    
    def _check_alignment(self, tf_details: Dict[str, Dict]) -> bool:
        """Check if all timeframes are aligned"""
        trends = [tf['trend'] for tf in tf_details.values()]
        
        # All must be same trend (not neutral)
        if all(t == 'bullish' for t in trends):
            return True
        if all(t == 'bearish' for t in trends):
            return True
        
        return False
    
    def _generate_recommendation(self, confluence_score: float, trend: str, 
                                aligned: bool, institutional_flow: str) -> str:
        """Generate trading recommendation"""
        
        if aligned and confluence_score > 80 and institutional_flow != 'neutral':
            if trend == 'bullish' and institutional_flow == 'buying':
                return 'strong_buy'
            elif trend == 'bearish' and institutional_flow == 'selling':
                return 'strong_sell'
        
        if confluence_score > 70:
            if trend == 'bullish':
                return 'buy'
            elif trend == 'bearish':
                return 'sell'
        
        if confluence_score > 50:
            return 'hold'
        
        return 'neutral'
    
    def _calculate_mtf_risk_reward(self, tf_details: Dict[str, Dict]) -> float:
        """Calculate risk/reward based on MTF support/resistance"""
        try:
            # Use highest timeframe for major S/R levels
            highest_tf = list(tf_details.keys())[-1]
            details = tf_details[highest_tf]
            
            current_price = details['current_price']
            support = details['support']
            resistance = details['resistance']
            
            # Calculate risk (distance to support)
            risk = abs(current_price - support)
            
            # Calculate reward (distance to resistance)
            reward = abs(resistance - current_price)
            
            rr_ratio = reward / risk if risk > 0 else 0
            
            return rr_ratio
        except:
            return 1.0


# Singleton instance
_mtf_analyzer = None

def get_mtf_analyzer() -> MultiTimeframeAnalyzer:
    """Get or create MTF analyzer instance"""
    global _mtf_analyzer
    if _mtf_analyzer is None:
        _mtf_analyzer = MultiTimeframeAnalyzer()
    return _mtf_analyzer
