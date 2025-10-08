# --------------------------------------
# ML-based pattern detection endpoints (no heuristics)
# --------------------------------------
from services.ml_patterns import train_from_outcomes, score_symbol  # type: ignore

@app.route('/api/ml/train', methods=['POST'])
@limiter.limit("10 per hour")
def ml_train():
    """Train an ML model from recorded trade outcomes and recent candles.
    Returns validation AUC and sample counts.
    """
    try:
        payload = request.get_json(silent=True) or {}
        lookback = str(payload.get('lookback', '180d'))
        res = train_from_outcomes(lookback=lookback)
        if not res.get('success'):
            return jsonify({'success': False, 'error': res.get('error')}), 400
        return jsonify({'success': True, 'metrics': res.get('metrics')})
    except Exception as e:
        logger.error(f"ml_train error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ml/score')
@limiter.limit("60 per minute")
def ml_score():
    """Score a symbol with the latest trained ML model. Query: symbol, timeframe (default 1h)"""
    try:
        symbol = (request.args.get('symbol') or '').upper()
        timeframe = request.args.get('timeframe', '1h')
        if not symbol:
            return jsonify({'success': False, 'error': 'symbol required'}), 400
        res = score_symbol(symbol, timeframe=timeframe)
        status = 200 if res.get('success') else 400
        return jsonify(res), status
    except Exception as e:
        logger.error(f"ml_score error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
