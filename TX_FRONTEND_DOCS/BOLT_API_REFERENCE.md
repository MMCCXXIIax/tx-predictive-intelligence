# 🔌 TX Backend API - Quick Reference for Bolt.new

## Base URL
```
Production: https://tx-predictive-intelligence.onrender.com
Development: http://localhost:5000
```

## Authentication
Currently: **No authentication required** (open API)

## CORS
✅ Configured to accept all origins

---

## 🎯 Core Endpoints

### 1. Pattern Detection (Dual-Mode)

**Detect pattern with chosen mode**
```http
POST /api/patterns/detect-dual-mode
Content-Type: application/json

{
  "symbol": "AAPL",
  "timeframe": "1h",
  "mode": "hybrid_pro"
}
```

**Response:**
```json
{
  "success": true,
  "mode": "hybrid_pro",
  "pattern": {
    "name": "Head and Shoulders",
    "type": "bearish",
    "confidence": 82.5,
    "breakdown": {
      "primary_detection": 85,
      "validation": 78,
      "sentiment": 72,
      "context": 80,
      "quality": 88,
      "risk": 75
    },
    "sentiment": {
      "news_sentiment": 0.6,
      "social_sentiment": 0.5,
      "market_sentiment": 0.7,
      "news_count": 24,
      "social_mentions": 1200,
      "trending_topics": ["earnings", "AI", "growth"]
    },
    "signals": {
      "entry_price": 175.50,
      "exit_price": 168.20,
      "stop_loss": 178.00,
      "take_profit": 165.00,
      "risk_reward_ratio": 3.2
    },
    "completion_probability": 78,
    "chart_data": [...]
  }
}
```

**Modes:**
- `hybrid_pro` - Conservative (75-85% accuracy)
- `ai_elite` - Aggressive (65-95% accuracy)

**Timeframes:** `1m`, `5m`, `15m`, `1h`, `4h`, `1D`

---

### 2. Live Market Scanner

**Scan multiple symbols**
```http
POST /api/patterns/scan-live
Content-Type: application/json

{
  "symbols": ["AAPL", "TSLA", "NVDA"],
  "timeframe": "1h",
  "min_confidence": 70,
  "mode": "hybrid_pro"
}
```

**Response:**
```json
{
  "success": true,
  "scan_time": "2024-01-15T10:30:00Z",
  "patterns_found": 5,
  "results": [
    {
      "symbol": "AAPL",
      "pattern": "Double Bottom",
      "confidence": 85.2,
      "type": "bullish",
      "sentiment_score": 72,
      "detected_at": "2024-01-15T10:29:45Z"
    }
  ]
}
```

---

### 3. Alerts Management

**Create alert**
```http
POST /api/alerts/create
Content-Type: application/json

{
  "symbol": "AAPL",
  "pattern": "any",
  "min_confidence": 75,
  "channels": ["email", "push"],
  "email": "user@example.com"
}
```

**Get active alerts**
```http
GET /api/alerts/active
```

**Delete alert**
```http
DELETE /api/alerts/{alert_id}
```

---

### 4. Trading Journal

**Log trade**
```http
POST /api/journal/log-trade
Content-Type: application/json

{
  "symbol": "AAPL",
  "pattern": "Head and Shoulders",
  "entry_price": 175.50,
  "exit_price": 168.20,
  "entry_time": "2024-01-15T09:00:00Z",
  "exit_time": "2024-01-15T15:00:00Z",
  "stop_loss": 178.00,
  "take_profit": 165.00,
  "position_size": 100,
  "pnl": 730.00,
  "emotion_tags": ["confident", "disciplined"],
  "notes": "Perfect setup, followed plan"
}
```

**Get journal entries**
```http
GET /api/journal/entries?start_date=2024-01-01&end_date=2024-01-31
```

**Get AI insights**
```http
GET /api/journal/insights
```

**Response:**
```json
{
  "insights": [
    {
      "type": "overtrading",
      "severity": "high",
      "description": "You've taken 12 trades in 3 hours on 2024-01-15",
      "recommendation": "Consider slowing down and waiting for high-quality setups"
    }
  ]
}
```

---

### 5. Risk Management

**Calculate position size**
```http
POST /api/risk/calculate-position-size
Content-Type: application/json

{
  "account_size": 100000,
  "risk_percentage": 2,
  "entry_price": 175.50,
  "stop_loss": 178.00,
  "method": "fixed_percentage"
}
```

**Response:**
```json
{
  "position_size": 800,
  "position_value": 140400,
  "risk_amount": 2000,
  "risk_per_share": 2.50,
  "risk_reward_ratio": 3.2
}
```

