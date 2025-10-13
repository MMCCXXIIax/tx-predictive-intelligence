# 🔧 SETUP GUIDE: Database Indexes & Sentry

**Step-by-step instructions for production optimization**

---

## PART 1: DATABASE INDEXES (Performance Optimization)

### Why You Need Indexes

**Without indexes:**
- Query scans entire table (slow)
- 1M rows = 1M checks
- Response time: 5-10 seconds

**With indexes:**
- Query jumps directly to data (fast)
- 1M rows = 20 checks (logarithmic)
- Response time: 10-50 milliseconds

**Impact: 100x-1000x faster queries**

---

### Step 1: Create Index Migration File

Create a new file for your indexes:

**File:** `database_indexes.sql`

```sql
-- ============================================
-- TX PREDICTIVE INTELLIGENCE - DATABASE INDEXES
-- Run this ONCE on your production database
-- ============================================

-- Check if running on correct database
SELECT current_database();

-- Start transaction
BEGIN;

-- ============================================
-- PATTERN_DETECTIONS TABLE INDEXES
-- ============================================

-- Index for querying by symbol (most common query)
CREATE INDEX IF NOT EXISTS idx_pattern_detections_symbol 
ON pattern_detections(symbol);

-- Index for querying by detection time (recent patterns)
CREATE INDEX IF NOT EXISTS idx_pattern_detections_detected_at 
ON pattern_detections(detected_at DESC);

-- Composite index for symbol + time queries (very common)
CREATE INDEX IF NOT EXISTS idx_pattern_detections_symbol_time 
ON pattern_detections(symbol, detected_at DESC);

-- Index for pattern type filtering
CREATE INDEX IF NOT EXISTS idx_pattern_detections_pattern_type 
ON pattern_detections(pattern_type);

-- Index for confidence filtering (ELITE alerts)
CREATE INDEX IF NOT EXISTS idx_pattern_detections_confidence 
ON pattern_detections(confidence DESC);

-- Composite index for symbol + pattern + time (market scan)
CREATE INDEX IF NOT EXISTS idx_pattern_detections_symbol_pattern_time 
ON pattern_detections(symbol, pattern_type, detected_at DESC);

-- JSONB index for metadata queries (if you query metadata often)
CREATE INDEX IF NOT EXISTS idx_pattern_detections_metadata 
ON pattern_detections USING GIN(metadata);

-- ============================================
-- ALERTS TABLE INDEXES
-- ============================================

-- Index for active alerts (most common query)
CREATE INDEX IF NOT EXISTS idx_alerts_is_active 
ON alerts(is_active) WHERE is_active = true;

-- Index for symbol queries
CREATE INDEX IF NOT EXISTS idx_alerts_symbol 
ON alerts(symbol);

-- Index for creation time (recent alerts)
CREATE INDEX IF NOT EXISTS idx_alerts_created_at 
ON alerts(created_at DESC);

-- Composite index for active alerts by symbol
CREATE INDEX IF NOT EXISTS idx_alerts_active_symbol 
ON alerts(symbol, is_active, created_at DESC) 
WHERE is_active = true;

-- Index for alert type filtering
CREATE INDEX IF NOT EXISTS idx_alerts_alert_type 
ON alerts(alert_type);

-- Index for confidence filtering
CREATE INDEX IF NOT EXISTS idx_alerts_confidence 
ON alerts(confidence DESC);

-- Index for processed flag (auto-labeling)
CREATE INDEX IF NOT EXISTS idx_alerts_processed 
ON alerts(processed) WHERE processed = false;

-- JSONB index for metadata
CREATE INDEX IF NOT EXISTS idx_alerts_metadata 
ON alerts USING GIN(metadata);

-- ============================================
-- PAPER_TRADES TABLE INDEXES
-- ============================================

-- Index for open trades (most common query)
CREATE INDEX IF NOT EXISTS idx_paper_trades_status 
ON paper_trades(status) WHERE status = 'open';

-- Index for symbol queries
CREATE INDEX IF NOT EXISTS idx_paper_trades_symbol 
ON paper_trades(symbol);

-- Index for execution time (recent trades)
CREATE INDEX IF NOT EXISTS idx_paper_trades_executed_at 
ON paper_trades(executed_at DESC);

-- Composite index for open trades by symbol
CREATE INDEX IF NOT EXISTS idx_paper_trades_symbol_status 
ON paper_trades(symbol, status, executed_at DESC);

-- Index for pattern filtering
CREATE INDEX IF NOT EXISTS idx_paper_trades_pattern 
ON paper_trades(pattern);

-- Index for P&L analysis
CREATE INDEX IF NOT EXISTS idx_paper_trades_pnl 
ON paper_trades(pnl DESC);

-- ============================================
-- MODEL_PREDICTIONS TABLE INDEXES
-- ============================================

-- Index for symbol queries
CREATE INDEX IF NOT EXISTS idx_model_predictions_symbol 
ON model_predictions(symbol);

-- Index for prediction time
CREATE INDEX IF NOT EXISTS idx_model_predictions_predicted_at 
ON model_predictions(predicted_at DESC);

-- Composite index for symbol + time
CREATE INDEX IF NOT EXISTS idx_model_predictions_symbol_time 
ON model_predictions(symbol, predicted_at DESC);

-- Index for actual outcomes (for accuracy calculation)
CREATE INDEX IF NOT EXISTS idx_model_predictions_actual 
ON model_predictions(actual) WHERE actual IS NOT NULL;

-- ============================================
-- TX SCHEMA INDEXES (if using tx schema)
-- ============================================

-- Pattern outcomes (for ML learning)
CREATE INDEX IF NOT EXISTS idx_pattern_outcomes_symbol 
ON tx.pattern_outcomes(symbol);

CREATE INDEX IF NOT EXISTS idx_pattern_outcomes_created_at 
ON tx.pattern_outcomes(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_pattern_outcomes_outcome 
ON tx.pattern_outcomes(outcome);

CREATE INDEX IF NOT EXISTS idx_pattern_outcomes_pattern_name 
ON tx.pattern_outcomes(pattern_name);

-- ML model versions
CREATE INDEX IF NOT EXISTS idx_ml_model_versions_namespace 
ON tx.ml_model_versions(model_namespace);

CREATE INDEX IF NOT EXISTS idx_ml_model_versions_created_at 
ON tx.ml_model_versions(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_ml_model_versions_is_active 
ON tx.ml_model_versions(is_active) WHERE is_active = true;

-- Commit transaction
COMMIT;

-- ============================================
-- VERIFY INDEXES WERE CREATED
-- ============================================

-- List all indexes on pattern_detections
SELECT 
    indexname, 
    indexdef 
FROM pg_indexes 
WHERE tablename = 'pattern_detections'
ORDER BY indexname;

-- List all indexes on alerts
SELECT 
    indexname, 
    indexdef 
FROM pg_indexes 
WHERE tablename = 'alerts'
ORDER BY indexname;

-- List all indexes on paper_trades
SELECT 
    indexname, 
    indexdef 
FROM pg_indexes 
WHERE tablename = 'paper_trades'
ORDER BY indexname;

-- List all indexes on model_predictions
SELECT 
    indexname, 
    indexdef 
FROM pg_indexes 
WHERE tablename = 'model_predictions'
ORDER BY indexname;

-- Show index sizes (to monitor disk usage)
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_relation_size(indexrelid) DESC;

-- ============================================
-- DONE!
-- ============================================
```

