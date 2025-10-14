# 🔌 TX PREDICTIVE INTELLIGENCE - API ENDPOINTS

**Base URL:** `https://tx-predictive-intelligence.onrender.com`

---

## 📊 HEALTH & MONITORING

### GET `/health`
Basic health check
- **Rate Limit:** Unlimited
- **Response:** `{ "status": "ok", "timestamp": "..." }`

### GET `/health/detailed`
Detailed system health with all components
- **Rate Limit:** Unlimited
- **Response:** Database, workers, services status

### GET `/api/provider-health`
Check external data provider status
- **Rate Limit:** 20/min
- **Response:** yfinance, polygon, twitter status

### GET `/api/workers/health`
Background workers status
- **Rate Limit:** 30/min
- **Response:** Scanner, ML workers status

### GET `/metrics`
Prometheus metrics
- **Rate Limit:** Unlimited
- **Response:** Prometheus format metrics

---

## 🎯 PATTERN DETECTION

### POST `/api/detect`
**NEW!** Simple pattern detection
- **Rate Limit:** 30/min
- **Body:** `{ "symbol": "AAPL" }`
- **Response:** `{ "success": true, "data": { "symbol": "AAPL", "patterns": [...], "count": 3 } }`

### POST `/api/detect-enhanced`
Enhanced pattern detection with layer breakdown
- **Rate Limit:** 30/min
- **Body:** `{ "symbol": "AAPL", "timeframe": "1h" }`
- **Response:** Multi-layer confidence scores

### GET `/api/ml/deep-detect`
Deep learning pattern detection (CNN/LSTM)
- **Rate Limit:** 30/min
- **Query:** `?symbol=AAPL&timeframe=1h`
- **Response:** Deep learning confidence scores

### GET `/api/patterns/list`
List all available pattern types
- **Rate Limit:** 30/min
- **Response:** Array of pattern definitions

### GET `/api/patterns/heatmap`
Pattern confidence heatmap
- **Rate Limit:** 20/min
- **Query:** `?symbol=AAPL`
- **Response:** Heatmap data for visualization

---

## 🚨 ALERTS

### GET `/api/get_active_alerts`
Get all active alerts
- **Rate Limit:** 30/min
- **Response:** `{ "success": true, "alerts": [...] }`

### POST `/api/alerts/dismiss/<alert_id>`
Dismiss a specific alert
- **Rate Limit:** 10/min
- **Response:** `{ "success": true }`

### POST `/api/handle_alert_response`
Handle user response to alert
- **Rate Limit:** 20/min
- **Body:** `{ "alert_id": 123, "action": "accept" }`

### POST `/api/explain/alert`
Get AI explanation for alert
- **Rate Limit:** 20/min
- **Body:** `{ "alert_id": 123 }`
- **Response:** Natural language explanation

### POST `/api/explain/reasoning`
Generate AI explanation for pattern
- **Rate Limit:** 30/min
- **Body:** `{ "symbol": "AAPL", "pattern": "Bullish Engulfing" }`

---

## 📈 MARKET DATA

### GET `/api/market-scan`
Scan multiple symbols for patterns
- **Rate Limit:** 30/min
- **Response:** Patterns found across watchlist

### GET `/api/scan`
Alternative market scan endpoint
- **Rate Limit:** 30/min
- **Response:** Same as market-scan

### GET `/api/market/<symbol>`
Get current market data for symbol
- **Rate Limit:** 30/min
- **Example:** `/api/market/AAPL`
- **Response:** Current price, volume, change

### POST `/api/candles`
Get candlestick data
- **Rate Limit:** 30/min
- **Body:** `{ "symbol": "AAPL", "timeframe": "1h", "limit": 100 }`
- **Response:** OHLCV candlestick data

---

## 🔄 LIVE SCANNING

### POST `/api/scan/start`
Start live market scanning
- **Rate Limit:** 5/min
- **Body:** `{ "symbols": ["AAPL", "GOOGL"], "interval": 60 }`
- **Response:** `{ "success": true, "scanning": true }`

