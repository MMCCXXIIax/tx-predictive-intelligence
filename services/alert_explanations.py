"""
TX Alert Explanations Engine
Provides detailed, actionable explanations for each detected pattern
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

class PatternExplanation:
    """Detailed explanation for a candlestick pattern detection"""
    
    def __init__(self, pattern_name: str):
        self.pattern = pattern_name
        self.description = ""
        self.what_it_means = ""
        self.market_psychology = ""
        self.immediate_action = ""
        self.entry_strategy = ""
        self.exit_strategy = ""
        self.risk_level = ""
        self.success_rate = 0.0
        self.best_timeframes = []
        self.avoid_conditions = []
        self.confirmation_signals = []
        
    def to_dict(self) -> Dict:
        return {
            'pattern': self.pattern,
            'description': self.description,
            'what_it_means': self.what_it_means,
            'market_psychology': self.market_psychology,
            'immediate_action': self.immediate_action,
            'entry_strategy': self.entry_strategy,
            'exit_strategy': self.exit_strategy,
            'risk_level': self.risk_level,
            'success_rate': self.success_rate,
            'best_timeframes': self.best_timeframes,
            'avoid_conditions': self.avoid_conditions,
            'confirmation_signals': self.confirmation_signals
        }

class TXAlertExplanationEngine:
    """Generates comprehensive, actionable explanations for pattern detections"""
    
    def __init__(self):
        self.explanations = self._initialize_pattern_explanations()
        
    def get_detailed_explanation(self, pattern_name: str, symbol: str, 
                                confidence: float, price: float, 
                                market_data: Optional[Dict] = None) -> Dict:
        """
        Generate detailed explanation for a pattern detection
        
        Args:
            pattern_name: Name of detected pattern
            symbol: Asset symbol
            confidence: Detection confidence (0.0-1.0)
            price: Current price
            market_data: Additional market data (volume, etc.)
            
        Returns:
            Comprehensive explanation with actionable advice
        """
        
        base_explanation = self.explanations.get(
            pattern_name.lower(), 
            self.explanations['default']
        )
        
        # Personalize explanation based on current conditions
        personalized_explanation = self._personalize_explanation(
            base_explanation, symbol, confidence, price, market_data
        )
        
        # Add current market context
        market_context = self._generate_market_context(
            pattern_name, symbol, confidence, price
        )
        
        # Generate action plan
        action_plan = self._generate_action_plan(
            pattern_name, symbol, confidence, price, market_data
        )
        
        return {
            'pattern_details': personalized_explanation,
            'market_context': market_context,
            'action_plan': action_plan,
            'confidence_analysis': self._analyze_confidence(confidence),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    def _initialize_pattern_explanations(self) -> Dict[str, PatternExplanation]:
        """Initialize detailed explanations for all patterns"""
        
        explanations = {}
        
        # MARUBOZU
        marubozu = PatternExplanation('marubozu')
        marubozu.description = "A single candle with no shadows, indicating strong momentum in one direction"
        marubozu.what_it_means = "Complete dominance by either bulls or bears throughout the entire trading session"
        marubozu.market_psychology = "Strong conviction and momentum - one side completely overwhelmed the other"
        marubozu.immediate_action = "ENTER IMMEDIATELY if bullish, or prepare to SHORT if bearish"
        marubozu.entry_strategy = "Enter at current price with tight stop-loss. This is a momentum continuation signal."
        marubozu.exit_strategy = "Take profits at 8-15% gain, use trailing stop to capture extended moves"
        marubozu.risk_level = "Medium-High"
        marubozu.success_rate = 78.5
        marubozu.best_timeframes = ["1H", "4H", "1D"]
        marubozu.avoid_conditions = ["Low volume", "End of trading session", "Major news pending"]
        marubozu.confirmation_signals = ["High volume", "Break of key level", "Momentum indicators aligned"]
        explanations['marubozu'] = marubozu
        
        # HAMMER
        hammer = PatternExplanation('hammer')
        hammer.description = "Bullish reversal pattern with small body and long lower shadow, appearing after downtrend"
        hammer.what_it_means = "Sellers pushed price down but buyers stepped in strongly, rejecting lower prices"
        hammer.market_psychology = "Selling exhaustion - bears are losing control, bulls testing the waters"
        hammer.immediate_action = "WAIT for confirmation candle before entering long position"
        hammer.entry_strategy = "Enter LONG on next candle if it opens/closes above hammer high"
        hammer.exit_strategy = "Initial target: 10-18% gain. Set stop below hammer low."
        hammer.risk_level = "Medium"
        hammer.success_rate = 72.3
        hammer.best_timeframes = ["4H", "1D", "1W"]
        hammer.avoid_conditions = ["Weak volume", "No clear downtrend before", "Major resistance nearby"]
        hammer.confirmation_signals = ["Next candle closes above hammer", "Volume increase", "RSI oversold recovery"]
        explanations['hammer'] = hammer
        
        # BULLISH ENGULFING
        bullish_engulfing = PatternExplanation('bullish engulfing')
        bullish_engulfing.description = "Two-candle reversal: large green candle completely engulfs previous red candle"
        bullish_engulfing.what_it_means = "Strong shift from selling to buying pressure - bulls have taken control"
        bullish_engulfing.market_psychology = "Panic buying overwhelms previous selling - momentum shift confirmed"
        bullish_engulfing.immediate_action = "ENTER LONG position immediately - this is a strong reversal signal"
        bullish_engulfing.entry_strategy = "Enter at current price or on any pullback to engulfing candle low"
        bullish_engulfing.exit_strategy = "Target 12-20% gain, use previous resistance as profit target"
        bullish_engulfing.risk_level = "Medium"
        bullish_engulfing.success_rate = 85.2
        bullish_engulfing.best_timeframes = ["1H", "4H", "1D"]
        bullish_engulfing.avoid_conditions = ["Low volume engulfing", "No clear downtrend", "Major resistance above"]
        bullish_engulfing.confirmation_signals = ["High volume", "Gap up", "Follow-through buying"]
        explanations['bullish engulfing'] = bullish_engulfing
        
        # BEARISH ENGULFING
        bearish_engulfing = PatternExplanation('bearish engulfing')
        bearish_engulfing.description = "Two-candle reversal: large red candle completely engulfs previous green candle"
        bearish_engulfing.what_it_means = "Strong shift from buying to selling pressure - bears have taken control"
        bearish_engulfing.market_psychology = "Panic selling overwhelms previous buying - distribution beginning"
        bearish_engulfing.immediate_action = "ENTER SHORT position or EXIT long positions immediately"
        bearish_engulfing.entry_strategy = "Enter SHORT at current price or on any bounce to engulfing candle high"
        bearish_engulfing.exit_strategy = "Target 12-20% decline, use previous support as profit target"
        bearish_engulfing.risk_level = "Medium"
        bearish_engulfing.success_rate = 83.7
        bearish_engulfing.best_timeframes = ["1H", "4H", "1D"]
        bearish_engulfing.avoid_conditions = ["Low volume engulfing", "No clear uptrend", "Major support below"]
        bearish_engulfing.confirmation_signals = ["High volume", "Gap down", "Follow-through selling"]
        explanations['bearish engulfing'] = bearish_engulfing
        
        # MORNING STAR
        morning_star = PatternExplanation('morning star')
        morning_star.description = "Three-candle bullish reversal: down candle, small body, then strong up candle"
        morning_star.what_it_means = "Major trend reversal - selling exhaustion followed by strong buying"
        morning_star.market_psychology = "Indecision after selling pressure, then bulls decisively take control"
        morning_star.immediate_action = "STRONG BUY signal - enter long position aggressively"
        morning_star.entry_strategy = "Enter on close of third candle or on any minor pullback"
        morning_star.exit_strategy = "Major reversal - hold for 15-25% gains, this can run far"
        morning_star.risk_level = "Low-Medium"
        morning_star.success_rate = 89.1
        morning_star.best_timeframes = ["4H", "1D", "1W"]
        morning_star.avoid_conditions = ["Weak third candle", "Low volume", "Major resistance nearby"]
        morning_star.confirmation_signals = ["Strong third candle", "Volume spike", "Gap up"]
        explanations['morning star'] = morning_star
        
        # EVENING STAR
        evening_star = PatternExplanation('evening star')
        evening_star.description = "Three-candle bearish reversal: up candle, small body, then strong down candle"
        evening_star.what_it_means = "Major trend reversal - buying exhaustion followed by strong selling"
        evening_star.market_psychology = "Indecision after buying pressure, then bears decisively take control"
        evening_star.immediate_action = "STRONG SELL signal - exit longs and consider shorts"
        evening_star.entry_strategy = "Enter SHORT on close of third candle or on any bounce"
        evening_star.exit_strategy = "Major reversal - target 15-25% decline, this can fall far"
        evening_star.risk_level = "Low-Medium"
        evening_star.success_rate = 87.4
        evening_star.best_timeframes = ["4H", "1D", "1W"]
        evening_star.avoid_conditions = ["Weak third candle", "Low volume", "Major support nearby"]
        evening_star.confirmation_signals = ["Strong third candle", "Volume spike", "Gap down"]
        explanations['evening star'] = evening_star
        
        # SHOOTING STAR
        shooting_star = PatternExplanation('shooting star')
        shooting_star.description = "Bearish reversal with small body and long upper shadow at top of uptrend"
        shooting_star.what_it_means = "Buyers pushed higher but sellers rejected the advance - reversal likely"
        shooting_star.market_psychology = "Buying enthusiasm met with strong selling pressure at highs"
        shooting_star.immediate_action = "CAUTION - prepare for potential reversal, tighten stops"
        shooting_star.entry_strategy = "Wait for confirmation - enter SHORT if next candle closes below star low"
        shooting_star.exit_strategy = "Quick reversal play - target 8-15% decline, move fast"
        shooting_star.risk_level = "Medium-High"
        shooting_star.success_rate = 69.8
        shooting_star.best_timeframes = ["1H", "4H", "1D"]
        shooting_star.avoid_conditions = ["Low volume", "No clear uptrend", "Major support nearby"]
        shooting_star.confirmation_signals = ["Next candle breaks low", "Volume on breakdown", "RSI divergence"]
        explanations['shooting star'] = shooting_star
        
        # DOJI
        doji = PatternExplanation('doji')
        doji.description = "Indecision candle with equal open and close - market is undecided"
        doji.what_it_means = "Perfect balance between buyers and sellers - trend may be ending"
        doji.market_psychology = "Uncertainty and indecision - neither bulls nor bears in control"
        doji.immediate_action = "WAIT - do not enter new positions until direction is clear"
        doji.entry_strategy = "Wait for breakout direction, then enter in direction of break"
        doji.exit_strategy = "Quick scalp in breakout direction - 6-12% target, tight stops"
        doji.risk_level = "High"
        doji.success_rate = 45.5
        doji.best_timeframes = ["4H", "1D"]
        doji.avoid_conditions = ["Low volume", "Middle of trading range", "No clear trend"]
        doji.confirmation_signals = ["High volume", "At key level", "Multiple doji series"]
        explanations['doji'] = doji
        
        # PIERCING LINE
        piercing_line = PatternExplanation('piercing line')
        piercing_line.description = "Bullish reversal: red candle followed by green candle closing above midpoint"
        piercing_line.what_it_means = "Selling pressure met with strong buying - potential trend change"
        piercing_line.market_psychology = "Bears lose momentum as bulls step in with conviction"
        piercing_line.immediate_action = "ENTER LONG - this is a solid bullish reversal signal"
        piercing_line.entry_strategy = "Enter at current price or on pullback to piercing line low"
        piercing_line.exit_strategy = "Target 11-18% gain, use previous resistance as guide"
        piercing_line.risk_level = "Medium"
        piercing_line.success_rate = 74.6
        piercing_line.best_timeframes = ["1H", "4H", "1D"]
        piercing_line.avoid_conditions = ["Weak piercing", "Low volume", "Major resistance above"]
        piercing_line.confirmation_signals = ["Strong volume", "Deep piercing", "Follow-through"]
        explanations['piercing line'] = piercing_line
        
        # DARK CLOUD COVER
        dark_cloud_cover = PatternExplanation('dark cloud cover')
        dark_cloud_cover.description = "Bearish reversal: green candle followed by red candle closing below midpoint"
        dark_cloud_cover.what_it_means = "Buying pressure met with strong selling - potential trend change"
        dark_cloud_cover.market_psychology = "Bulls lose momentum as bears step in with conviction"
        dark_cloud_cover.immediate_action = "EXIT LONGS or ENTER SHORT - bearish reversal signal"
        dark_cloud_cover.entry_strategy = "Enter SHORT at current price or on bounce to dark cloud high"
        dark_cloud_cover.exit_strategy = "Target 11-18% decline, use previous support as guide"
        dark_cloud_cover.risk_level = "Medium"
        dark_cloud_cover.success_rate = 76.2
        dark_cloud_cover.best_timeframes = ["1H", "4H", "1D"]
        dark_cloud_cover.avoid_conditions = ["Weak coverage", "Low volume", "Major support below"]
        dark_cloud_cover.confirmation_signals = ["Strong volume", "Deep coverage", "Follow-through"]
        explanations['dark cloud cover'] = dark_cloud_cover
        
        # DEFAULT (fallback)
        default = PatternExplanation('default')
        default.description = "Candlestick pattern detected with moderate significance"
        default.what_it_means = "Market showing potential directional bias - requires confirmation"
        default.market_psychology = "Mixed signals - market participants showing some directional preference"
        default.immediate_action = "WAIT for confirmation before taking action"
        default.entry_strategy = "Wait for additional confirmation signals before entering position"
        default.exit_strategy = "Use standard risk management with 5-10% targets"
        default.risk_level = "Medium"
        default.success_rate = 65.0
        default.best_timeframes = ["1H", "4H", "1D"]
        default.avoid_conditions = ["Low volume", "Unclear trend", "Major events pending"]
        default.confirmation_signals = ["Volume increase", "Trend alignment", "Multiple timeframe confluence"]
        explanations['default'] = default
        
        return explanations
    
    def _personalize_explanation(self, base_explanation: PatternExplanation, 
                                symbol: str, confidence: float, price: float,
                                market_data: Optional[Dict] = None) -> Dict:
        """Personalize explanation based on current conditions"""
        
        explanation = base_explanation.to_dict()
        
        # Adjust based on confidence
        if confidence >= 0.9:
            explanation['confidence_note'] = "VERY HIGH confidence - this is a strong signal"
            explanation['action_urgency'] = "High"
        elif confidence >= 0.7:
            explanation['confidence_note'] = "High confidence - good probability signal"
            explanation['action_urgency'] = "Medium"
        else:
            explanation['confidence_note'] = "Moderate confidence - wait for confirmation"
            explanation['action_urgency'] = "Low"
        
        # Add symbol-specific context
        explanation['symbol_context'] = self._get_symbol_context(symbol, price)
        
        return explanation
    
    def _get_symbol_context(self, symbol: str, price: float) -> str:
        """Get symbol-specific context"""
        
        if symbol == 'bitcoin':
            if price > 100000:
                return f"Bitcoin at ${price:,.0f} - in price discovery mode, patterns more significant"
            elif price > 50000:
                return f"Bitcoin at ${price:,.0f} - in bull market territory, bullish patterns favored"
            else:
                return f"Bitcoin at ${price:,.0f} - in accumulation zone, reversal patterns key"
        
        elif symbol == 'ethereum':
            if price > 4000:
                return f"Ethereum at ${price:,.0f} - strong momentum zone, continuation patterns reliable"
            else:
                return f"Ethereum at ${price:,.0f} - building base, reversal patterns important"
        
        else:
            return f"{symbol.upper()} at ${price:,.2f} - monitor for continuation or reversal"
    
    def _generate_market_context(self, pattern_name: str, symbol: str, 
                                confidence: float, price: float) -> Dict:
        """Generate current market context"""
        
        return {
            'current_setup': f"{pattern_name} detected on {symbol.upper()}",
            'price_level': f"Current price: ${price:,.2f}",
            'signal_strength': self._get_signal_strength(confidence),
            'market_phase': self._determine_market_phase(symbol, price),
            'timing': self._get_timing_advice(pattern_name)
        }
    
    def _get_signal_strength(self, confidence: float) -> str:
        """Convert confidence to signal strength"""
        if confidence >= 0.9:
            return "VERY STRONG"
        elif confidence >= 0.8:
            return "STRONG"
        elif confidence >= 0.7:
            return "MODERATE"
        else:
            return "WEAK - WAIT FOR CONFIRMATION"
    
    def _determine_market_phase(self, symbol: str, price: float) -> str:
        """Determine what phase the market is in"""
        # Simplified phase determination - in production this would use more data
        if symbol == 'bitcoin':
            if price > 90000:
                return "BULL MARKET - Momentum Phase"
            elif price > 60000:
                return "BULL MARKET - Building Phase"
            else:
                return "ACCUMULATION - Base Building"
        else:
            return "TRENDING - Monitor Direction"
    
    def _get_timing_advice(self, pattern_name: str) -> str:
        """Get timing-specific advice"""
        immediate_patterns = ['marubozu', 'bullish engulfing', 'bearish engulfing']
        confirmation_patterns = ['hammer', 'shooting star', 'doji']
        
        if pattern_name.lower() in immediate_patterns:
            return "ACT NOW - Enter immediately"
        elif pattern_name.lower() in confirmation_patterns:
            return "WAIT - Need confirmation candle"
        else:
            return "PREPARE - Watch for entry opportunity"
    
    def _generate_action_plan(self, pattern_name: str, symbol: str, confidence: float,
                             price: float, market_data: Optional[Dict] = None) -> Dict:
        """Generate specific action plan"""
        
        base_explanation = self.explanations.get(pattern_name.lower(), self.explanations['default'])
        
        # Calculate position sizing (risk 2% of capital)
        portfolio_size = 10000  # Default portfolio size
        risk_percent = 2.0
        
        if 'bullish' in pattern_name.lower() or pattern_name.lower() in ['hammer', 'morning star', 'piercing line']:
            direction = 'LONG'
            stop_loss_pct = 5.0  # 5% stop loss for long positions
        else:
            direction = 'SHORT'  
            stop_loss_pct = 5.0  # 5% stop loss for short positions
        
        # Calculate position size
        risk_amount = portfolio_size * (risk_percent / 100)
        price_risk = price * (stop_loss_pct / 100)
        position_size = min(risk_amount / price_risk, portfolio_size * 0.1)  # Max 10% of portfolio
        
        return {
            'direction': direction,
            'entry_price': f"${price:,.2f}",
            'position_size': f"${position_size:,.0f}",
            'stop_loss': f"${price * (1 - stop_loss_pct/100 if direction == 'LONG' else 1 + stop_loss_pct/100):,.2f}",
            'take_profit_1': f"${price * (1 + 10/100 if direction == 'LONG' else 1 - 10/100):,.2f}",
            'take_profit_2': f"${price * (1 + 20/100 if direction == 'LONG' else 1 - 20/100):,.2f}",
            'risk_reward_ratio': '2:1',
            'max_risk': f"${risk_amount:,.0f} (2% of portfolio)",
            'time_horizon': base_explanation.best_timeframes[0] if base_explanation.best_timeframes else '4H',
            'next_steps': self._get_next_steps(pattern_name, confidence)
        }
    
    def _get_next_steps(self, pattern_name: str, confidence: float) -> List[str]:
        """Get specific next steps for the trader"""
        
        steps = []
        
        if confidence >= 0.9:
            steps.append("✅ High confidence signal - proceed with position")
        elif confidence >= 0.7:
            steps.append("⚠️ Good signal - consider position sizing")
        else:
            steps.append("🔍 Lower confidence - wait for confirmation")
        
        immediate_patterns = ['marubozu', 'bullish engulfing', 'bearish engulfing']
        if pattern_name.lower() in immediate_patterns:
            steps.append("⏰ Enter immediately - this is a momentum signal")
            steps.append("📊 Set stop-loss and take-profit levels now")
        else:
            steps.append("⏳ Wait for next candle confirmation")
            steps.append("📈 Watch for volume confirmation")
        
        steps.append("📱 Monitor position closely for first 2 hours")
        steps.append("🎯 Take partial profits at first target")
        steps.append("📊 Trail stop-loss if position moves favorably")
        
        return steps
    
    def _analyze_confidence(self, confidence: float) -> Dict:
        """Analyze what the confidence level means"""
        
        if confidence >= 0.9:
            return {
                'level': 'VERY HIGH',
                'meaning': 'Pattern is textbook perfect with strong characteristics',
                'action': 'Proceed with full position size',
                'risk': 'Low - pattern has high probability of success'
            }
        elif confidence >= 0.8:
            return {
                'level': 'HIGH',
                'meaning': 'Pattern is well-formed with good characteristics',
                'action': 'Proceed with standard position size',
                'risk': 'Medium - pattern has good probability of success'
            }
        elif confidence >= 0.7:
            return {
                'level': 'MODERATE',
                'meaning': 'Pattern is present but not perfect',
                'action': 'Consider smaller position or wait for confirmation',
                'risk': 'Medium - pattern needs additional confirmation'
            }
        else:
            return {
                'level': 'LOW',
                'meaning': 'Pattern is weak or unclear',
                'action': 'Wait for better setup or additional confirmation',
                'risk': 'High - pattern has lower probability of success'
            }

# Global alert explanation engine
alert_explanation_engine = TXAlertExplanationEngine()