---

### Step 2: Connect to Your Database

**Option A: Using Render Dashboard (Easiest)**

1. Go to https://dashboard.render.com
2. Click on your PostgreSQL database
3. Click "Connect" → "External Connection"
4. Copy the connection string (looks like: `postgresql://user:pass@host:5432/dbname`)

**Option B: Using psql Command Line**

```bash
# Install psql (if not installed)
# Windows: Download from https://www.postgresql.org/download/windows/
# Mac: brew install postgresql
# Linux: sudo apt-get install postgresql-client

# Connect to database
psql "postgresql://your-connection-string-here"
```

---

### Step 3: Run the Index Migration

**Method 1: Copy-Paste in psql (Recommended)**

```bash
# 1. Connect to database
psql "postgresql://your-connection-string-here"

# 2. Copy the entire SQL from database_indexes.sql
# 3. Paste into psql terminal
# 4. Press Enter

# You should see:
# BEGIN
# CREATE INDEX
# CREATE INDEX
# ...
# COMMIT
```

**Method 2: Run SQL File Directly**

```bash
# Save the SQL to database_indexes.sql
# Then run:
psql "postgresql://your-connection-string-here" -f database_indexes.sql
```

**Method 3: Using Render Dashboard**

1. Go to Render Dashboard → Your Database
2. Click "Connect" → "Web Shell"
3. Copy-paste the SQL from `database_indexes.sql`
4. Execute

