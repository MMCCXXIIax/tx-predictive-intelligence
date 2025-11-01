# 🚀 TX PREDICTIVE INTELLIGENCE - ULTIMATE FRONTEND PROMPT
## PART 5 OF 8: Component Library & State Management

---

## 🔧 COMPLETE COMPONENT LIBRARY

### 1. AnimatedCounter Component
```typescript
// components/AnimatedCounter.tsx
'use client';

import { useEffect, useState } from 'react';
import { useSpring, animated } from '@react-spring/web';

interface AnimatedCounterProps {
  value: number;
  format?: 'number' | 'currency' | 'percentage';
  decimals?: number;
  className?: string;
  prefix?: string;
  suffix?: string;
}

export function AnimatedCounter({
  value,
  format = 'number',
  decimals = 2,
  className = '',
  prefix = '',
  suffix = ''
}: AnimatedCounterProps) {
  const [displayValue, setDisplayValue] = useState(0);

  const { number } = useSpring({
    from: { number: displayValue },
    number: value,
    delay: 0,
    config: { mass: 1, tension: 20, friction: 10 },
    onRest: () => setDisplayValue(value),
  });

  const formatNumber = (n: number) => {
    switch (format) {
      case 'currency':
        return `$${n.toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })}`;
      case 'percentage':
        return `${n.toFixed(decimals)}%`;
      default:
        return n.toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
    }
  };

  return (
    <animated.span className={className}>
      {prefix}
      {number.to(n => formatNumber(n))}
      {suffix}
    </animated.span>
  );
}
```

---

