# 🚀 TX PREDICTIVE INTELLIGENCE - ULTIMATE FRONTEND PROMPT
## PART 2 OF 5: Complete API Reference (All 72+ Endpoints)

---

## 📡 API ENDPOINTS - COMPLETE REFERENCE

### Base URL
```typescript
const API_BASE = 'https://tx-predictive-intelligence-latest.onrender.com';
```

---

## 1️⃣ HEALTH & STATUS ENDPOINTS (4)

### GET /health
**Purpose:** Basic health check  
**Rate Limit:** Exempt  
**Use Case:** App initialization, footer status indicator

```typescript
const checkHealth = async () => {
  const res = await fetch(`${API_BASE}/health`);
  return await res.json();
};

// Response
{
  "status": "ok",
  "timestamp": "2024-10-26T20:30:00Z"
}

// UI Implementation:
// - Green dot in footer if status === "ok"
// - Red dot if request fails
// - Show timestamp on hover
```

---

### GET /health/detailed
**Purpose:** Detailed system status  
**Rate Limit:** 30/min  
**Use Case:** Admin dashboard, system monitoring

```typescript
const getDetailedHealth = async () => {
  const res = await fetch(`${API_BASE}/health/detailed`);
  return await res.json();
};

// Response
{
  "status": "healthy",
  "components": {
    "database": {
      "status": "connected",
      "latency_ms": 12,
      "pool_size": 10,
      "active_connections": 3
    },
    "deep_learning": {
      "status": "available",
      "pytorch_version": "2.8.0",
      "cuda_available": false
    },
    "ml_models": {
      "count": 15,
      "status": "loaded"
    },
    "workers": {
      "scanner": "active",
      "ml_trainer": "active"
    }
  },
  "timestamp": "2024-10-26T20:30:00Z",
  "uptime_seconds": 345600
}

// UI: System status page with component cards
```

---

### GET /api/provider-health
**Purpose:** Check external data providers  
**Rate Limit:** 20/min

```typescript
const getProviderHealth = async () => {
  const res = await fetch(`${API_BASE}/api/provider-health`);
  return await res.json();
};

// Response
{
  "success": true,
  "data": {
    "yfinance": {
      "ok": true,
      "latency_ms": 234
    },
    "finnhub": {
      "ok": true,
      "latency_ms": 156
    },
    "polygon": {
      "ok": false,
      "error": "no_api_key"
    }
  },
  "timestamp": "2024-10-26T20:30:00Z"
}

// UI: Provider status cards with latency bars
```

---

### GET /api/workers/health
**Purpose:** Background worker status  
**Rate Limit:** 30/min

```typescript
const getWorkersHealth = async () => {
  const res = await fetch(`${API_BASE}/api/workers/health`);
  return await res.json();
};

// Response
{
  "success": true,
  "data": {
    "live_scanner_active": true,
    "scanning_status": {},
    "background_workers_enabled": true
  },
  "timestamp": "2024-10-26T20:30:00Z"
}

// UI: Worker status badges
```

---

## 2️⃣ DUAL-MODE PATTERN DETECTION (REVOLUTIONARY!)

### POST /api/patterns/detect-dual-mode
**Purpose:** Detect patterns with chosen AI mode  
**Rate Limit:** 60/min  
**Use Case:** Main detection engine

