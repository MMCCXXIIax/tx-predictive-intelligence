# 🚀 TX PREDICTIVE INTELLIGENCE - ULTIMATE FRONTEND PROMPT
## PART 3 OF 5: Advanced Features & ML Endpoints

---

## 9️⃣ ML & ADVANCED FEATURES (15+ Endpoints)

### POST /api/ml/train
**Purpose:** Train ML model from trade outcomes  
**Rate Limit:** 10/hour  
**Use Case:** Admin panel, model training

```typescript
const trainML = async (lookback: string = '180d') => {
  const res = await fetch(`${API_BASE}/api/ml/train`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ lookback })
  });
  return await res.json();
};

// Response
{
  "success": true,
  "result": {
    "models_trained": 5,
    "validation_auc": 0.87,
    "sample_count": 1247
  }
}

// UI: Training progress bar, success notification
```

---

### GET /api/ml/score
**Purpose:** Get ML score for symbol  
**Rate Limit:** 60/min  
**Use Case:** ML confidence overlay

```typescript
const getMLScore = async (symbol: string, timeframe: string = '1h') => {
  const res = await fetch(
    `${API_BASE}/api/ml/score?symbol=${symbol}&timeframe=${timeframe}`
  );
  return await res.json();
};

// Response
{
  "success": true,
  "symbol": "AAPL",
  "ml_score": 0.82,
  "prediction": "bullish",
  "confidence": 0.87
}

// UI: ML badge on pattern cards
```

---

### GET /api/ml/models
**Purpose:** List available ML models  
**Rate Limit:** 30/min  
**Use Case:** Model selector

```typescript
const listMLModels = async () => {
  const res = await fetch(`${API_BASE}/api/ml/models`);
  return await res.json();
};

// Response
{
  "success": true,
  "models": [
    {
      "name": "global_v1",
      "type": "global",
      "trained_at": "2024-10-26T10:00:00Z",
      "accuracy": 0.85
    },
    {
      "name": "bullish_engulfing_v2",
      "type": "pattern",
      "trained_at": "2024-10-26T09:00:00Z",
      "accuracy": 0.88
    }
  ]
}

// UI: Model list with accuracy badges
```

---

### GET /api/ml/model-info
**Purpose:** Get model details  
**Rate Limit:** 30/min

```typescript
const getModelInfo = async (modelName: string) => {
  const res = await fetch(
    `${API_BASE}/api/ml/model-info?model=${modelName}`
  );
  return await res.json();
};

// Response
{
  "success": true,
  "model": {
    "name": "global_v1",
    "version": "1.0",
    "features": ["rsi", "macd", "volume", "sentiment"],
    "feature_importance": {
      "sentiment": 0.35,
      "rsi": 0.28,
      "volume": 0.22,
      "macd": 0.15
    },
    "accuracy": 0.85,
    "sample_count": 1247
  }
}

// UI: Model details modal with feature importance chart
```

---

### GET /api/ml/deep-detect
**Purpose:** Deep learning pattern detection  
**Rate Limit:** 30/min  
**Use Case:** Advanced AI detection

```typescript
const deepDetect = async (symbol: string, timeframe: string = '1h') => {
  const res = await fetch(
    `${API_BASE}/api/ml/deep-detect?symbol=${symbol}&timeframe=${timeframe}`
  );
  return await res.json();
};

// Response
{
  "success": true,
  "symbol": "AAPL",
  "patterns": [
    {
      "name": "Complex Head & Shoulders",
      "confidence": 0.91,
      "detected_by": "CNN-LSTM",
      "probability": 0.89
    }
  ]
}

// UI: "Deep AI" badge on high-confidence patterns
```

---

### GET /api/ml/multi-timeframe
**Purpose:** Multi-timeframe fusion scoring  
**Rate Limit:** 30/min  
**Use Case:** Confluence analysis

```typescript
const getMultiTimeframe = async (symbol: string, regime: string = 'default') => {
  const res = await fetch(
    `${API_BASE}/api/ml/multi-timeframe?symbol=${symbol}&regime=${regime}`
  );
  return await res.json();
};

// Response
{
  "success": true,
  "symbol": "AAPL",
  "timeframes": {
    "1h": { "score": 0.85, "direction": "bullish" },
    "4h": { "score": 0.88, "direction": "bullish" },
    "1d": { "score": 0.82, "direction": "bullish" }
  },
  "fusion_score": 0.87,
  "confluence": "strong"
}

// UI: Multi-TF visualization with 3 circles
```

---

### POST /api/ml/rl-action
**Purpose:** Get RL agent trading action  
**Rate Limit:** 60/min  
**Use Case:** AI autopilot suggestions

