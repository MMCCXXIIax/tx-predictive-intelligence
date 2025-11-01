-- TX Predictive Intelligence - Database Initialization
-- Run this SQL script on your Render PostgreSQL database

-- Create trade_outcomes table
CREATE TABLE IF NOT EXISTS trade_outcomes (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    pattern VARCHAR(64),
    entry_price FLOAT,
    exit_price FLOAT,
    pnl FLOAT,
    quantity FLOAT,
    timeframe VARCHAR(16),
    opened_at TIMESTAMP,
    closed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB,
    
    -- Indexes for better query performance
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_trade_outcomes_symbol ON trade_outcomes(symbol);
CREATE INDEX IF NOT EXISTS idx_trade_outcomes_pattern ON trade_outcomes(pattern);
CREATE INDEX IF NOT EXISTS idx_trade_outcomes_closed_at ON trade_outcomes(closed_at);
CREATE INDEX IF NOT EXISTS idx_trade_outcomes_pnl ON trade_outcomes(pnl);

-- Create trade_journal table (for AI Trading Journal feature)
CREATE TABLE IF NOT EXISTS trade_journal (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL DEFAULT 'default',
    symbol VARCHAR(20) NOT NULL,
    pattern VARCHAR(64),
    entry_price FLOAT,
    exit_price FLOAT,
    pnl FLOAT,
    outcome VARCHAR(20),
    emotion VARCHAR(50),
    lesson TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_trade_journal_user_id ON trade_journal(user_id);
CREATE INDEX IF NOT EXISTS idx_trade_journal_symbol ON trade_journal(symbol);
CREATE INDEX IF NOT EXISTS idx_trade_journal_created_at ON trade_journal(created_at);

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'TX Predictive Intelligence database tables created successfully!';
END $$;