```typescript
interface DetectDualModeRequest {
  symbol: string;
  timeframe: '1m' | '5m' | '15m' | '1h' | '4h' | '1d' | '1wk';
  mode: 'hybrid_pro' | 'ai_elite';
}

const detectDualMode = async (params: DetectDualModeRequest) => {
  const res = await fetch(`${API_BASE}/api/patterns/detect-dual-mode`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params)
  });
  return await res.json();
};

// Request
{
  "symbol": "AAPL",
  "timeframe": "1h",
  "mode": "hybrid_pro"
}

// Response (COMPREHENSIVE!)
{
  "success": true,
  "mode": "hybrid_pro",
  "mode_info": {
    "name": "Hybrid Pro",
    "icon": "🛡️",
    "description": "Conservative, institutional-grade",
    "accuracy_range": "75-85%"
  },
  "symbol": "AAPL",
  "timeframe": "1h",
  "current_price": 180.50,
  "patterns": [
    {
      "name": "Bullish Engulfing",
      "confidence": 0.87,
      "direction": "bullish",
      "strength": "strong",
      
      // 🔥 6-LAYER BREAKDOWN (DISPLAY THIS!)
      "layer_breakdown": {
        "deep_learning_score": 0.82,
        "rule_validation_score": 0.88,
        "sentiment_score": 0.75,        // NEW!
        "context_score": 0.90,
        "quality_factors": {
          "volume_confirmation": true,
          "trend_alignment": true,
          "candle_body_ratio": 2.3
        },
        "risk_management": {
          "risk_reward_ratio": 2.1,
          "stop_loss_distance_pct": 1.5
        }
      },
      
      // 🎯 SENTIMENT (SHOW PROMINENTLY!)
      "sentiment_analysis": {
        "overall_sentiment": 0.75,
        "overall_label": "Bullish",
        "news_sentiment": 0.81,
        "social_sentiment": 0.72,
        "market_sentiment": 0.68,
        "news_count": 12,
        "social_mentions": 245,
        "trending_topics": ["#AAPL", "#Earnings"],
        "latest_headline": "Apple reports record earnings"
      },
      
      // 💰 TRADING SIGNALS
      "entry_price": 180.50,
      "stop_loss": 177.80,
      "take_profit_1": 183.20,
      "take_profit_2": 186.20,
      "risk_reward_ratio": 2.1,
      "expected_return_pct": 3.2,
      
      // 📊 HISTORICAL PERFORMANCE
      "historical_performance": {
        "win_rate": 82.0,
        "avg_return": 2.8,
        "sample_size": 47
      },
      
      // 📈 MULTI-TIMEFRAME
      "multi_timeframe": {
        "1h": "bullish",
        "4h": "bullish",
        "1d": "bullish",
        "confluence_score": 0.92
      }
    }
  ]
}

// UI IMPLEMENTATION (CRITICAL!):
// 1. Mode Badge: "🛡️ Hybrid Pro" or "⚡ AI Elite"
// 2. Confidence Meter: Circular 87%
// 3. 6-Layer Breakdown: Expandable accordion
// 4. Sentiment Gauge: Semicircle with news/social counts
// 5. Entry/Exit Prices: With "Trade Now" button
// 6. Historical Win Rate: With sparkline
// 7. Multi-Timeframe: 3 circles (1H, 4H, 1D)
```

---

### POST /api/patterns/detect-both
**Purpose:** Compare both modes side-by-side  
**Rate Limit:** 60/min

```typescript
const detectBoth = async (symbol: string, timeframe: string) => {
  const res = await fetch(`${API_BASE}/api/patterns/detect-both`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ symbol, timeframe })
  });
  return await res.json();
};

// Response
{
  "success": true,
  "symbol": "AAPL",
  "timeframe": "1h",
  "comparison": {
    "hybrid_pro": {
      "confidence": 0.82,
      "patterns": [...]
    },
    "ai_elite": {
      "confidence": 0.87,
      "patterns": [...]
    },
    "recommendation": "AI Elite shows 5% higher confidence",
    "agreement": true
  }
}

// UI: Split-screen comparison
```

---

### GET /api/patterns/modes
**Purpose:** Get mode information  
**Rate Limit:** 30/min

```typescript
const getPatternModes = async () => {
  const res = await fetch(`${API_BASE}/api/patterns/modes`);
  return await res.json();
};

// Response
{
  "success": true,
  "modes": {
    "hybrid_pro": {
      "name": "Hybrid Pro",
      "icon": "🛡️",
      "description": "Conservative, institutional-grade",
      "accuracy_range": "75-85%",
      "layers": [
        { "name": "Deep Learning", "weight": "35%" },
        { "name": "Rule Validation", "weight": "35%" },
        { "name": "Sentiment", "weight": "15%" },
        { "name": "Context", "weight": "15%" }
      ]
    },
    "ai_elite": {
      "name": "AI Elite",
      "icon": "⚡",
      "description": "Aggressive, cutting-edge AI",
      "accuracy_range": "65-95%",
      "layers": [
        { "name": "Vision Transformer", "weight": "30%" },
        { "name": "RL", "weight": "25%" },
        { "name": "Sentiment", "weight": "20%" },
        { "name": "Context", "weight": "15%" },
        { "name": "Historical", "weight": "10%" }
      ]
    }
  }
}

// UI: Mode selector cards
```

