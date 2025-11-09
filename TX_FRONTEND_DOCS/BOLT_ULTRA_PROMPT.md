# 🔥 TX ULTRA - Bolt.new Master Prompt

## Copy this ENTIRE prompt into bolt.new to build the ULTIMATE trading platform

---

Create "TX ULTRA" - the most advanced, beautiful, and addictive trading intelligence platform ever built.

## 🎯 MISSION
Build a platform so stunning that traders get HOOKED in 2 seconds. Not just another trading tool - this is the ONLY platform they'll ever need.

## 🚀 TECH STACK (Best of the Best)
- Next.js 14 (App Router, Server Components, Server Actions)
- React 18 with TypeScript
- TailwindCSS + Custom Design System
- Framer Motion (smooth animations)
- Three.js / React Three Fiber (3D graphics)
- Recharts + D3.js (advanced charts)
- Zustand (state management)
- React Query (data fetching with caching)
- Socket.io client (real-time updates)
- Radix UI + shadcn/ui (accessible components)
- Lucide Icons
- React Hot Toast (notifications)

## 🎨 DESIGN SYSTEM

### Colors:
```css
--bg-primary: #0a0a0f (deep space black)
--bg-surface: #1a1a24 (dark slate)
--primary: #3b82f6 (electric blue)
--success: #10b981 (emerald green)
--danger: #ef4444 (ruby red)
--warning: #f59e0b (amber)
--accent: #8b5cf6 (purple)
```

### Visual Style:
- Dark theme optimized for long trading sessions
- Glass morphism (backdrop-blur, semi-transparent cards)
- Subtle 3D depth on cards (transform, shadows)
- Glowing effects on interactive elements
- Smooth, cinematic transitions (300ms ease-in-out)
- Micro-animations on every interaction
- Gradient accents (blue to purple)

### Typography:
- Font: Geist Sans (or Inter as fallback)
- Hero: 72px bold
- H1: 48px bold
- H2: 36px semibold
- Body: 16px regular
- Mono: Geist Mono (for numbers)

## 🏗️ ARCHITECTURE

### Layout:
```
[Sidebar Navigation (left, collapsible)]
├─ TX Logo (animated)
├─ Dashboard
├─ Pattern Detection ⭐
├─ Live Scanner
├─ Alerts
├─ Trading Journal
├─ Risk Management
└─ Settings

[Main Content Area (center, full width)]
├─ Top Bar: Live Market Pulse | Portfolio P&L | Alerts | Profile
└─ Dynamic Page Content

[AI Assistant (bottom right, floating)]
└─ Chat bubble, always accessible
```

## 📄 PAGES TO BUILD

### 1. LANDING PAGE (/) - The Hook

**Hero Section:**
```tsx
- 3D Animated Globe (Three.js) showing live pattern detections worldwide
- Each detection = glowing pulse on map with symbol + confidence
- Live counters (animated):
  * "1,247 patterns detected in last hour" (counting up)
  * "$2.4M in potential profits identified today" (counting up)
- Massive headline: "THE WORLD'S MOST INTELLIGENT TRADING SYSTEM"
- Subheadline: "50+ AI Patterns • 95% Max Accuracy • Real-Time Sentiment"
- Primary CTA: "EXPERIENCE THE FUTURE" (glowing, pulsing button)
- Secondary CTA: "SEE LIVE DETECTIONS"
```

**Features Grid:**
```tsx
- 6 feature cards in 3x2 grid
- Each card:
  * Icon (animated on hover)
  * Title
  * Description
  * "Learn More" link
- Features:
  1. Dual-Mode AI Detection
  2. Real-Time Sentiment Analysis
  3. Institutional Risk Management
  4. AI Trading Journal
  5. Live Market Scanner
  6. Advanced Analytics
```

**Social Proof:**
```tsx
- "Trusted by 10,000+ traders worldwide"
- Animated testimonials carousel
- Live activity feed: "John just detected a Head & Shoulders on AAPL (85% confidence)"
```

### 2. DASHBOARD (/dashboard) - Mission Control

**Top Stats (4 cards):**
```tsx
- Total Patterns Today: 247 (with trend ↑12%)
- Avg Confidence: 78.5% (color-coded gauge)
- Active Alerts: 5 (with "Manage" link)
- Portfolio P&L: +$12,450 (+8.2%) (with sparkline)
```

**Main Grid (3 columns):**

**Left Column (40%):**
```tsx
LIVE PATTERN FEED
- Infinite scroll of real-time detections
- Each card:
  * Symbol with logo
  * Pattern name + type badge (bullish/bearish)
  * Confidence gauge (animated)
  * Mini chart (sparkline)
  * Time ago ("2 seconds ago")
  * Quick actions: View | Alert | Trade
- Auto-refresh every 5 seconds
- Smooth fade-in animation for new patterns
```