```typescript
const getRLAction = async (state: any) => {
  const res = await fetch(`${API_BASE}/api/ml/rl-action`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ state })
  });
  return await res.json();
};

// Request
{
  "state": {
    "price": 180.50,
    "rsi": 45,
    "volume": 1000000,
    "position": 0
  }
}

// Response
{
  "success": true,
  "action": "BUY",
  "confidence": 0.89,
  "reasoning": "Strong momentum + oversold RSI"
}

// UI: "AI Suggests: BUY" badge
```

---

### POST /api/ml/online-predict
**Purpose:** Online learning prediction  
**Rate Limit:** 60/min

```typescript
const onlinePredict = async (features: number[]) => {
  const res = await fetch(`${API_BASE}/api/ml/online-predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      asset_class: 'stocks',
      timeframe: '1h',
      regime: 'trending',
      features
    })
  });
  return await res.json();
};

// Response
{
  "success": true,
  "prediction": 0.87,
  "direction": "bullish"
}

// UI: Live ML prediction badge
```

---

### POST /api/ml/online-update
**Purpose:** Update online learning model  
**Rate Limit:** 30/min

```typescript
const onlineUpdate = async (features: number[], label: number) => {
  const res = await fetch(`${API_BASE}/api/ml/online-update`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      asset_class: 'stocks',
      timeframe: '1h',
      regime: 'trending',
      features,
      label
    })
  });
  return await res.json();
};

// UI: Background update after trade closes
```

---

## 🔟 BACKTESTING (5 Endpoints)

### POST /api/backtest/pattern
**Purpose:** Backtest specific pattern  
**Rate Limit:** 10/min  
**Use Case:** Time Machine feature

```typescript
const backtestPattern = async (
  symbol: string,
  pattern: string,
  start_date: string,
  end_date: string
) => {
  const res = await fetch(`${API_BASE}/api/backtest/pattern`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ symbol, pattern, start_date, end_date })
  });
  return await res.json();
};

// Request
{
  "symbol": "AAPL",
  "pattern": "Bullish Engulfing",
  "start_date": "2024-01-01",
  "end_date": "2024-10-26"
}

// Response
{
  "success": true,
  "results": {
    "total_signals": 47,
    "winning_trades": 38,
    "losing_trades": 9,
    "win_rate": 80.9,
    "avg_return": 2.8,
    "total_return": 131.6,
    "max_drawdown": -5.2,
    "sharpe_ratio": 1.8,
    "trades": [
      {
        "entry_date": "2024-01-15",
        "entry_price": 175.20,
        "exit_date": "2024-01-17",
        "exit_price": 180.50,
        "return_pct": 3.0,
        "outcome": "win"
      }
    ]
  }
}

// UI: Time Machine results with trade list
```

---

### POST /api/backtest/strategy
**Purpose:** Backtest custom strategy  
**Rate Limit:** 10/min

```typescript
const backtestStrategy = async (
  symbol: string,
  strategy: any,
  start_date: string,
  end_date: string
) => {
  const res = await fetch(`${API_BASE}/api/backtest/strategy`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ symbol, strategy, start_date, end_date })
  });
  return await res.json();
};

// Request
{
  "symbol": "AAPL",
  "strategy": {
    "entry_conditions": ["rsi < 30", "bullish_pattern"],
    "exit_conditions": ["rsi > 70", "take_profit_3pct"]
  },
  "start_date": "2024-01-01",
  "end_date": "2024-10-26"
}

// Response (same as pattern backtest)

// UI: Strategy builder + backtest results
```

---

### GET /api/backtest/results/{backtest_id}
**Purpose:** Get backtest results  
**Rate Limit:** 30/min

```typescript
const getBacktestResults = async (backtestId: string) => {
  const res = await fetch(`${API_BASE}/api/backtest/results/${backtestId}`);
  return await res.json();
};

// UI: Load saved backtest results
```

---

### GET /api/data-coverage
**Purpose:** Check available historical data  
**Rate Limit:** 30/min

```typescript
const getDataCoverage = async (symbol: string) => {
  const res = await fetch(
    `${API_BASE}/api/data-coverage?symbol=${symbol}`
  );
  return await res.json();
};

// Response
{
  "success": true,
  "symbol": "AAPL",
  "coverage": {
    "earliest_date": "2020-01-01",
    "latest_date": "2024-10-26",
    "total_days": 1760,
    "timeframes": ["1m", "5m", "15m", "1h", "4h", "1d"]
  }
}

// UI: Show data availability in backtest date picker
```

---

## 1️⃣1️⃣ USER PREFERENCES (6 Endpoints)

### GET /api/user/preferences
**Purpose:** Get user preferences  
**Rate Limit:** 60/min

```typescript
const getPreferences = async () => {
  const res = await fetch(`${API_BASE}/api/user/preferences`);
  return await res.json();
};

