-- ============================================
-- TX PREDICTIVE INTELLIGENCE - DATABASE INDEXES
-- Run this ONCE on your production database (Supabase)
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

-- Index for confidence filtering (high confidence patterns)
CREATE INDEX IF NOT EXISTS idx_pattern_detections_confidence 
ON pattern_detections(confidence DESC);

-- ============================================
-- ALERTS TABLE INDEXES
-- ============================================

-- Index for querying by symbol
CREATE INDEX IF NOT EXISTS idx_alerts_symbol 
ON alerts(symbol);

-- Index for querying by creation time (recent alerts)
CREATE INDEX IF NOT EXISTS idx_alerts_created_at 
ON alerts(created_at DESC);

-- Index for active alerts (most common query)
CREATE INDEX IF NOT EXISTS idx_alerts_active 
ON alerts(is_active, created_at DESC) 
WHERE is_active = true;

-- Index for alert type filtering
CREATE INDEX IF NOT EXISTS idx_alerts_type 
ON alerts(alert_type);

-- ============================================
-- PAPER_TRADES TABLE INDEXES
-- ============================================

-- Index for querying by symbol
CREATE INDEX IF NOT EXISTS idx_paper_trades_symbol 
ON paper_trades(symbol);

-- Index for querying by execution time
CREATE INDEX IF NOT EXISTS idx_paper_trades_executed_at 
ON paper_trades(executed_at DESC);

-- Index for status filtering (open/closed trades)
CREATE INDEX IF NOT EXISTS idx_paper_trades_status 
ON paper_trades(status);

-- Composite index for symbol + status (common query)
CREATE INDEX IF NOT EXISTS idx_paper_trades_symbol_status 
ON paper_trades(symbol, status);

-- ============================================
-- MODEL_PREDICTIONS TABLE INDEXES
-- ============================================

-- Index for querying by symbol
CREATE INDEX IF NOT EXISTS idx_model_predictions_symbol 
ON model_predictions(symbol);

-- Index for querying by prediction time
CREATE INDEX IF NOT EXISTS idx_model_predictions_predicted_at 
ON model_predictions(predicted_at DESC);

-- Composite index for symbol + time (common query)
CREATE INDEX IF NOT EXISTS idx_model_predictions_symbol_time 
ON model_predictions(symbol, predicted_at DESC);

-- Commit transaction
COMMIT;

-- ============================================
-- VERIFY INDEXES WERE CREATED
-- ============================================

SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
  AND tablename IN ('pattern_detections', 'alerts', 'paper_trades', 'model_predictions')
ORDER BY tablename, indexname;