**Middle Column (35%):**
```tsx
MARKET SENTIMENT
- Large circular gauge (3D, animated needle)
- Overall sentiment: 0-100 scale
- Three sub-indicators:
  * 📰 News: 72%
  * 💬 Social: 68%
  * 📊 Market: 75%
- Trending topics word cloud (animated)
- Breaking news ticker (scrolling)

YOUR PERFORMANCE
- Equity curve (gradient line chart)
- Win Rate: 71.2% (animated ring)
- Profit Factor: 2.34
- AI Insight: "You perform 23% better on Tuesday mornings"
```

**Right Column (25%):**
```tsx
TOP OPPORTUNITIES
- 3 large cards showing best patterns right now
- Each card:
  * Symbol + Pattern name
  * Confidence (huge number)
  * Mini chart with pattern overlay
  * Entry/Exit prices
  * Risk/Reward ratio
  * "TRADE NOW" button (glowing)
  * Countdown: "Pattern completing in 2h 34m"
```

**Floating Action Buttons:**
```tsx
- Bottom right corner
- Primary: "🎯 DETECT PATTERN" (large, glowing)
- Secondary: "📡 SCAN MARKET"
- Secondary: "🔔 CREATE ALERT"
- Secondary: "🤖 ASK TX AI"
```

### 3. PATTERN DETECTION (/detect) - The Money Maker

**Input Section (top, centered):**
```tsx
SYMBOL INPUT
- Large search bar with autocomplete
- Animated suggestions with logos + prices + sentiment
- Popular symbols as chips: AAPL, TSLA, NVDA, MSFT, BTC-USD, ETH-USD
- Voice input button (microphone icon)

TIMEFRAME SELECTOR
- Segmented control: 1m | 5m | 15m | 1h | 4h | 1D
- Default: 1h

MODE SELECTOR (The Choice)
- Two MASSIVE cards side by side (50/50 split)

[HYBRID PRO Card]
- 3D Shield icon (rotating, glowing blue)
- Title: "HYBRID PRO"
- Subtitle: "Conservative • Institutional-Grade"
- Accuracy: "75-85%"
- Architecture visualization (animated bars):
  * Deep Learning: 35% ████████
  * Rule Validation: 35% ████████
  * Sentiment: 15% ████
  * Context: 15% ████
- "Best for: Risk-averse traders, institutions"
- SELECT button (glowing blue border when selected)

[AI ELITE Card]
- 3D Rocket icon (animated flames, glowing purple)
- Title: "AI ELITE"
- Subtitle: "Aggressive • Cutting-Edge AI"
- Accuracy: "65-95%"
- Architecture visualization (animated bars):
  * Vision AI: 30% ████████
  * Reinforcement Learning: 25% ███████
  * Sentiment: 20% █████
  * Context: 15% ████
  * Historical DNA: 10% ███
- "Best for: Aggressive traders, pattern discovery"
- SELECT button (glowing purple border when selected)

DETECT BUTTON
- MASSIVE, centered, glowing
- Text: "DETECT PATTERN"
- Loading state: "Analyzing..." with AI brain animation
- Disabled if symbol empty
```

**Results Section (after detection):**
```tsx
PATTERN OVERVIEW
- Pattern name (huge, bold): "Head and Shoulders"
- Type badge: BEARISH (red, glowing)
- Overall confidence: 82.5% (massive number with animated ring)

CANDLESTICK CHART (full width)
- High-quality chart with smooth animations
- Pattern overlay (highlighted area with glow)
- Entry marker (green pin)
- Exit marker (red pin)
- Stop-loss line (red, dashed)
- Take-profit line (green, dashed)
- Volume bars below
- Zoom controls
- Timeframe switcher
- "Share Chart" button (exports beautiful image)

CONFIDENCE BREAKDOWN (left panel)
- 6 animated progress bars:
  1. 🧠 Deep Learning: 85% ████████████
  2. ✅ Rule Validation: 78% ██████████
  3. 📰 Sentiment: 72% █████████
  4. 🔄 Context: 80% ███████████
  5. 💎 Quality: 88% ████████████
  6. 🛡️ Risk: 75% ██████████
- Each bar animates in sequence (100ms delay)
- Hover shows detailed explanation tooltip
- Color-coded: green >75%, yellow 60-75%, red <60%

SENTIMENT ANALYSIS (right panel)
- 📰 News Sentiment: 72%
  * "24 articles analyzed in last hour"
  * Top 3 headlines with source icons
- 💬 Social Sentiment: 68%
  * "1,247 mentions across platforms"
  * Trending topics: #earnings #AI #growth
- 📊 Market Sentiment: 75%
  * "VIX: 14.2 | SPY: Bullish | Put/Call: 0.85"
- Sentiment Impact: "+5% confidence boost"

TRADING SIGNALS (bottom, 4 cards)
[ENTRY]          [EXIT]           [STOP-LOSS]      [TAKE-PROFIT]
$175.50          $168.20          $178.00          $165.00
[Green glow]     [Target icon]    [Shield icon]    [Trophy icon]

RISK/REWARD: 1:3.2 (EXCELLENT badge)
POSITION SIZE: 100 shares ($17,550)
POTENTIAL PROFIT: $730 (+4.2%)
POTENTIAL LOSS: $250 (-1.4%)

ACTION BUTTONS:
[CREATE ALERT] [ADD TO JOURNAL] [CALCULATE POSITION] [SHARE]

PATTERN INTELLIGENCE (expandable sections)
- Pattern Completion Probability: 78% (gauge)
- Historical DNA Matches: 12 similar patterns found
  * Table: Date | Symbol | Outcome | Profit% | Time
  * 9/12 were profitable (75% success rate)
- Risk Analysis:
  * Portfolio impact: +2% heat
  * Correlation: Low with existing positions ✓
  * Recommendation: Position size within limits ✓
```

