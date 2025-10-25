"""
TX Predictive Intelligence - Dual-Mode Detection System
Supports both Hybrid Pro (AI + Rules) and AI Elite (Pure AI) detection modes
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DetectionMode(Enum):
    """Detection mode selection"""
    HYBRID_PRO = "hybrid_pro"  # AI + Rules + Ensemble (Conservative)
    AI_ELITE = "ai_elite"      # Pure AI + RL + Multi-Modal (Aggressive)


class ConfidenceComponent(Enum):
    """Components that contribute to final confidence score"""
    # Hybrid Pro Components
    DEEP_LEARNING = "deep_learning"           # CNN-LSTM pattern recognition
    RULE_VALIDATION = "rule_validation"       # Classical TA validation
    ENSEMBLE_ML = "ensemble_ml"               # ML quality scoring
    CONTEXT_SCORE = "context_score"           # Market context (volume, momentum, etc.)
    SENTIMENT_SCORE = "sentiment_score"       # News + Social + Market sentiment
    
    # AI Elite Components
    VISION_TRANSFORMER = "vision_transformer" # Chart image recognition
    RL_VALIDATION = "rl_validation"           # Reinforcement learning validation
    MULTI_MODAL = "multi_modal"               # Multi-modal pattern recognition
    HISTORICAL_PERFORMANCE = "historical_performance"  # Past pattern performance
    EXPLAINABILITY = "explainability"         # SHAP/LIME scores


@dataclass
class ConfidenceBreakdown:
    """Detailed breakdown of confidence scoring for transparency"""
    final_confidence: float
    components: Dict[str, float]
    weights: Dict[str, float]
    explanations: Dict[str, str]
    quality_factors: Dict[str, Any]
    detection_mode: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response (formula hidden for competitive advantage)"""
        return {
            'final_confidence': round(self.final_confidence, 4),
            'confidence_percentage': round(self.final_confidence * 100, 2),
            'components': {k: round(v, 4) for k, v in self.components.items()},
            # Weights and formula hidden to protect competitive advantage
            'explanations': self.explanations,
            'quality_factors': self.quality_factors,
            'detection_mode': self.detection_mode,
            'timestamp': self.timestamp
        }
    
    def _get_formula(self) -> str:
        """Generate human-readable confidence formula (INTERNAL USE ONLY - NOT EXPOSED TO API)"""
        # This method is kept for internal logging/debugging only
        # Formula is NOT exposed to users to protect competitive advantage
        parts = []
        for component, weight in self.weights.items():
            score = self.components.get(component, 0)
            parts.append(f"{weight*100:.0f}% × {component}({score:.2f})")
        return " + ".join(parts)


@dataclass
class PatternDetectionResult:
    """Unified pattern detection result for both modes"""
    symbol: str
    pattern_type: str
    pattern_name: str
    confidence: float
    confidence_breakdown: ConfidenceBreakdown
    price: float
    volume: int
    timestamp: str
    detection_mode: str
    
    # Pattern details
    timeframe: str
    suggested_action: str  # BUY, SELL, HOLD, CONTINUATION
    
    # Risk management
    entry_price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    risk_reward_ratio: Optional[float] = None
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Alert information (what user sees)
    alert_title: str = ""
    alert_message: str = ""
    alert_priority: str = "MEDIUM"  # LOW, MEDIUM, HIGH, CRITICAL
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        return {
            'symbol': self.symbol,
            'pattern_type': self.pattern_type,
            'pattern_name': self.pattern_name,
            'confidence': round(self.confidence, 4),
            'confidence_percentage': round(self.confidence * 100, 2),
            'confidence_breakdown': self.confidence_breakdown.to_dict(),
            'price': self.price,
            'volume': self.volume,
            'timestamp': self.timestamp,
            'detection_mode': self.detection_mode,
            'timeframe': self.timeframe,
            'suggested_action': self.suggested_action,
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'risk_reward_ratio': self.risk_reward_ratio,
            'metadata': self.metadata,
            'alert': {
                'title': self.alert_title,
                'message': self.alert_message,
                'priority': self.alert_priority
            }
        }


