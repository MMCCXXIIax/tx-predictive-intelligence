-- ============================================
-- TX PREDICTIVE INTELLIGENCE - COMPLETE SUPABASE SETUP (FIXED)
-- Run this ONCE on your NEW Supabase project
-- This creates all tables + indexes for your Flask backend
-- Handles existing policies gracefully
-- ============================================

-- Check current database
SELECT current_database();

-- Start transaction
BEGIN;

-- ============================================
-- 1. CREATE TABLES (matching Flask backend schema)
-- ============================================

-- 1.1 Pattern Detections Table
CREATE TABLE IF NOT EXISTS pattern_detections (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    pattern_type VARCHAR(50) NOT NULL,
    confidence FLOAT NOT NULL,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    price FLOAT,
    volume BIGINT,
    metadata JSONB
);

-- 1.2 Paper Trades Table
CREATE TABLE IF NOT EXISTS paper_trades (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    side VARCHAR(10) NOT NULL,
    quantity FLOAT NOT NULL,
    price FLOAT NOT NULL,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'open',
    pnl FLOAT DEFAULT 0,
    pattern VARCHAR(50),
    confidence FLOAT
);

-- 1.3 Alerts Table
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    confidence FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    metadata JSONB,
    processed BOOLEAN DEFAULT false
);