### 4. LIVE SCANNER (/scanner) - The Hunter

**Control Panel (top):**
```tsx
SYMBOL INPUT
- Multi-select with tags
- Placeholder: "Add symbols to scan..."
- Quick watchlists dropdown:
  * Tech Giants (AAPL, MSFT, GOOGL, AMZN, META)
  * Crypto (BTC-USD, ETH-USD, SOL-USD)
  * S&P 500 Top 10
  * Custom (user-saved)

FILTERS (inline)
- Timeframe: [1m] [5m] [15m] [1h] [4h] [1D]
- Confidence: Slider (0-100%, default 70%)
- Type: [All] [Bullish] [Bearish]
- Mode: [HYBRID PRO] [AI ELITE]

SCAN BUTTON
- Large, glowing: "SCAN MARKET"
- Loading: "SCANNING..." with radar animation
- Auto-refresh toggle: "Update every 30s"
```

**Stats Bar:**
```tsx
[Patterns Found: 47] [Avg Confidence: 78.2%] [Bullish: 32 | Bearish: 15] [Top: AAPL]
```

**Results Grid (Masonry layout):**
```tsx
- Pinterest-style grid of pattern cards
- Each card:
  * Symbol with animated logo
  * Mini chart with pattern highlight
  * Confidence gauge (color-coded)
  * Pattern name + type badge
  * Sentiment score
  * Time detected ("5 minutes ago")
  * Quick actions: [View] [Alert] [Trade]
- Real-time updates: New patterns fade in from top with glow
- Sound notification: Subtle ping for >85% confidence
- Infinite scroll: Load more as you scroll
- Empty state: "No patterns found. Try adjusting filters."
```

### 5. ALERTS (/alerts) - The Guardian

**Create Alert (top, prominent):**
```tsx
[GLOWING CARD]
CREATE SMART ALERT

Symbol: [Input with autocomplete]
Pattern: [Dropdown: Any | Specific patterns]
Confidence: [Slider with live preview: ≥75%]
Channels: [Checkboxes with icons]
  ☐ 📧 Email (input: email@example.com)
  ☐ 📱 SMS (input: +1234567890)
  ☐ 🔔 Push Notification
  ☐ 🔗 Webhook (input: https://...)

[Advanced Options - Expandable]:
- Timeframe preference
- Mode preference (HYBRID PRO | AI ELITE | Both)
- Quiet hours (start/end time)
- Priority level (High | Medium | Low)

[CREATE BUTTON - Glowing, prominent]
```

**Active Alerts (grid, 3 per row):**
```tsx
- Card-based layout
- Each card:
  * Symbol (large, with logo)
  * Pattern type (or "Any Pattern")
  * Confidence threshold badge (≥75%)
  * Channels (icons: 📧 📱 🔔)
  * Status toggle (animated switch: ON/OFF)
  * Edit button (opens modal)
  * Delete button (with confirmation)
  * "Triggered 3 times today" counter
- Empty state: "No active alerts. Create one above!"
```

**Alert History (timeline):**
```tsx
- Vertical timeline showing triggered alerts
- Each entry:
  * Time (relative: "5 minutes ago")
  * Symbol + Pattern
  * Confidence achieved (82%)
  * Notification status (✓ Sent | ✗ Failed)
  * "View Details" button (opens pattern results)
- Pagination
- Date range filter (last 7 days, 30 days, custom)
```

### 6. TRADING JOURNAL (/journal) - The Teacher