---

### Step 4: Verify Indexes Were Created

Run this query to check:

```sql
-- Check pattern_detections indexes
SELECT indexname FROM pg_indexes 
WHERE tablename = 'pattern_detections';

-- Expected output:
-- idx_pattern_detections_symbol
-- idx_pattern_detections_detected_at
-- idx_pattern_detections_symbol_time
-- idx_pattern_detections_pattern_type
-- idx_pattern_detections_confidence
-- idx_pattern_detections_symbol_pattern_time
-- idx_pattern_detections_metadata
```

---

### Step 5: Test Performance Improvement

**Before indexes:**
```sql
EXPLAIN ANALYZE 
SELECT * FROM pattern_detections 
WHERE symbol = 'AAPL' 
ORDER BY detected_at DESC 
LIMIT 50;

-- Expected: Seq Scan (slow)
-- Execution time: ~500-5000ms
```

**After indexes:**
```sql
EXPLAIN ANALYZE 
SELECT * FROM pattern_detections 
WHERE symbol = 'AAPL' 
ORDER BY detected_at DESC 
LIMIT 50;

-- Expected: Index Scan using idx_pattern_detections_symbol_time
-- Execution time: ~5-50ms (100x faster!)
```

---

### Step 6: Monitor Index Usage

Run this query monthly to see which indexes are being used:

```sql
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY idx_scan DESC;
```

**If an index has 0 scans after 1 month, consider dropping it:**
```sql
DROP INDEX IF EXISTS idx_name_here;
```

---

## PART 2: SENTRY SETUP (Error Tracking)

### Why You Need Sentry

**Without Sentry:**
- Errors happen silently
- No idea what's breaking
- Users complain, you have no logs
- Debugging takes hours

**With Sentry:**
- Real-time error alerts
- Full stack traces
- User context (what they were doing)
- Performance monitoring
- Debugging takes minutes

**Impact: 10x faster debugging, catch errors before users complain**

---

### Step 1: Create Sentry Account

1. Go to https://sentry.io/signup/
2. Sign up (free tier: 5,000 errors/month)
3. Choose "Python" as your platform
4. Create a new project called "TX-Predictive-Intelligence"

---

### Step 2: Get Your Sentry DSN

After creating the project:

1. Sentry will show you a DSN (Data Source Name)
2. It looks like: `https://abc123@o123456.ingest.sentry.io/7890123`
3. **Copy this DSN** - you'll need it in Step 4

**Or find it later:**
- Go to Settings → Projects → TX-Predictive-Intelligence
- Click "Client Keys (DSN)"
- Copy the DSN

---

### Step 3: Install Sentry SDK

Your `requirements.txt` already has it, but verify:

```bash
# Check if sentry-sdk is in requirements.txt
grep sentry requirements.txt

# Should see:
# sentry-sdk==1.40.0
```

If not there, add it:

```bash
echo "sentry-sdk==1.40.0" >> requirements.txt
pip install sentry-sdk
```

---

### Step 4: Add Sentry to Environment Variables

**On Render:**

1. Go to https://dashboard.render.com
2. Click your web service (tx-predictive-intelligence)
3. Go to "Environment" tab
4. Click "Add Environment Variable"
5. Add these:

