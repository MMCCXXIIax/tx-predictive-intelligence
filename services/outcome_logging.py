import os
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

import sqlalchemy as sa
from sqlalchemy import create_engine, text


def _build_engine_from_env():
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        return None
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    if db_url.startswith('postgresql://') and 'psycopg' not in db_url:
        db_url = db_url.replace('postgresql://', 'postgresql+psycopg://')
    # Hard disable prepared statements for PgBouncer
    connect_args = {'sslmode': 'require'} if db_url.startswith('postgresql') else {}
    if '+psycopg' in db_url:
        connect_args['prepare_threshold'] = None
    engine = create_engine(db_url, pool_pre_ping=True, pool_recycle=1800, connect_args=connect_args)
    return engine


_engine = _build_engine_from_env()


def ensure_tables():
    if _engine is None:
        return
    with _engine.begin() as conn:
        conn.execute(text(
            """
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
                metadata JSONB
            )
            """
        ))


def log_outcome(data: Dict[str, Any]) -> bool:
    """Insert a trade outcome row. Returns True if inserted."""
    if _engine is None:
        return False
    ensure_tables()
    with _engine.begin() as conn:
        conn.execute(text(
            """
            INSERT INTO trade_outcomes (symbol, pattern, entry_price, exit_price, pnl, quantity, timeframe, opened_at, closed_at, metadata)
            VALUES (:symbol, :pattern, :entry_price, :exit_price, :pnl, :quantity, :timeframe, :opened_at, :closed_at, CAST(:metadata AS JSONB))
            """
        ), {
            'symbol': data.get('symbol'),
            'pattern': data.get('pattern'),
            'entry_price': data.get('entry_price'),
            'exit_price': data.get('exit_price'),
            'pnl': data.get('pnl'),
            'quantity': data.get('quantity'),
            'timeframe': data.get('timeframe'),
            'opened_at': data.get('opened_at'),
            'closed_at': data.get('closed_at'),
            'metadata': (data.get('metadata') or '{}')
        })
    return True


def summarize_outcomes(window_days: int = 30, pattern: Optional[str] = None, symbol: Optional[str] = None) -> Dict[str, Any]:
    """Return rolling win-rate and aggregates from trade_outcomes."""
    if _engine is None:
        return {'available': False, 'by_pattern': [], 'by_symbol': []}
    ensure_tables()
    with _engine.begin() as conn:
        base_where = " closed_at > NOW() - INTERVAL :days::text || ' days' "
        params = {'days': str(int(window_days))}
        if pattern:
            base_where += " AND pattern = :pattern"
            params['pattern'] = pattern
        if symbol:
            base_where += " AND symbol = :symbol"
            params['symbol'] = symbol
        rows = conn.execute(text(
            f"""
            SELECT pattern,
                   COUNT(*) AS n,
                   AVG(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) AS win_rate,
                   AVG(pnl) AS avg_pnl
            FROM trade_outcomes
            WHERE {base_where}
            GROUP BY pattern
            ORDER BY n DESC
            """
        ), params).fetchall()
        by_pattern = [
            {'pattern': r.pattern, 'trades': int(r.n or 0), 'win_rate': float(r.win_rate or 0), 'avg_pnl': float(r.avg_pnl or 0)}
            for r in rows
        ]
        rows2 = conn.execute(text(
            f"""
            SELECT symbol,
                   COUNT(*) AS n,
                   AVG(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) AS win_rate,
                   AVG(pnl) AS avg_pnl
            FROM trade_outcomes
            WHERE {base_where}
            GROUP BY symbol
            ORDER BY n DESC
            LIMIT 25
            """
        ), params).fetchall()
        by_symbol = [
            {'symbol': r.symbol, 'trades': int(r.n or 0), 'win_rate': float(r.win_rate or 0), 'avg_pnl': float(r.avg_pnl or 0)}
            for r in rows2
        ]
        return {'available': True, 'by_pattern': by_pattern, 'by_symbol': by_symbol}
