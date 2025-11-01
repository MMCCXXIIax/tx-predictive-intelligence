# 🚀 TX PREDICTIVE INTELLIGENCE - ULTIMATE FRONTEND PROMPT
## PART 6 OF 8: WebSocket, Notifications & Sound System

---

## 🌐 COMPLETE WEBSOCKET INTEGRATION

### WebSocket Provider Component
```typescript
// components/WebSocketProvider.tsx
'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import { io, Socket } from 'socket.io-client';
import { useAlertsStore } from '@/stores/alertsStore';
import { usePortfolioStore } from '@/stores/portfolioStore';
import toast from 'react-hot-toast';

interface WebSocketContextType {
  socket: Socket | null;
  isConnected: boolean;
  reconnectAttempts: number;
}

const WebSocketContext = createContext<WebSocketContextType>({
  socket: null,
  isConnected: false,
  reconnectAttempts: 0,
});

export const useWebSocket = () => useContext(WebSocketContext);

export function WebSocketProvider({ children }: { children: React.ReactNode }) {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  
  const { addAlert } = useAlertsStore();
  const { fetchPortfolio, fetchPositions } = usePortfolioStore();

  useEffect(() => {
    const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:10000';
    
    const socketInstance = io(WS_URL, {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: 10,
      timeout: 20000,
    });

    // Connection events
    socketInstance.on('connect', () => {
      console.log('✅ WebSocket connected');
      setIsConnected(true);
      setReconnectAttempts(0);
      
      // Subscribe to channels
      socketInstance.emit('subscribe_alerts');
      socketInstance.emit('subscribe_portfolio');
      socketInstance.emit('subscribe_market_scan');
      
      // Show success toast
      toast.success('Connected to live data', {
        icon: '🟢',
        duration: 2000,
      });
    });

    socketInstance.on('disconnect', (reason) => {
      console.log('❌ WebSocket disconnected:', reason);
      setIsConnected(false);
      
      toast.error('Disconnected from live data', {
        icon: '🔴',
        duration: 3000,
      });
    });

    socketInstance.on('connect_error', (error) => {
      setReconnectAttempts(prev => prev + 1);
      console.error(`WebSocket connection error (attempt ${reconnectAttempts + 1}):`, error);
    });

    socketInstance.on('reconnect', (attemptNumber) => {
      console.log(`✅ WebSocket reconnected after ${attemptNumber} attempts`);
      toast.success('Reconnected to live data', {
        icon: '🟢',
        duration: 2000,
      });
    });

    // Alert events
    socketInstance.on('new_alert', (alert) => {
      console.log('🚨 New alert received:', alert);
      addAlert(alert);
      
      // Show toast notification
      toast.custom((t) => (
        <div className="bg-gradient-to-r from-blue-500 to-purple-500 text-white px-6 py-4 rounded-xl shadow-2xl flex items-center gap-4">
          <div className="text-2xl">🚨</div>
          <div>
            <div className="font-bold">{alert.symbol} - {alert.pattern}</div>
            <div className="text-sm opacity-90">{(alert.confidence * 100).toFixed(0)}% confidence</div>
          </div>
        </div>
      ), {
        duration: 5000,
        position: 'top-right',
      });
    });

    // Portfolio events
    socketInstance.on('portfolio_update', (data) => {
      console.log('💰 Portfolio updated:', data);
      fetchPortfolio();
    });

    socketInstance.on('trade_executed', (trade) => {
      console.log('✅ Trade executed:', trade);
      fetchPortfolio();
      fetchPositions();
      
      toast.success(`Trade executed: ${trade.symbol}`, {
        icon: '✅',
        duration: 3000,
      });
    });

    socketInstance.on('position_closed', (data) => {
      console.log('🔒 Position closed:', data);
      fetchPortfolio();
      fetchPositions();
      
      const isProfit = data.pnl > 0;
      toast.custom((t) => (
        <div className={`${isProfit ? 'bg-green-500' : 'bg-red-500'} text-white px-6 py-4 rounded-xl shadow-2xl`}>
          <div className="font-bold">Position Closed: {data.symbol}</div>
          <div className="text-sm">
            P&L: ${Math.abs(data.pnl).toFixed(2)} ({data.pnl_pct.toFixed(2)}%)
          </div>
        </div>
      ), {
        duration: 5000,
        position: 'top-right',
      });
    });

    // Market scan events
    socketInstance.on('scan_complete', (data) => {
      console.log('🔍 Scan complete:', data);
      
      if (data.patterns_found > 0) {
        toast.success(`Scan complete: ${data.patterns_found} patterns found`, {
          icon: '🔍',
          duration: 3000,
        });
      }
    });

    socketInstance.on('scan_progress', (data) => {
      console.log('📊 Scan progress:', data);
      // Update UI with scan progress
    });

    setSocket(socketInstance);

    return () => {
      socketInstance.disconnect();
    };
  }, []);

  return (
    <WebSocketContext.Provider value={{ socket, isConnected, reconnectAttempts }}>
      {children}
    </WebSocketContext.Provider>
  );
}
```

