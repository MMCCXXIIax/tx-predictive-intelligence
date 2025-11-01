"""
Advanced Raw Data Analysis Service
Provides institutional-grade analysis beyond basic pattern detection:
- Multi-asset correlation analysis
- Order flow imbalance detection
- Market microstructure analysis
- Regime-adaptive modeling

NO MOCK DATA - 100% real-time market data
"""

import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

import numpy as np
import pandas as pd
import yfinance as yf
from scipy import stats
from scipy.signal import find_peaks
from sklearn.preprocessing import StandardScaler

# Technical indicators
from ta.trend import ADXIndicator, EMAIndicator
from ta.volatility import AverageTrueRange, BollingerBands
from ta.volume import OnBalanceVolumeIndicator, ChaikinMoneyFlowIndicator

logger = logging.getLogger(__name__)


class MarketRegime(Enum):
    """Market regime types"""
    BULL_TREND = "bull_trend"
    BEAR_TREND = "bear_trend"
    RANGING = "ranging"
    VOLATILE = "volatile"
    UNKNOWN = "unknown"


class OrderFlowType(Enum):
    """Order flow classification"""
    ACCUMULATION = "accumulation"
    DISTRIBUTION = "distribution"
    NEUTRAL = "neutral"
    ABSORPTION = "absorption"


@dataclass
class CorrelationInsight:
    """Correlation analysis result"""
    symbol: str
    correlated_with: str
    correlation: float
    lead_lag_hours: int
    strength: str
    relationship_type: str


@dataclass
class OrderFlowSignal:
    """Order flow imbalance signal"""
    symbol: str
    flow_type: OrderFlowType
    confidence: float
    buy_pressure: float
    sell_pressure: float
    institutional_footprint: bool
    volume_anomaly: float


@dataclass
class MicrostructureInsight:
    """Market microstructure analysis"""
    symbol: str
    spread_estimate: float
    volatility_regime: str
    optimal_entry_time: str
    market_maker_activity: str
    liquidity_score: float


@dataclass
class RegimeSignal:
    """Market regime detection"""
    symbol: str
    current_regime: MarketRegime
    regime_confidence: float
    regime_duration_hours: int
    transition_probability: Dict[str, float]


