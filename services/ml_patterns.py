import os
import math
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


def _download_candles(symbol: str, timeframe: str = '1h', lookback: str = '180d') -> pd.DataFrame:
    interval = timeframe
    # Map some common timeframe aliases to yfinance intervals if needed
    tf_map = {
        '1m': '1m', '5m': '5m', '15m': '15m', '30m': '30m', '1h': '60m', '1d': '1d'
    }
    interval = tf_map.get(timeframe, timeframe)
    df = yf.download(symbol, period=lookback, interval=interval, auto_adjust=True, progress=False)
    if isinstance(df, pd.DataFrame) and not df.empty:
        df = df.rename(columns=str.lower)
    return df


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
                'label': 1 if (r.pnl or 0) > 0 else 0
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

    # Build per (asset_class, timeframe, regime) groups
    cache: Dict[Tuple[str, str], pd.DataFrame] = {}
    groups: Dict[Tuple[str, str, str], Dict[str, Any]] = {}

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
        row = feats.iloc[-1]
        asset = _asset_class(sym)
        regime = _detect_trend_regime(feats)
        gk = (asset, tf, regime)
        g = groups.setdefault(gk, {'X': [], 'y': [], 'columns': feats.columns.tolist()})
        g['X'].append(row.values.astype(float))
        g['y'].append(int(o['label']))

    results = {'trained': [], 'skipped': []}
    for (asset, tf, regime), data in groups.items():
        X_list = data['X']
        y_list = data['y']
        if len(X_list) < 30:
            results['skipped'].append({'asset': asset, 'timeframe': tf, 'regime': regime, 'count': len(X_list)})
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
        results['trained'].append({'asset': asset, 'timeframe': tf, 'regime': regime, 'val_auc': float(auc), 'n': int(len(X_list)), 'path': path})

    if not results['trained']:
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