---

## 3️⃣ SENTIMENT ANALYSIS

### GET /api/sentiment/{symbol}
**Purpose:** Real-time sentiment  
**Rate Limit:** 60/min

```typescript
const getSentiment = async (symbol: string) => {
  const res = await fetch(`${API_BASE}/api/sentiment/${symbol}`);
  return await res.json();
};

// Response
{
  "success": true,
  "symbol": "AAPL",
  "sentiment": {
    "overall_score": 0.75,
    "overall_label": "Bullish",
    "news": {
      "score": 0.81,
      "article_count": 12,
      "latest_headline": "Apple reports record earnings"
    },
    "social": {
      "score": 0.72,
      "mention_count": 245,
      "trending_topics": ["#AAPL", "#Earnings"]
    },
    "market": {
      "score": 0.68,
      "vix_level": 14.2,
      "spy_trend": "bullish"
    }
  }
}

// UI: Sentiment gauge + breakdown
```

---

## 4️⃣ ALERT MANAGEMENT

### GET /api/get_active_alerts
**Purpose:** Get all active alerts  
**Rate Limit:** 60/min

```typescript
const getActiveAlerts = async () => {
  const res = await fetch(`${API_BASE}/api/get_active_alerts`);
  return await res.json();
};

// Response
{
  "success": true,
  "alerts": [
    {
      "id": 123,
      "symbol": "AAPL",
      "pattern": "Bullish Engulfing",
      "confidence": 0.87,
      "timeframe": "1h",
      "entry_price": 180.50,
      "stop_loss": 177.80,
      "take_profit": 186.20,
      "created_at": "2024-10-26T20:30:00Z",
      "status": "active"
    }
  ],
  "count": 8
}

// UI: Dashboard alert carousel
```

---

### POST /api/alerts/dismiss/{alert_id}
**Purpose:** Dismiss alert  
**Rate Limit:** 60/min

```typescript
const dismissAlert = async (alertId: number) => {
  const res = await fetch(`${API_BASE}/api/alerts/dismiss/${alertId}`, {
    method: 'POST'
  });
  return await res.json();
};

// UI: Dismiss button on alert card
```

---

### POST /api/explain/reasoning
**Purpose:** Get AI explanation  
**Rate Limit:** 60/min

```typescript
const explainReasoning = async (symbol: string, pattern: string) => {
  const res = await fetch(`${API_BASE}/api/explain/reasoning`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ symbol, pattern })
  });
  return await res.json();
};

// Response
{
  "success": true,
  "explanation": {
    "pattern_quality": "Excellent - 2.3x body ratio",
    "multi_timeframe": "All 3 TFs aligned (92% win rate)",
    "sentiment": "Positive: News +0.81, Social +0.72",
    "historical": "82% win rate on AAPL",
    "risk_reward": "1:2.1 ratio - excellent"
  }
}

// UI: AI reasoning modal with 5 reasons
```

---

## 5️⃣ PORTFOLIO & PAPER TRADING

### GET /api/paper-trade/portfolio
**Purpose:** Portfolio summary  
**Rate Limit:** 60/min

```typescript
const getPortfolio = async () => {
  const res = await fetch(`${API_BASE}/api/paper-trade/portfolio`);
  return await res.json();
};

// Response
{
  "success": true,
  "portfolio": {
    "total_value": 12450.00,
    "cash": 2450.00,
    "positions_value": 10000.00,
    "today_pnl": 320.00,
    "today_pnl_pct": 2.6,
    "all_time_pnl": 2450.00,
    "all_time_pnl_pct": 24.5,
    "open_positions": 5,
    "win_rate": 78.0,
    "total_trades": 29
  }
}

// UI: Animated counters, donut chart
```

---

### GET /api/paper-trades
**Purpose:** All paper trades  
**Rate Limit:** 60/min

```typescript
const getPaperTrades = async () => {
  const res = await fetch(`${API_BASE}/api/paper-trades`);
  return await res.json();
};

// Response
{
  "success": true,
  "trades": [
    {
      "id": 1,
      "symbol": "AAPL",
      "side": "BUY",
      "quantity": 10,
      "entry_price": 180.50,
      "current_price": 183.20,
      "pnl": 27.00,
      "pnl_pct": 1.5,
      "status": "open"
    }
  ]
}

// UI: Position cards with live P&L
```