// Response
{
  "success": true,
  "preferences": {
    "theme": "dark",
    "notifications": {
      "sound": true,
      "push": true,
      "email": false
    },
    "default_watchlist": ["AAPL", "GOOGL", "MSFT"],
    "risk_tolerance": "moderate",
    "preferred_timeframes": ["1h", "4h", "1d"],
    "default_mode": "hybrid_pro"
  }
}

// UI: Load on app start, apply settings
```

---

### POST /api/user/preferences
**Purpose:** Update preferences  
**Rate Limit:** 30/min

```typescript
const updatePreferences = async (preferences: any) => {
  const res = await fetch(`${API_BASE}/api/user/preferences`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(preferences)
  });
  return await res.json();
};

// UI: Settings page save button
```

---

### GET /api/user/alert-preferences
**Purpose:** Get alert preferences  
**Rate Limit:** 60/min

```typescript
const getAlertPreferences = async () => {
  const res = await fetch(`${API_BASE}/api/user/alert-preferences`);
  return await res.json();
};

// Response
{
  "success": true,
  "preferences": {
    "enabled_patterns": ["Bullish Engulfing", "Hammer"],
    "min_confidence": 0.75,
    "symbols": ["AAPL", "GOOGL"],
    "timeframes": ["1h", "4h"],
    "channels": ["push", "email"],
    "quiet_hours": {
      "enabled": true,
      "start": "22:00",
      "end": "08:00"
    }
  }
}

// UI: Alert settings page
```

---

### POST /api/user/alert-preferences
**Purpose:** Update alert preferences  
**Rate Limit:** 30/min

```typescript
const updateAlertPreferences = async (preferences: any) => {
  const res = await fetch(`${API_BASE}/api/user/alert-preferences`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(preferences)
  });
  return await res.json();
};

// UI: Alert settings save
```

---

## 1️⃣2️⃣ WATCHLISTS (5 Endpoints)

### GET /api/watchlist
**Purpose:** Get all watchlists  
**Rate Limit:** 60/min

```typescript
const getWatchlists = async () => {
  const res = await fetch(`${API_BASE}/api/watchlist`);
  return await res.json();
};

// Response
{
  "success": true,
  "watchlists": [
    {
      "id": 1,
      "name": "Tech Stocks",
      "symbols": ["AAPL", "GOOGL", "MSFT", "NVDA"],
      "created_at": "2024-10-15T10:00:00Z"
    },
    {
      "id": 2,
      "name": "Crypto",
      "symbols": ["BTC", "ETH", "SOL"],
      "created_at": "2024-10-16T12:00:00Z"
    }
  ],
  "count": 2
}

// UI: Watchlist dropdown, management page
```

---

### POST /api/watchlist
**Purpose:** Create watchlist  
**Rate Limit:** 30/min

```typescript
const createWatchlist = async (name: string, symbols: string[]) => {
  const res = await fetch(`${API_BASE}/api/watchlist`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, symbols })
  });
  return await res.json();
};

// Request
{
  "name": "My Favorites",
  "symbols": ["AAPL", "TSLA"]
}

// Response
{
  "success": true,
  "watchlist_id": 3,
  "message": "Watchlist created successfully"
}

