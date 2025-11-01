# 🚀 TX PREDICTIVE INTELLIGENCE - ULTIMATE FRONTEND PROMPT
## PART 7 OF 8: Deployment, Optimization & Security

---

## 🚀 DEPLOYMENT GUIDE

### Vercel Deployment (Recommended for Next.js)

#### 1. Project Setup
```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Initialize project
vercel
```

#### 2. Environment Variables
Create `.env.production` file:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=https://tx-predictive-intelligence-latest.onrender.com
NEXT_PUBLIC_WS_URL=wss://tx-predictive-intelligence-latest.onrender.com

# Analytics (Optional)
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
NEXT_PUBLIC_SENTRY_DSN=https://xxxxx@sentry.io/xxxxx

# Feature Flags
NEXT_PUBLIC_ENABLE_NOTIFICATIONS=true
NEXT_PUBLIC_ENABLE_SOUND=true
NEXT_PUBLIC_ENABLE_HAPTICS=true
```

#### 3. Vercel Configuration
Create `vercel.json`:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "nextjs",
  "regions": ["iad1"],
  "env": {
    "NEXT_PUBLIC_API_URL": "@api-url",
    "NEXT_PUBLIC_WS_URL": "@ws-url"
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
        },
        {
          "key": "Referrer-Policy",
          "value": "strict-origin-when-cross-origin"
        }
      ]
    }
  ],
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://tx-predictive-intelligence-latest.onrender.com/api/:path*"
    }
  ]
}
```

#### 4. Deploy
```bash
# Production deployment
vercel --prod

# Or use GitHub integration (auto-deploy on push)
# Connect repo in Vercel dashboard
```

---

### Alternative: Netlify Deployment

#### netlify.toml
```toml
[build]
  command = "npm run build"
  publish = ".next"

[[redirects]]
  from = "/api/*"
  to = "https://tx-predictive-intelligence-latest.onrender.com/api/:splat"
  status = 200
  force = true

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-Content-Type-Options = "nosniff"
    X-XSS-Protection = "1; mode=block"
```

---

## ⚡ PERFORMANCE OPTIMIZATION

### 1. Next.js Configuration
```typescript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable React strict mode
  reactStrictMode: true,

  // Enable SWC minification
  swcMinify: true,

  // Image optimization
  images: {
    domains: ['tx-predictive-intelligence-latest.onrender.com'],
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },

  // Compression
  compress: true,

  // Production source maps (disable for smaller bundle)
  productionBrowserSourceMaps: false,

  // Experimental features
  experimental: {
    optimizeCss: true,
    optimizePackageImports: ['lucide-react', 'framer-motion'],
  },

  // Webpack optimization
  webpack: (config, { dev, isServer }) => {
    // Production optimizations
    if (!dev && !isServer) {
      config.optimization = {
        ...config.optimization,
        splitChunks: {
          chunks: 'all',
          cacheGroups: {
            default: false,
            vendors: false,
            // Vendor chunk
            vendor: {
              name: 'vendor',
              chunks: 'all',
              test: /node_modules/,
              priority: 20,
            },
            // Common chunk
            common: {
              name: 'common',
              minChunks: 2,
              chunks: 'all',
              priority: 10,
              reuseExistingChunk: true,
              enforce: true,
            },
            // Lightweight Charts (large library)
            charts: {
              name: 'charts',
              test: /[\\/]node_modules[\\/](lightweight-charts)[\\/]/,
              priority: 30,
            },
          },
        },
      };
    }

    return config;
  },

  // Headers for caching
  async headers() {
    return [
      {
        source: '/static/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
```

---

### 2. Code Splitting & Lazy Loading
```typescript
// app/layout.tsx
import dynamic from 'next/dynamic';

// Lazy load heavy components
const Chart = dynamic(() => import('@/components/Chart'), {
  loading: () => <LoadingSkeleton className="h-96" />,
  ssr: false, // Disable SSR for chart
});

const WebSocketProvider = dynamic(() => import('@/components/WebSocketProvider').then(mod => mod.WebSocketProvider), {
  ssr: false,
});

// Lazy load sounds (only when needed)
const soundManager = dynamic(() => import('@/lib/soundManager').then(mod => mod.soundManager), {
  ssr: false,
});
```

---