---

### POST /api/paper-trade/execute
**Purpose:** Execute trade  
**Rate Limit:** 60/min

```typescript
const executeTrade = async (symbol: string, side: string, quantity: number, price: number) => {
  const res = await fetch(`${API_BASE}/api/paper-trade/execute`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ symbol, side, quantity, price })
  });
  return await res.json();
};

// UI: "Trade Now" button + confetti on success
```

---

### POST /api/paper-trade/close
**Purpose:** Close position  
**Rate Limit:** 60/min

```typescript
const closePosition = async (tradeId: number) => {
  const res = await fetch(`${API_BASE}/api/paper-trade/close`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ trade_id: tradeId })
  });
  return await res.json();
};

// UI: "Close Position" button
```

---

## 6️⃣ ANALYTICS & PERFORMANCE

### GET /api/pattern-performance
**Purpose:** Pattern performance stats  
**Rate Limit:** 20/min

```typescript
const getPatternPerformance = async () => {
  const res = await fetch(`${API_BASE}/api/pattern-performance`);
  return await res.json();
};

// Response
{
  "success": true,
  "data": {
    "by_pattern": [
      {
        "pattern": "Bullish Engulfing",
        "detections": 45,
        "avg_confidence": 0.85
      }
    ]
  }
}

// UI: Pattern cards with sparklines
```

---

### GET /api/stats/trading
**Purpose:** Trading statistics  
**Rate Limit:** 60/min

```typescript
const getTradingStats = async () => {
  const res = await fetch(`${API_BASE}/api/stats/trading`);
  return await res.json();
};

// Response
{
  "success": true,
  "stats": {
    "total_trades": 29,
    "winning_trades": 23,
    "losing_trades": 6,
    "win_rate": 79.3,
    "avg_return": 2.3,
    "best_trade": 8.5,
    "worst_trade": -2.1
  }
}

// UI: Analytics dashboard
```

---

## 7️⃣ LIVE SCANNING

### POST /api/scan/start
**Purpose:** Start live scanning  
**Rate Limit:** 10/min

```typescript
const startScanning = async (symbols: string[], interval: number) => {
  const res = await fetch(`${API_BASE}/api/scan/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ symbols, interval, auto_alerts: true })
  });
  return await res.json();
};

// UI: "Start Scan" button
```

---

### POST /api/scan/stop
**Purpose:** Stop scanning  
**Rate Limit:** 10/min

```typescript
const stopScanning = async () => {
  const res = await fetch(`${API_BASE}/api/scan/stop`, {
    method: 'POST'
  });
  return await res.json();
};

// UI: "Stop" button
```

---

### GET /api/scan/status
**Purpose:** Scanner status  
**Rate Limit:** 30/min

```typescript
const getScanStatus = async () => {
  const res = await fetch(`${API_BASE}/api/scan/status`);
  return await res.json();
};

// Response
{
  "success": true,
  "status": "running",
  "config": {
    "symbols": ["AAPL", "GOOGL"],
    "interval": 180,
    "last_scan": "2024-10-26T20:30:00Z"
  }
}

// UI: Status badge
```

---

## 8️⃣ WEBSOCKET EVENTS

```typescript
import { io } from 'socket.io-client';

const socket = io(API_BASE);

// Subscribe to alerts
socket.emit('subscribe_alerts');

// New alert
socket.on('new_alert', (alert) => {
  // Show notification
  // Play sound
  // Add to list
});

// Subscribe to portfolio
socket.emit('subscribe_portfolio');

// Portfolio update
socket.on('portfolio_update', (data) => {
  // Update stats
  // Animate counters
});

// Trade executed
socket.on('trade_executed', (trade) => {
  // Show success
  // Play sound
  // Confetti
});
```

---

## ✅ PART 2 COMPLETE

Covered 30+ core endpoints. **Ready for PART 3?**

**PART 3 will cover:**
- ML & Advanced Features (15+ endpoints)
- Backtesting (5 endpoints)
- User Preferences (6 endpoints)
- Watchlists (5 endpoints)
- Journal & Risk Management (10+ endpoints)
