import os
import math
import time
import random
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import yfinance as yf
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from joblib import dump, load

import sqlalchemy as sa
from sqlalchemy import create_engine, text
from zoneinfo import ZoneInfo

# Base models directory; segmented models are stored under models/<asset_class>/<timeframe>/<regime>/
MODEL_BASE = os.path.join(os.getcwd(), 'models')


def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def _asset_class(symbol: str) -> str:
    s = (symbol or '').upper()
    if s.endswith('=X') or '/' in s:
        return 'fx'
    if '-USD' in s or s in {'BTC', 'ETH', 'BTCUSD', 'ETHUSD', 'BTC-USD', 'ETH-USD'}:
        return 'crypto'
    return 'equity'


def _model_path(asset: str, timeframe: str, regime: str = 'all') -> str:
    d = os.path.join(MODEL_BASE, asset, timeframe, regime)
    _ensure_dir(d)
    return os.path.join(d, 'model_ml_patterns.pkl')


def _model_path_pattern(asset: str, timeframe: str, pattern: str, regime: str = 'all') -> str:
    safe_pat = (pattern or 'UNKNOWN').replace('/', '_').replace(' ', '_')
    d = os.path.join(MODEL_BASE, asset, timeframe, safe_pat, regime)
    _ensure_dir(d)
    return os.path.join(d, 'model_ml_patterns.pkl')


def _get_engine() -> Optional[sa.Engine]:
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        return None
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    if db_url.startswith('postgresql://') and 'psycopg' not in db_url:
        db_url = db_url.replace('postgresql://', 'postgresql+psycopg://')
    connect_args = {'sslmode': 'require'} if db_url.startswith('postgresql') else {}
    if '+psycopg' in db_url:
        connect_args['prepare_threshold'] = None
    return create_engine(db_url, pool_pre_ping=True, pool_recycle=1800, connect_args=connect_args)


def _safe_yf_download(symbol: str, *, period: Optional[str] = None, interval: Optional[str] = None,
                      start: Optional[str] = None, end: Optional[str] = None, max_attempts: int = 3) -> Optional[pd.DataFrame]:
    """Safe wrapper for yfinance.download with retries and handling of 401/Invalid Crumb."""
    backoff_base = 0.6
    last_err: Optional[Exception] = None
    for attempt in range(1, max_attempts + 1):
        try:
            df = yf.download(symbol, period=period, interval=interval, start=start, end=end,
                             auto_adjust=True, progress=False)
            if isinstance(df, pd.DataFrame) and not df.empty:
                return df
            # Treat empty as retryable
            raise ValueError("yfinance download returned empty history")
        except Exception as e:
            last_err = e
            msg = str(e).lower()
            if any(tok in msg for tok in ['401', 'unauthorized', 'invalid crumb', 'forbidden', '403']):
                # Hard fail for auth issues (callers can degrade gracefully)
                return None
            if 'rate limit' in msg or 'too many requests' in msg or '999' in msg:
                # Short sleep and give up to avoid hammering
                time.sleep(2.0 + random.uniform(0, 1.0))
                return None
            if attempt < max_attempts:
                time.sleep(backoff_base * (2 ** (attempt - 1)) + random.uniform(0, 0.3))
            else:
                return None

def _download_candles(symbol: str, timeframe: str = '1h', lookback: str = '180d') -> pd.DataFrame:
    interval = timeframe
    # Map some common timeframe aliases to yfinance intervals if needed
    tf_map = {
        '1m': '1m', '5m': '5m', '15m': '15m', '30m': '30m', '1h': '60m', '1d': '1d'
    }
    interval = tf_map.get(timeframe, timeframe)
    df = _safe_yf_download(symbol, period=lookback, interval=interval)
    if isinstance(df, pd.DataFrame) and not df.empty:
        df = df.rename(columns=str.lower)
        return df
    return pd.DataFrame()


