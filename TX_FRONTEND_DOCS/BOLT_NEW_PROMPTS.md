# 🤖 Bolt.new v2 - TX Frontend Prompts (Copy & Paste Ready)

## 📋 How to Use

1. Go to https://bolt.new
2. Start new project
3. Copy each prompt in sequence
4. Paste into bolt.new chat
5. Let AI build the feature
6. Move to next prompt

---

## 🚀 PROMPT 1: Initial Setup

Create a modern trading intelligence web app called "TX Predictive Intelligence":

TECH STACK:
- React 18 + TypeScript
- Vite
- TailwindCSS + shadcn/ui
- Lucide React icons
- React Query
- Recharts
- React Router
- Zustand

DESIGN:
- Dark mode (trading platform style)
- Electric blue (#3B82F6) primary
- Green (#10B981) bullish
- Red (#EF4444) bearish
- Clean, minimalist
- Mobile-responsive

STRUCTURE:
- Sidebar navigation
- Routes: Dashboard, Pattern Detection, Live Scanner, Alerts, Journal, Risk, Settings
- API base: https://tx-predictive-intelligence.onrender.com
- Error boundaries

Make it look like TradingView meets modern SaaS.

---

## 📊 PROMPT 2: Dashboard

Build comprehensive Dashboard:

1. HERO: Title, subtitle, "Detect Pattern" CTA
2. STATS CARDS: Total patterns, avg confidence, active alerts, portfolio P&L
3. RECENT ALERTS FEED: List recent detections
4. MARKET SENTIMENT: Gauge + news/social/market indicators + trending topics
5. TOP PATTERNS TODAY: Table of best patterns
6. QUICK ACTIONS: Floating buttons

Fetch from: GET /api/patterns/stats, /api/alerts/recent, /api/sentiment/overview, /api/patterns/top-today

Make it visually impressive with animations.

---

## 🎯 PROMPT 3: Pattern Detection

Build Pattern Detection page (core feature):

1. FORM:
   - Symbol input with autocomplete
   - Timeframe selector (1m, 5m, 15m, 1h, 4h, 1D)
   - Mode selector (2 large cards):
     * HYBRID PRO: Shield icon, "Conservative 75-85%"
     * AI ELITE: Rocket icon, "Aggressive 65-95%"
   - "Detect Pattern" button

2. RESULTS:
   - Pattern name + confidence (huge)
   - Candlestick chart with overlay
   - 6-layer confidence breakdown (progress bars)
   - Sentiment analysis (news, social, market)
   - Trading signals (entry, exit, SL, TP)
   - Pattern completion probability
   - Historical DNA matches

API: POST /api/patterns/detect-dual-mode

Make it stunning with smooth animations.

---

## 📡 PROMPT 4: Live Scanner

Create Live Market Scanner:

1. FILTERS:
   - Multi-symbol input (tags)
   - Timeframe selector
   - Confidence slider (0-100%)
   - Pattern type filter
   - Mode selector
   - "Start Scan" button + auto-refresh toggle

2. STATS: Total found, avg confidence, bullish/bearish ratio, top symbol

3. RESULTS TABLE:
   - Columns: Symbol, Pattern, Confidence, Timeframe, Sentiment, Action
   - Sortable, color-coded confidence
   - Actions: "View Chart", "Set Alert"
   - Real-time updates (poll every 30s)

API: POST /api/patterns/scan-live

Make it feel like a trading terminal.

---

## 🔔 PROMPT 5: Alerts

Build Alerts page:

1. CREATE ALERT FORM:
   - Symbol, pattern type, confidence threshold
   - Channels: Email, SMS, Push, Webhook
   - "Create Alert" button

2. ACTIVE ALERTS: Grid of cards with enable/disable toggle, edit, delete

3. ALERT HISTORY: Table of triggered alerts

4. NOTIFICATION SETTINGS:
   - Quiet hours
   - Priority filtering
   - Digest mode
   - Test notification button

API: POST /api/alerts/create, GET /api/alerts/active, DELETE /api/alerts/{id}

---

## 📖 PROMPT 6: Trading Journal

Build AI Trading Journal:

1. ADD TRADE FORM: Symbol, pattern, entry/exit, SL/TP, emotion tags, notes

2. PERFORMANCE ANALYTICS:
   - Key metrics: Total trades, win rate, profit factor
   - Charts: Equity curve, P&L by pattern, performance by timeframe/day

3. AI INSIGHTS:
   - Overtrading detection
   - Revenge trading alerts
   - Best/worst patterns
   - Recommendations

4. JOURNAL ENTRIES: Card/table view of trades

API: POST /api/journal/log-trade, GET /api/journal/entries, GET /api/journal/insights

---

## 🛡️ PROMPT 7: Risk Management

Create Risk Management Dashboard:

1. POSITION SIZE CALCULATOR:
   - Account size, risk %, entry, stop-loss
   - Methods: Fixed%, ATR, Kelly
   - Results: Position size, risk amount

2. PORTFOLIO HEAT MONITOR:
   - Gauge (0-100%)
   - Open positions list
   - Warning if > 6%

3. LOSS LIMITS:
   - Daily/weekly progress bars
   - Edit limits button

4. CORRELATION ANALYSIS:
   - Heatmap of position correlations
   - Diversification score

5. TRADE APPROVAL:
   - Pending trades with risk assessment
   - Approve/reject buttons

API: POST /api/risk/calculate-position-size, GET /api/risk/portfolio-heat

---

## 📝 Quick Tips

- Build features iteratively
- Test with live backend after each feature
- Use loading states and error handling
- Keep dark theme consistent
- Make it mobile-responsive
- Add smooth animations

**Backend API**: https://tx-predictive-intelligence.onrender.com
**Full API Docs**: See API_ENDPOINTS_COMPLETE.md

Let's build! 🚀
