"""
TX Backtesting Engine - Professional Historical Strategy Testing
Tests trading strategies against historical data with comprehensive metrics
"""

import json
import pandas as pd
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional, Tuple
import statistics

class BacktestResult:
    """Holds backtesting results and performance metrics"""
    def __init__(self):
        self.trades = []
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.win_rate = 0.0
        self.total_pnl = 0.0
        self.max_drawdown = 0.0
        self.sharpe_ratio = 0.0
        self.profit_factor = 0.0
        self.avg_win = 0.0
        self.avg_loss = 0.0
        self.largest_win = 0.0
        self.largest_loss = 0.0
        self.start_date = None
        self.end_date = None
        self.duration_days = 0
        
    def calculate_metrics(self):
        """Calculate all performance metrics from trades"""
        if not self.trades:
            return
            
        self.total_trades = len(self.trades)
        winning_trades = [t for t in self.trades if t['pnl'] > 0]
        losing_trades = [t for t in self.trades if t['pnl'] < 0]
        
        self.winning_trades = len(winning_trades)
        self.losing_trades = len(losing_trades)
        self.win_rate = (self.winning_trades / self.total_trades) * 100 if self.total_trades > 0 else 0
        
        # PnL calculations
        self.total_pnl = sum(t['pnl'] for t in self.trades)
        
        if winning_trades:
            self.avg_win = statistics.mean([t['pnl'] for t in winning_trades])
            self.largest_win = max([t['pnl'] for t in winning_trades])
        
        if losing_trades:
            self.avg_loss = statistics.mean([t['pnl'] for t in losing_trades])
            self.largest_loss = min([t['pnl'] for t in losing_trades])
        
        # Profit factor
        gross_profit = sum([t['pnl'] for t in winning_trades]) if winning_trades else 0
        gross_loss = abs(sum([t['pnl'] for t in losing_trades])) if losing_trades else 0
        self.profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Calculate drawdown and Sharpe ratio
        self._calculate_drawdown()
        self._calculate_sharpe_ratio()
        
    def _calculate_drawdown(self):
        """Calculate maximum drawdown"""
        if not self.trades:
            return
            
        cumulative_pnl = []
        running_total = 0
        for trade in self.trades:
            running_total += trade['pnl']
            cumulative_pnl.append(running_total)
        
        peak = cumulative_pnl[0]
        max_drawdown = 0
        
        for pnl in cumulative_pnl:
            if pnl > peak:
                peak = pnl
            drawdown = peak - pnl
            if drawdown > max_drawdown:
                max_drawdown = drawdown
                
        self.max_drawdown = max_drawdown
    
    def _calculate_sharpe_ratio(self):
        """Calculate Sharpe ratio (simplified)"""
        if not self.trades or len(self.trades) < 2:
            self.sharpe_ratio = 0
            return
            
        returns = [t['pnl'] for t in self.trades]
        avg_return = statistics.mean(returns)
        std_return = statistics.stdev(returns)
        
        # Simplified Sharpe ratio (assuming risk-free rate of 0)
        self.sharpe_ratio = avg_return / std_return if std_return > 0 else 0
    
    def to_dict(self):
        """Convert results to dictionary"""
        return {
            'trades': self.trades,
            'metrics': {
                'total_trades': self.total_trades,
                'winning_trades': self.winning_trades,
                'losing_trades': self.losing_trades,
                'win_rate': round(self.win_rate, 2),
                'total_pnl': round(self.total_pnl, 2),
                'max_drawdown': round(self.max_drawdown, 2),
                'sharpe_ratio': round(self.sharpe_ratio, 3),
                'profit_factor': round(self.profit_factor, 2) if self.profit_factor != float('inf') else 'inf',
                'avg_win': round(self.avg_win, 2),
                'avg_loss': round(self.avg_loss, 2),
                'largest_win': round(self.largest_win, 2),
                'largest_loss': round(self.largest_loss, 2),
                'start_date': self.start_date,
                'end_date': self.end_date,
                'duration_days': self.duration_days
            }
        }