### 3. Image Optimization
```typescript
// components/OptimizedImage.tsx
import Image from 'next/image';

export function OptimizedImage({ src, alt, ...props }) {
  return (
    <Image
      src={src}
      alt={alt}
      loading="lazy"
      placeholder="blur"
      blurDataURL="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
      quality={85}
      {...props}
    />
  );
}
```

---

### 4. Bundle Analysis
```bash
# Install bundle analyzer
npm install --save-dev @next/bundle-analyzer

# Add to next.config.js
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
});

module.exports = withBundleAnalyzer(nextConfig);

# Run analysis
ANALYZE=true npm run build
```

---

### 5. React Query Optimization
```typescript
// lib/queryClient.ts
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Stale time: 5 minutes
      staleTime: 5 * 60 * 1000,
      
      // Cache time: 10 minutes
      cacheTime: 10 * 60 * 1000,
      
      // Refetch on window focus (only in production)
      refetchOnWindowFocus: process.env.NODE_ENV === 'production',
      
      // Retry failed requests
      retry: 2,
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      
      // Suspense mode
      suspense: false,
    },
  },
});
```

---

## 📊 ANALYTICS INTEGRATION

### 1. Google Analytics
```typescript
// lib/gtag.ts
export const GA_TRACKING_ID = process.env.NEXT_PUBLIC_GA_ID;

// Track page views
export const pageview = (url: string) => {
  if (!GA_TRACKING_ID) return;
  
  window.gtag('config', GA_TRACKING_ID, {
    page_path: url,
  });
};

// Track events
export const event = ({ action, category, label, value }: {
  action: string;
  category: string;
  label?: string;
  value?: number;
}) => {
  if (!GA_TRACKING_ID) return;
  
  window.gtag('event', action, {
    event_category: category,
    event_label: label,
    value: value,
  });
};

// Track custom events
export const trackPatternDetection = (symbol: string, pattern: string, confidence: number) => {
  event({
    action: 'pattern_detected',
    category: 'Trading',
    label: `${symbol} - ${pattern}`,
    value: Math.round(confidence * 100),
  });
};

export const trackTrade = (symbol: string, side: string, amount: number) => {
  event({
    action: 'trade_executed',
    category: 'Trading',
    label: `${side} ${symbol}`,
    value: amount,
  });
};

export const trackAlert = (symbol: string, pattern: string) => {
  event({
    action: 'alert_created',
    category: 'Alerts',
    label: `${symbol} - ${pattern}`,
  });
};
```

```typescript
// app/layout.tsx
import Script from 'next/script';
import { GA_TRACKING_ID } from '@/lib/gtag';

export default function RootLayout({ children }) {
  return (
    <html>
      <head>
        {/* Google Analytics */}
        {GA_TRACKING_ID && (
          <>
            <Script
              src={`https://www.googletagmanager.com/gtag/js?id=${GA_TRACKING_ID}`}
              strategy="afterInteractive"
            />
            <Script id="google-analytics" strategy="afterInteractive">
              {`
                window.dataLayer = window.dataLayer || [];
                function gtag(){dataLayer.push(arguments);}
                gtag('js', new Date());
                gtag('config', '${GA_TRACKING_ID}', {
                  page_path: window.location.pathname,
                });
              `}
            </Script>
          </>
        )}
      </head>
      <body>{children}</body>
    </html>
  );
}
```

---

### 2. Error Tracking (Sentry)
```bash
npm install @sentry/nextjs
```

```typescript
// sentry.client.config.ts
import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  
  // Performance monitoring
  tracesSampleRate: 0.1,
  
  // Session replay
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
  
  // Environment
  environment: process.env.NODE_ENV,
  
  // Ignore errors
  ignoreErrors: [
    'ResizeObserver loop limit exceeded',
    'Non-Error promise rejection captured',
  ],
  
  // Before send hook
  beforeSend(event, hint) {
    // Filter out non-critical errors
    if (event.level === 'warning') {
      return null;
    }
    return event;
  },
});
```

---

### 3. User Behavior Tracking
```typescript
// lib/analytics.ts
import { event } from './gtag';