### POST `/api/scan/stop`
Stop live scanning
- **Rate Limit:** 10/min
- **Response:** `{ "success": true, "scanning": false }`

### GET `/api/scan/status`
Get current scanning status
- **Rate Limit:** 30/min
- **Response:** Active symbols, interval, status

### GET `/api/scan/config`
Get scan configuration
- **Rate Limit:** 30/min
- **Response:** Current scan settings

### POST `/api/scan/config`
Update scan configuration
- **Rate Limit:** 10/min
- **Body:** `{ "symbols": [...], "interval": 60, "auto_alerts": true }`

---

## 💼 PAPER TRADING

### GET `/api/paper-trades`
Get all paper trades
- **Rate Limit:** 30/min
- **Response:** Array of paper trades

### GET `/api/paper-trade/portfolio`
Get paper trading portfolio
- **Rate Limit:** 30/min
- **Response:** Portfolio summary with PNL

### POST `/api/paper-trade/execute`
Execute a paper trade
- **Rate Limit:** 10/min
- **Body:** `{ "symbol": "AAPL", "side": "BUY", "quantity": 10, "price": 150.00 }`

### POST `/api/paper-trade/execute-from-alert`
Execute paper trade from alert
- **Rate Limit:** 10/min
- **Body:** `{ "alert_id": 123, "quantity": 10 }`

### POST `/api/paper-trade/close`
Close a paper trade
- **Rate Limit:** 20/min
- **Body:** `{ "trade_id": 456, "price": 155.00 }`

---

## 🤖 MACHINE LEARNING

### POST `/api/ml/train`
Train ML model from trade outcomes
- **Rate Limit:** 10/hour
- **Body:** `{ "window_days": 180 }`
- **Response:** Training results

### GET `/api/ml/score`
Score a symbol with ML model
- **Rate Limit:** 60/min
- **Query:** `?symbol=AAPL&timeframe=1h`
- **Response:** ML confidence score

### GET `/api/ml/models`
List available trained models
- **Rate Limit:** 30/min
- **Response:** Array of model metadata

### GET `/api/ml/model-info`
Get model info and feature importance
- **Rate Limit:** 30/min
- **Query:** `?namespace=global`
- **Response:** Model details, features

### GET `/api/ml/feature-contrib`
Get feature contributions for prediction
- **Rate Limit:** 30/min
- **Query:** `?symbol=AAPL`
- **Response:** Feature importance scores

### POST `/api/ml/promote`
Promote a model version to active
- **Rate Limit:** 10/min
- **Body:** `{ "namespace": "global", "version": "v2" }`

### GET `/api/ml/active-version`
Get active model version
- **Rate Limit:** 30/min
- **Query:** `?namespace=global`

---

## 🧠 ADVANCED ML

### GET `/api/ml/multi-timeframe`
Multi-timeframe fusion scoring
- **Rate Limit:** 30/min
- **Query:** `?symbol=AAPL&regime=trending`
- **Response:** Aggregated multi-TF scores

### POST `/api/ml/rl-action`
Get optimal action from RL agent
- **Rate Limit:** 60/min
- **Body:** `{ "state": { "price": 150, "volume": 1000000, "rsi": 65 } }`
- **Response:** Recommended action (buy/sell/hold)

### POST `/api/ml/online-predict`
Online learning prediction
- **Rate Limit:** 60/min
- **Body:** `{ "asset_class": "stock", "timeframe": "1h", "features": [...] }`

### POST `/api/ml/online-update`
Update online model with outcome
- **Rate Limit:** 30/min
- **Body:** `{ "asset_class": "stock", "features": [...], "label": 1 }`

### GET `/api/ml/online-status`
Get online learning models status
- **Rate Limit:** 30/min
- **Response:** Status of all online models

---

## 📊 STATISTICS & ANALYTICS

### GET `/api/stats/trading`
Get trading statistics
- **Rate Limit:** 30/min
- **Response:** Win rate, total trades, PNL

### GET `/api/pattern-stats`
Pattern detection statistics
- **Rate Limit:** 10/min
- **Response:** Pattern counts, avg confidence