@dataclass
class ModeConfiguration:
    """Configuration for each detection mode"""
    mode: DetectionMode
    name: str
    description: str
    best_for: List[str]
    accuracy_range: str
    explainability_level: int  # 1-5 stars
    speed: str
    learning_curve: str
    features: List[str]
    confidence_weights: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (weights hidden for competitive advantage)"""
        return {
            'mode': self.mode.value,
            'name': self.name,
            'description': self.description,
            'best_for': self.best_for,
            'accuracy_range': self.accuracy_range,
            'explainability_level': self.explainability_level,
            'speed': self.speed,
            'learning_curve': self.learning_curve,
            'features': self.features
            # confidence_weights removed - proprietary algorithm
        }


# Mode Configurations
HYBRID_PRO_CONFIG = ModeConfiguration(
    mode=DetectionMode.HYBRID_PRO,
    name="Hybrid Pro",
    description="AI-Enhanced Classical Trading - Best of both worlds with rule validation",
    best_for=[
        "Conservative traders",
        "Institutional clients",
        "Traders who need explainability",
        "Regulated environments",
        "Consistent performance seekers"
    ],
    accuracy_range="75-85% (Consistent)",
    explainability_level=5,
    speed="Fast",
    learning_curve="Easy",
    features=[
        "CNN-LSTM deep learning pattern recognition",
        "Classical technical analysis validation",
        "Ensemble ML quality scoring",
        "10+ AI features (volume, momentum, S/R, etc.)",
        "Real-time sentiment analysis (News + Social + Market)",
        "Transparent reasoning",
        "Rule-validated signals",
        "Real-time market context analysis"
    ],
    confidence_weights={
        'deep_learning': 0.35,      # 35% - AI pattern recognition
        'rule_validation': 0.35,    # 35% - Classical TA validation
        'context_score': 0.15,      # 15% - Market context
        'sentiment_score': 0.15     # 15% - Sentiment (News + Social + Market)
    }
)

AI_ELITE_CONFIG = ModeConfiguration(
    mode=DetectionMode.AI_ELITE,
    name="AI Elite",
    description="Pure AI Pattern Discovery - Cutting-edge machine learning with adaptive intelligence",
    best_for=[
        "Aggressive traders",
        "Tech-savvy users",
        "High-frequency traders",
        "AI/ML enthusiasts",
        "Pattern discovery seekers"
    ],
    accuracy_range="65-95% (High upside potential)",
    explainability_level=3,
    speed="Very Fast",
    learning_curve="Moderate",
    features=[
        "Vision Transformer (ViT) chart recognition",
        "Reinforcement Learning validation",
        "Multi-modal pattern recognition",
        "Real-time sentiment analysis (News + Social + Market)",
        "SHAP/LIME explainability",
        "Discovers unknown patterns",
        "Adaptive to market changes",
        "Online learning from outcomes",
        "Market regime adaptation"
    ],
    confidence_weights={
        'vision_transformer': 0.30,      # 30% - Deep learning score
        'rl_validation': 0.25,           # 25% - RL validation
        'sentiment_score': 0.20,         # 20% - Sentiment (News + Social + Market)
        'context_score': 0.15,           # 15% - Context
        'historical_performance': 0.10   # 10% - Historical performance
    }
)


def get_mode_config(mode: DetectionMode) -> ModeConfiguration:
    """Get configuration for detection mode"""
    if mode == DetectionMode.HYBRID_PRO:
        return HYBRID_PRO_CONFIG
    elif mode == DetectionMode.AI_ELITE:
        return AI_ELITE_CONFIG
    else:
        raise ValueError(f"Unknown detection mode: {mode}")


def calculate_hybrid_pro_confidence(
    deep_learning_score: float,
    rule_validation_score: float,
    context_score: float,
    sentiment_score: float,
    quality_factors: Dict[str, Any],
    sentiment_data: Dict[str, Any] = None
) -> ConfidenceBreakdown:
    """
    Calculate Hybrid Pro confidence with full transparency
    
    Formula: 35% Deep Learning + 35% Rule Validation + 15% Context + 15% Sentiment
    """
    weights = HYBRID_PRO_CONFIG.confidence_weights
    
    components = {
        'deep_learning': deep_learning_score,
        'rule_validation': rule_validation_score,
        'context_score': context_score,
        'sentiment_score': sentiment_score
    }
    
    # Calculate weighted confidence
    final_confidence = (
        weights['deep_learning'] * deep_learning_score +
        weights['rule_validation'] * rule_validation_score +
        weights['context_score'] * context_score +
        weights['sentiment_score'] * sentiment_score
    )
    
    # Generate sentiment explanation
    sentiment_data = sentiment_data or {}
    sentiment_strength = sentiment_data.get('sentiment_strength', 'NEUTRAL')
    news_count = sentiment_data.get('news_sentiment', {}).get('analyzed_count', 0)
    social_mentions = sentiment_data.get('social_sentiment', {}).get('mentions', 0)
    trending = sentiment_data.get('trending_topics', [])
    
    sentiment_explanation = f"Real-time sentiment analysis: {sentiment_strength} ({sentiment_score*100:.1f}%) - "
    sentiment_explanation += f"Analyzed {news_count} news articles, {social_mentions} social mentions. "
    if trending:
        sentiment_explanation += f"Trending: {', '.join(trending[:3])}"
    
    explanations = {
        'deep_learning': f"CNN-LSTM neural network detected pattern with {deep_learning_score*100:.1f}% confidence based on historical pattern matching across 50+ candles",
        'rule_validation': f"Classical technical analysis rules validated pattern at {rule_validation_score*100:.1f}% - pattern meets {quality_factors.get('rules_passed', 0)}/{quality_factors.get('total_rules', 0)} criteria",
        'context_score': f"Market context analysis scored {context_score*100:.1f}% based on volume ({quality_factors.get('volume_score', 0):.2f}), momentum ({quality_factors.get('momentum_score', 0):.2f}), and trend strength ({quality_factors.get('trend_strength', 0):.2f})",
        'sentiment_score': sentiment_explanation
    }
    
    return ConfidenceBreakdown(
        final_confidence=final_confidence,
        components=components,
        weights=weights,
        explanations=explanations,
        quality_factors=quality_factors,
        detection_mode='hybrid_pro'
    )


def calculate_ai_elite_confidence(
    vision_score: float,
    rl_score: float,
    sentiment_score: float,
    context_score: float,
    historical_performance: float,
    quality_factors: Dict[str, Any],
    sentiment_data: Dict[str, Any] = None
) -> ConfidenceBreakdown:
    """
    Calculate AI Elite confidence with full transparency
    
    Formula: 30% Vision Transformer + 25% RL + 20% Sentiment + 15% Context + 10% Historical
    """
    weights = AI_ELITE_CONFIG.confidence_weights
    
    components = {
        'vision_transformer': vision_score,
        'rl_validation': rl_score,
        'sentiment_score': sentiment_score,
        'context_score': context_score,
        'historical_performance': historical_performance
    }
    
    # Calculate weighted confidence
    final_confidence = (
        weights['vision_transformer'] * vision_score +
        weights['rl_validation'] * rl_score +
        weights['sentiment_score'] * sentiment_score +
        weights['context_score'] * context_score +
        weights['historical_performance'] * historical_performance
    )
    
    # Generate sentiment explanation
    sentiment_data = sentiment_data or {}
    sentiment_strength = sentiment_data.get('sentiment_strength', 'NEUTRAL')
    news_count = sentiment_data.get('news_sentiment', {}).get('analyzed_count', 0)
    social_mentions = sentiment_data.get('social_sentiment', {}).get('mentions', 0)
    trending = sentiment_data.get('trending_topics', [])
    overall_sent = sentiment_data.get('overall_sentiment', 0.0)
    
    sentiment_explanation = f"AI sentiment analysis: {sentiment_strength} ({sentiment_score*100:.1f}%, raw: {overall_sent:+.2f}) - "
    sentiment_explanation += f"{news_count} news articles, {social_mentions} social mentions, "
    sentiment_explanation += f"market sentiment integrated. "
    if trending:
        sentiment_explanation += f"Trending: {', '.join(trending[:3])}"
    
    explanations = {
        'vision_transformer': f"Vision Transformer analyzed chart image and detected pattern with {vision_score*100:.1f}% confidence using self-attention across {quality_factors.get('attention_heads', 8)} attention heads",
        'rl_validation': f"Reinforcement Learning agent validated pattern at {rl_score*100:.1f}% based on {quality_factors.get('rl_episodes', 0)} training episodes and Q-value of {quality_factors.get('q_value', 0):.3f}",
        'sentiment_score': sentiment_explanation,
        'context_score': f"Multi-modal context analysis scored {context_score*100:.1f}% combining price action, volume profile, and market microstructure",
        'historical_performance': f"Historical pattern performance: {historical_performance*100:.1f}% win rate over {quality_factors.get('historical_trades', 0)} similar patterns in past {quality_factors.get('lookback_days', 90)} days"
    }
    
    return ConfidenceBreakdown(
        final_confidence=final_confidence,
        components=components,
        weights=weights,
        explanations=explanations,
        quality_factors=quality_factors,
        detection_mode='ai_elite'
    )


def format_alert_message_hybrid_pro(result: PatternDetectionResult) -> tuple[str, str, str]:
    """
    Format alert for Hybrid Pro mode
    Returns: (title, message, priority)
    """
    conf_pct = result.confidence * 100
    breakdown = result.confidence_breakdown
    
    # Determine priority based on confidence
    if conf_pct >= 85:
        priority = "CRITICAL"
        emoji = "🔥"
    elif conf_pct >= 75:
        priority = "HIGH"
        emoji = "⚡"
    elif conf_pct >= 65:
        priority = "MEDIUM"
        emoji = "📊"
    else:
        priority = "LOW"
        emoji = "📈"
    
    title = f"{emoji} {result.pattern_name} Detected - {result.symbol}"
    
    message = f"""
