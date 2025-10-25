# 🧪 Dual-Mode Detection API Testing Guide

## Quick Start Testing

### 1. Get Available Modes
```bash
curl http://localhost:5000/api/patterns/modes
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "hybrid_pro": {
      "mode": "hybrid_pro",
      "name": "Hybrid Pro",
      "description": "AI-Enhanced Classical Trading - Best of both worlds with rule validation",
      "accuracy_range": "75-85% (Consistent)",
      "explainability_level": 5,
      "speed": "Fast",
      "features": [...],
      "confidence_weights": {
        "deep_learning": 0.40,
        "rule_validation": 0.40,
        "context_score": 0.20
      }
    },
    "ai_elite": {
      "mode": "ai_elite",
      "name": "AI Elite",
      "description": "Pure AI Pattern Discovery - Cutting-edge machine learning with adaptive intelligence",
      "accuracy_range": "65-95% (High upside potential)",
      "explainability_level": 3,
      "speed": "Very Fast",
      "features": [...],
      "confidence_weights": {
        "vision_transformer": 0.40,
        "rl_validation": 0.30,
        "context_score": 0.20,
        "historical_performance": 0.10
      }
    }
  }
}
```

---

### 2. Detect with Hybrid Pro Mode
```bash
curl -X POST http://localhost:5000/api/patterns/detect-dual-mode \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "mode": "hybrid_pro",
    "timeframe": "1h",
    "lookback_days": 5
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "symbol": "AAPL",
    "mode": "hybrid_pro",
    "timeframe": "1h",
    "patterns": [
      {
        "symbol": "AAPL",
        "pattern_type": "Technical",
        "pattern_name": "Bullish Engulfing",
        "confidence": 0.824,
        "confidence_percentage": 82.4,
        "confidence_breakdown": {
          "final_confidence": 0.824,
          "confidence_percentage": 82.4,
          "components": {
            "deep_learning": 0.853,
            "rule_validation": 0.800,
            "context_score": 0.820
          },
          "weights": {
            "deep_learning": 0.40,
            "rule_validation": 0.40,
            "context_score": 0.20
          },
          "explanations": {
            "deep_learning": "CNN-LSTM neural network detected pattern with 85.3% confidence based on historical pattern matching across 50+ candles",
            "rule_validation": "Classical technical analysis rules validated pattern at 80.0% - pattern meets 4/5 criteria",
            "context_score": "Market context analysis scored 82.0% based on volume (1.80), momentum (0.42), and trend strength (0.28)"
          },
          "quality_factors": {
            "volume_score": 1.80,
            "momentum_score": 0.42,
            "trend_strength": 0.28,
            "sr_proximity": 0.92,
            "rules_passed": 4,
            "total_rules": 5
          },
          "detection_mode": "hybrid_pro",
          "calculation_formula": "40% × deep_learning(0.85) + 40% × rule_validation(0.80) + 20% × context_score(0.82)"
        },
        "price": 150.25,
        "volume": 45678900,
        "timestamp": "2025-10-25T14:30:15.123456",
        "detection_mode": "hybrid_pro",
        "timeframe": "1h",
        "suggested_action": "BUY",
        "entry_price": 150.25,
        "stop_loss": 146.58,
        "take_profit": 155.15,
        "risk_reward_ratio": 1.33,
        "alert": {
          "title": "🔥 Bullish Engulfing Detected - AAPL",
          "message": "...(full 5-layer breakdown)...",
          "priority": "HIGH"
        }
      }
    ],
    "count": 1,
    "timestamp": "2025-10-25T14:30:15.123456"
  }
}
```

---