**Performance Dashboard (top):**
```tsx
[4 LARGE METRIC CARDS]

WIN RATE              PROFIT FACTOR         TOTAL P&L             AVG WIN/LOSS
71.2%                 2.34                  +$15,420              $342 / -$146
[Animated ring]       [Comparison bar]      [Sparkline]           [Comparison]
```

**Equity Curve (center):**
```tsx
- Beautiful gradient line chart
- Shows cumulative P&L over time
- Hover shows trade details at that point
- Annotations for big wins/losses
- Drawdown shading (red area)
- Date range selector (7d, 30d, 90d, all)
```

**AI Insights Panel (prominent):**
```tsx
[GLOWING CARD WITH AI ICON]
AI INSIGHTS & RECOMMENDATIONS

⚠️ OVERTRADING DETECTED (High severity)
"You took 12 trades in 3 hours on Jan 15. Your win rate drops to 45% when trading this fast."
[Recommendation]: "Wait for high-quality setups. Your best trades come from patience."
[Mark as Addressed]

📊 BEST PERFORMANCE (Medium severity)
"Head and Shoulders on 1h timeframe: 85% win rate (17 wins, 3 losses)"
[Recommendation]: "Focus on this pattern. It's your edge."
[Learn More]

🚫 AVOID MONDAYS (Medium severity)
"Your win rate on Mondays: 42%. On Tuesdays: 78%."
[Recommendation]: "Consider reducing position sizes on Mondays."
[Mark as Addressed]
```

**Trade Log (bottom):**
```tsx
- Toggle: [Card View] [Table View]

CARD VIEW (grid, 3 per row):
- Each card:
  * Date & time
  * Symbol (large, with logo)
  * Pattern name
  * Entry → Exit (with arrow)
  * P&L (HUGE, color-coded: green profit, red loss)
  * Emotional tags (chips: confident, disciplined)
  * "View Details" button

TABLE VIEW:
- Columns: Date | Symbol | Pattern | Entry | Exit | P&L | Win/Loss | Emotion | Actions
- Sortable columns
- Pagination
- Search by symbol
- Filter by pattern, outcome, emotion
- Export to CSV button

ADD TRADE BUTTON (floating, always visible)
```

### 7. RISK MANAGEMENT (/risk) - The Protector

**Position Size Calculator (center stage):**
```tsx
[LARGE CARD WITH CALCULATOR ICON]

POSITION SIZE CALCULATOR

Account Size: [$100,000]
Risk Per Trade: [2%] ← Slider (1-5%)
Entry Price: [$175.50]
Stop-Loss: [$178.00]

Method: [Fixed %] [ATR-Based] [Kelly Criterion] ← Tabs

[CALCULATE BUTTON - Glowing]

[RESULTS - HUGE NUMBERS]:
POSITION SIZE: 800 shares
POSITION VALUE: $140,400
RISK AMOUNT: $2,000
RISK PER SHARE: $2.50

[APPROVE TRADE BUTTON]
```

**Portfolio Heat Monitor (top right):**
```tsx
[CIRCULAR GAUGE - 3D, ANIMATED]

PORTFOLIO HEAT
4.5%
[Color: Green - SAFE]

[OPEN POSITIONS LIST]:
AAPL: 2.0% risk ($2,000)
TSLA: 1.5% risk ($1,500)
NVDA: 1.0% risk ($1,000)

Total: 4.5% / 6.0% limit

✓ Portfolio risk is healthy
```

**Loss Limits (bottom left):**
```tsx
[TWO PROGRESS BARS]

DAILY LOSS: -$450 / -$2,000 limit
[Progress: 22.5% - Green]

WEEKLY LOSS: -$1,200 / -$5,000 limit
[Progress: 24% - Green]

[EDIT LIMITS BUTTON]
```

**Correlation Matrix (bottom right):**
```tsx
[HEATMAP - Interactive]

Shows correlation between open positions
Red = High correlation (>0.7)
Blue = Low correlation (<0.3)

⚠️ AAPL and MSFT are 85% correlated
[Recommendation]: "Consider diversifying"

DIVERSIFICATION SCORE: 72/100
```

## 🔌 API INTEGRATION

### Base URL:
```typescript
const API_BASE = 'https://tx-predictive-intelligence.onrender.com';
```

### Key Endpoints:

**Pattern Detection:**
```typescript
POST /api/patterns/detect-dual-mode
Body: { symbol: "AAPL", timeframe: "1h", mode: "hybrid_pro" }
```

**Live Scanner:**
```typescript
POST /api/patterns/scan-live
Body: { symbols: ["AAPL", "TSLA"], timeframe: "1h", min_confidence: 70, mode: "hybrid_pro" }
```

