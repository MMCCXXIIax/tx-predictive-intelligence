"""
AI Explanation Service
Generates natural language explanations for AI trading decisions
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class AIExplainer:
    """
    Generates human-readable explanations for AI trading decisions
    """
    
    def __init__(self):
        self.logger = logger
    
    def explain_alert(
        self,
        symbol: str,
        pattern_name: str,
        composite_score: float,
        quality_badge: str,
        layers: Dict[str, Any],
        recommendation: Optional[Dict[str, Any]] = None,
        historical_accuracy: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive explanation for an alert
        
        Args:
            symbol: Stock symbol
            pattern_name: Pattern name
            composite_score: Overall confidence score
            quality_badge: ELITE/HIGH/GOOD/MODERATE
            layers: Detailed layer breakdown
            recommendation: Trading recommendation
            historical_accuracy: Historical performance data
        
        Returns:
            Dict with structured explanation
        """
        try:
            explanation = {
                'title': f'Why This Alert is {quality_badge} ({composite_score:.1f}%)',
                'symbol': symbol,
                'pattern': pattern_name,
                'timestamp': datetime.utcnow().isoformat(),
                'reasoning_steps': [],
                'recommendation': None,
                'historical_accuracy': None,
                'risk_assessment': None
            }
            
            # Step 1: Rule-Based Analysis
            rule_layer = layers.get('rule_based', {})
            if rule_layer.get('score'):
                step = {
                    'icon': '🎯',
                    'title': 'Technical Pattern Detected',
                    'status': rule_layer.get('status', 'moderate'),
                    'description': self._generate_rule_based_description(
                        pattern_name,
                        rule_layer.get('score', 0),
                        rule_layer.get('status', 'moderate')
                    ),
                    'details': rule_layer.get('details', ''),
                    'confidence': rule_layer.get('score', 0)
                }
                explanation['reasoning_steps'].append(step)
            
            # Step 2: Deep Learning Confirmation
            dl_layer = layers.get('deep_learning', {})
            if dl_layer.get('score'):
                step = {
                    'icon': '🧠',
                    'title': 'AI Confirmation',
                    'status': dl_layer.get('status', 'moderate'),
                    'description': self._generate_dl_description(
                        dl_layer.get('score', 0),
                        dl_layer.get('boost', 0),
                        dl_layer.get('status', 'moderate')
                    ),
                    'details': dl_layer.get('details', ''),
                    'confidence': dl_layer.get('score', 0),
                    'boost': dl_layer.get('boost', 0),
                    'model_version': dl_layer.get('model_version', 'v2.1')
                }
                explanation['reasoning_steps'].append(step)
            
            # Step 3: Multi-Timeframe Analysis
            mtf_layer = layers.get('multi_timeframe', {})
            if mtf_layer.get('score'):
                step = {
                    'icon': '📊',
                    'title': 'Multi-Timeframe Validation',
                    'status': mtf_layer.get('status', 'moderate'),
                    'description': self._generate_mtf_description(
                        mtf_layer.get('timeframes', {}),
                        mtf_layer.get('alignment', 0),
                        mtf_layer.get('status', 'moderate')
                    ),
                    'details': mtf_layer.get('details', ''),
                    'confidence': mtf_layer.get('score', 0),
                    'alignment': mtf_layer.get('alignment', 0),
                    'timeframes': mtf_layer.get('timeframes', {})
                }
                explanation['reasoning_steps'].append(step)
            
            # Step 4: Sentiment Analysis
            sent_layer = layers.get('sentiment', {})
            if sent_layer.get('score'):
                step = {
                    'icon': '💬',
                    'title': 'Market Sentiment',
                    'status': sent_layer.get('status', 'moderate'),
                    'description': self._generate_sentiment_description(
                        sent_layer.get('score', 0),
                        sent_layer.get('sources', {}),
                        sent_layer.get('boost', 0)
                    ),
                    'details': sent_layer.get('details', ''),
                    'confidence': sent_layer.get('score', 0),
                    'boost': sent_layer.get('boost', 0),
                    'sources': sent_layer.get('sources', {})
                }
                explanation['reasoning_steps'].append(step)
            
            # Add recommendation if provided
            if recommendation:
                explanation['recommendation'] = {
                    'action': recommendation.get('action', 'HOLD'),
                    'confidence': composite_score,
                    'entry_price': recommendation.get('entry_price'),
                    'target_price': recommendation.get('target_price'),
                    'stop_loss': recommendation.get('stop_loss'),
                    'risk_score': recommendation.get('risk_score'),
                    'risk_label': self._get_risk_label(recommendation.get('risk_score', 50)),
                    'position_size': recommendation.get('position_size'),
                    'reasoning': recommendation.get('reasoning', '')
                }
            
            # Add historical accuracy if provided
            if historical_accuracy:
                explanation['historical_accuracy'] = {
                    'accuracy': historical_accuracy.get('accuracy', 0),
                    'sample_size': historical_accuracy.get('sample_size', 0),
                    'avg_return': historical_accuracy.get('avg_return', 0),
                    'win_rate': historical_accuracy.get('win_rate', 0),
                    'description': self._generate_historical_description(historical_accuracy)
                }
            
            # Generate overall summary
            explanation['summary'] = self._generate_summary(
                pattern_name,
                quality_badge,
                composite_score,
                len(explanation['reasoning_steps'])
            )
            
            return {
                'success': True,
                'data': explanation
            }
            
        except Exception as e:
            self.logger.error(f"Error generating explanation: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_rule_based_description(
        self,
        pattern_name: str,
        score: float,
        status: str
    ) -> str:
        """Generate description for rule-based detection"""
        if status == 'strong':
            strength = 'strong'
            probability = 'high-probability'
        elif status == 'moderate':
            strength = 'moderate'
            probability = 'reasonable'
        else:
            strength = 'weak'
            probability = 'low-probability'
        
        return f'{pattern_name} pattern detected with {score:.1f}% confidence using traditional technical analysis. This is a {strength} {probability} signal based on candlestick formations and price action.'
    
    def _generate_dl_description(
        self,
        score: float,
        boost: float,
        status: str
    ) -> str:
        """Generate description for deep learning layer"""
        if status == 'strong':
            confirmation = 'strongly confirms'
            analysis = 'with very high confidence'
        elif status == 'moderate':
            confirmation = 'confirms'
            analysis = 'with moderate confidence'
        else:
            confirmation = 'weakly supports'
            analysis = 'with low confidence'
        
        boost_text = f' This adds a +{boost}% confidence boost.' if boost > 0 else ''
        
        return f'Our CNN-LSTM neural network analyzed the last 50 candles and {confirmation} this pattern {analysis} ({score:.1f}%).{boost_text} The deep learning model has learned from thousands of historical patterns.'
    
    def _generate_mtf_description(
        self,
        timeframes: Dict[str, Any],
        alignment: float,
        status: str
    ) -> str:
        """Generate description for multi-timeframe analysis"""
        tf_count = len(timeframes)
        
        if tf_count == 0:
            return 'Multi-timeframe analysis not available.'
        
        # Get timeframe scores
        tf_scores = {tf: data.get('score', 0) for tf, data in timeframes.items()}
        strong_tfs = [tf for tf, score in tf_scores.items() if score >= 75]
        
        if alignment >= 0.8:
            alignment_desc = 'very high alignment'
            consensus = 'strong consensus'
        elif alignment >= 0.6:
            alignment_desc = 'good alignment'
            consensus = 'reasonable consensus'
        else:
            alignment_desc = 'low alignment'
            consensus = 'weak consensus'
        
        tf_list = ', '.join(timeframes.keys())
        
        return f'Pattern validated across {tf_count} timeframes ({tf_list}). {len(strong_tfs)} timeframe(s) show strong confirmation (≥75%). Alignment score of {alignment:.2f} indicates {alignment_desc} and {consensus} across different time horizons.'
    
    def _generate_sentiment_description(
        self,
        score: float,
        sources: Dict[str, Any],
        boost: float
    ) -> str:
        """Generate description for sentiment analysis"""
        if score >= 75:
            sentiment_label = 'strongly bullish'
        elif score >= 60:
            sentiment_label = 'bullish'
        elif score >= 40:
            sentiment_label = 'neutral'
        elif score >= 25:
            sentiment_label = 'bearish'
        else:
            sentiment_label = 'strongly bearish'
        
        # Count sources
        news_count = sources.get('news', {}).get('count', 0)
        social_count = sources.get('social', {}).get('count', 0)
        
        boost_text = f' This adds a +{boost}% confidence boost to the overall signal.' if boost > 0 else ''
        
        return f'Market sentiment is {sentiment_label} ({score:.0f}%). Analysis of {news_count} news articles and {social_count} social media mentions supports this direction.{boost_text}'
    
    def _generate_historical_description(self, historical_data: Dict[str, Any]) -> str:
        """Generate description for historical accuracy"""
        accuracy = historical_data.get('accuracy', 0)
        sample_size = historical_data.get('sample_size', 0)
        win_rate = historical_data.get('win_rate', 0)
        avg_return = historical_data.get('avg_return', 0)
        
        return f'This pattern type has a {accuracy:.1f}% accuracy rate based on {sample_size} historical occurrences. Win rate: {win_rate:.1f}%, Average return: {avg_return:+.2f}%.'
    
    def _generate_summary(
        self,
        pattern_name: str,
        quality_badge: str,
        composite_score: float,
        validation_layers: int
    ) -> str:
        """Generate overall summary"""
        if quality_badge == 'ELITE':
            quality_desc = 'exceptional'
            recommendation = 'This is a high-confidence trading opportunity.'
        elif quality_badge == 'HIGH':
            quality_desc = 'strong'
            recommendation = 'This is a good trading opportunity with solid confirmation.'
        elif quality_badge == 'GOOD':
            quality_desc = 'moderate'
            recommendation = 'This is a reasonable trading opportunity but requires careful risk management.'
        else:
            quality_desc = 'basic'
            recommendation = 'This signal should be treated with caution and may require additional confirmation.'
        
        return f'{pattern_name} detected with {quality_desc} quality ({composite_score:.1f}% composite score). Signal validated through {validation_layers} independent AI layers. {recommendation}'
    
    def _get_risk_label(self, risk_score: float) -> str:
        """Get risk label from score"""
        if risk_score <= 25:
            return 'Low Risk'
        elif risk_score <= 50:
            return 'Medium Risk'
        elif risk_score <= 75:
            return 'High Risk'
        else:
            return 'Very High Risk'


# Global instance
ai_explainer = AIExplainer()