---

### Connection Status Indicator
```typescript
// components/ConnectionStatus.tsx
'use client';

import { useWebSocket } from './WebSocketProvider';
import { motion, AnimatePresence } from 'framer-motion';
import { Wifi, WifiOff } from 'lucide-react';

export function ConnectionStatus() {
  const { isConnected, reconnectAttempts } = useWebSocket();

  return (
    <AnimatePresence>
      {!isConnected && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          className="fixed top-4 right-4 z-50 bg-red-500/90 backdrop-blur-xl text-white px-4 py-2 rounded-xl shadow-2xl flex items-center gap-2"
        >
          <WifiOff className="w-4 h-4 animate-pulse" />
          <span className="text-sm font-semibold">
            {reconnectAttempts > 0 ? `Reconnecting... (${reconnectAttempts})` : 'Disconnected'}
          </span>
        </motion.div>
      )}
      
      {isConnected && (
        <div className="fixed bottom-4 right-4 z-50 bg-green-500/20 backdrop-blur-xl border border-green-500/50 text-green-400 px-3 py-1 rounded-full text-xs font-semibold flex items-center gap-2">
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
          <span>LIVE</span>
        </div>
      )}
    </AnimatePresence>
  );
}
```

---

## 🔔 NOTIFICATION SYSTEM

### Notification Manager
```typescript
// lib/notificationManager.ts
import { usePreferencesStore } from '@/stores/preferencesStore';

class NotificationManager {
  private permission: NotificationPermission = 'default';

  async requestPermission(): Promise<boolean> {
    if (!('Notification' in window)) {
      console.warn('Notifications not supported');
      return false;
    }

    if (this.permission === 'granted') {
      return true;
    }

    const permission = await Notification.requestPermission();
    this.permission = permission;
    return permission === 'granted';
  }

  show(title: string, options?: NotificationOptions) {
    const { notificationsEnabled } = usePreferencesStore.getState();
    
    if (!notificationsEnabled) {
      console.log('Notifications disabled by user');
      return;
    }

    if (this.permission !== 'granted') {
      console.warn('Notification permission not granted');
      return;
    }

    const notification = new Notification(title, {
      icon: '/icon.png',
      badge: '/badge.png',
      vibrate: [200, 100, 200],
      ...options,
    });

    notification.onclick = () => {
      window.focus();
      notification.close();
    };

    return notification;
  }

  showAlert(alert: any) {
    this.show('New Trading Alert', {
      body: `${alert.symbol}: ${alert.pattern} detected (${(alert.confidence * 100).toFixed(0)}% confidence)`,
      tag: `alert-${alert.id}`,
      requireInteraction: true,
      actions: [
        { action: 'view', title: 'View' },
        { action: 'dismiss', title: 'Dismiss' },
      ],
    });
  }

  showTrade(trade: any) {
    this.show('Trade Executed', {
      body: `${trade.side} ${trade.quantity} shares of ${trade.symbol} at $${trade.price.toFixed(2)}`,
      tag: `trade-${trade.id}`,
    });
  }

  showPositionClosed(data: any) {
    const isProfit = data.pnl > 0;
    this.show('Position Closed', {
      body: `${data.symbol}: ${isProfit ? '+' : ''}$${data.pnl.toFixed(2)} (${data.pnl_pct.toFixed(2)}%)`,
      tag: `position-${data.id}`,
      icon: isProfit ? '/icon-profit.png' : '/icon-loss.png',
    });
  }
}

export const notificationManager = new NotificationManager();
```