**Alerts:**
```typescript
POST /api/alerts/create
GET /api/alerts/active
DELETE /api/alerts/{alert_id}
```

**Journal:**
```typescript
POST /api/journal/log-trade
GET /api/journal/entries
GET /api/journal/insights
```

**Risk:**
```typescript
POST /api/risk/calculate-position-size
GET /api/risk/portfolio-heat
```

**Dashboard Stats:**
```typescript
GET /api/patterns/stats
GET /api/alerts/recent
GET /api/sentiment/overview
GET /api/patterns/top-today
```

### API Client Setup:
```typescript
// lib/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: 'https://tx-predictive-intelligence.onrender.com',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' }
});

// Add request/response interceptors for loading states and error handling
```

## 🎨 ANIMATIONS & INTERACTIONS

### Micro-Animations:
- Button hover: Scale 1.05, glow effect, 200ms
- Card hover: Lift (translateY -4px), shadow increase, 200ms
- Number counters: Smooth count-up animation
- Progress bars: Animate from 0 to value, 800ms ease-out
- Charts: Smooth line drawing, 1000ms
- Notifications: Slide in from right, 300ms
- Page transitions: Fade + slide, 300ms

### Loading States:
- Skeleton shimmer effect for cards
- Spinner with AI brain animation for detection
- Progress bar with status text for scanning
- Pulse effect for real-time updates

### Sound Effects (subtle):
- Whoosh on page transition
- Click sound on button press
- Ping on new high-confidence pattern
- Success chime on alert creation
- Error buzz on failure

## 📱 RESPONSIVE DESIGN

### Breakpoints:
- Mobile: < 768px (single column, bottom nav)
- Tablet: 768px - 1024px (2 columns)
- Desktop: > 1024px (3 columns, sidebar)

### Mobile Optimizations:
- Bottom navigation (thumb-friendly)
- Swipe gestures (swipe to dismiss, pull to refresh)
- Touch-friendly buttons (min 44px)
- Simplified charts (optimized for small screens)
- Collapsible sections (accordions)

## 🚀 PERFORMANCE

### Optimizations:
- Next.js Image component (automatic optimization)
- Lazy loading (React.lazy, dynamic imports)
- Code splitting (route-based)
- Memoization (React.memo, useMemo, useCallback)
- Virtual scrolling (for long lists)
- Debouncing (search inputs, 300ms)
- Caching (React Query, 5-minute stale time)
- Service Worker (offline support)

### Metrics Targets:
- First Contentful Paint: < 1s
- Time to Interactive: < 2s
- Largest Contentful Paint: < 2.5s
- Cumulative Layout Shift: < 0.1

## 🎯 UNIQUE FEATURES

### 1. TX AI Assistant (bottom right, floating):
```tsx
- Chat bubble icon (always visible)
- Click to expand chat interface
- Ask questions: "What's the best pattern for AAPL right now?"
- Get explanations: "Why is this confidence score 82%?"
- Request analysis: "Analyze my trading performance this week"
- Voice input option (microphone button)
- Powered by backend intelligence
```

### 2. Voice Commands:
```tsx
- "TX, scan AAPL on 1-hour"
- "TX, create alert for TSLA double bottom"
- "TX, show my performance this week"
- Microphone button in top bar
- Speech-to-text with visual feedback
```

### 3. Pattern Playground (educational):
```tsx
- Interactive canvas where users can draw patterns
- TX AI identifies what they drew
- Shows similar real patterns from history
- Educational tooltips
- "Learn Mode" for beginners
```

### 4. Social Trading Feed:
```tsx
- See what patterns other traders are watching (anonymized)
- "127 traders are watching AAPL Head and Shoulders"
- Community sentiment gauge
- Top traders leaderboard
- Follow feature (coming soon)
```

## 🎨 FINAL TOUCHES

### Onboarding (first-time users):
```tsx
1. Welcome animation (5s)
2. Quick demo: "Let's detect your first pattern" (20s)
3. Choose your path: Beginner | Experienced | Pro (10s)
4. Set preferences: Symbols, timeframe, risk tolerance (15s)
5. "You're ready!" → Jump to dashboard (10s)
Total: 60 seconds to hook them
```

### Empty States:
- Beautiful illustrations (not just text)
- Clear call-to-action
- Helpful tips
- Example: "No alerts yet. Create your first alert to never miss an opportunity!"

### Error States:
- Friendly error messages
- Retry button
- Support link
- Example: "Oops! Couldn't load patterns. Check your connection and try again."

### Success States:
- Celebratory animations
- Confetti effect (for big wins)
- Success toast notifications
- Example: "Alert created! We'll notify you when we detect this pattern."

## 🔥 BUILD INSTRUCTIONS