export const analytics = {
  // Page views
  trackPageView: (pageName: string) => {
    event({
      action: 'page_view',
      category: 'Navigation',
      label: pageName,
    });
  },

  // Feature usage
  trackFeatureUsage: (feature: string) => {
    event({
      action: 'feature_used',
      category: 'Features',
      label: feature,
    });
  },

  // Mode selection
  trackModeSelection: (mode: 'hybrid_pro' | 'ai_elite') => {
    event({
      action: 'mode_selected',
      category: 'Settings',
      label: mode,
    });
  },

  // Scan initiated
  trackScan: (symbol: string, timeframe: string) => {
    event({
      action: 'scan_initiated',
      category: 'Trading',
      label: `${symbol} - ${timeframe}`,
    });
  },

  // Alert actions
  trackAlertAction: (action: 'dismiss' | 'trade' | 'view') => {
    event({
      action: `alert_${action}`,
      category: 'Alerts',
    });
  },

  // Performance metrics
  trackPerformance: (metric: string, value: number) => {
    event({
      action: 'performance_metric',
      category: 'Performance',
      label: metric,
      value: Math.round(value),
    });
  },
};
```

---

## 🔒 SECURITY BEST PRACTICES

### 1. API Key Protection
```typescript
// lib/api-service.ts
import axios from 'axios';

// Never expose API keys in frontend
// All sensitive keys should be on backend

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor (add auth token if needed)
api.interceptors.request.use(
  (config) => {
    // Add CSRF token if available
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    if (csrfToken) {
      config.headers['X-CSRF-Token'] = csrfToken;
    }
    
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor (handle errors)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle rate limiting
    if (error.response?.status === 429) {
      console.error('Rate limit exceeded');
      // Show user-friendly message
    }
    
    // Handle unauthorized
    if (error.response?.status === 401) {
      console.error('Unauthorized');
      // Redirect to login if needed
    }
    
    return Promise.reject(error);
  }
);

export { api };
```

---

### 2. Content Security Policy
```typescript
// next.config.js
const ContentSecurityPolicy = `
  default-src 'self';
  script-src 'self' 'unsafe-eval' 'unsafe-inline' https://www.googletagmanager.com https://cdn.jsdelivr.net;
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  font-src 'self' data:;
  connect-src 'self' https://tx-predictive-intelligence-latest.onrender.com wss://tx-predictive-intelligence-latest.onrender.com https://www.google-analytics.com;
  media-src 'self';
  frame-src 'none';
`;

const securityHeaders = [
  {
    key: 'Content-Security-Policy',
    value: ContentSecurityPolicy.replace(/\s{2,}/g, ' ').trim(),
  },
  {
    key: 'X-DNS-Prefetch-Control',
    value: 'on',
  },
  {
    key: 'Strict-Transport-Security',
    value: 'max-age=63072000; includeSubDomains; preload',
  },
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff',
  },
  {
    key: 'X-Frame-Options',
    value: 'DENY',
  },
  {
    key: 'X-XSS-Protection',
    value: '1; mode=block',
  },
  {
    key: 'Referrer-Policy',
    value: 'strict-origin-when-cross-origin',
  },
  {
    key: 'Permissions-Policy',
    value: 'camera=(), microphone=(), geolocation=()',
  },
];

module.exports = {
  async headers() {
    return [
      {
        source: '/:path*',
        headers: securityHeaders,
      },
    ];
  },
};
```

---

### 3. Input Sanitization
```typescript
// lib/sanitize.ts
import DOMPurify from 'isomorphic-dompurify';

export const sanitize = {
  // Sanitize HTML
  html: (dirty: string): string => {
    return DOMPurify.sanitize(dirty, {
      ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a'],
      ALLOWED_ATTR: ['href'],
    });
  },

  // Sanitize symbol input
  symbol: (input: string): string => {
    return input.toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 10);
  },

  // Sanitize numeric input
  number: (input: string): number => {
    const num = parseFloat(input);
    return isNaN(num) ? 0 : num;
  },
};
```

---

### 4. Rate Limiting (Client-Side)
```typescript
// lib/rateLimiter.ts
class RateLimiter {
  private requests: Map<string, number[]> = new Map();
  private limits: Map<string, { max: number; window: number }> = new Map();

  constructor() {
    // Define limits
    this.limits.set('scan', { max: 10, window: 60000 }); // 10 per minute
    this.limits.set('trade', { max: 5, window: 60000 }); // 5 per minute
    this.limits.set('alert', { max: 20, window: 60000 }); // 20 per minute
  }