**Get portfolio heat**
```http
GET /api/risk/portfolio-heat
```

**Response:**
```json
{
  "total_heat": 4.5,
  "status": "safe",
  "positions": [
    {
      "symbol": "AAPL",
      "risk_amount": 2000,
      "risk_percentage": 2.0
    }
  ],
  "warnings": []
}
```

---

### 6. Backtesting

**Pattern backtest**
```http
POST /api/backtest/pattern
Content-Type: application/json

{
  "symbol": "AAPL",
  "pattern": "Head and Shoulders",
  "start_date": "2023-01-01",
  "end_date": "2024-01-01",
  "timeframe": "1h"
}
```

**Strategy backtest**
```http
POST /api/backtest/strategy
Content-Type: application/json

{
  "symbols": ["AAPL", "TSLA"],
  "patterns": ["Head and Shoulders", "Double Bottom"],
  "start_date": "2023-01-01",
  "end_date": "2024-01-01",
  "timeframe": "1h",
  "initial_capital": 100000
}
```

**Response:**
```json
{
  "total_trades": 45,
  "winning_trades": 32,
  "losing_trades": 13,
  "win_rate": 71.1,
  "profit_factor": 2.3,
  "total_pnl": 15420,
  "sharpe_ratio": 1.8,
  "max_drawdown": -3200,
  "equity_curve": [...]
}
```

---

### 7. Advanced Analysis

**Correlation analysis**
```http
POST /api/analysis/correlations
Content-Type: application/json

{
  "symbols": ["AAPL", "MSFT", "GOOGL"],
  "period": "90d"
}
```

**Order flow analysis**
```http
GET /api/analysis/order-flow/AAPL?timeframe=1h&period=7d
```

**Market microstructure**
```http
GET /api/analysis/microstructure/AAPL?timeframe=1h
```

**Regime detection**
```http
GET /api/analysis/regime/AAPL?period=90d
```

**Comprehensive analysis**
```http
GET /api/analysis/comprehensive/AAPL?timeframe=1h&period=30d
```

---

### 8. Dashboard Stats

**Pattern stats**
```http
GET /api/patterns/stats
```

**Recent alerts**
```http
GET /api/alerts/recent?limit=10
```

**Sentiment overview**
```http
GET /api/sentiment/overview
```

**Top patterns today**
```http
GET /api/patterns/top-today?limit=10
```

---

## 🎨 Response Format

All endpoints return JSON with this structure:

**Success:**
```json
{
  "success": true,
  "data": {...}
}
```

**Error:**
```json
{
  "success": false,
  "error": "Error message",
  "details": "Additional details"
}
```

---

## 🚦 HTTP Status Codes

- `200` - Success
- `400` - Bad request (invalid parameters)
- `404` - Not found
- `429` - Rate limit exceeded
- `500` - Server error

---

## 📊 Data Types

**Timeframes:** `1m`, `5m`, `15m`, `1h`, `4h`, `1D`

**Pattern Types:** `bullish`, `bearish`, `neutral`

**Detection Modes:** `hybrid_pro`, `ai_elite`

**Notification Channels:** `email`, `sms`, `push`, `webhook`

**Emotion Tags:** `confident`, `fearful`, `greedy`, `disciplined`, `impulsive`, `revenge_trading`, `fomo`, `patient`

---

## 🔥 Quick Integration Example (React)

```typescript
// API client setup
const API_BASE = 'https://tx-predictive-intelligence.onrender.com';

// Detect pattern
async function detectPattern(symbol: string, timeframe: string, mode: string) {
  const response = await fetch(`${API_BASE}/api/patterns/detect-dual-mode`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ symbol, timeframe, mode })
  });
  return response.json();
}

// Usage
const result = await detectPattern('AAPL', '1h', 'hybrid_pro');
console.log(result.pattern.confidence); // 82.5
```

---

## 📝 Notes

- All timestamps in ISO 8601 format (UTC)
- Prices in USD (or native currency)
- Confidence scores: 0-100
- Sentiment scores: -1 to 1 (converted to 0-100 for display)
- No rate limiting currently (but may be added)

---

## 🆘 Troubleshooting

**CORS errors?**
- Backend already configured for all origins
- Check if backend is running

**Slow responses?**
- First request may be slow (cold start on Render)
- Subsequent requests are fast

**Empty results?**
- Check symbol format (e.g., `BTC-USD` not `BTCUSD`)
- Verify timeframe is valid
- Check date ranges

---

**Full API Documentation:** See `API_ENDPOINTS_COMPLETE.md`
**Backend Status:** https://tx-predictive-intelligence.onrender.com/health