---

### Notification Permission Component
```typescript
// components/NotificationPermission.tsx
'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bell, X } from 'lucide-react';
import { notificationManager } from '@/lib/notificationManager';

export function NotificationPermission() {
  const [show, setShow] = useState(false);
  const [permission, setPermission] = useState<NotificationPermission>('default');

  useEffect(() => {
    if ('Notification' in window) {
      setPermission(Notification.permission);
      
      // Show prompt after 10 seconds if not granted
      if (Notification.permission === 'default') {
        const timer = setTimeout(() => setShow(true), 10000);
        return () => clearTimeout(timer);
      }
    }
  }, []);

  const handleRequest = async () => {
    const granted = await notificationManager.requestPermission();
    setPermission(granted ? 'granted' : 'denied');
    setShow(false);
  };

  return (
    <AnimatePresence>
      {show && permission === 'default' && (
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 50 }}
          className="fixed bottom-4 left-4 right-4 md:left-auto md:w-96 z-50 bg-gradient-to-r from-blue-500 to-purple-500 text-white p-6 rounded-2xl shadow-2xl"
        >
          <button
            onClick={() => setShow(false)}
            className="absolute top-2 right-2 p-1 hover:bg-white/20 rounded-lg transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
          
          <div className="flex items-start gap-4">
            <Bell className="w-8 h-8 flex-shrink-0" />
            <div className="flex-1">
              <h3 className="font-bold text-lg mb-2">Enable Notifications</h3>
              <p className="text-sm opacity-90 mb-4">
                Get instant alerts when new trading patterns are detected
              </p>
              <button
                onClick={handleRequest}
                className="w-full py-2 bg-white text-blue-600 rounded-xl font-semibold hover:bg-gray-100 transition-colors"
              >
                Enable Notifications
              </button>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
```

---

## 🎵 SOUND MANAGER

### Sound Manager Class
```typescript
// lib/soundManager.ts
import { Howl } from 'howler';
import { usePreferencesStore } from '@/stores/preferencesStore';

class SoundManager {
  private sounds: Map<string, Howl> = new Map();
  private initialized = false;

  init() {
    if (this.initialized) return;

    // Preload all sounds
    const soundFiles = {
      scan: '/sounds/scan.mp3',
      alert: '/sounds/alert.mp3',
      win: '/sounds/win.mp3',
      loss: '/sounds/loss.mp3',
      achievement: '/sounds/achievement.mp3',
      trade: '/sounds/trade.mp3',
      notification: '/sounds/notification.mp3',
      click: '/sounds/click.mp3',
      hover: '/sounds/hover.mp3',
      error: '/sounds/error.mp3',
    };

    Object.entries(soundFiles).forEach(([name, src]) => {
      this.sounds.set(name, new Howl({
        src: [src],
        volume: 0.5,
        preload: true,
      }));
    });

    this.initialized = true;
  }

  play(name: string, volume?: number) {
    const { soundEnabled } = usePreferencesStore.getState();
    
    if (!soundEnabled) {
      return;
    }

    const sound = this.sounds.get(name);
    if (!sound) {
      console.warn(`Sound "${name}" not found`);
      return;
    }

    if (volume !== undefined) {
      sound.volume(volume);
    }

    sound.play();
  }

  // Convenience methods
  playAlert() {
    this.play('alert', 0.7);
  }

  playWin() {
    this.play('win', 0.6);
  }

  playLoss() {
    this.play('loss', 0.4);
  }

  playAchievement() {
    this.play('achievement', 0.8);
  }

  playTrade() {
    this.play('trade', 0.5);
  }

  playScan() {
    this.play('scan', 0.4);
  }

  playClick() {
    this.play('click', 0.3);
  }

  playHover() {
    this.play('hover', 0.2);
  }

  playError() {
    this.play('error', 0.5);
  }

  setVolume(volume: number) {
    this.sounds.forEach(sound => sound.volume(volume));
  }

  mute() {
    this.sounds.forEach(sound => sound.mute(true));
  }

  unmute() {
    this.sounds.forEach(sound => sound.mute(false));
  }
}

export const soundManager = new SoundManager();

// Initialize on first user interaction
if (typeof window !== 'undefined') {
  const initOnInteraction = () => {
    soundManager.init();
    document.removeEventListener('click', initOnInteraction);
    document.removeEventListener('keydown', initOnInteraction);
  };
  
  document.addEventListener('click', initOnInteraction);
  document.addEventListener('keydown', initOnInteraction);
}
```