  canMakeRequest(key: string): boolean {
    const limit = this.limits.get(key);
    if (!limit) return true;

    const now = Date.now();
    const requests = this.requests.get(key) || [];
    
    // Remove old requests outside window
    const validRequests = requests.filter(time => now - time < limit.window);
    
    if (validRequests.length >= limit.max) {
      return false;
    }

    // Add new request
    validRequests.push(now);
    this.requests.set(key, validRequests);
    
    return true;
  }

  getTimeUntilNextRequest(key: string): number {
    const limit = this.limits.get(key);
    if (!limit) return 0;

    const requests = this.requests.get(key) || [];
    if (requests.length < limit.max) return 0;

    const oldestRequest = requests[0];
    const timeElapsed = Date.now() - oldestRequest;
    
    return Math.max(0, limit.window - timeElapsed);
  }
}

export const rateLimiter = new RateLimiter();
```

---

## 🧪 TESTING STRATEGY

### 1. Unit Tests (Jest + React Testing Library)
```bash
npm install --save-dev jest @testing-library/react @testing-library/jest-dom
```

```typescript
// __tests__/components/AnimatedCounter.test.tsx
import { render, screen } from '@testing-library/react';
import { AnimatedCounter } from '@/components/AnimatedCounter';

describe('AnimatedCounter', () => {
  it('renders currency format correctly', () => {
    render(<AnimatedCounter value={1234.56} format="currency" />);
    expect(screen.getByText(/\$1,234\.56/)).toBeInTheDocument();
  });

  it('renders percentage format correctly', () => {
    render(<AnimatedCounter value={12.34} format="percentage" />);
    expect(screen.getByText(/12\.34%/)).toBeInTheDocument();
  });
});
```

---

### 2. Integration Tests
```typescript
// __tests__/integration/portfolio.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from '@/lib/queryClient';
import Portfolio from '@/app/portfolio/page';

describe('Portfolio Integration', () => {
  it('fetches and displays portfolio data', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <Portfolio />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/Portfolio Summary/i)).toBeInTheDocument();
    });
  });
});
```

---

### 3. E2E Tests (Playwright)
```bash
npm install --save-dev @playwright/test
```

```typescript
// e2e/scanner.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Pattern Scanner', () => {
  test('should scan symbol and display patterns', async ({ page }) => {
    await page.goto('/scanner');
    
    // Enter symbol
    await page.fill('input[placeholder*="symbol"]', 'AAPL');
    
    // Select timeframe
    await page.selectOption('select', '1h');
    
    // Click scan
    await page.click('button:has-text("Scan")');
    
    // Wait for results
    await page.waitForSelector('[data-testid="pattern-card"]', { timeout: 10000 });
    
    // Verify pattern displayed
    const patterns = await page.locator('[data-testid="pattern-card"]').count();
    expect(patterns).toBeGreaterThan(0);
  });
});
```

---

## 📋 PRE-LAUNCH CHECKLIST

### Performance
- [ ] Bundle size < 500KB (gzipped)
- [ ] First Contentful Paint < 1.5s
- [ ] Time to Interactive < 3s
- [ ] Lighthouse score > 90

### Security
- [ ] All API keys on backend
- [ ] CSP headers configured
- [ ] HTTPS enforced
- [ ] Input sanitization implemented

### Functionality
- [ ] All API endpoints tested
- [ ] WebSocket reconnection works
- [ ] Notifications working
- [ ] Sound effects playing
- [ ] Mobile responsive

### Analytics
- [ ] Google Analytics tracking
- [ ] Error tracking (Sentry)
- [ ] User behavior tracking

### SEO
- [ ] Meta tags configured
- [ ] Open Graph tags
- [ ] Sitemap generated
- [ ] Robots.txt configured

---

## ✅ PART 7 COMPLETE

Covered:
- ✅ Vercel & Netlify Deployment
- ✅ Performance Optimization (code splitting, lazy loading, bundle analysis)
- ✅ Analytics Integration (GA, Sentry, custom tracking)
- ✅ Security Best Practices (CSP, rate limiting, sanitization)
- ✅ Testing Strategy (unit, integration, E2E)
- ✅ Pre-Launch Checklist

---

## 🚀 READY FOR PART 8 (FINAL)?

**PART 8 will cover:**
- 📚 Complete Project Structure
- 🎯 Final Implementation Checklist
- 🚀 Quick Start Guide
- 💡 Pro Tips & Best Practices
- 🔧 Troubleshooting Guide

**Should I proceed with PART 8 (FINAL)?** 🎯