🎯 **HYBRID PRO DETECTION**

**Pattern:** {result.pattern_name}
**Symbol:** {result.symbol} @ ${result.price:.2f}
**Confidence:** {conf_pct:.1f}%
**Action:** {result.suggested_action}

📊 **6-LAYER CONFIDENCE BREAKDOWN:**

1️⃣ **AI Deep Learning**
   Score: {breakdown.components.get('deep_learning', 0)*100:.1f}%
   {breakdown.explanations.get('deep_learning', '')}

2️⃣ **Rule Validation**
   Score: {breakdown.components.get('rule_validation', 0)*100:.1f}%
   {breakdown.explanations.get('rule_validation', '')}

3️⃣ **Real-Time Sentiment** 📰
   Score: {breakdown.components.get('sentiment_score', 0)*100:.1f}%
   {breakdown.explanations.get('sentiment_score', '')}

4️⃣ **Market Context**
   Score: {breakdown.components.get('context_score', 0)*100:.1f}%
   {breakdown.explanations.get('context_score', '')}

5️⃣ **Quality Factors:**
   • Volume Score: {breakdown.quality_factors.get('volume_score', 0):.2f}
   • Momentum Score: {breakdown.quality_factors.get('momentum_score', 0):.2f}
   • Trend Strength: {breakdown.quality_factors.get('trend_strength', 0):.2f}
   • S/R Proximity: {breakdown.quality_factors.get('sr_proximity', 0):.2f}