---

### Sound Toggle Component
```typescript
// components/SoundToggle.tsx
'use client';

import { Volume2, VolumeX } from 'lucide-react';
import { usePreferencesStore } from '@/stores/preferencesStore';
import { soundManager } from '@/lib/soundManager';
import { motion } from 'framer-motion';

export function SoundToggle() {
  const { soundEnabled, toggleSound } = usePreferencesStore();

  const handleToggle = () => {
    toggleSound();
    
    if (!soundEnabled) {
      soundManager.unmute();
      soundManager.playClick();
    } else {
      soundManager.mute();
    }
  };

  return (
    <motion.button
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      onClick={handleToggle}
      className="p-2 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 transition-colors"
      title={soundEnabled ? 'Mute sounds' : 'Unmute sounds'}
    >
      {soundEnabled ? (
        <Volume2 className="w-5 h-5" />
      ) : (
        <VolumeX className="w-5 h-5 text-gray-400" />
      )}
    </motion.button>
  );
}
```

---

## 📱 MOBILE COMPONENTS

### Mobile Navigation
```typescript
// components/MobileNav.tsx
'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Home, Search, Briefcase, BarChart3, Settings } from 'lucide-react';
import { useRouter, usePathname } from 'next/navigation';
import { soundManager } from '@/lib/soundManager';

const navItems = [
  { icon: Home, label: 'Home', path: '/' },
  { icon: Search, label: 'Scanner', path: '/scanner' },
  { icon: Briefcase, label: 'Portfolio', path: '/portfolio' },
  { icon: BarChart3, label: 'Analytics', path: '/analytics' },
  { icon: Settings, label: 'Settings', path: '/settings' },
];

export function MobileNav() {
  const router = useRouter();
  const pathname = usePathname();

  const handleNav = (path: string) => {
    soundManager.playClick();
    router.push(path);
  };

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 md:hidden bg-slate-950/90 backdrop-blur-xl border-t border-white/10">
      <div className="flex items-center justify-around px-4 py-3">
        {navItems.map(({ icon: Icon, label, path }) => {
          const isActive = pathname === path;
          
          return (
            <motion.button
              key={path}
              whileTap={{ scale: 0.9 }}
              onClick={() => handleNav(path)}
              className={`flex flex-col items-center gap-1 px-3 py-2 rounded-xl transition-colors ${
                isActive ? 'text-blue-400' : 'text-gray-400'
              }`}
            >
              <Icon className={`w-6 h-6 ${isActive ? 'text-blue-400' : ''}`} />
              <span className="text-xs font-medium">{label}</span>
              {isActive && (
                <motion.div
                  layoutId="activeTab"
                  className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-1 h-1 bg-blue-400 rounded-full"
                />
              )}
            </motion.button>
          );
        })}
      </div>
    </nav>
  );
}
```

---