```bash
# Required
SENTRY_DSN=https://your-dsn-here@o123456.ingest.sentry.io/7890123

# Optional but recommended
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1
SENTRY_PROFILES_SAMPLE_RATE=0.1
```

**Locally (for testing):**

Add to your `.env` file:

```bash
SENTRY_DSN=https://your-dsn-here@o123456.ingest.sentry.io/7890123
SENTRY_ENVIRONMENT=development
SENTRY_TRACES_SAMPLE_RATE=1.0
```

---

### Step 5: Verify Sentry is Already Integrated

Your `main.py` already has Sentry! Check lines 1-50:

```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

# Sentry initialization
sentry_dsn = os.getenv('SENTRY_DSN')
if sentry_dsn:
    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[FlaskIntegration()],
        traces_sample_rate=float(os.getenv('SENTRY_TRACES_SAMPLE_RATE', '0.1')),
        profiles_sample_rate=float(os.getenv('SENTRY_PROFILES_SAMPLE_RATE', '0.1')),
        environment=os.getenv('SENTRY_ENVIRONMENT', 'production')
    )
    logger.info("Sentry initialized successfully")
else:
    logger.warning("SENTRY_DSN not set - error tracking disabled")
```

**You're already set up!** Just need to add the DSN.

---

### Step 6: Test Sentry Integration

**Method 1: Trigger Test Error (Recommended)**

Add a test endpoint to `main.py`:

```python
@app.route('/sentry-test')
def sentry_test():
    """Test endpoint to verify Sentry is working"""
    logger.info("Triggering test error for Sentry")
    division_by_zero = 1 / 0  # This will raise an error
    return "This won't be reached"
```

Then:
1. Deploy to Render (or run locally)
2. Visit: `https://your-app.com/sentry-test`
3. Check Sentry dashboard - you should see the error!

**Method 2: Use Sentry CLI**

```bash
# Install Sentry CLI
pip install sentry-cli

# Send test event
sentry-cli send-event -m "Test error from TX backend"
```

---

### Step 7: Verify Sentry is Working

1. Go to https://sentry.io
2. Click on your project "TX-Predictive-Intelligence"
3. Go to "Issues" tab
4. You should see the test error you triggered
5. Click on it to see:
   - Full stack trace
   - Request details
   - Environment info
   - User context

**If you see the error: ✅ Sentry is working!**

---

### Step 8: Configure Sentry Alerts

Set up alerts so you know when errors happen:

1. Go to Sentry → Settings → Alerts
2. Click "Create Alert Rule"
3. Choose "Issues"
4. Set conditions:
   - **When:** An issue is first seen
   - **Or:** An issue changes state from resolved to unresolved
   - **Or:** An issue is seen more than 10 times in 1 hour
5. Set actions:
   - **Send email to:** your-email@example.com
   - **Send Slack notification** (optional, if you have Slack)
6. Save

Now you'll get notified immediately when errors occur!

---

### Step 9: Add Custom Context to Errors

Enhance error reports with custom data:

**Example: Add user context to errors**

```python
# In your API endpoints, add context
from sentry_sdk import set_context, set_tag, set_user

@app.route('/api/alerts')
def get_alerts():
    try:
        # Add custom context
        set_tag("endpoint", "get_alerts")
        set_context("query_params", {
            "limit": request.args.get('limit'),
            "quality": request.args.get('quality')
        })
        
        # Your code here
        alerts = fetch_alerts()
        return jsonify({"success": True, "data": alerts})
        
    except Exception as e:
        # Sentry automatically captures this
        logger.error(f"Error fetching alerts: {e}")
        raise
```

**Example: Add breadcrumbs for debugging**