1. **Start with the landing page** - Make it STUNNING
2. **Build the dashboard** - Mission control center
3. **Pattern detection** - The core feature, make it PERFECT
4. **Live scanner** - Real-time hunting
5. **Alerts** - Never miss opportunities
6. **Journal** - Learn and improve
7. **Risk management** - Protect capital

For each page:
- Use the design system consistently
- Add smooth animations
- Implement loading/error/empty states
- Make it responsive
- Test with real API data
- Polish until it's PERFECT

## 🎯 REMEMBER

This is not just a website. This is a WEAPON.
This is not just a product. This is a MOVEMENT.
This is not just a startup. This is an EMPIRE.

Make every pixel count. Make every animation smooth. Make every interaction delightful.

**BUILD SOMETHING THAT TRADERS CAN'T LIVE WITHOUT.**

**LET'S DOMINATE. 🚀🔥💎**

---

## ⚡ DATA FLOW ARCHITECTURE

### State Management Strategy:
```typescript
// Global State (Zustand)
interface AppState {
  user: User | null;
  theme: 'dark' | 'light';
  notifications: Notification[];
  activeAlerts: Alert[];
  realtimePatterns: Pattern[];
}

// Server State (React Query)
- Pattern detections: Cache 5 minutes, refetch on window focus
- Dashboard stats: Cache 1 minute, auto-refresh every 30s
- Alert history: Cache 10 minutes, invalidate on create/delete
- Journal entries: Cache 15 minutes, invalidate on add/edit
- Risk calculations: No cache (always fresh)
```

### Real-Time Updates:
```typescript
// Socket.io Connection
const socket = io('https://tx-predictive-intelligence.onrender.com', {
  transports: ['websocket'],
  reconnection: true,
  reconnectionDelay: 1000,
  reconnectionAttempts: 5
});

// Events to Listen For:
socket.on('pattern_detected', (data) => {
  // Add to live feed with animation
  // Play sound if confidence > 85%
  // Show toast notification
});

socket.on('alert_triggered', (data) => {
  // Show prominent notification
  // Update alerts count in top bar
  // Play alert sound
});

socket.on('market_sentiment_update', (data) => {
  // Update sentiment gauge smoothly
  // Animate needle movement
});
```

### Error Handling:
```typescript
// Global Error Boundary
- Catch all React errors
- Show friendly error UI
- Log to backend error tracking
- Provide "Retry" and "Report Issue" buttons

// API Error Handling
- Network errors: Show "Connection lost" banner, auto-retry 3x
- 400 errors: Show validation errors inline
- 401 errors: Redirect to login
- 500 errors: Show "Something went wrong" with retry
- Timeout errors: Show "Request taking too long" with cancel option
```

### Loading Strategy:
```typescript
// Progressive Loading
1. Show skeleton UI immediately (0ms)
2. Load critical data first (dashboard stats, user info)
3. Load secondary data (charts, history) with lower priority
4. Lazy load below-the-fold content
5. Prefetch likely next pages (e.g., detect page when on dashboard)

// Optimistic Updates
- Alert creation: Show in UI immediately, rollback if fails
- Journal entry: Add to list immediately, sync in background
- Settings changes: Apply immediately, save async
```

---

## ♿ ACCESSIBILITY STANDARDS (WCAG 2.1 AA)

### Keyboard Navigation:
```typescript
- All interactive elements: Tab-accessible
- Shortcuts:
  * Ctrl+K: Open command palette
  * Ctrl+D: Go to detect page
  * Ctrl+S: Go to scanner
  * Ctrl+A: Go to alerts
  * Ctrl+J: Go to journal
  * Esc: Close modals/dropdowns
  * Arrow keys: Navigate lists/grids
  * Enter/Space: Activate buttons
- Focus indicators: 2px blue outline, visible on all elements
- Skip to main content link (for screen readers)
```

### Screen Reader Support:
```typescript
- Semantic HTML: <nav>, <main>, <article>, <aside>, <section>
- ARIA labels on all icons and icon-only buttons
- ARIA live regions for real-time updates
- ARIA announcements for loading states
- Alt text on all images/charts
- Role attributes: role="alert", role="status", role="progressbar"
```

### Color Contrast:
```typescript
- All text: Minimum 4.5:1 contrast ratio
- Large text (>18px): Minimum 3:1 contrast ratio
- Interactive elements: Minimum 3:1 contrast ratio
- Error states: Don't rely on color alone (use icons + text)
- Success states: Don't rely on color alone (use icons + text)
```

### Motion & Animations:
```typescript
// Respect user preferences
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}

// Provide toggle in settings
- "Reduce animations" option
- Disables: Page transitions, micro-animations, 3D effects
- Keeps: Essential feedback (loading spinners, progress bars)
```