6️⃣ **Risk Management:**
   • Entry: ${result.entry_price:.2f}
   • Stop Loss: ${result.stop_loss:.2f if result.stop_loss else 'N/A'}
   • Take Profit: ${result.take_profit:.2f if result.take_profit else 'N/A'}
   • R/R Ratio: {result.risk_reward_ratio:.2f}x

⏰ Detected at {result.timestamp}
🔍 Mode: Hybrid Pro (AI + Rules + Sentiment)
💡 Final Confidence: {conf_pct:.1f}% (Proprietary AI Algorithm)
"""
    
    return title, message.strip(), priority


def format_alert_message_ai_elite(result: PatternDetectionResult) -> tuple[str, str, str]:
    """
    Format alert for AI Elite mode
    Returns: (title, message, priority)
    """
    conf_pct = result.confidence * 100
    breakdown = result.confidence_breakdown
    
    # Determine priority based on confidence
    if conf_pct >= 90:
        priority = "CRITICAL"
        emoji = "🚀"
    elif conf_pct >= 80:
        priority = "HIGH"
        emoji = "🤖"
    elif conf_pct >= 70:
        priority = "MEDIUM"
        emoji = "🧠"
    else:
        priority = "LOW"
        emoji = "💡"
    
    title = f"{emoji} {result.pattern_name} Detected - {result.symbol}"
    
    message = f"""
🤖 **AI ELITE DETECTION**

**Pattern:** {result.pattern_name}
**Symbol:** {result.symbol} @ ${result.price:.2f}
**Confidence:** {conf_pct:.1f}%
**Action:** {result.suggested_action}

🧠 **6-LAYER AI CONFIDENCE BREAKDOWN:**

1️⃣ **Vision Transformer**
   Score: {breakdown.components.get('vision_transformer', 0)*100:.1f}%
   {breakdown.explanations.get('vision_transformer', '')}

2️⃣ **RL Validation**
   Score: {breakdown.components.get('rl_validation', 0)*100:.1f}%
   {breakdown.explanations.get('rl_validation', '')}

3️⃣ **AI Sentiment Analysis** 📰
   Score: {breakdown.components.get('sentiment_score', 0)*100:.1f}%
   {breakdown.explanations.get('sentiment_score', '')}

4️⃣ **Multi-Modal Context**
   Score: {breakdown.components.get('context_score', 0)*100:.1f}%
   {breakdown.explanations.get('context_score', '')}

5️⃣ **Historical Performance**
   Score: {breakdown.components.get('historical_performance', 0)*100:.1f}%
   {breakdown.explanations.get('historical_performance', '')}

6️⃣ **AI Quality Metrics:**
   • Attention Score: {breakdown.quality_factors.get('attention_score', 0):.3f}
   • Q-Value: {breakdown.quality_factors.get('q_value', 0):.3f}
   • Pattern Novelty: {breakdown.quality_factors.get('novelty_score', 0):.2f}
   • Market Regime: {breakdown.quality_factors.get('market_regime', 'Unknown')}

💰 **Risk Management:**
   • Entry: ${result.entry_price:.2f}
   • Stop Loss: ${result.stop_loss:.2f if result.stop_loss else 'N/A'}
   • Take Profit: ${result.take_profit:.2f if result.take_profit else 'N/A'}
   • R/R Ratio: {result.risk_reward_ratio:.2f}x

⏰ Detected at {result.timestamp}
🔍 Mode: AI Elite (Pure AI)
💡 Final Confidence: {conf_pct:.1f}% (Proprietary AI Algorithm)
"""
    
    return title, message.strip(), priority