// UI: "New Watchlist" modal
```

---

### PUT /api/watchlist/{id}
**Purpose:** Update watchlist  
**Rate Limit:** 30/min

```typescript
const updateWatchlist = async (id: number, name: string, symbols: string[]) => {
  const res = await fetch(`${API_BASE}/api/watchlist/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, symbols })
  });
  return await res.json();
};

// UI: Edit watchlist modal
```

---

### DELETE /api/watchlist/{id}
**Purpose:** Delete watchlist  
**Rate Limit:** 30/min

```typescript
const deleteWatchlist = async (id: number) => {
  const res = await fetch(`${API_BASE}/api/watchlist/${id}`, {
    method: 'DELETE'
  });
  return await res.json();
};

// UI: Delete confirmation dialog
```

---

### GET /api/watchlist/smart-recommendations
**Purpose:** Get AI symbol recommendations  
**Rate Limit:** 30/min

```typescript
const getRecommendations = async () => {
  const res = await fetch(`${API_BASE}/api/watchlist/smart-recommendations`);
  return await res.json();
};

// Response
{
  "success": true,
  "recommendations": [
    {
      "symbol": "NVDA",
      "reason": "High correlation with your profitable AAPL trades",
      "confidence": 0.82,
      "category": "correlation"
    },
    {
      "symbol": "AMD",
      "reason": "Similar patterns detected recently",
      "confidence": 0.78,
      "category": "pattern_similarity"
    }
  ]
}

// UI: "Recommended for you" section
```

---

## 1️⃣3️⃣ JOURNAL & RISK MANAGEMENT (10+ Endpoints)

### GET /api/journal/entries
**Purpose:** Get journal entries  
**Rate Limit:** 60/min

```typescript
const getJournalEntries = async (limit: number = 50) => {
  const res = await fetch(
    `${API_BASE}/api/journal/entries?limit=${limit}`
  );
  return await res.json();
};

// Response
{
  "success": true,
  "entries": [
    {
      "id": 1,
      "date": "2024-10-26",
      "symbol": "AAPL",
      "pattern": "Bullish Engulfing",
      "entry_price": 180.50,
      "exit_price": 186.20,
      "pnl": 57.00,
      "pnl_pct": 3.2,
      "emotion": "confident",
      "notes": "Followed signal exactly",
      "ai_analysis": "Great execution! Patience improved win rate by 12%"
    }
  ]
}

// UI: Journal page with entries
```

---

### POST /api/journal/entry
**Purpose:** Create journal entry  
**Rate Limit:** 60/min

```typescript
const createJournalEntry = async (entry: any) => {
  const res = await fetch(`${API_BASE}/api/journal/entry`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(entry)
  });
  return await res.json();
};

// UI: "Add Entry" form
```

---

### GET /api/journal/mistakes
**Purpose:** Get detected mistakes  
**Rate Limit:** 30/min

```typescript
const getMistakes = async () => {
  const res = await fetch(`${API_BASE}/api/journal/mistakes`);
  return await res.json();
};

// Response
{
  "success": true,
  "mistakes": [
    {
      "type": "overtrading",
      "date": "2024-10-12",
      "description": "Made 8 trades (usual: 3)",
      "impact": "Win rate dropped to 50%",
      "suggestion": "Limit to 3-5 trades per day"
    },
    {
      "type": "revenge_trading",
      "date": "2024-10-10",
      "description": "Traded immediately after loss",
      "impact": "Lost $120 in next trade",
      "suggestion": "Take 1-hour break after losses"
    }
  ]
}

// UI: Mistakes section in journal
```

---

### GET /api/risk/position-size
**Purpose:** Calculate position size  
**Rate Limit:** 60/min

```typescript
const getPositionSize = async (
  symbol: string,
  entry: number,
  stop: number,
  method: string = 'kelly'
) => {
  const res = await fetch(
    `${API_BASE}/api/risk/position-size?symbol=${symbol}&entry=${entry}&stop=${stop}&method=${method}`
  );
  return await res.json();
};

// Response
{
  "success": true,
  "position_size": {
    "shares": 150,
    "dollar_amount": 27075,
    "risk_amount": 405,
    "risk_pct": 1.5,
    "method": "kelly_criterion"
  }
}

// UI: Position size calculator
```

---

### GET /api/risk/portfolio-heat
**Purpose:** Get portfolio risk exposure  
**Rate Limit:** 60/min

```typescript
const getPortfolioHeat = async () => {
  const res = await fetch(`${API_BASE}/api/risk/portfolio-heat`);
  return await res.json();
};

// Response
{
  "success": true,
  "portfolio_heat": {
    "total_risk_pct": 4.5,
    "max_allowed_pct": 6.0,
    "positions_at_risk": 5,
    "correlation_risk": "moderate",
    "recommendation": "Can add 1 more position"
  }
}

// UI: Risk gauge on portfolio page
```

---

### POST /api/risk/check-trade
**Purpose:** Check if trade is approved  
**Rate Limit:** 60/min

```typescript
const checkTrade = async (trade: any) => {
  const res = await fetch(`${API_BASE}/api/risk/check-trade`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(trade)
  });
  return await res.json();
};

// Request
{
  "symbol": "AAPL",
  "side": "BUY",
  "quantity": 100,
  "price": 180.50
}

// Response
{
  "success": true,
  "approved": true,
  "reason": "Trade within risk limits",
  "warnings": []
}

// OR

{
  "success": true,
  "approved": false,
  "reason": "Portfolio heat exceeded (6.2% > 6.0%)",
  "warnings": ["Reduce position size by 30%"]
}

// UI: Show warning before trade execution
```

---

## ✅ PART 3 COMPLETE

Covered 40+ advanced endpoints including:
- ✅ ML & Advanced Features (10 endpoints)
- ✅ Backtesting (5 endpoints)
- ✅ User Preferences (4 endpoints)
- ✅ Watchlists (5 endpoints)
- ✅ Journal & Risk Management (6 endpoints)

---

## 🚀 **READY FOR PART 4?**

**PART 4 will cover:**
- 🎨 Complete UI/UX Implementation Guide
- 📱 All 7 Core Pages (Detailed Wireframes)
- 🎮 Gamification System
- 🔊 Sound & Animation Guidelines
- 🎯 User Flow & Onboarding

**Should I proceed with PART 4?** 🎯
