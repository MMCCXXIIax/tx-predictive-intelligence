"""
TX Entry/Exit Signal Generator
Determines optimal entry and exit points for detected patterns
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone

class EntryExitSignal:
    """Represents an entry/exit trading signal"""
    def __init__(self, pattern_name: str, symbol: str, confidence: float):
        self.pattern = pattern_name
        self.symbol = symbol
        self.confidence = confidence
        self.current_price = 0.0
        self.entry_price = 0.0
        self.entry_timing = "immediate"  # immediate, next_candle, pullback
        self.stop_loss = 0.0
        self.take_profit_1 = 0.0
        self.take_profit_2 = 0.0
        self.risk_reward_ratio = 0.0
        self.position_size_recommendation = 0.0
        self.direction = "long"  # long or short
        self.entry_reason = ""
        self.exit_strategy = ""
        self.time_horizon = "short"  # short (1-3 days), medium (1-2 weeks), long (1+ month)
        
    def to_dict(self) -> Dict:
        """Convert signal to dictionary"""
        return {
            'pattern': self.pattern,
            'symbol': self.symbol,
            'confidence': self.confidence,
            'current_price': self.current_price,
            'entry_price': self.entry_price,
            'entry_timing': self.entry_timing,
            'stop_loss': self.stop_loss,
            'take_profit_1': self.take_profit_1,
            'take_profit_2': self.take_profit_2,
            'risk_reward_ratio': self.risk_reward_ratio,
            'position_size_recommendation': self.position_size_recommendation,
            'direction': self.direction,
            'entry_reason': self.entry_reason,
            'exit_strategy': self.exit_strategy,
            'time_horizon': self.time_horizon,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

class TXEntryExitEngine:
    """Generates smart entry/exit signals for detected patterns"""
    
    def __init__(self):
        # Pattern-specific entry/exit rules
        self.pattern_rules = self._initialize_pattern_rules()
        
    def generate_signal(self, pattern_name: str, symbol: str, market_data: Dict, 
                       confidence: float) -> EntryExitSignal:
        """
        Generate entry/exit signal for a detected pattern
        
        Args:
            pattern_name: Name of detected pattern
            symbol: Asset symbol
            market_data: Current market data (OHLC, volume, etc.)
            confidence: Pattern detection confidence (0.0 - 1.0)
        """
        
        signal = EntryExitSignal(pattern_name, symbol, confidence)
        signal.current_price = market_data.get('price', market_data.get('close', 0))
        
        # Get pattern-specific rules
        rules = self.pattern_rules.get(pattern_name.lower(), self.pattern_rules['default'])
        
        # Calculate entry point
        signal.entry_price, signal.entry_timing = self._calculate_entry_point(
            signal.current_price, market_data, rules
        )
        
        # Determine trade direction
        signal.direction = rules['direction']
        
        # Calculate stop loss and take profit levels
        signal.stop_loss = self._calculate_stop_loss(
            signal.entry_price, market_data, rules, signal.direction
        )
        
        signal.take_profit_1, signal.take_profit_2 = self._calculate_take_profits(
            signal.entry_price, market_data, rules, signal.direction
        )
        
        # Calculate risk/reward ratio
        if signal.direction == "long":
            risk = abs(signal.entry_price - signal.stop_loss)
            reward = abs(signal.take_profit_1 - signal.entry_price)
        else:
            risk = abs(signal.stop_loss - signal.entry_price)
            reward = abs(signal.entry_price - signal.take_profit_1)
            
        signal.risk_reward_ratio = reward / risk if risk > 0 else 0
        
        # Position size recommendation (risk 2% of capital)
        signal.position_size_recommendation = self._calculate_position_size(
            signal.entry_price, signal.stop_loss, portfolio_size=10000
        )
        
        # Set additional properties
        signal.entry_reason = rules['entry_reason']
        signal.exit_strategy = rules['exit_strategy']
        signal.time_horizon = rules['time_horizon']
        
        return signal
    
    def _initialize_pattern_rules(self) -> Dict:
        """Initialize pattern-specific trading rules"""
        return {
            'marubozu': {
                'direction': 'long',  # or 'short' based on color
                'entry_timing': 'immediate',
                'stop_loss_pct': 3.0,
                'take_profit_1_pct': 8.0,
                'take_profit_2_pct': 15.0,
                'entry_reason': 'Strong momentum continuation expected',
                'exit_strategy': 'Staged exit at profit targets or momentum reversal',
                'time_horizon': 'short'
            },
            'hammer': {
                'direction': 'long',
                'entry_timing': 'next_candle',  # Wait for confirmation
                'stop_loss_pct': 4.0,
                'take_profit_1_pct': 10.0,
                'take_profit_2_pct': 18.0,
                'entry_reason': 'Reversal pattern at support level',
                'exit_strategy': 'Take profits on strength, exit on reversal signals',
                'time_horizon': 'medium'
            },
            'bullish engulfing': {
                'direction': 'long',
                'entry_timing': 'immediate',
                'stop_loss_pct': 5.0,
                'take_profit_1_pct': 12.0,
                'take_profit_2_pct': 20.0,
                'entry_reason': 'Strong bullish reversal confirmed',
                'exit_strategy': 'Hold for trend continuation, exit on bearish signals',
                'time_horizon': 'medium'
            },
            'bearish engulfing': {
                'direction': 'short',
                'entry_timing': 'immediate',
                'stop_loss_pct': 5.0,
                'take_profit_1_pct': 12.0,
                'take_profit_2_pct': 20.0,
                'entry_reason': 'Strong bearish reversal confirmed',
                'exit_strategy': 'Hold for trend continuation, exit on bullish signals',
                'time_horizon': 'medium'
            },
            'morning star': {
                'direction': 'long',
                'entry_timing': 'next_candle',
                'stop_loss_pct': 6.0,
                'take_profit_1_pct': 15.0,
                'take_profit_2_pct': 25.0,
                'entry_reason': 'Three-candle reversal pattern completed',
                'exit_strategy': 'Major reversal - hold for larger moves',
                'time_horizon': 'long'
            },
            'evening star': {
                'direction': 'short',
                'entry_timing': 'next_candle',
                'stop_loss_pct': 6.0,
                'take_profit_1_pct': 15.0,
                'take_profit_2_pct': 25.0,
                'entry_reason': 'Three-candle bearish reversal completed',
                'exit_strategy': 'Major reversal - hold for larger moves',
                'time_horizon': 'long'
            },
            'shooting star': {
                'direction': 'short',
                'entry_timing': 'next_candle',
                'stop_loss_pct': 4.0,
                'take_profit_1_pct': 8.0,
                'take_profit_2_pct': 15.0,
                'entry_reason': 'Rejection at resistance level',
                'exit_strategy': 'Quick reversal play, exit on support test',
                'time_horizon': 'short'
            },
            'doji': {
                'direction': 'neutral',  # Direction based on context
                'entry_timing': 'next_candle',  # Wait for direction confirmation
                'stop_loss_pct': 3.0,
                'take_profit_1_pct': 6.0,
                'take_profit_2_pct': 12.0,
                'entry_reason': 'Indecision - wait for breakout direction',
                'exit_strategy': 'Quick move in breakout direction',
                'time_horizon': 'short'
            },
            'piercing line': {
                'direction': 'long',
                'entry_timing': 'immediate',
                'stop_loss_pct': 4.5,
                'take_profit_1_pct': 11.0,
                'take_profit_2_pct': 18.0,
                'entry_reason': 'Bullish reversal with strong buying pressure',
                'exit_strategy': 'Partial profits on resistance, hold core position',
                'time_horizon': 'medium'
            },
            'dark cloud cover': {
                'direction': 'short',
                'entry_timing': 'immediate',
                'stop_loss_pct': 4.5,
                'take_profit_1_pct': 11.0,
                'take_profit_2_pct': 18.0,
                'entry_reason': 'Bearish reversal with strong selling pressure',
                'exit_strategy': 'Partial profits on support, hold core position',
                'time_horizon': 'medium'
            },
            'default': {
                'direction': 'long',
                'entry_timing': 'next_candle',
                'stop_loss_pct': 5.0,
                'take_profit_1_pct': 10.0,
                'take_profit_2_pct': 20.0,
                'entry_reason': 'Pattern detected - standard entry rules',
                'exit_strategy': 'Standard risk management approach',
                'time_horizon': 'medium'
            }
        }
    
    def _calculate_entry_point(self, current_price: float, market_data: Dict, 
                             rules: Dict) -> Tuple[float, str]:
        """Calculate optimal entry price and timing"""
        
        entry_timing = rules['entry_timing']
        
        if entry_timing == 'immediate':
            return current_price, 'immediate'
        elif entry_timing == 'next_candle':
            # Recommend entering at next candle open
            return current_price, 'next_candle'  # In real implementation, this would be next open
        elif entry_timing == 'pullback':
            # Wait for small pullback before entering
            pullback_price = current_price * 0.98  # 2% pullback
            return pullback_price, 'pullback'
        
        return current_price, 'immediate'
    
    def _calculate_stop_loss(self, entry_price: float, market_data: Dict, 
                           rules: Dict, direction: str) -> float:
        """Calculate stop loss level"""
        
        stop_loss_pct = rules['stop_loss_pct']
        
        if direction == 'long':
            return entry_price * (1 - stop_loss_pct / 100)
        else:
            return entry_price * (1 + stop_loss_pct / 100)
    
    def _calculate_take_profits(self, entry_price: float, market_data: Dict,
                              rules: Dict, direction: str) -> Tuple[float, float]:
        """Calculate take profit levels"""
        
        tp1_pct = rules['take_profit_1_pct']
        tp2_pct = rules['take_profit_2_pct']
        
        if direction == 'long':
            tp1 = entry_price * (1 + tp1_pct / 100)
            tp2 = entry_price * (1 + tp2_pct / 100)
        else:
            tp1 = entry_price * (1 - tp1_pct / 100)
            tp2 = entry_price * (1 - tp2_pct / 100)
        
        return tp1, tp2
    
    def _calculate_position_size(self, entry_price: float, stop_loss: float, 
                               portfolio_size: float = 10000, 
                               risk_pct: float = 2.0) -> float:
        """Calculate recommended position size based on risk management"""
        
        risk_amount = portfolio_size * (risk_pct / 100)
        price_risk = abs(entry_price - stop_loss)
        
        if price_risk > 0:
            position_size = risk_amount / price_risk
            return min(position_size, portfolio_size * 0.1)  # Max 10% of portfolio
        
        return 0.0
    
    def get_pattern_analysis(self, pattern_name: str) -> Dict:
        """Get detailed analysis for a specific pattern"""
        
        rules = self.pattern_rules.get(pattern_name.lower(), self.pattern_rules['default'])
        
        return {
            'pattern': pattern_name,
            'typical_direction': rules['direction'],
            'success_rate': self._get_pattern_success_rate(pattern_name),
            'avg_gain': self._get_pattern_avg_gain(pattern_name),
            'avg_loss': self._get_pattern_avg_loss(pattern_name),
            'best_timeframes': ['1h', '4h', '1d'],  # Pattern works best on these timeframes
            'market_conditions': 'Works best in trending markets',
            'entry_strategy': rules['entry_reason'],
            'exit_strategy': rules['exit_strategy'],
            'risk_level': 'Medium',
            'time_horizon': rules['time_horizon']
        }
    
    def _get_pattern_success_rate(self, pattern_name: str) -> float:
        """Get historical success rate for pattern (simulated)"""
        # In production, this would come from historical backtesting
        success_rates = {
            'marubozu': 78.5,
            'hammer': 72.3,
            'bullish engulfing': 85.2,
            'bearish engulfing': 83.7,
            'morning star': 89.1,
            'evening star': 87.4,
            'shooting star': 69.8,
            'doji': 45.5,  # Lower because it's indecision
            'piercing line': 74.6,
            'dark cloud cover': 76.2
        }
        
        return success_rates.get(pattern_name.lower(), 65.0)
    
    def _get_pattern_avg_gain(self, pattern_name: str) -> float:
        """Get average gain when pattern succeeds (simulated)"""
        avg_gains = {
            'marubozu': 12.3,
            'hammer': 15.7,
            'bullish engulfing': 18.9,
            'bearish engulfing': 16.4,
            'morning star': 24.2,
            'evening star': 22.1,
            'shooting star': 9.8,
            'doji': 8.5,
            'piercing line': 14.2,
            'dark cloud cover': 13.8
        }
        
        return avg_gains.get(pattern_name.lower(), 12.0)
    
    def _get_pattern_avg_loss(self, pattern_name: str) -> float:
        """Get average loss when pattern fails (simulated)"""
        avg_losses = {
            'marubozu': -6.2,
            'hammer': -7.1,
            'bullish engulfing': -8.3,
            'bearish engulfing': -7.9,
            'morning star': -9.8,
            'evening star': -9.2,
            'shooting star': -5.4,
            'doji': -4.8,
            'piercing line': -6.7,
            'dark cloud cover': -6.9
        }
        
        return avg_losses.get(pattern_name.lower(), -6.5)

# Global entry/exit signal engine
entry_exit_engine = TXEntryExitEngine()