### Pull to Refresh
```typescript
// components/PullToRefresh.tsx
'use client';

import { useState, useRef } from 'react';
import { motion, useMotionValue, useTransform } from 'framer-motion';
import { RefreshCw } from 'lucide-react';

interface PullToRefreshProps {
  onRefresh: () => Promise<void>;
  children: React.ReactNode;
}

export function PullToRefresh({ onRefresh, children }: PullToRefreshProps) {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const y = useMotionValue(0);
  const rotate = useTransform(y, [0, 100], [0, 360]);
  const opacity = useTransform(y, [0, 100], [0, 1]);

  const handleDragEnd = async (event: any, info: any) => {
    if (info.offset.y > 100 && !isRefreshing) {
      setIsRefreshing(true);
      await onRefresh();
      setIsRefreshing(false);
    }
    y.set(0);
  };

  return (
    <div ref={containerRef} className="relative overflow-hidden">
      <motion.div
        drag="y"
        dragConstraints={{ top: 0, bottom: 100 }}
        dragElastic={0.2}
        onDragEnd={handleDragEnd}
        style={{ y }}
        className="relative"
      >
        {/* Refresh Indicator */}
        <motion.div
          style={{ opacity }}
          className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-full py-4"
        >
          <motion.div style={{ rotate }}>
            <RefreshCw className={`w-6 h-6 ${isRefreshing ? 'animate-spin' : ''}`} />
          </motion.div>
        </motion.div>

        {children}
      </motion.div>
    </div>
  );
}
```

---

### Haptic Feedback (iOS)
```typescript
// lib/haptics.ts
class HapticManager {
  private supported = false;

  constructor() {
    // Check if haptics are supported
    this.supported = 'vibrate' in navigator;
  }

  light() {
    if (!this.supported) return;
    navigator.vibrate(10);
  }

  medium() {
    if (!this.supported) return;
    navigator.vibrate(20);
  }

  heavy() {
    if (!this.supported) return;
    navigator.vibrate(30);
  }

  success() {
    if (!this.supported) return;
    navigator.vibrate([10, 50, 10]);
  }

  error() {
    if (!this.supported) return;
    navigator.vibrate([30, 50, 30]);
  }

  selection() {
    if (!this.supported) return;
    navigator.vibrate(5);
  }
}

export const haptics = new HapticManager();
```

---

## 🎨 ADDITIONAL UI COMPONENTS

### Loading Skeleton
```typescript
// components/LoadingSkeleton.tsx
export function LoadingSkeleton({ className = '' }: { className?: string }) {
  return (
    <div className={`animate-pulse bg-white/5 rounded-xl ${className}`} />
  );
}

export function PatternCardSkeleton() {
  return (
    <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1 space-y-3">
          <LoadingSkeleton className="h-6 w-48" />
          <LoadingSkeleton className="h-4 w-32" />
        </div>
        <LoadingSkeleton className="w-16 h-16 rounded-full" />
      </div>
      <LoadingSkeleton className="h-24 w-full mb-4" />
      <div className="grid grid-cols-3 gap-4">
        <LoadingSkeleton className="h-16" />
        <LoadingSkeleton className="h-16" />
        <LoadingSkeleton className="h-16" />
      </div>
    </div>
  );
}
```

---

### Empty State
```typescript
// components/EmptyState.tsx
import { LucideIcon } from 'lucide-react';

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export function EmptyState({ icon: Icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <div className="w-16 h-16 rounded-full bg-white/5 flex items-center justify-center mb-4">
        <Icon className="w-8 h-8 text-gray-400" />
      </div>
      <h3 className="text-xl font-bold mb-2">{title}</h3>
      <p className="text-gray-400 mb-6 max-w-md">{description}</p>
      {action && (
        <button
          onClick={action.onClick}
          className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl font-semibold hover:shadow-lg hover:shadow-blue-500/50 transition-shadow"
        >
          {action.label}
        </button>
      )}
    </div>
  );
}
```

---

## ✅ PART 6 COMPLETE

Covered:
- ✅ Complete WebSocket Integration
- ✅ Connection Status Indicator
- ✅ Notification System (Browser + Toast)
- ✅ Sound Manager with Preloading
- ✅ Mobile Navigation
- ✅ Pull to Refresh
- ✅ Haptic Feedback
- ✅ Loading Skeletons
- ✅ Empty States

---

## 🚀 READY FOR PART 7?

**PART 7 will cover:**
- 🚀 Deployment Guide (Render + Vercel)
- 🔧 Environment Variables
- ⚡ Performance Optimization
- 📊 Analytics Integration
- 🔒 Security Best Practices

**Should I proceed with PART 7?** 🎯