def _build_features(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()
    out = df.copy()
    # Ensure timezone awareness for session features
    try:
        idx = out.index
        if getattr(idx, 'tz', None) is None:
            out.index = out.index.tz_localize('UTC')
        out.index = out.index.tz_convert(ZoneInfo('America/New_York'))
    except Exception:
        pass

    # Basic indicators + regimes
    try:
        out['rsi14'] = RSIIndicator(out['close'], window=14).rsi()
        macd = MACD(out['close'])
        out['macd'] = macd.macd()
        out['macd_signal'] = macd.macd_signal()
        out['sma20'] = SMAIndicator(out['close'], window=20).sma_indicator()
        out['sma50'] = SMAIndicator(out['close'], window=50).sma_indicator()
        out['sma200'] = SMAIndicator(out['close'], window=200).sma_indicator()
        bb = BollingerBands(out['close'], window=20, window_dev=2)
        out['bb_high'] = bb.bollinger_hband()
        out['bb_low'] = bb.bollinger_lband()
        out['bb_width'] = (out['bb_high'] - out['bb_low']) / out['close']
        # ATR and normalizations
        atr = AverageTrueRange(high=out['high'], low=out['low'], close=out['close'], window=14)
        out['atr14'] = atr.average_true_range()
        out['atr_pct'] = (out['atr14'] / out['close']).replace([np.inf, -np.inf], np.nan)
        out['ret_1'] = out['close'].pct_change(1)
        out['ret_5'] = out['close'].pct_change(5)
        out['ret_10'] = out['close'].pct_change(10)
        vol_ma20 = out['volume'].rolling(20).mean()
        out['vol_ma20'] = vol_ma20
        out['vol_ratio'] = (out['volume'] / vol_ma20).replace([np.inf, -np.inf], np.nan)
        # Trend regime feature
        out['trend_up'] = (out['sma50'] > out['sma200']).astype(int)
        # Session/time-of-day features (Eastern Time)
        out['hour'] = out.index.hour
        out['dow'] = out.index.dayofweek
        out['is_open_session'] = ((out['hour'] >= 9) & (out['hour'] < 11)).astype(int)
        out['is_power_hour'] = ((out['hour'] >= 15) & (out['hour'] <= 16)).astype(int)
    except Exception:
        pass
    # Candlestick geometry features
    try:
        rng = (out['high'] - out['low']).replace(0, np.nan)
        body = (out['close'] - out['open']).abs()
        out['body_pct'] = (body / rng).clip(0, 1)
        out['upper_wick_pct'] = ((out['high'] - out[['open', 'close']].max(axis=1)) / rng).clip(0, 1)
        out['lower_wick_pct'] = (((out[['open', 'close']].min(axis=1)) - out['low']) / rng).clip(0, 1)
        # Heuristic scores (not labels):
        out['hammer_score'] = (out['lower_wick_pct'] - out['body_pct']).fillna(0)
        out['marubozu_score'] = out['body_pct'].fillna(0)
    except Exception:
        pass

    out = out.dropna().copy()
    return out


def _labels_from_outcomes(engine: sa.Engine, window_days: int = 180) -> List[Dict[str, Any]]:
    with engine.connect() as conn:
        rows = conn.execute(text(
            """
            SELECT symbol, pattern, entry_price, exit_price, pnl, quantity, timeframe, opened_at, closed_at
            FROM trade_outcomes
            WHERE closed_at > NOW() - INTERVAL :days::text || ' days'
            ORDER BY closed_at DESC
            LIMIT 2000
            """
        ), {'days': str(int(window_days))}).fetchall()
        data = []
        for r in rows:
            data.append({
                'symbol': r.symbol,
                'timeframe': r.timeframe or '1h',
                'closed_at': r.closed_at,
                'label': 1 if (r.pnl or 0) > 0 else 0,
                'pattern': r.pattern or 'UNKNOWN'
            })
        return data


def _detect_trend_regime(feats: pd.DataFrame) -> str:
    try:
        last = feats.iloc[-1]
        if 'sma50' in feats.columns and 'sma200' in feats.columns and not math.isnan(last['sma50']) and not math.isnan(last['sma200']):
            return 'trend_up' if float(last['sma50']) > float(last['sma200']) else 'trend_down'
    except Exception:
        pass
    return 'all'


def train_from_outcomes(lookback: str = '180d') -> Dict[str, Any]:
    engine = _get_engine()
    if engine is None:
        return {'success': False, 'error': 'no_database'}
    outcomes = _labels_from_outcomes(engine)
    if not outcomes:
        return {'success': False, 'error': 'no_outcomes'}

    # Build per (asset_class, timeframe, regime) groups (global)
    cache: Dict[Tuple[str, str], pd.DataFrame] = {}
    groups_global: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
    # Build per-pattern groups (asset, timeframe, pattern, regime)
    groups_pat: Dict[Tuple[str, str, str, str], Dict[str, Any]] = {}

    for o in outcomes:
        tf = o['timeframe']
        sym = o['symbol']
        key = (sym, tf)
        if key not in cache:
            candles = _download_candles(sym, tf, lookback)
            feats = _build_features(candles)
            cache[key] = feats if feats is not None else pd.DataFrame()
        feats = cache.get(key)
        if feats is None or feats.empty:
            continue
        row = feats.iloc[-1].copy()
        asset = _asset_class(sym)
        regime = _detect_trend_regime(feats)
        # Global group
        gk = (asset, tf, regime)
        g = groups_global.setdefault(gk, {'X': [], 'y': [], 'columns': feats.columns.tolist()})
        g['X'].append(row.values.astype(float))
        g['y'].append(int(o['label']))
        # Pattern group: no extra features yet; pattern itself handled via segmentation
        pat = (o.get('pattern') or 'UNKNOWN')
        pgk = (asset, tf, pat, regime)
        pg = groups_pat.setdefault(pgk, {'X': [], 'y': [], 'columns': feats.columns.tolist(), 'pattern': pat})
        pg['X'].append(row.values.astype(float))
        pg['y'].append(int(o['label']))

    results = {'trained_global': [], 'skipped_global': [], 'trained_pattern': [], 'skipped_pattern': []}
    # Train global models
    for (asset, tf, regime), data in groups_global.items():
        X_list = data['X']
        y_list = data['y']
        if len(X_list) < 30:
            results['skipped_global'].append({'asset': asset, 'timeframe': tf, 'regime': regime, 'count': len(X_list)})
            continue
        X = np.vstack(X_list)
        y = np.array(y_list)
        try:
            X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        except Exception:
            X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
        model = GradientBoostingClassifier(random_state=42)
        model.fit(X_train, y_train)
        val_proba = model.predict_proba(X_val)[:, 1]
        auc = roc_auc_score(y_val, val_proba)
        # Save model bundle
        path = _model_path(asset, tf, regime)
        dump({'model': model, 'columns': data['columns']}, path)
        results['trained_global'].append({'asset': asset, 'timeframe': tf, 'regime': regime, 'val_auc': float(auc), 'n': int(len(X_list)), 'path': path})

    # Train per-pattern models
    for (asset, tf, pat, regime), data in groups_pat.items():
        X_list = data['X']
        y_list = data['y']
        if len(X_list) < 30:
            results['skipped_pattern'].append({'asset': asset, 'timeframe': tf, 'pattern': pat, 'regime': regime, 'count': len(X_list)})
            continue
        X = np.vstack(X_list)
        y = np.array(y_list)
        try:
            X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        except Exception:
            X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
        model = GradientBoostingClassifier(random_state=42)
        model.fit(X_train, y_train)
        val_proba = model.predict_proba(X_val)[:, 1]
        auc = roc_auc_score(y_val, val_proba)
        path = _model_path_pattern(asset, tf, pat, regime)
        dump({'model': model, 'columns': data['columns']}, path)
        results['trained_pattern'].append({'asset': asset, 'timeframe': tf, 'pattern': pat, 'regime': regime, 'val_auc': float(auc), 'n': int(len(X_list)), 'path': path})

    if not results['trained_global'] and not results['trained_pattern']:
        return {'success': False, 'error': 'no_models_trained', 'details': results}
    return {'success': True, 'metrics': results}


def score_symbol(symbol: str, timeframe: str = '1h') -> Dict[str, Any]:
    candles = _download_candles(symbol, timeframe)
    feats = _build_features(candles)
    if feats is None or feats.empty:
        return {'success': False, 'error': 'no_features'}
    asset = _asset_class(symbol)
    regime = _detect_trend_regime(feats)
    # Try exact segmented model, then fallback to 'all'
    path_exact = _model_path(asset, timeframe, regime)
    path_fallback = _model_path(asset, timeframe, 'all')
    path = path_exact if os.path.exists(path_exact) else path_fallback if os.path.exists(path_fallback) else None
    if not path:
        return {'success': False, 'error': 'model_not_trained', 'asset_class': asset, 'timeframe': timeframe, 'regime': regime}
    bundle = load(path)
    model = bundle['model']
    cols = bundle.get('columns')
    x_row = feats.iloc[-1]
    if cols:
        # align columns
        missing = [c for c in cols if c not in feats.columns]
        extra = [c for c in feats.columns if c not in cols]
        # pad missing with zeros
        for c in missing:
            x_row[c] = 0.0
        x = x_row[cols].values.reshape(1, -1)
    else:
        x = x_row.values.reshape(1, -1)
    proba = float(model.predict_proba(x)[:, 1][0])
    return {
        'success': True,
        'symbol': symbol.upper(),
        'timeframe': timeframe,
        'asset_class': asset,
        'regime': regime,
        'score': proba,
        'model_path': path
    }


def score_symbol_with_pattern(symbol: str, timeframe: str, pattern: str) -> Dict[str, Any]:
    # Base features
    candles = _download_candles(symbol, timeframe)
    feats = _build_features(candles)
    if feats is None or feats.empty:
        return {'success': False, 'error': 'no_features'}
    asset = _asset_class(symbol)
    regime = _detect_trend_regime(feats)

    # Load global model
    p_global_exact = _model_path(asset, timeframe, regime)
    p_global_fb = _model_path(asset, timeframe, 'all')
    p_global = p_global_exact if os.path.exists(p_global_exact) else p_global_fb if os.path.exists(p_global_fb) else None

    # Load pattern model
    p_pat_exact = _model_path_pattern(asset, timeframe, pattern, regime)
    p_pat_fb = _model_path_pattern(asset, timeframe, pattern, 'all')
    p_pat = p_pat_exact if os.path.exists(p_pat_exact) else p_pat_fb if os.path.exists(p_pat_fb) else None

    if not p_global and not p_pat:
        return {'success': False, 'error': 'model_not_trained', 'asset_class': asset, 'timeframe': timeframe, 'regime': regime}

    x_row = feats.iloc[-1]
    def _predict(path: Optional[str]) -> Optional[float]:
        if not path:
            return None
        bundle = load(path)
        model = bundle['model']
        cols = bundle.get('columns')
        row = x_row.copy()
        if cols:
            for c in [c for c in cols if c not in feats.columns]:
                row[c] = 0.0
            x = row[cols].values.reshape(1, -1)
        else:
            x = row.values.reshape(1, -1)
        return float(model.predict_proba(x)[:, 1][0])

    g_score = _predict(p_global)
    pat_score = _predict(p_pat)

    # Blend scores if both available; weight configurable
    weight = float(os.getenv('PATTERN_SCORE_WEIGHT', '0.6'))
    if g_score is not None and pat_score is not None:
        final = float((weight * pat_score) + ((1.0 - weight) * g_score))
    else:
        final = float(pat_score if pat_score is not None else g_score)

    return {
        'success': True,
        'symbol': symbol.upper(),
        'timeframe': timeframe,
        'asset_class': asset,
        'regime': regime,
        'pattern': pattern,
        'score': final,
        'global_score': g_score,
        'pattern_score': pat_score,
        'weights': {'pattern': weight, 'global': 1.0 - weight},
        'global_model_path': p_global,
        'pattern_model_path': p_pat,
    }