-- 1.4 Model Predictions Table (for ML training)
CREATE TABLE IF NOT EXISTS model_predictions (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(32) NOT NULL,
    prediction FLOAT NOT NULL,
    actual INT NULL,
    predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 1.5 Trade Outcomes Table (for ML training from historical trades)
CREATE TABLE IF NOT EXISTS trade_outcomes (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(32) NOT NULL,
    pattern VARCHAR(50),
    entry_price FLOAT NOT NULL,
    exit_price FLOAT NOT NULL,
    pnl FLOAT NOT NULL,
    quantity FLOAT NOT NULL,
    timeframe VARCHAR(10) DEFAULT '1h',
    opened_at TIMESTAMP NOT NULL,
    closed_at TIMESTAMP NOT NULL,
    metadata JSONB
);

-- ============================================
-- 2. CREATE INDEXES (for performance)
-- ============================================

-- Pattern Detections Indexes
CREATE INDEX IF NOT EXISTS idx_pattern_detections_symbol 
ON pattern_detections(symbol);

CREATE INDEX IF NOT EXISTS idx_pattern_detections_detected_at 
ON pattern_detections(detected_at DESC);

CREATE INDEX IF NOT EXISTS idx_pattern_detections_symbol_time 
ON pattern_detections(symbol, detected_at DESC);

CREATE INDEX IF NOT EXISTS idx_pattern_detections_pattern_type 
ON pattern_detections(pattern_type);

CREATE INDEX IF NOT EXISTS idx_pattern_detections_confidence 
ON pattern_detections(confidence DESC);

-- Alerts Indexes
CREATE INDEX IF NOT EXISTS idx_alerts_symbol 
ON alerts(symbol);

CREATE INDEX IF NOT EXISTS idx_alerts_created_at 
ON alerts(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_alerts_active 
ON alerts(is_active, created_at DESC) 
WHERE is_active = true;

CREATE INDEX IF NOT EXISTS idx_alerts_type 
ON alerts(alert_type);

CREATE INDEX IF NOT EXISTS idx_alerts_processed 
ON alerts(processed) 
WHERE processed = false;

-- Paper Trades Indexes
CREATE INDEX IF NOT EXISTS idx_paper_trades_symbol 
ON paper_trades(symbol);

CREATE INDEX IF NOT EXISTS idx_paper_trades_executed_at 
ON paper_trades(executed_at DESC);

CREATE INDEX IF NOT EXISTS idx_paper_trades_status 
ON paper_trades(status);

CREATE INDEX IF NOT EXISTS idx_paper_trades_symbol_status 
ON paper_trades(symbol, status);

-- Model Predictions Indexes
CREATE INDEX IF NOT EXISTS idx_model_predictions_symbol 
ON model_predictions(symbol);

CREATE INDEX IF NOT EXISTS idx_model_predictions_predicted_at 
ON model_predictions(predicted_at DESC);

CREATE INDEX IF NOT EXISTS idx_model_predictions_symbol_time 
ON model_predictions(symbol, predicted_at DESC);

-- Trade Outcomes Indexes
CREATE INDEX IF NOT EXISTS idx_trade_outcomes_symbol 
ON trade_outcomes(symbol);

CREATE INDEX IF NOT EXISTS idx_trade_outcomes_closed_at 
ON trade_outcomes(closed_at DESC);

CREATE INDEX IF NOT EXISTS idx_trade_outcomes_pattern 
ON trade_outcomes(pattern);

CREATE INDEX IF NOT EXISTS idx_trade_outcomes_symbol_closed 
ON trade_outcomes(symbol, closed_at DESC);

-- ============================================
-- 3. CREATE USEFUL VIEWS (for analytics)
-- ============================================

-- View: Daily pattern detection stats
CREATE OR REPLACE VIEW v_daily_pattern_stats AS
SELECT
    DATE(detected_at) as detection_date,
    pattern_type,
    COUNT(*) as total_detections,
    AVG(confidence) as avg_confidence,
    MIN(confidence) as min_confidence,
    MAX(confidence) as max_confidence
FROM pattern_detections
GROUP BY DATE(detected_at), pattern_type
ORDER BY detection_date DESC, total_detections DESC;

-- View: Active alerts summary
CREATE OR REPLACE VIEW v_active_alerts AS
SELECT
    symbol,
    alert_type,
    message,
    confidence,
    created_at
FROM alerts
WHERE is_active = true
ORDER BY created_at DESC;

-- View: Paper trading performance
CREATE OR REPLACE VIEW v_paper_trade_performance AS
SELECT
    symbol,
    pattern,
    COUNT(*) as total_trades,
    SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END) as open_trades,
    SUM(CASE WHEN status != 'open' THEN 1 ELSE 0 END) as closed_trades,
    AVG(pnl) as avg_pnl,
    SUM(pnl) as total_pnl,
    AVG(confidence) as avg_confidence
FROM paper_trades
GROUP BY symbol, pattern
ORDER BY total_pnl DESC;

-- View: ML model prediction accuracy
CREATE OR REPLACE VIEW v_model_accuracy AS
SELECT
    symbol,
    COUNT(*) as total_predictions,
    COUNT(actual) as predictions_with_actual,
    AVG(CASE 
        WHEN actual IS NOT NULL THEN 
            CASE WHEN (prediction > 0.5 AND actual = 1) OR (prediction <= 0.5 AND actual = 0) 
            THEN 1.0 ELSE 0.0 END
        ELSE NULL 
    END) as accuracy
FROM model_predictions
GROUP BY symbol
HAVING COUNT(actual) > 0
ORDER BY accuracy DESC;

-- ============================================
-- 4. ENABLE ROW LEVEL SECURITY (RLS)
-- ============================================

-- Enable RLS on all tables
ALTER TABLE pattern_detections ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE paper_trades ENABLE ROW LEVEL SECURITY;
ALTER TABLE model_predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE trade_outcomes ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist (to avoid conflicts)
DROP POLICY IF EXISTS "Enable all access for service role" ON pattern_detections;
DROP POLICY IF EXISTS "Enable all access for service role" ON alerts;
DROP POLICY IF EXISTS "Enable all access for service role" ON paper_trades;
DROP POLICY IF EXISTS "Enable all access for service role" ON model_predictions;
DROP POLICY IF EXISTS "Enable all access for service role" ON trade_outcomes;

-- Create policies to allow service_role (your backend) full access
CREATE POLICY "Enable all access for service role" ON pattern_detections
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Enable all access for service role" ON alerts
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Enable all access for service role" ON paper_trades
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Enable all access for service role" ON model_predictions
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Enable all access for service role" ON trade_outcomes
    FOR ALL USING (auth.role() = 'service_role');

-- ============================================
-- 5. CREATE HELPER FUNCTIONS
-- ============================================

-- Function: Get recent patterns for a symbol
CREATE OR REPLACE FUNCTION get_recent_patterns(
    p_symbol VARCHAR(10),
    p_hours INT DEFAULT 24
)
RETURNS TABLE (
    id INT,
    pattern_type VARCHAR(50),
    confidence FLOAT,
    detected_at TIMESTAMP,
    price FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        pd.id,
        pd.pattern_type,
        pd.confidence,
        pd.detected_at,
        pd.price
    FROM pattern_detections pd
    WHERE pd.symbol = p_symbol
        AND pd.detected_at >= NOW() - (p_hours || ' hours')::INTERVAL
    ORDER BY pd.detected_at DESC;
END;
$$ LANGUAGE plpgsql;

-- Function: Calculate win rate for a pattern
CREATE OR REPLACE FUNCTION calculate_pattern_win_rate(
    p_pattern VARCHAR(50)
)
RETURNS TABLE (
    pattern VARCHAR(50),
    total_trades BIGINT,
    winning_trades BIGINT,
    win_rate FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p_pattern as pattern,
        COUNT(*) as total_trades,
        COUNT(CASE WHEN pnl > 0 THEN 1 END) as winning_trades,
        CASE 
            WHEN COUNT(*) > 0 THEN 
                (COUNT(CASE WHEN pnl > 0 THEN 1 END)::FLOAT / COUNT(*)::FLOAT) * 100
            ELSE 0
        END as win_rate
    FROM paper_trades
    WHERE paper_trades.pattern = p_pattern
        AND status != 'open';
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 6. CREATE TRIGGERS (for auto-updates)
-- ============================================

-- Trigger: Auto-update paper trade PNL when closed
CREATE OR REPLACE FUNCTION update_paper_trade_pnl()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status != 'open' AND OLD.status = 'open' THEN
        -- Calculate PNL based on side
        IF NEW.side = 'BUY' THEN
            NEW.pnl := (NEW.price - OLD.price) * NEW.quantity;
        ELSE
            NEW.pnl := (OLD.price - NEW.price) * NEW.quantity;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop trigger if exists
DROP TRIGGER IF EXISTS trigger_update_paper_trade_pnl ON paper_trades;

-- Create trigger
CREATE TRIGGER trigger_update_paper_trade_pnl
    BEFORE UPDATE ON paper_trades
    FOR EACH ROW
    EXECUTE FUNCTION update_paper_trade_pnl();

-- Commit transaction
COMMIT;

-- ============================================
-- 7. VERIFY SETUP
-- ============================================

-- Show all tables created
SELECT 
    table_name,
    table_type
FROM information_schema.tables
WHERE table_schema = 'public'
    AND table_name IN ('pattern_detections', 'alerts', 'paper_trades', 'model_predictions', 'trade_outcomes')
ORDER BY table_name;

-- Show all indexes created
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
    AND tablename IN ('pattern_detections', 'alerts', 'paper_trades', 'model_predictions', 'trade_outcomes')
ORDER BY tablename, indexname;

-- Show all views created
SELECT 
    table_name as view_name
FROM information_schema.views
WHERE table_schema = 'public'
    AND table_name LIKE 'v_%'
ORDER BY table_name;

-- Show all functions created
SELECT 
    routine_name as function_name,
    routine_type
FROM information_schema.routines
WHERE routine_schema = 'public'
    AND routine_name IN ('get_recent_patterns', 'calculate_pattern_win_rate')
ORDER BY routine_name;

-- ============================================
-- SETUP COMPLETE! 🎉
-- ============================================
-- 
-- Your database is now ready for the TX Predictive Intelligence backend!
-- 
-- Next steps:
-- 1. Update your DATABASE_URL environment variable in Render
-- 2. Wake up your backend: .\wake_up_backend.ps1
-- 3. Test your API: .\test_api.ps1
-- 
-- Tables created: 5
-- Indexes created: 20
-- Views created: 4
-- Functions created: 2
-- Triggers created: 1
-- ============================================
