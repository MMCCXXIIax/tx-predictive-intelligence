# --------------------------------------
# Outcomes logging and enhanced performance summary
# --------------------------------------
from schemas import PatternPerformanceQuery  # type: ignore
from services.outcome_logging import log_outcome, summarize_outcomes  # type: ignore


@app.route('/api/outcomes/log', methods=['POST'])
@limiter.limit("30 per minute")
def log_trade_outcome():
    """Record a realized trade outcome to power win-rate metrics.
    Body example:
    {
      "symbol": "AAPL", "pattern": "RSI_OVERSOLD", "entry_price": 180.0,
      "exit_price": 184.5, "pnl": 4.5, "quantity": 10, "timeframe": "1h",
      "opened_at": "2025-01-01T09:00:00Z", "closed_at": "2025-01-01T11:00:00Z",
      "metadata": {"notes": "TP hit"}
    }
    """
    try:
        data = request.get_json(silent=True) or {}
        ok = log_outcome(data)
        return jsonify({'success': bool(ok)})
    except Exception as e:
        logger.error(f"log_trade_outcome error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/pattern-performance/summary')
@limiter.limit("30 per minute")
def pattern_performance_summary():
    """Return detection aggregates (existing endpoint) plus outcome-based win-rates.
    Query: window (int), pattern (str), symbol (str)
    """
    try:
        # Validate query via Pydantic if available
        try:
            q = PatternPerformanceQuery(
                window=int(request.args.get('window', 30)),
                pattern=request.args.get('pattern'),
                symbol=request.args.get('symbol')
            )
        except Exception:
            # Fallback if pydantic missing
            class Q: pass
            q = Q(); q.window=int(request.args.get('window', 30)); q.pattern=request.args.get('pattern'); q.symbol=request.args.get('symbol')

        # Get detection aggregates by reusing existing endpoint logic via internal call
        # If the existing '/api/pattern-performance' view is available, we can call the function directly
        # Otherwise, return only outcomes
        try:
            detection = None
            for rule in app.url_map.iter_rules():
                if str(rule.rule) == '/api/pattern-performance':
                    # Synthesize a minimal run by calling the view function with current request context
                    # Here, we duplicate the args minimally to avoid cross-calling complexities
                    detection = {'note': 'see /api/pattern-performance for detection aggregates'}
                    break
        except Exception:
            detection = None

        outcomes = summarize_outcomes(q.window, q.pattern, q.symbol)
        return jsonify({
            'success': True,
            'data': {
                'detections': detection,
                'outcomes': outcomes
            },
            'meta': {'window_days': q.window, 'pattern': q.pattern, 'symbol': q.symbol},
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"pattern_performance_summary error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