class TXBacktestEngine:
    """Professional backtesting engine for TX strategies"""
    
    def __init__(self):
        self.historical_data = {}
        
    def run_pattern_backtest(self, pattern_name: str, symbol: str, 
                           start_date: str, end_date: str,
                           entry_strategy: str = "immediate",
                           exit_strategy: str = "fixed_profit",
                           stop_loss_pct: float = 5.0,
                           take_profit_pct: float = 10.0) -> BacktestResult:
        """
        Run backtest for a specific pattern on historical data
        
        Args:
            pattern_name: Name of candlestick pattern to test
            symbol: Asset symbol (bitcoin, ethereum, etc.)
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            entry_strategy: When to enter (immediate, next_candle, pullback)
            exit_strategy: When to exit (fixed_profit, trailing_stop, pattern_reversal)
            stop_loss_pct: Stop loss percentage
            take_profit_pct: Take profit percentage
        """
        
        result = BacktestResult()
        result.start_date = start_date
        result.end_date = end_date
        
        # Calculate duration
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        result.duration_days = (end_dt - start_dt).days
        
        # Get historical data (simulated for now)
        historical_data = self._get_historical_data(symbol, start_date, end_date)
        
        # Run pattern detection on historical data
        pattern_signals = self._detect_historical_patterns(historical_data, pattern_name)
        
        # Execute trades based on signals
        for signal in pattern_signals:
            trade = self._execute_backtest_trade(
                signal, historical_data, 
                entry_strategy, exit_strategy,
                stop_loss_pct, take_profit_pct
            )
            if trade:
                result.trades.append(trade)
        
        result.calculate_metrics()
        return result
    
    def run_strategy_backtest(self, strategy_config: Dict, 
                            start_date: str, end_date: str) -> BacktestResult:
        """Run backtest for a complete trading strategy"""
        
        result = BacktestResult()
        result.start_date = start_date
        result.end_date = end_date
        
        # Strategy backtesting logic here
        # This would integrate with the strategy builder
        
        return result
    
    def _get_historical_data(self, symbol: str, start_date: str, end_date: str) -> List[Dict]:
        """
        Get historical OHLC data for backtesting
        In production, this would fetch real historical data
        """
        
        # Simulate historical data for demonstration
        import random
        data = []
        current_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        base_price = 95000 if symbol == "bitcoin" else 3500 if symbol == "ethereum" else 180
        
        while current_date <= end_date_dt:
            # Simulate realistic price movement
            change_pct = random.uniform(-5, 5)  # -5% to +5% daily change
            base_price *= (1 + change_pct / 100)
            
            # Generate OHLC
            open_price = base_price
            high_price = open_price * (1 + random.uniform(0, 3) / 100)
            low_price = open_price * (1 - random.uniform(0, 3) / 100)
            close_price = low_price + random.uniform(0, 1) * (high_price - low_price)
            
            data.append({
                'date': current_date.strftime("%Y-%m-%d"),
                'timestamp': current_date.timestamp(),
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2),
                'volume': random.randint(1000000, 5000000)
            })
            
            current_date += timedelta(days=1)
            base_price = close_price
        
        return data
    
    def _detect_historical_patterns(self, data: List[Dict], pattern_name: str) -> List[Dict]:
        """Detect patterns in historical data"""
        signals = []
        
        # Simple pattern detection simulation
        # In production, this would use the actual pattern detection engine
        
        for i in range(3, len(data)):  # Need at least 4 candles for most patterns
            candles = data[i-3:i+1]  # Last 4 candles
            
            # Simulate pattern detection
            if self._simulate_pattern_match(candles, pattern_name):
                confidence = random.uniform(0.75, 0.95)  # 75-95% confidence
                
                signals.append({
                    'date': data[i]['date'],
                    'pattern': pattern_name,
                    'confidence': confidence,
                    'price': data[i]['close'],
                    'candle_index': i
                })
        
        return signals
    
    def _simulate_pattern_match(self, candles: List[Dict], pattern_name: str) -> bool:
        """Simulate pattern matching (placeholder)"""
        # This is a simplified simulation
        # In production, this would use the actual AI pattern detection
        
        last_candle = candles[-1]
        prev_candle = candles[-2] if len(candles) > 1 else last_candle
        
        # Simple rules for common patterns
        if pattern_name.lower() == "marubozu":
            body_size = abs(last_candle['close'] - last_candle['open'])
            total_range = last_candle['high'] - last_candle['low']
            return body_size / total_range > 0.9 if total_range > 0 else False
            
        elif pattern_name.lower() == "hammer":
            body_size = abs(last_candle['close'] - last_candle['open'])
            lower_shadow = min(last_candle['open'], last_candle['close']) - last_candle['low']
            return lower_shadow > (body_size * 2)
            
        # Random chance for other patterns (simulation)
        return random.random() < 0.05  # 5% chance of pattern detection per candle
    
    def _execute_backtest_trade(self, signal: Dict, data: List[Dict], 
                               entry_strategy: str, exit_strategy: str,
                               stop_loss_pct: float, take_profit_pct: float) -> Optional[Dict]:
        """Execute a single trade in backtesting"""
        
        signal_index = signal['candle_index']
        
        # Determine entry point
        if entry_strategy == "immediate":
            entry_index = signal_index
            entry_price = signal['price']
        elif entry_strategy == "next_candle":
            entry_index = signal_index + 1
            if entry_index >= len(data):
                return None
            entry_price = data[entry_index]['open']
        else:
            entry_price = signal['price']
            entry_index = signal_index
        
        # Determine trade direction based on pattern
        is_bullish = self._is_bullish_pattern(signal['pattern'])
        
        # Calculate stop loss and take profit levels
        if is_bullish:
            stop_loss = entry_price * (1 - stop_loss_pct / 100)
            take_profit = entry_price * (1 + take_profit_pct / 100)
        else:
            stop_loss = entry_price * (1 + stop_loss_pct / 100)
            take_profit = entry_price * (1 - take_profit_pct / 100)
        
        # Find exit point
        exit_info = self._find_exit_point(
            data, entry_index + 1, stop_loss, take_profit, is_bullish
        )
        
        if not exit_info:
            return None
        
        # Calculate P&L
        if is_bullish:
            pnl_pct = ((exit_info['price'] - entry_price) / entry_price) * 100
        else:
            pnl_pct = ((entry_price - exit_info['price']) / entry_price) * 100
        
        # Simulate position size of $1000
        position_size = 1000
        pnl_dollars = (pnl_pct / 100) * position_size
        
        return {
            'entry_date': data[entry_index]['date'],
            'exit_date': exit_info['date'],
            'pattern': signal['pattern'],
            'confidence': signal['confidence'],
            'direction': 'long' if is_bullish else 'short',
            'entry_price': round(entry_price, 2),
            'exit_price': round(exit_info['price'], 2),
            'stop_loss': round(stop_loss, 2),
            'take_profit': round(take_profit, 2),
            'exit_reason': exit_info['reason'],
            'pnl_pct': round(pnl_pct, 2),
            'pnl': round(pnl_dollars, 2),
            'position_size': position_size,
            'duration_days': (datetime.strptime(exit_info['date'], "%Y-%m-%d") - 
                            datetime.strptime(data[entry_index]['date'], "%Y-%m-%d")).days
        }
    
    def _is_bullish_pattern(self, pattern_name: str) -> bool:
        """Determine if pattern is bullish or bearish"""
        bullish_patterns = [
            "hammer", "bullish engulfing", "morning star", "piercing line",
            "marubozu", "three white soldiers", "bullish harami"
        ]
        return pattern_name.lower() in bullish_patterns
    
    def _find_exit_point(self, data: List[Dict], start_index: int, 
                        stop_loss: float, take_profit: float, 
                        is_bullish: bool) -> Optional[Dict]:
        """Find where trade should exit based on conditions"""
        
        max_duration = 30  # Maximum 30 days for a trade
        
        for i in range(start_index, min(start_index + max_duration, len(data))):
            candle = data[i]
            
            if is_bullish:
                # Check for take profit (high reached target)
                if candle['high'] >= take_profit:
                    return {
                        'date': candle['date'],
                        'price': take_profit,
                        'reason': 'take_profit'
                    }
                
                # Check for stop loss (low hit stop)
                if candle['low'] <= stop_loss:
                    return {
                        'date': candle['date'],
                        'price': stop_loss,
                        'reason': 'stop_loss'
                    }
            else:
                # Check for take profit (low reached target)
                if candle['low'] <= take_profit:
                    return {
                        'date': candle['date'],
                        'price': take_profit,
                        'reason': 'take_profit'
                    }
                
                # Check for stop loss (high hit stop)
                if candle['high'] >= stop_loss:
                    return {
                        'date': candle['date'],
                        'price': stop_loss,
                        'reason': 'stop_loss'
                    }
        
        # Exit at end of max duration
        if start_index + max_duration - 1 < len(data):
            final_candle = data[start_index + max_duration - 1]
            return {
                'date': final_candle['date'],
                'price': final_candle['close'],
                'reason': 'max_duration'
            }
        
        return None

# Global backtesting engine
backtest_engine = TXBacktestEngine()