### 3. Detect with AI Elite Mode
```bash
curl -X POST http://localhost:5000/api/patterns/detect-dual-mode \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "mode": "ai_elite",
    "timeframe": "1h",
    "lookback_days": 5
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "symbol": "AAPL",
    "mode": "ai_elite",
    "timeframe": "1h",
    "patterns": [
      {
        "symbol": "AAPL",
        "pattern_type": "AI_Discovered",
        "pattern_name": "DOUBLE_BOTTOM",
        "confidence": 0.887,
        "confidence_percentage": 88.7,
        "confidence_breakdown": {
          "final_confidence": 0.887,
          "confidence_percentage": 88.7,
          "components": {
            "vision_transformer": 0.882,
            "rl_validation": 0.765,
            "context_score": 0.921,
            "historical_performance": 0.783
          },
          "weights": {
            "vision_transformer": 0.40,
            "rl_validation": 0.30,
            "context_score": 0.20,
            "historical_performance": 0.10
          },
          "explanations": {
            "vision_transformer": "Vision Transformer analyzed chart image and detected pattern with 88.2% confidence using self-attention across 8 attention heads",
            "rl_validation": "Reinforcement Learning agent validated pattern at 76.5% based on 1,247 training episodes and Q-value of 0.823",
            "context_score": "Multi-modal context analysis scored 92.1% combining price action, volume profile, and market microstructure",
            "historical_performance": "Historical pattern performance: 78.3% win rate over 156 similar patterns in past 90 days"
          },
          "quality_factors": {
            "attention_heads": 8,
            "attention_score": 0.882,
            "q_value": 0.823,
            "rl_episodes": 1247,
            "historical_trades": 156,
            "lookback_days": 90,
            "novelty_score": 0.85,
            "market_regime": "TRENDING_UP_HIGH_VOL"
          },
          "detection_mode": "ai_elite",
          "calculation_formula": "40% × vision_transformer(0.88) + 30% × rl_validation(0.77) + 20% × context_score(0.92) + 10% × historical_performance(0.78)"
        },
        "price": 150.25,
        "volume": 45678900,
        "timestamp": "2025-10-25T14:30:15.123456",
        "detection_mode": "ai_elite",
        "timeframe": "1h",
        "suggested_action": "BUY",
        "entry_price": 150.25,
        "stop_loss": 146.58,
        "take_profit": 157.88,
        "risk_reward_ratio": 1.67,
        "alert": {
          "title": "🚀 DOUBLE_BOTTOM Detected - AAPL",
          "message": "...(full 5-layer breakdown)...",
          "priority": "CRITICAL"
        }
      }
    ],
    "count": 1,
    "timestamp": "2025-10-25T14:30:15.123456"
  }
}
```

---

### 4. Compare Both Modes
```bash
curl -X POST http://localhost:5000/api/patterns/detect-both \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "timeframe": "1h",
    "lookback_days": 5
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "symbol": "AAPL",
    "timeframe": "1h",
    "hybrid_pro": {
      "patterns": [...],
      "count": 3
    },
    "ai_elite": {
      "patterns": [...],
      "count": 5
    },
    "comparison": {
      "pattern_counts": {
        "hybrid_pro": 3,
        "ai_elite": 5,
        "difference": 2
      },
      "average_confidence": {
        "hybrid_pro": 0.7856,
        "ai_elite": 0.8234,
        "difference": 0.0378
      },
      "pattern_overlap": {
        "common": ["Bullish Engulfing", "Hammer"],
        "unique_to_hybrid": ["Morning Star"],
        "unique_to_ai_elite": ["DOUBLE_BOTTOM", "ASCENDING_TRIANGLE", "BULL_FLAG"],
        "overlap_percentage": 66.7
      },
      "priority_distribution": {
        "hybrid_pro": {"HIGH": 2, "MEDIUM": 1},
        "ai_elite": {"CRITICAL": 1, "HIGH": 3, "MEDIUM": 1}
      },
      "recommendation": "AI Elite finding more patterns - good for discovery"
    },
    "timestamp": "2025-10-25T14:30:15.123456"
  }
}
```

---

### 5. Get Mode Details
```bash
curl http://localhost:5000/api/patterns/mode-info/hybrid_pro
```

```bash
curl http://localhost:5000/api/patterns/mode-info/ai_elite
```

---

### 6. Set User Preference
```bash
curl -X POST http://localhost:5000/api/user/detection-mode \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "ai_elite"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "mode": "ai_elite",
    "message": "Detection mode set to ai_elite"
  },
  "timestamp": "2025-10-25T14:30:15.123456"
}
```

---

## Testing Different Symbols

### Stocks
```bash
# Apple
curl -X POST http://localhost:5000/api/patterns/detect-dual-mode \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "mode": "hybrid_pro", "timeframe": "1h"}'

# Tesla
curl -X POST http://localhost:5000/api/patterns/detect-dual-mode \
  -H "Content-Type: application/json" \
  -d '{"symbol": "TSLA", "mode": "ai_elite", "timeframe": "1h"}'

# Microsoft
curl -X POST http://localhost:5000/api/patterns/detect-dual-mode \
  -H "Content-Type: application/json" \
  -d '{"symbol": "MSFT", "mode": "hybrid_pro", "timeframe": "4h"}'
```

### Crypto
```bash
# Bitcoin
curl -X POST http://localhost:5000/api/patterns/detect-dual-mode \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTC-USD", "mode": "ai_elite", "timeframe": "1h"}'

# Ethereum
curl -X POST http://localhost:5000/api/patterns/detect-dual-mode \
  -H "Content-Type: application/json" \
  -d '{"symbol": "ETH-USD", "mode": "hybrid_pro", "timeframe": "1h"}'
```

### Forex
```bash
# EUR/USD
curl -X POST http://localhost:5000/api/patterns/detect-dual-mode \
  -H "Content-Type: application/json" \
  -d '{"symbol": "EURUSD=X", "mode": "ai_elite", "timeframe": "1h"}'
```

---

## Testing Different Timeframes