### 2. PatternCard Component
```typescript
// components/PatternCard.tsx
'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, TrendingUp, TrendingDown, Newspaper, MessageCircle, BarChart3 } from 'lucide-react';
import { AnimatedCounter } from './AnimatedCounter';
import confetti from 'canvas-confetti';

interface PatternCardProps {
  pattern: any;
  symbol: string;
  onTrade?: () => void;
}

export function PatternCard({ pattern, symbol, onTrade }: PatternCardProps) {
  const [expanded, setExpanded] = useState(false);
  const isBullish = pattern.direction === 'bullish';

  const handleTrade = () => {
    // Trigger confetti
    confetti({
      particleCount: 100,
      spread: 70,
      origin: { y: 0.6 }
    });
    
    // Play sound
    const audio = new Audio('/sounds/trade.mp3');
    audio.volume = 0.5;
    audio.play();
    
    onTrade?.();
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 hover:border-white/20 transition-colors"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h3 className="text-xl font-bold">{pattern.name}</h3>
            <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
              isBullish ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
            }`}>
              {isBullish ? <TrendingUp className="w-4 h-4 inline mr-1" /> : <TrendingDown className="w-4 h-4 inline mr-1" />}
              {pattern.direction.toUpperCase()}
            </span>
          </div>
          
          {/* Confidence Meter */}
          <div className="flex items-center gap-3">
            <div className="relative w-16 h-16">
              <svg className="transform -rotate-90 w-16 h-16">
                <circle
                  cx="32"
                  cy="32"
                  r="28"
                  stroke="currentColor"
                  strokeWidth="4"
                  fill="none"
                  className="text-white/10"
                />
                <circle
                  cx="32"
                  cy="32"
                  r="28"
                  stroke="currentColor"
                  strokeWidth="4"
                  fill="none"
                  strokeDasharray={`${2 * Math.PI * 28}`}
                  strokeDashoffset={`${2 * Math.PI * 28 * (1 - pattern.confidence)}`}
                  className={`${
                    pattern.confidence >= 0.85 ? 'text-purple-500' :
                    pattern.confidence >= 0.75 ? 'text-green-500' :
                    'text-amber-500'
                  }`}
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-sm font-bold">{(pattern.confidence * 100).toFixed(0)}%</span>
              </div>
            </div>
            
            <div>
              <div className="text-sm text-gray-400">Confidence</div>
              <div className={`text-lg font-bold ${
                pattern.confidence >= 0.85 ? 'text-purple-400' :
                pattern.confidence >= 0.75 ? 'text-green-400' :
                'text-amber-400'
              }`}>
                {pattern.confidence >= 0.85 ? 'ELITE' :
                 pattern.confidence >= 0.75 ? 'HIGH' : 'GOOD'}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 6-Layer Breakdown Toggle */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between py-3 px-4 bg-white/5 rounded-xl mb-4 hover:bg-white/10 transition-colors"
      >
        <span className="font-semibold">6-Layer AI Breakdown</span>
        <ChevronDown className={`w-5 h-5 transition-transform ${expanded ? 'rotate-180' : ''}`} />
      </button>

      {/* Expanded Breakdown */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="space-y-3 mb-4"
          >
            {/* Layer 1 */}
            <div className="flex items-center justify-between py-2 px-4 bg-white/5 rounded-lg">
              <span className="text-sm">Deep Learning</span>
              <div className="flex items-center gap-2">
                <div className="w-32 h-2 bg-white/10 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-500"
                    style={{ width: `${pattern.layer_breakdown.deep_learning_score * 100}%` }}
                  />
                </div>
                <span className="text-sm font-semibold w-12 text-right">
                  {(pattern.layer_breakdown.deep_learning_score * 100).toFixed(0)}%
                </span>
              </div>
            </div>

            {/* Layer 2 */}
            <div className="flex items-center justify-between py-2 px-4 bg-white/5 rounded-lg">
              <span className="text-sm">Rule Validation</span>
              <div className="flex items-center gap-2">
                <div className="w-32 h-2 bg-white/10 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-cyan-500"
                    style={{ width: `${pattern.layer_breakdown.rule_validation_score * 100}%` }}
                  />
                </div>
                <span className="text-sm font-semibold w-12 text-right">
                  {(pattern.layer_breakdown.rule_validation_score * 100).toFixed(0)}%
                </span>
              </div>
            </div>

            {/* Layer 3 - Sentiment (HIGHLIGHT!) */}
            <div className="flex items-center justify-between py-2 px-4 bg-purple-500/10 border border-purple-500/30 rounded-lg">
              <div className="flex items-center gap-2">
                <span className="text-sm font-semibold">Sentiment Analysis</span>
                <div className="flex items-center gap-1 text-xs text-gray-400">
                  <Newspaper className="w-3 h-3" />
                  <span>{pattern.sentiment_analysis.news_count}</span>
                  <MessageCircle className="w-3 h-3 ml-1" />
                  <span>{pattern.sentiment_analysis.social_mentions}</span>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-32 h-2 bg-white/10 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-purple-500"
                    style={{ width: `${pattern.layer_breakdown.sentiment_score * 100}%` }}
                  />
                </div>
                <span className="text-sm font-semibold w-12 text-right text-purple-400">
                  {(pattern.layer_breakdown.sentiment_score * 100).toFixed(0)}%
                </span>
              </div>
            </div>

            {/* Layer 4 */}
            <div className="flex items-center justify-between py-2 px-4 bg-white/5 rounded-lg">
              <span className="text-sm">Context Score</span>
              <div className="flex items-center gap-2">
                <div className="w-32 h-2 bg-white/10 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-green-500"
                    style={{ width: `${pattern.layer_breakdown.context_score * 100}%` }}
                  />
                </div>
                <span className="text-sm font-semibold w-12 text-right">
                  {(pattern.layer_breakdown.context_score * 100).toFixed(0)}%
                </span>
              </div>
            </div>

            {/* Sentiment Details */}
            <div className="p-4 bg-purple-500/5 border border-purple-500/20 rounded-lg">
              <div className="text-sm font-semibold mb-2 text-purple-400">Market Sentiment</div>
              <div className="space-y-1 text-xs text-gray-400">
                <div className="flex justify-between">
                  <span>News Sentiment:</span>
                  <span className="text-white">{pattern.sentiment_analysis.news_sentiment.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span>Social Sentiment:</span>
                  <span className="text-white">{pattern.sentiment_analysis.social_sentiment.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span>Market Sentiment:</span>
                  <span className="text-white">{pattern.sentiment_analysis.market_sentiment.toFixed(2)}</span>
                </div>
                {pattern.sentiment_analysis.trending_topics?.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-purple-500/20">
                    <span className="text-purple-400">Trending: </span>
                    {pattern.sentiment_analysis.trending_topics.join(', ')}
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Trading Signals */}
      <div className="grid grid-cols-3 gap-4 mb-4">
        <div className="text-center p-3 bg-green-500/10 border border-green-500/30 rounded-lg">
          <div className="text-xs text-gray-400 mb-1">Entry</div>
          <div className="text-lg font-bold text-green-400">
            ${pattern.entry_price.toFixed(2)}
          </div>
        </div>
        <div className="text-center p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
          <div className="text-xs text-gray-400 mb-1">Stop Loss</div>
          <div className="text-lg font-bold text-red-400">
            ${pattern.stop_loss.toFixed(2)}
          </div>
        </div>
        <div className="text-center p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
          <div className="text-xs text-gray-400 mb-1">Target</div>
          <div className="text-lg font-bold text-blue-400">
            ${pattern.take_profit_1.toFixed(2)}
          </div>
        </div>
      </div>

      {/* Historical Performance */}
      <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg mb-4">
        <div className="flex items-center gap-2">
          <BarChart3 className="w-4 h-4 text-gray-400" />
          <span className="text-sm text-gray-400">Historical Win Rate</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-lg font-bold text-green-400">
            {pattern.historical_performance.win_rate.toFixed(1)}%
          </span>
          <span className="text-xs text-gray-400">
            ({pattern.historical_performance.sample_size} trades)
          </span>
        </div>
      </div>

      {/* Multi-Timeframe */}
      <div className="flex items-center justify-center gap-4 mb-4">
        {Object.entries(pattern.multi_timeframe).map(([tf, direction]) => {
          if (tf === 'confluence_score') return null;
          const isPositive = direction === 'bullish';
          return (
            <div key={tf} className="text-center">
              <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                isPositive ? 'bg-green-500/20 border-2 border-green-500' : 'bg-red-500/20 border-2 border-red-500'
              }`}>
                {isPositive ? <TrendingUp className="w-6 h-6 text-green-400" /> : <TrendingDown className="w-6 h-6 text-red-400" />}
              </div>
              <div className="text-xs text-gray-400 mt-1">{tf.toUpperCase()}</div>
            </div>
          );
        })}
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3">
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={handleTrade}
          className="flex-1 py-3 bg-gradient-to-r from-green-500 to-emerald-500 rounded-xl font-semibold text-white shadow-lg shadow-green-500/50"
        >
          Trade Now
        </motion.button>
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="px-6 py-3 bg-white/5 border border-white/10 rounded-xl font-semibold hover:bg-white/10"
        >
          Add Alert
        </motion.button>
      </div>
    </motion.div>
  );
}
```

---

### 3. Chart Component
```typescript
// components/Chart.tsx
'use client';

import { useEffect, useRef } from 'react';
import { createChart, ColorType } from 'lightweight-charts';

interface ChartProps {
  symbol: string;
  timeframe: string;
  patterns?: any[];
}

export function Chart({ symbol, timeframe, patterns }: ChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: 'transparent' },
        textColor: '#9CA3AF',
      },
      grid: {
        vertLines: { color: 'rgba(255, 255, 255, 0.05)' },
        horzLines: { color: 'rgba(255, 255, 255, 0.05)' },
      },
      width: chartContainerRef.current.clientWidth,
      height: 400,
    });

    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#10b981',
      downColor: '#ef4444',
      borderVisible: false,
      wickUpColor: '#10b981',
      wickDownColor: '#ef4444',
    });

    // Fetch and set data
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/candles/${symbol}?timeframe=${timeframe}&limit=100`)
      .then(res => res.json())
      .then(data => {
        if (data.success && data.candles) {
          candlestickSeries.setData(data.candles);
        }
      });

    // Add pattern markers
    if (patterns && patterns.length > 0) {
      const markers = patterns.map(p => ({
        time: p.timestamp,
        position: p.direction === 'bullish' ? 'belowBar' : 'aboveBar',
        color: p.direction === 'bullish' ? '#10b981' : '#ef4444',
        shape: 'arrowUp',
        text: p.name,
      }));
      candlestickSeries.setMarkers(markers);
    }

    // Responsive
    const handleResize = () => {
      chart.applyOptions({ width: chartContainerRef.current!.clientWidth });
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, [symbol, timeframe, patterns]);

  return (
    <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold">{symbol} - {timeframe}</h3>
      </div>
      <div ref={chartContainerRef} />
    </div>
  );
}
```

---

## 📦 STATE MANAGEMENT (Zustand)

### 1. Portfolio Store
```typescript
// stores/portfolioStore.ts
import { create } from 'zustand';
import { api } from '@/lib/api-service';

interface PortfolioState {
  portfolio: any;
  positions: any[];
  isLoading: boolean;
  fetchPortfolio: () => Promise<void>;
  fetchPositions: () => Promise<void>;
  closePosition: (tradeId: number) => Promise<void>;
}

export const usePortfolioStore = create<PortfolioState>((set, get) => ({
  portfolio: null,
  positions: [],
  isLoading: false,

  fetchPortfolio: async () => {
    set({ isLoading: true });
    try {
      const res = await api.get('/api/paper-trade/portfolio');
      set({ portfolio: res.data.portfolio, isLoading: false });
    } catch (error) {
      console.error('Failed to fetch portfolio:', error);
      set({ isLoading: false });
    }
  },

  fetchPositions: async () => {
    try {
      const res = await api.get('/api/paper-trades');
      set({ positions: res.data.trades.filter((t: any) => t.status === 'open') });
    } catch (error) {
      console.error('Failed to fetch positions:', error);
    }
  },

  closePosition: async (tradeId: number) => {
    try {
      await api.post('/api/paper-trade/close', { trade_id: tradeId });
      await get().fetchPortfolio();
      await get().fetchPositions();
    } catch (error) {
      console.error('Failed to close position:', error);
    }
  },
}));
```

---

### 2. Alerts Store
```typescript
// stores/alertsStore.ts
import { create } from 'zustand';
import { api } from '@/lib/api-service';

interface AlertsState {
  alerts: any[];
  unreadCount: number;
  fetchAlerts: () => Promise<void>;
  dismissAlert: (alertId: number) => Promise<void>;
  addAlert: (alert: any) => void;
}

export const useAlertsStore = create<AlertsState>((set, get) => ({
  alerts: [],
  unreadCount: 0,

  fetchAlerts: async () => {
    try {
      const res = await api.get('/api/get_active_alerts');
      set({ 
        alerts: res.data.alerts,
        unreadCount: res.data.alerts.filter((a: any) => !a.read).length
      });
    } catch (error) {
      console.error('Failed to fetch alerts:', error);
    }
  },

  dismissAlert: async (alertId: number) => {
    try {
      await api.post(`/api/alerts/dismiss/${alertId}`);
      set({ alerts: get().alerts.filter(a => a.id !== alertId) });
    } catch (error) {
      console.error('Failed to dismiss alert:', error);
    }
  },

  addAlert: (alert: any) => {
    set({ 
      alerts: [alert, ...get().alerts],
      unreadCount: get().unreadCount + 1
    });
    
    // Play sound
    const audio = new Audio('/sounds/alert.mp3');
    audio.volume = 0.5;
    audio.play();
    
    // Show notification
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification('New Trading Alert', {
        body: `${alert.symbol}: ${alert.pattern} detected`,
        icon: '/icon.png',
      });
    }
  },
}));
```

---

### 3. Preferences Store
```typescript
// stores/preferencesStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { api } from '@/lib/api-service';

interface PreferencesState {
  theme: 'dark' | 'light';
  soundEnabled: boolean;
  notificationsEnabled: boolean;
  defaultMode: 'hybrid_pro' | 'ai_elite';
  defaultWatchlist: string[];
  setTheme: (theme: 'dark' | 'light') => void;
  toggleSound: () => void;
  toggleNotifications: () => void;
  setDefaultMode: (mode: 'hybrid_pro' | 'ai_elite') => void;
  updateWatchlist: (symbols: string[]) => void;
  savePreferences: () => Promise<void>;
}

export const usePreferencesStore = create<PreferencesState>()(
  persist(
    (set, get) => ({
      theme: 'dark',
      soundEnabled: true,
      notificationsEnabled: true,
      defaultMode: 'hybrid_pro',
      defaultWatchlist: ['AAPL', 'GOOGL', 'MSFT', 'NVDA'],

      setTheme: (theme) => set({ theme }),
      
      toggleSound: () => set({ soundEnabled: !get().soundEnabled }),
      
      toggleNotifications: () => set({ notificationsEnabled: !get().notificationsEnabled }),
      
      setDefaultMode: (mode) => set({ defaultMode: mode }),
      
      updateWatchlist: (symbols) => set({ defaultWatchlist: symbols }),
      
      savePreferences: async () => {
        try {
          const prefs = {
            theme: get().theme,
            notifications: {
              sound: get().soundEnabled,
              push: get().notificationsEnabled,
            },
            default_watchlist: get().defaultWatchlist,
            default_mode: get().defaultMode,
          };
          await api.post('/api/user/preferences', prefs);
        } catch (error) {
          console.error('Failed to save preferences:', error);
        }
      },
    }),
    {
      name: 'tx-preferences',
    }
  )
);
```

---

## ✅ PART 5 COMPLETE

Covered:
- ✅ AnimatedCounter Component
- ✅ PatternCard Component (with 6-layer breakdown)
- ✅ Chart Component (Lightweight Charts)
- ✅ Portfolio Store (Zustand)
- ✅ Alerts Store (Zustand)
- ✅ Preferences Store (Zustand with persistence)

---

## 🚀 READY FOR PART 6?

**PART 6 will cover:**
- 🌐 Complete WebSocket Integration
- 🔔 Real-time Notifications System
- 🎵 Sound Manager
- 📱 Mobile Components
- 🎨 Additional UI Components

**Should I proceed with PART 6?** 🎯