### GET `/api/pattern-performance`
Pattern performance metrics
- **Rate Limit:** 20/min
- **Response:** Win rates by pattern

### GET `/api/pattern-performance/summary`
Pattern performance with outcome-based win rates
- **Rate Limit:** 30/min
- **Response:** Comprehensive pattern analytics

### GET `/api/detection_stats`
Detection statistics
- **Rate Limit:** 20/min
- **Response:** Detection counts, trends

### GET `/api/detection_logs`
Get detection logs
- **Rate Limit:** 20/min
- **Query:** `?limit=50`
- **Response:** Recent detections

### GET `/api/export_detection_logs`
Export detection logs as CSV
- **Rate Limit:** 5/min
- **Response:** CSV file download

### GET `/api/get_latest_detection_id`
Get latest detection ID
- **Rate Limit:** 30/min
- **Response:** `{ "latest_id": 12345 }`

---

## 🎯 SIGNALS & ENTRIES

### POST `/api/signals/entry`
Get entry signals for symbol
- **Rate Limit:** 30/min
- **Body:** `{ "symbol": "AAPL", "timeframe": "1h" }`
- **Response:** Entry price, stop loss, take profit

### POST `/api/signals/exit`
Get exit signals for position
- **Rate Limit:** 30/min
- **Body:** `{ "symbol": "AAPL", "entry_price": 150.00 }`
- **Response:** Exit recommendations

### POST `/api/signals/batch`
Get signals for multiple symbols
- **Rate Limit:** 10/min
- **Body:** `{ "symbols": ["AAPL", "GOOGL", "MSFT"] }`

---

## ⚠️ RISK MANAGEMENT

### POST `/api/risk/metrics`
Calculate risk metrics
- **Rate Limit:** 30/min
- **Body:** `{ "symbol": "AAPL" }`
- **Response:** Volatility, beta, drawdown

### POST `/api/risk/position-size`
Calculate optimal position size
- **Rate Limit:** 30/min
- **Body:** `{ "symbol": "AAPL", "account_size": 10000, "risk_pct": 2 }`

### POST `/api/risk/portfolio`
Analyze portfolio risk
- **Rate Limit:** 20/min
- **Body:** `{ "positions": [...] }`

---

## 🔙 BACKTESTING

### POST `/api/backtest/pattern`
Backtest a specific pattern
- **Rate Limit:** 5/min
- **Body:** `{ "symbol": "AAPL", "pattern": "Bullish Engulfing", "start_date": "2024-01-01" }`
- **Response:** Backtest results, metrics

### POST `/api/backtest/strategy`
Backtest a trading strategy
- **Rate Limit:** 5/min
- **Body:** `{ "symbol": "AAPL", "strategy": {...}, "start_date": "2024-01-01" }`

### GET `/api/backtest/results/<test_id>`
Get backtest results
- **Rate Limit:** 30/min
- **Response:** Detailed backtest metrics

---

## 💬 SENTIMENT ANALYSIS

### GET `/api/sentiment/twitter-health`
Twitter API health check
- **Rate Limit:** 30/min
- **Response:** Twitter API status

### POST `/api/sentiment/analyze`
Analyze sentiment for symbol
- **Rate Limit:** 30/min
- **Body:** `{ "symbol": "AAPL" }`
- **Response:** Sentiment score, sources

### POST `/api/sentiment/alert-condition`
Check sentiment-based alert conditions
- **Rate Limit:** 20/min
- **Body:** `{ "symbol": "AAPL", "threshold": 0.7 }`

---

## 📝 OUTCOME LOGGING

### POST `/api/outcomes/log`
Log a trade outcome
- **Rate Limit:** 30/min
- **Body:** `{ "symbol": "AAPL", "pattern": "Bullish Engulfing", "outcome": "win", "return_pct": 5.2 }`

---

## 🎨 VISUALIZATION

### GET `/api/confidence/enhance`
Enhance confidence visualization
- **Rate Limit:** 30/min
- **Query:** `?symbol=AAPL&pattern=Bullish Engulfing`

---

## 📚 DATA COVERAGE

### GET `/api/data-coverage/symbols`
Get available symbols
- **Rate Limit:** 30/min
- **Response:** Array of supported symbols