```bash
# 1-minute
curl -X POST http://localhost:5000/api/patterns/detect-dual-mode \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "mode": "hybrid_pro", "timeframe": "1m"}'

# 5-minute
curl -X POST http://localhost:5000/api/patterns/detect-dual-mode \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "mode": "ai_elite", "timeframe": "5m"}'

# 15-minute
curl -X POST http://localhost:5000/api/patterns/detect-dual-mode \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "mode": "hybrid_pro", "timeframe": "15m"}'

# 1-hour
curl -X POST http://localhost:5000/api/patterns/detect-dual-mode \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "mode": "ai_elite", "timeframe": "1h"}'

# 4-hour
curl -X POST http://localhost:5000/api/patterns/detect-dual-mode \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "mode": "hybrid_pro", "timeframe": "4h"}'

# Daily
curl -X POST http://localhost:5000/api/patterns/detect-dual-mode \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "mode": "ai_elite", "timeframe": "1d"}'
```

---

## Python Testing Script

```python
import requests
import json

BASE_URL = "http://localhost:5000"

def test_get_modes():
    """Test getting available modes"""
    response = requests.get(f"{BASE_URL}/api/patterns/modes")
    print("Available Modes:")
    print(json.dumps(response.json(), indent=2))
    return response.json()

def test_hybrid_pro(symbol="AAPL"):
    """Test Hybrid Pro detection"""
    payload = {
        "symbol": symbol,
        "mode": "hybrid_pro",
        "timeframe": "1h",
        "lookback_days": 5
    }
    response = requests.post(
        f"{BASE_URL}/api/patterns/detect-dual-mode",
        json=payload
    )
    print(f"\nHybrid Pro Detection for {symbol}:")
    print(json.dumps(response.json(), indent=2))
    return response.json()

def test_ai_elite(symbol="AAPL"):
    """Test AI Elite detection"""
    payload = {
        "symbol": symbol,
        "mode": "ai_elite",
        "timeframe": "1h",
        "lookback_days": 5
    }
    response = requests.post(
        f"{BASE_URL}/api/patterns/detect-dual-mode",
        json=payload
    )
    print(f"\nAI Elite Detection for {symbol}:")
    print(json.dumps(response.json(), indent=2))
    return response.json()

def test_both_modes(symbol="AAPL"):
    """Test both modes comparison"""
    payload = {
        "symbol": symbol,
        "timeframe": "1h",
        "lookback_days": 5
    }
    response = requests.post(
        f"{BASE_URL}/api/patterns/detect-both",
        json=payload
    )
    print(f"\nBoth Modes Comparison for {symbol}:")
    print(json.dumps(response.json(), indent=2))
    return response.json()

def test_set_mode(mode="ai_elite"):
    """Test setting user mode preference"""
    payload = {"mode": mode}
    response = requests.post(
        f"{BASE_URL}/api/user/detection-mode",
        json=payload
    )
    print(f"\nSet Mode to {mode}:")
    print(json.dumps(response.json(), indent=2))
    return response.json()

if __name__ == "__main__":
    # Run all tests
    test_get_modes()
    test_hybrid_pro("AAPL")
    test_ai_elite("AAPL")
    test_both_modes("AAPL")
    test_set_mode("ai_elite")
    
    # Test multiple symbols
    for symbol in ["TSLA", "MSFT", "BTC-USD"]:
        test_both_modes(symbol)
```

---

## Expected Behavior

### Hybrid Pro Mode
- ✅ Returns 1-5 patterns typically
- ✅ Higher confidence scores (75-85%)
- ✅ More conservative (fewer false positives)
- ✅ Classical pattern names (Hammer, Engulfing, etc.)
- ✅ Rule validation always present
- ✅ 5-layer breakdown with rules passed count

### AI Elite Mode
- ✅ Returns 2-8 patterns typically
- ✅ Variable confidence (65-95%)
- ✅ More aggressive (more discoveries)
- ✅ AI pattern names (DOUBLE_BOTTOM, ASCENDING_TRIANGLE, etc.)
- ✅ RL validation with Q-values
- ✅ 5-layer breakdown with attention scores

### Both Modes Comparison
- ✅ Shows patterns from both
- ✅ Identifies common patterns
- ✅ Shows unique patterns per mode
- ✅ Provides recommendation
- ✅ Compares average confidence

---

## Troubleshooting

### Error: "Dual-mode detection not available"
- Check that all service files are present
- Verify imports are working
- Check logs for initialization errors

### Error: "Symbol required"
- Ensure symbol is provided in request body
- Symbol must be uppercase string

### Error: "Invalid mode"
- Use "hybrid_pro" or "ai_elite" exactly
- Check spelling and case

### No patterns detected
- Try different timeframe
- Increase lookback_days
- Check if market is open
- Verify symbol is valid

---

**Ready to test the revolutionary dual-mode system!** 🚀