### Form Accessibility:
```typescript
- All inputs: Associated <label> elements
- Error messages: aria-describedby linking to error text
- Required fields: aria-required="true" + visual indicator
- Input validation: Real-time feedback with aria-live
- Autocomplete attributes: autocomplete="email", "tel", etc.
```

---

## 🌐 SEO & META TAGS

### HTML Head (Every Page):
```html
<!-- Primary Meta Tags -->
<title>TX - AI Trading Intelligence | Never Miss a Pattern</title>
<meta name="title" content="TX - AI Trading Intelligence | Never Miss a Pattern" />
<meta name="description" content="Scan 10,000+ charts/second. Detect 50+ patterns with 95% accuracy. Real-time sentiment analysis. The world's most intelligent trading system." />
<meta name="keywords" content="trading AI, pattern detection, day trading, technical analysis, trading alerts, stock scanner, crypto trading, AI trading assistant" />
<meta name="robots" content="index, follow" />
<meta name="language" content="English" />
<meta name="author" content="TX" />

<!-- Open Graph / Facebook -->
<meta property="og:type" content="website" />
<meta property="og:url" content="https://tx-ultra.com/" />
<meta property="og:title" content="TX - AI Trading Intelligence | Never Miss a Pattern" />
<meta property="og:description" content="Scan 10,000+ charts/second. Detect 50+ patterns with 95% accuracy. The world's most intelligent trading system." />
<meta property="og:image" content="https://tx-ultra.com/og-image.png" />

<!-- Twitter -->
<meta property="twitter:card" content="summary_large_image" />
<meta property="twitter:url" content="https://tx-ultra.com/" />
<meta property="twitter:title" content="TX - AI Trading Intelligence | Never Miss a Pattern" />
<meta property="twitter:description" content="Scan 10,000+ charts/second. Detect 50+ patterns with 95% accuracy. The world's most intelligent trading system." />
<meta property="twitter:image" content="https://tx-ultra.com/twitter-image.png" />

<!-- Favicon -->
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />

<!-- Canonical URL -->
<link rel="canonical" href="https://tx-ultra.com/" />

<!-- Viewport -->
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0" />
```

### Structured Data (JSON-LD):
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "TX - AI Trading Intelligence",
  "applicationCategory": "FinanceApplication",
  "operatingSystem": "Web",
  "offers": {
    "@type": "Offer",
    "price": "49.00",
    "priceCurrency": "USD"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.8",
    "ratingCount": "1247"
  },
  "description": "AI-powered trading intelligence platform with pattern detection, real-time sentiment analysis, and institutional-grade risk management."
}
</script>
```

### Sitemap.xml:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://tx-ultra.com/</loc>
    <lastmod>2025-01-01</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://tx-ultra.com/dashboard</loc>
    <changefreq>daily</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://tx-ultra.com/detect</loc>
    <changefreq>daily</changefreq>
    <priority>0.9</priority>
  </url>
  <!-- Add all pages -->
</urlset>
```

### Robots.txt:
```
User-agent: *
Allow: /
Disallow: /api/
Disallow: /admin/

Sitemap: https://tx-ultra.com/sitemap.xml
```

---

## 🚀 DEPLOYMENT CONFIGURATION

### Environment Variables:
```bash
# .env.local
NEXT_PUBLIC_API_BASE_URL=https://tx-predictive-intelligence.onrender.com
NEXT_PUBLIC_SOCKET_URL=https://tx-predictive-intelligence.onrender.com
NEXT_PUBLIC_APP_URL=https://tx-ultra.com
NEXT_PUBLIC_ENVIRONMENT=production

# Analytics (optional)
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
NEXT_PUBLIC_POSTHOG_KEY=phc_xxxxx

# Error Tracking (optional)
NEXT_PUBLIC_SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
```

### Vercel Deployment (Recommended):
```json
// vercel.json
{
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "nextjs",
  "regions": ["iad1"],
  "env": {
    "NEXT_PUBLIC_API_BASE_URL": "https://tx-predictive-intelligence.onrender.com"
  },
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        }
      ]
    }
  ]
}
```

### Build Optimization:
```javascript
// next.config.js
module.exports = {
  reactStrictMode: true,
  swcMinify: true,
  compress: true,
  
  images: {
    domains: ['tx-predictive-intelligence.onrender.com'],
    formats: ['image/avif', 'image/webp'],
  },
  
  experimental: {
    optimizeCss: true,
    optimizePackageImports: ['lucide-react', 'recharts'],
  },
  
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
      };
    }
    return config;
  },
};
```