class AdvancedRawDataAnalyzer:
    """
    Advanced raw data analysis system
    Processes OHLCV data for institutional-grade insights
    """
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        
    # ==================== A. MULTI-ASSET CORRELATION ANALYSIS ====================
    
    def analyze_correlations(
        self, 
        symbols: List[str],
        period: str = '30d',
        interval: str = '1h'
    ) -> Dict[str, Any]:
        """
        Analyze raw price correlations across multiple assets
        
        Returns:
            - Correlation matrix
            - Leading/lagging relationships
            - Sector rotation signals
            - Cross-asset trading opportunities
        """
        try:
            logger.info(f"Analyzing correlations for {len(symbols)} symbols")
            
            # Download raw OHLCV data for all symbols
            price_data = {}
            for symbol in symbols:
                try:
                    df = yf.download(
                        symbol,
                        period=period,
                        interval=interval,
                        progress=False,
                        auto_adjust=True
                    )
                    if not df.empty:
                        price_data[symbol] = df['Close']
                    time.sleep(0.2)  # Rate limiting
                except Exception as e:
                    logger.warning(f"Failed to download {symbol}: {e}")
                    continue
            
            if len(price_data) < 2:
                return {'error': 'Insufficient data for correlation analysis'}
            
            # Create price dataframe
            prices_df = pd.DataFrame(price_data)
            prices_df = prices_df.dropna()
            
            # Calculate returns
            returns_df = prices_df.pct_change().dropna()
            
            # Correlation matrix
            corr_matrix = returns_df.corr()
            
            # Find strong correlations
            strong_correlations = []
            for i, sym1 in enumerate(symbols):
                if sym1 not in corr_matrix.columns:
                    continue
                for j, sym2 in enumerate(symbols):
                    if i >= j or sym2 not in corr_matrix.columns:
                        continue
                    
                    corr_val = corr_matrix.loc[sym1, sym2]
                    if abs(corr_val) > 0.7:  # Strong correlation threshold
                        # Detect lead-lag relationship
                        lead_lag = self._detect_lead_lag(
                            returns_df[sym1], 
                            returns_df[sym2]
                        )
                        
                        strong_correlations.append({
                            'symbol_1': sym1,
                            'symbol_2': sym2,
                            'correlation': float(corr_val),
                            'strength': 'very_strong' if abs(corr_val) > 0.9 else 'strong',
                            'type': 'positive' if corr_val > 0 else 'negative',
                            'lead_lag_hours': lead_lag,
                            'trading_opportunity': abs(corr_val) > 0.85
                        })
            
            # Detect sector rotations
            sector_signals = self._detect_sector_rotation(returns_df)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'symbols_analyzed': len(price_data),
                'correlation_matrix': corr_matrix.to_dict(),
                'strong_correlations': strong_correlations,
                'sector_rotation_signals': sector_signals,
                'data_source': 'yfinance_real_time',
                'period': period,
                'interval': interval
            }
            
        except Exception as e:
            logger.error(f"Correlation analysis failed: {e}")
            return {'error': str(e)}
    
    def _detect_lead_lag(
        self, 
        series1: pd.Series, 
        series2: pd.Series, 
        max_lag: int = 24
    ) -> int:
        """Detect lead-lag relationship between two series"""
        try:
            correlations = []
            for lag in range(-max_lag, max_lag + 1):
                if lag < 0:
                    corr = series1.iloc[:lag].corr(series2.iloc[-lag:])
                elif lag > 0:
                    corr = series1.iloc[lag:].corr(series2.iloc[:-lag])
                else:
                    corr = series1.corr(series2)
                correlations.append((lag, corr))
            
            # Find lag with maximum absolute correlation
            best_lag = max(correlations, key=lambda x: abs(x[1]))[0]
            return best_lag
        except:
            return 0
    
    def _detect_sector_rotation(self, returns_df: pd.DataFrame) -> List[Dict]:
        """Detect sector rotation patterns"""
        try:
            signals = []
            
            # Calculate recent performance (last 7 days vs previous 7 days)
            if len(returns_df) < 14:
                return signals
            
            recent_returns = returns_df.iloc[-7:].mean()
            previous_returns = returns_df.iloc[-14:-7].mean()
            
            momentum_change = recent_returns - previous_returns
            
            # Find symbols with significant momentum shifts
            for symbol in momentum_change.index:
                change = momentum_change[symbol]
                if abs(change) > 0.02:  # 2% threshold
                    signals.append({
                        'symbol': symbol,
                        'momentum_shift': float(change),
                        'direction': 'gaining' if change > 0 else 'losing',
                        'rotation_signal': 'buy' if change > 0.03 else ('sell' if change < -0.03 else 'hold')
                    })
            
            return signals
        except:
            return []
    
    # ==================== B. ORDER FLOW IMBALANCE DETECTION ====================
    
    def detect_order_flow_imbalance(
        self,
        symbol: str,
        period: str = '5d',
        interval: str = '5m'
    ) -> Dict[str, Any]:
        """
        Analyze raw volume and price action for institutional flow
        
        Detects:
            - Buy/sell pressure from volume analysis
            - Price-volume divergence
            - Absorption patterns (large volume, small price move)
            - Institutional footprints
        """
        try:
            logger.info(f"Analyzing order flow for {symbol}")
            
            # Download intraday OHLCV data
            df = yf.download(
                symbol,
                period=period,
                interval=interval,
                progress=False,
                auto_adjust=True
            )
            
            if df.empty or len(df) < 20:
                return {'error': 'Insufficient data'}
            
            df.columns = [c.lower() for c in df.columns]
            
            # Calculate buy/sell pressure
            df['price_change'] = df['close'] - df['open']
            df['range'] = df['high'] - df['low']
            
            # Buy pressure: close near high with volume
            df['buy_pressure'] = np.where(
                (df['close'] - df['low']) / (df['range'] + 1e-9) > 0.7,
                df['volume'],
                0
            )
            
            # Sell pressure: close near low with volume
            df['sell_pressure'] = np.where(
                (df['high'] - df['close']) / (df['range'] + 1e-9) > 0.7,
                df['volume'],
                0
            )
            
            # Calculate cumulative pressure
            total_buy = df['buy_pressure'].sum()
            total_sell = df['sell_pressure'].sum()
            total_volume = df['volume'].sum()
            
            # Pressure ratio
            if total_sell > 0:
                pressure_ratio = total_buy / total_sell
            else:
                pressure_ratio = 10.0 if total_buy > 0 else 1.0
            
            # Detect absorption (large volume, small price move)
            df['absorption'] = (df['volume'] > df['volume'].quantile(0.9)) & \
                              (abs(df['price_change']) < df['price_change'].std() * 0.5)
            
            absorption_count = df['absorption'].sum()
            
            # Detect institutional footprints
            # Large volume spikes with follow-through
            df['volume_spike'] = df['volume'] > df['volume'].rolling(20).mean() * 2
            df['follow_through'] = df['price_change'].rolling(3).sum() * df['price_change'] > 0
            
            institutional_signals = (df['volume_spike'] & df['follow_through']).sum()
            
            # Classify flow type
            if pressure_ratio > 1.5 and absorption_count < 3:
                flow_type = OrderFlowType.ACCUMULATION
                confidence = min(0.95, 0.6 + (pressure_ratio - 1.5) * 0.1)
            elif pressure_ratio < 0.67 and absorption_count < 3:
                flow_type = OrderFlowType.DISTRIBUTION
                confidence = min(0.95, 0.6 + (1.5 - pressure_ratio) * 0.1)
            elif absorption_count > 5:
                flow_type = OrderFlowType.ABSORPTION
                confidence = min(0.90, 0.5 + absorption_count * 0.05)
            else:
                flow_type = OrderFlowType.NEUTRAL
                confidence = 0.5
            
            # Volume anomaly score
            recent_vol = df['volume'].iloc[-10:].mean()
            avg_vol = df['volume'].mean()
            volume_anomaly = (recent_vol - avg_vol) / (avg_vol + 1e-9)
            
            return {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'flow_type': flow_type.value,
                'confidence': float(confidence),
                'buy_pressure_pct': float(total_buy / (total_volume + 1e-9) * 100),
                'sell_pressure_pct': float(total_sell / (total_volume + 1e-9) * 100),
                'pressure_ratio': float(pressure_ratio),
                'absorption_events': int(absorption_count),
                'institutional_footprints': int(institutional_signals),
                'volume_anomaly': float(volume_anomaly),
                'interpretation': self._interpret_order_flow(flow_type, confidence),
                'data_source': 'yfinance_real_time',
                'period': period,
                'interval': interval
            }
            
        except Exception as e:
            logger.error(f"Order flow analysis failed for {symbol}: {e}")
            return {'error': str(e)}
    
    def _interpret_order_flow(self, flow_type: OrderFlowType, confidence: float) -> str:
        """Provide human-readable interpretation"""
        interpretations = {
            OrderFlowType.ACCUMULATION: f"Strong buying pressure detected ({confidence:.0%} confidence). Institutions may be accumulating positions. Consider bullish bias.",
            OrderFlowType.DISTRIBUTION: f"Strong selling pressure detected ({confidence:.0%} confidence). Institutions may be distributing positions. Consider bearish bias.",
            OrderFlowType.ABSORPTION: f"Large volume with minimal price movement ({confidence:.0%} confidence). Smart money absorbing supply/demand. Watch for breakout direction.",
            OrderFlowType.NEUTRAL: "Balanced order flow. No clear institutional bias detected. Wait for clearer signals."
        }
        return interpretations.get(flow_type, "Unknown flow pattern")
    
    # ==================== C. MARKET MICROSTRUCTURE ANALYSIS ====================
    
    def analyze_microstructure(
        self,
        symbol: str,
        period: str = '1d',
        interval: str = '1m'
    ) -> Dict[str, Any]:
        """
        High-frequency raw data analysis
        
        Analyzes:
            - Bid-ask spread inference from OHLC
            - Intraday volatility patterns
            - Opening/closing auction behavior
            - Market maker activity
            - Optimal entry times
        """
        try:
            logger.info(f"Analyzing microstructure for {symbol}")
            
            # Download 1-minute intraday data
            df = yf.download(
                symbol,
                period=period,
                interval=interval,
                progress=False,
                auto_adjust=True
            )
            
            if df.empty or len(df) < 60:
                return {'error': 'Insufficient intraday data'}
            
            df.columns = [c.lower() for c in df.columns]
            
            # Estimate bid-ask spread from high-low range
            df['spread_estimate'] = (df['high'] - df['low']) / df['close']
            avg_spread = df['spread_estimate'].mean()
            
            # Intraday volatility pattern
            df['hour'] = df.index.hour
            df['minute'] = df.index.minute
            df['returns'] = df['close'].pct_change()
            df['volatility'] = df['returns'].rolling(15).std()
            
            # Volatility by hour
            hourly_vol = df.groupby('hour')['volatility'].mean()
            
            # Find high/low volatility hours
            high_vol_hours = hourly_vol.nlargest(3).index.tolist()
            low_vol_hours = hourly_vol.nsmallest(3).index.tolist()
            
            # Detect market maker patterns
            # Look for mean reversion behavior
            df['price_deviation'] = (df['close'] - df['close'].rolling(20).mean()) / df['close'].rolling(20).std()
            mean_reversion_strength = df['price_deviation'].autocorr(lag=1)
            
            if mean_reversion_strength < -0.3:
                mm_activity = "high_mean_reversion"
            elif mean_reversion_strength > 0.3:
                mm_activity = "trending"
            else:
                mm_activity = "balanced"
            
            # Liquidity score (inverse of spread + volume consideration)
            recent_volume = df['volume'].iloc[-30:].mean()
            avg_volume = df['volume'].mean()
            liquidity_score = (recent_volume / (avg_volume + 1e-9)) * (1 / (avg_spread + 1e-9))
            liquidity_score = min(10.0, liquidity_score)  # Cap at 10
            
            # Optimal entry time (lowest spread + decent volume)
            df['entry_score'] = (1 / (df['spread_estimate'] + 1e-9)) * (df['volume'] / df['volume'].mean())
            best_entry_idx = df['entry_score'].idxmax()
            optimal_entry_time = f"{best_entry_idx.hour:02d}:{best_entry_idx.minute:02d}"
            
            # Current volatility regime
            current_vol = df['volatility'].iloc[-1]
            vol_percentile = stats.percentileofscore(df['volatility'].dropna(), current_vol)
            
            if vol_percentile > 80:
                vol_regime = "high_volatility"
            elif vol_percentile < 20:
                vol_regime = "low_volatility"
            else:
                vol_regime = "normal_volatility"
            
            return {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'spread_estimate_pct': float(avg_spread * 100),
                'current_spread_pct': float(df['spread_estimate'].iloc[-1] * 100),
                'volatility_regime': vol_regime,
                'volatility_percentile': float(vol_percentile),
                'high_volatility_hours': [int(h) for h in high_vol_hours],
                'low_volatility_hours': [int(h) for h in low_vol_hours],
                'optimal_entry_time': optimal_entry_time,
                'market_maker_activity': mm_activity,
                'mean_reversion_strength': float(mean_reversion_strength),
                'liquidity_score': float(liquidity_score),
                'liquidity_rating': 'high' if liquidity_score > 5 else ('medium' if liquidity_score > 2 else 'low'),
                'trading_recommendation': self._microstructure_recommendation(vol_regime, mm_activity, liquidity_score),
                'data_source': 'yfinance_real_time',
                'period': period,
                'interval': interval
            }
            
        except Exception as e:
            logger.error(f"Microstructure analysis failed for {symbol}: {e}")
            return {'error': str(e)}
    
    def _microstructure_recommendation(self, vol_regime: str, mm_activity: str, liquidity: float) -> str:
        """Generate trading recommendation based on microstructure"""
        if vol_regime == "high_volatility" and liquidity < 2:
            return "High volatility + low liquidity. Use wider stops and smaller position sizes."
        elif vol_regime == "low_volatility" and mm_activity == "high_mean_reversion":
            return "Low volatility + mean reversion. Good for range trading strategies."
        elif mm_activity == "trending" and liquidity > 5:
            return "Trending market + high liquidity. Good for momentum strategies."
        else:
            return "Normal market conditions. Standard trading strategies applicable."
    
    # ==================== D. REGIME-ADAPTIVE MODELS ====================
    
    def detect_market_regime(
        self,
        symbol: str,
        period: str = '90d',
        interval: str = '1d'
    ) -> Dict[str, Any]:
        """
        Detect current market regime and provide regime-specific insights
        
        Regimes:
            - Bull Trend: Strong uptrend with momentum
            - Bear Trend: Strong downtrend with momentum
            - Ranging: Sideways movement, mean reversion
            - Volatile: High volatility, unpredictable
        """
        try:
            logger.info(f"Detecting market regime for {symbol}")
            
            # Download daily data
            df = yf.download(
                symbol,
                period=period,
                interval=interval,
                progress=False,
                auto_adjust=True
            )
            
            if df.empty or len(df) < 50:
                return {'error': 'Insufficient data for regime detection'}
            
            df.columns = [c.lower() for c in df.columns]
            
            # Calculate regime indicators
            # 1. Trend strength (ADX)
            adx = ADXIndicator(df['high'], df['low'], df['close'], window=14)
            df['adx'] = adx.adx()
            
            # 2. Trend direction (EMA crossover)
            df['ema_20'] = EMAIndicator(df['close'], window=20).ema_indicator()
            df['ema_50'] = EMAIndicator(df['close'], window=50).ema_indicator()
            
            # 3. Volatility (ATR and Bollinger Bands)
            atr = AverageTrueRange(df['high'], df['low'], df['close'], window=14)
            df['atr'] = atr.average_true_range()
            df['atr_pct'] = df['atr'] / df['close'] * 100
            
            bb = BollingerBands(df['close'], window=20, window_dev=2)
            df['bb_width'] = (bb.bollinger_hband() - bb.bollinger_lband()) / bb.bollinger_mavg() * 100
            
            # Current values
            current_adx = df['adx'].iloc[-1]
            current_ema_20 = df['ema_20'].iloc[-1]
            current_ema_50 = df['ema_50'].iloc[-1]
            current_atr_pct = df['atr_pct'].iloc[-1]
            current_bb_width = df['bb_width'].iloc[-1]
            current_price = df['close'].iloc[-1]
            
            # Regime classification logic
            regime, confidence = self._classify_regime(
                current_adx,
                current_ema_20,
                current_ema_50,
                current_price,
                current_atr_pct,
                current_bb_width
            )
            
            # Calculate regime duration
            regime_duration = self._calculate_regime_duration(df, regime)
            
            # Transition probabilities
            transition_probs = self._estimate_transition_probabilities(df)
            
            # Regime-specific recommendations
            recommendations = self._regime_specific_recommendations(regime)
            
            return {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'current_regime': regime.value,
                'regime_confidence': float(confidence),
                'regime_duration_days': int(regime_duration),
                'indicators': {
                    'adx': float(current_adx),
                    'ema_20_vs_50': 'bullish' if current_ema_20 > current_ema_50 else 'bearish',
                    'atr_pct': float(current_atr_pct),
                    'bb_width_pct': float(current_bb_width)
                },
                'transition_probabilities': transition_probs,
                'recommendations': recommendations,
                'optimal_strategy': self._get_optimal_strategy(regime),
                'data_source': 'yfinance_real_time',
                'period': period,
                'interval': interval
            }
            
        except Exception as e:
            logger.error(f"Regime detection failed for {symbol}: {e}")
            return {'error': str(e)}
    
    def _classify_regime(
        self,
        adx: float,
        ema_20: float,
        ema_50: float,
        price: float,
        atr_pct: float,
        bb_width: float
    ) -> Tuple[MarketRegime, float]:
        """Classify market regime based on indicators"""
        
        # High volatility regime
        if atr_pct > 3.0 or bb_width > 8.0:
            return MarketRegime.VOLATILE, 0.85
        
        # Trending regimes (ADX > 25 indicates strong trend)
        if adx > 25:
            if ema_20 > ema_50 and price > ema_20:
                # Strong uptrend
                confidence = min(0.95, 0.7 + (adx - 25) / 100)
                return MarketRegime.BULL_TREND, confidence
            elif ema_20 < ema_50 and price < ema_20:
                # Strong downtrend
                confidence = min(0.95, 0.7 + (adx - 25) / 100)
                return MarketRegime.BEAR_TREND, confidence
        
        # Ranging regime (weak ADX)
        if adx < 20:
            return MarketRegime.RANGING, 0.75
        
        # Default to unknown
        return MarketRegime.UNKNOWN, 0.50
    
    def _calculate_regime_duration(self, df: pd.DataFrame, current_regime: MarketRegime) -> int:
        """Estimate how long current regime has been active"""
        try:
            # Simplified: count consecutive days matching regime characteristics
            if current_regime == MarketRegime.BULL_TREND:
                # Count days where EMA20 > EMA50
                consecutive = 0
                for i in range(len(df) - 1, -1, -1):
                    if df['ema_20'].iloc[i] > df['ema_50'].iloc[i]:
                        consecutive += 1
                    else:
                        break
                return consecutive
            elif current_regime == MarketRegime.BEAR_TREND:
                consecutive = 0
                for i in range(len(df) - 1, -1, -1):
                    if df['ema_20'].iloc[i] < df['ema_50'].iloc[i]:
                        consecutive += 1
                    else:
                        break
                return consecutive
            else:
                return 0
        except:
            return 0
    
    def _estimate_transition_probabilities(self, df: pd.DataFrame) -> Dict[str, float]:
        """Estimate probability of transitioning to different regimes"""
        # Simplified transition model based on recent volatility and trend changes
        try:
            recent_vol = df['atr_pct'].iloc[-5:].mean()
            avg_vol = df['atr_pct'].mean()
            
            if recent_vol > avg_vol * 1.5:
                return {
                    'to_volatile': 0.60,
                    'to_bull_trend': 0.15,
                    'to_bear_trend': 0.15,
                    'to_ranging': 0.10
                }
            else:
                return {
                    'to_volatile': 0.10,
                    'to_bull_trend': 0.30,
                    'to_bear_trend': 0.30,
                    'to_ranging': 0.30
                }
        except:
            return {
                'to_volatile': 0.25,
                'to_bull_trend': 0.25,
                'to_bear_trend': 0.25,
                'to_ranging': 0.25
            }
    
    def _regime_specific_recommendations(self, regime: MarketRegime) -> List[str]:
        """Provide regime-specific trading recommendations"""
        recommendations = {
            MarketRegime.BULL_TREND: [
                "Use trend-following strategies (buy dips)",
                "Trail stops to protect profits",
                "Look for pullbacks to EMA20 for entries",
                "Avoid shorting against the trend"
            ],
            MarketRegime.BEAR_TREND: [
                "Use trend-following strategies (sell rallies)",
                "Consider short positions or protective puts",
                "Look for rallies to EMA20 for short entries",
                "Avoid buying against the trend"
            ],
            MarketRegime.RANGING: [
                "Use mean reversion strategies",
                "Buy support, sell resistance",
                "Tighter stops (range-bound movement)",
                "Avoid breakout strategies until regime changes"
            ],
            MarketRegime.VOLATILE: [
                "Reduce position sizes significantly",
                "Use wider stops to avoid whipsaws",
                "Wait for volatility to decrease",
                "Consider options strategies (straddles/strangles)"
            ],
            MarketRegime.UNKNOWN: [
                "Wait for clearer regime signals",
                "Use conservative position sizing",
                "Focus on high-probability setups only"
            ]
        }
        return recommendations.get(regime, ["No specific recommendations"])
    
    def _get_optimal_strategy(self, regime: MarketRegime) -> str:
        """Get optimal trading strategy for regime"""
        strategies = {
            MarketRegime.BULL_TREND: "Trend Following (Long Bias)",
            MarketRegime.BEAR_TREND: "Trend Following (Short Bias)",
            MarketRegime.RANGING: "Mean Reversion",
            MarketRegime.VOLATILE: "Volatility Trading / Options",
            MarketRegime.UNKNOWN: "Conservative / Wait"
        }
        return strategies.get(regime, "Undefined")


# Global instance
advanced_analyzer = AdvancedRawDataAnalyzer()