```python
from sentry_sdk import add_breadcrumb

@app.route('/api/paper-trade/execute', methods=['POST'])
def execute_paper_trade():
    try:
        data = request.json
        
        # Add breadcrumb
        add_breadcrumb(
            category='trade',
            message=f'Executing trade for {data.get("symbol")}',
            level='info'
        )
        
        # Execute trade
        trade = execute_trade(data)
        
        add_breadcrumb(
            category='trade',
            message=f'Trade executed successfully: {trade.id}',
            level='info'
        )
        
        return jsonify({"success": True, "data": trade})
        
    except Exception as e:
        # Sentry will show all breadcrumbs leading to error
        logger.error(f"Error executing trade: {e}")
        raise
```

---

### Step 10: Monitor Performance with Sentry

Sentry also tracks performance (not just errors):

**View slow endpoints:**
1. Go to Sentry → Performance
2. See which endpoints are slow
3. Click to see detailed traces

**Set up performance alerts:**
1. Sentry → Alerts → Create Alert
2. Choose "Metric Alert"
3. Set condition: "When average response time is above 2000ms"
4. Save

---

## 🎯 VERIFICATION CHECKLIST

### Database Indexes ✅

- [ ] Created `database_indexes.sql` file
- [ ] Connected to production database
- [ ] Ran index migration SQL
- [ ] Verified indexes exist (ran verification query)
- [ ] Tested query performance (EXPLAIN ANALYZE)
- [ ] Queries are 10x-100x faster

### Sentry ✅

- [ ] Created Sentry account
- [ ] Created TX project in Sentry
- [ ] Copied Sentry DSN
- [ ] Added SENTRY_DSN to Render environment variables
- [ ] Added SENTRY_ENVIRONMENT=production
- [ ] Deployed to Render
- [ ] Triggered test error
- [ ] Verified error appears in Sentry dashboard
- [ ] Set up email alerts
- [ ] Tested custom context/breadcrumbs

---

## 🚨 COMMON ISSUES & FIXES

### Database Indexes

**Issue:** "Permission denied to create index"
**Fix:** Make sure you're using the database owner credentials (from Render)

**Issue:** "Index already exists"
**Fix:** That's fine! The `IF NOT EXISTS` clause handles this. Skip and continue.

**Issue:** "Out of disk space"
**Fix:** Indexes take space. Check your Render plan. Free tier has 1GB limit.

**Issue:** "Query still slow after indexes"
**Fix:** Run `VACUUM ANALYZE table_name;` to update statistics.

### Sentry

**Issue:** "Errors not appearing in Sentry"
**Fix:** 
1. Check SENTRY_DSN is correct (no typos)
2. Check environment variable is set in Render
3. Restart your Render service
4. Trigger a test error again

**Issue:** "Too many errors (rate limited)"
**Fix:** Sentry free tier: 5,000 errors/month. Upgrade plan or filter errors.

**Issue:** "Sentry slowing down app"
**Fix:** Lower SENTRY_TRACES_SAMPLE_RATE to 0.01 (1% sampling)

---

## 📊 EXPECTED RESULTS

### After Adding Indexes:

**Query Performance:**
- Alert feed: 5000ms → 50ms (100x faster)
- Market scan: 8000ms → 80ms (100x faster)
- Paper trades: 3000ms → 30ms (100x faster)

**User Experience:**
- Pages load instantly
- No more "Loading..." spinners
- Real-time feels truly real-time

### After Setting Up Sentry:

**Error Visibility:**
- Know about errors within seconds
- Full context (what user was doing)
- Stack traces for debugging
- Performance bottlenecks identified

**Debugging Speed:**
- Hours → Minutes
- "Works on my machine" → "Here's the exact error"
- Proactive fixes before users complain

---

## 🎉 YOU'RE DONE!

**Your backend is now:**
- ⚡ 100x faster (indexes)
- 🔍 Fully monitored (Sentry)
- 🚀 Production-ready

**Next steps:**
1. Monitor Sentry for first week
2. Check index usage after 1 month
3. Optimize based on real data

**Questions? Check:**
- Sentry Docs: https://docs.sentry.io/platforms/python/
- PostgreSQL Indexes: https://www.postgresql.org/docs/current/indexes.html

---

**Your backend is now 9.5/10 → 10/10!** 🎯