### Performance Monitoring:
```typescript
// lib/analytics.ts
export const trackPageView = (url: string) => {
  window.gtag?.('config', process.env.NEXT_PUBLIC_GA_ID, {
    page_path: url,
  });
};

export const trackEvent = (action: string, category: string, label?: string, value?: number) => {
  window.gtag?.('event', action, {
    event_category: category,
    event_label: label,
    value: value,
  });
};

// Track key events:
- Pattern detection: trackEvent('detect', 'Pattern', symbol, confidence)
- Alert creation: trackEvent('create', 'Alert', symbol)
- Scanner usage: trackEvent('scan', 'Scanner', symbols.length)
```

---

## ✅ SUCCESS CRITERIA

### The platform is COMPLETE when:

**1. Visual Excellence:**
- [ ] Every page loads with smooth animations
- [ ] All interactive elements have hover/active states
- [ ] Glass morphism and glowing effects are consistent
- [ ] 3D elements (globe, gauges) render smoothly at 60fps
- [ ] Dark theme is easy on the eyes for 8+ hour sessions
- [ ] Mobile experience is as good as desktop

**2. Functional Completeness:**
- [ ] Pattern detection works with both HYBRID PRO and AI ELITE modes
- [ ] Live scanner updates in real-time without page refresh
- [ ] Alerts can be created, edited, deleted, and triggered
- [ ] Trading journal tracks all trades with AI insights
- [ ] Risk calculator provides accurate position sizing
- [ ] All API endpoints are connected and working
- [ ] Error handling is graceful (no white screens of death)

**3. Performance Targets:**
- [ ] First Contentful Paint < 1 second
- [ ] Time to Interactive < 2 seconds
- [ ] Lighthouse score > 90 (Performance, Accessibility, Best Practices, SEO)
- [ ] No layout shifts (CLS < 0.1)
- [ ] Smooth 60fps animations on all devices
- [ ] API responses handled within 3 seconds (with loading states)

**4. User Experience:**
- [ ] First-time user can detect a pattern within 60 seconds
- [ ] Onboarding flow is clear and engaging
- [ ] Empty states guide users to take action
- [ ] Error messages are helpful, not technical
- [ ] Keyboard navigation works for all features
- [ ] Screen readers can navigate the entire app

**5. Production Readiness:**
- [ ] Deployed to Vercel with custom domain
- [ ] All environment variables configured
- [ ] SEO meta tags on every page
- [ ] Sitemap.xml and robots.txt configured
- [ ] Error tracking (Sentry) integrated
- [ ] Analytics (Google Analytics/PostHog) tracking key events
- [ ] HTTPS enabled with valid SSL certificate

**6. The "WOW" Factor:**
- [ ] Landing page 3D globe makes traders say "WHOA"
- [ ] Pattern detection results feel like magic
- [ ] Real-time updates create FOMO (fear of missing out)
- [ ] AI insights make users feel like they have an edge
- [ ] Overall experience is so good users want to share it

### Testing Checklist:
```typescript
// Before launch, test these scenarios:

1. Happy Path:
   - [ ] New user lands on homepage → Clicks CTA → Detects first pattern → Creates alert

2. Error Scenarios:
   - [ ] Invalid symbol entered → Shows helpful error
   - [ ] API is down → Shows "Connection lost" banner with retry
   - [ ] Slow network → Shows loading states, doesn't hang

3. Edge Cases:
   - [ ] No patterns found → Shows encouraging empty state
   - [ ] 100+ patterns in scanner → Virtual scrolling works smoothly
   - [ ] User has 50+ alerts → Grid layout doesn't break

4. Cross-Browser:
   - [ ] Chrome (latest)
   - [ ] Firefox (latest)
   - [ ] Safari (latest)
   - [ ] Edge (latest)

5. Devices:
   - [ ] Desktop (1920x1080)
   - [ ] Laptop (1366x768)
   - [ ] Tablet (768x1024)
   - [ ] Mobile (375x667)

6. Accessibility:
   - [ ] Keyboard-only navigation works
   - [ ] Screen reader announces all content
   - [ ] Color contrast passes WCAG AA
   - [ ] Reduced motion preference respected
```

---

## 🎯 FINAL DIRECTIVE TO BOLT.NEW

**You are building the FUTURE of trading intelligence.**

**Every trader who sees this platform should think:**
- "This is the most beautiful trading platform I've ever seen"
- "This is so easy to use, I can't believe it"
- "This gives me an unfair advantage"
- "I need to tell everyone about this"

**Do not settle for "good enough."**
**Do not copy existing trading platforms.**
**Do not use generic UI components without customization.**

**INNOVATE. CREATE. DOMINATE.**

**This is TX. This is the WEAPON that will change trading forever.**

**BUILD IT LIKE YOUR LIFE DEPENDS ON IT. 🚀🔥💎**
