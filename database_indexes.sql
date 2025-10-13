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
