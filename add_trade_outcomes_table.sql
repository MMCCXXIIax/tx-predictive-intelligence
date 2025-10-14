-- ============================================
-- ADD TRADE_OUTCOMES TABLE
-- Run this in Supabase SQL Editor
-- ============================================

BEGIN;

-- Create trade_outcomes table (for ML training)
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

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_trade_outcomes_symbol 
ON trade_outcomes(symbol);

CREATE INDEX IF NOT EXISTS idx_trade_outcomes_closed_at 
ON trade_outcomes(closed_at DESC);

CREATE INDEX IF NOT EXISTS idx_trade_outcomes_pattern 
ON trade_outcomes(pattern);

CREATE INDEX IF NOT EXISTS idx_trade_outcomes_symbol_closed 
ON trade_outcomes(symbol, closed_at DESC);

-- Enable RLS
ALTER TABLE trade_outcomes ENABLE ROW LEVEL SECURITY;

-- Create policy for service role
CREATE POLICY "Enable all access for service role" ON trade_outcomes
    FOR ALL USING (auth.role() = 'service_role');

COMMIT;

-- Verify table created
SELECT 
    table_name,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_name = 'trade_outcomes'
ORDER BY ordinal_position;