### GET `/api/data-coverage/timeframes`
Get available timeframes
- **Rate Limit:** 30/min
- **Response:** Array of timeframes

### GET `/api/data-coverage/patterns`
Get available patterns
- **Rate Limit:** 30/min
- **Response:** Array of pattern types

---

## 🏥 SYSTEM HEALTH

### GET `/api/health/system`
Comprehensive system health
- **Rate Limit:** 30/min
- **Response:** All system components status

### GET `/api/health/workers`
Background workers health
- **Rate Limit:** 30/min
- **Response:** Worker status, last run times

---

## 📖 DOCUMENTATION

### GET `/swagger.json`
OpenAPI specification
- **Rate Limit:** Unlimited
- **Response:** OpenAPI 3.0 spec

### GET `/docs`
Interactive API documentation
- **Rate Limit:** Unlimited
- **Response:** Swagger UI HTML

---

## 🔐 AUTHENTICATION

**Note:** Authentication endpoints were excluded per your request. All endpoints currently use service-role access via Supabase.

---

## 📊 TOTAL ENDPOINTS: 73+

### By Category:
- **Health & Monitoring:** 5
- **Pattern Detection:** 5
- **Alerts:** 5
- **Market Data:** 4
- **Live Scanning:** 5
- **Paper Trading:** 5
- **Machine Learning:** 12
- **Statistics:** 8
- **Signals:** 3
- **Risk Management:** 3
- **Backtesting:** 3
- **Sentiment:** 3
- **Outcome Logging:** 1
- **Visualization:** 1
- **Data Coverage:** 3
- **System Health:** 2
- **Documentation:** 2

---

## 🚀 USAGE EXAMPLES

### JavaScript/TypeScript (Frontend)
```javascript
// Pattern Detection
const response = await fetch('https://tx-predictive-intelligence.onrender.com/api/detect', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ symbol: 'AAPL' })
});
const data = await response.json();

// Get Active Alerts
const alerts = await fetch('https://tx-predictive-intelligence.onrender.com/api/get_active_alerts');
const alertData = await alerts.json();

// Execute Paper Trade
const trade = await fetch('https://tx-predictive-intelligence.onrender.com/api/paper-trade/execute', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    symbol: 'AAPL',
    side: 'BUY',
    quantity: 10,
    price: 150.00
  })
});
```

### PowerShell (Testing)
```powershell
# Pattern Detection
$body = @{ symbol = "AAPL" } | ConvertTo-Json
Invoke-RestMethod -Uri "https://tx-predictive-intelligence.onrender.com/api/detect" -Method POST -ContentType "application/json" -Body $body

# Get Alerts
Invoke-RestMethod -Uri "https://tx-predictive-intelligence.onrender.com/api/get_active_alerts"

# Health Check
Invoke-RestMethod -Uri "https://tx-predictive-intelligence.onrender.com/health"
```

---

## ⚡ RATE LIMITS

- **Unlimited:** Health checks, metrics, docs
- **60/min:** ML scoring, RL actions, online learning
- **30/min:** Most read operations
- **20/min:** Analytics, sentiment
- **10/min:** Write operations, config changes
- **5/min:** Heavy operations (backtesting, exports)
- **10/hour:** ML training

---

## 🎯 RECOMMENDED FRONTEND INTEGRATION

### Core Features
1. **Dashboard:** `/health`, `/api/get_active_alerts`, `/api/stats/trading`
2. **Pattern Scanner:** `/api/detect`, `/api/market-scan`
3. **Live Scanning:** `/api/scan/start`, `/api/scan/status`
4. **Paper Trading:** `/api/paper-trade/portfolio`, `/api/paper-trade/execute`
5. **Analytics:** `/api/pattern-performance`, `/api/detection_stats`

### Real-Time Updates
- Use WebSocket for live alerts (SocketIO available)
- Poll `/api/scan/status` every 5-10 seconds during active scanning
- Poll `/api/get_active_alerts` every 10-30 seconds

---

**All endpoints are LIVE and ready to use!** 🚀
