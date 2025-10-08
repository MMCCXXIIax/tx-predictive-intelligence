# --------------------------------------
# OpenAPI docs and health endpoints (additive)
# --------------------------------------
if Config.ENABLE_OPENAPI:
    def _generate_openapi_from_map() -> Dict[str, Any]:
        spec: Dict[str, Any] = {
            'openapi': '3.0.0',
            'info': {'title': 'TX Trade Whisperer API', 'version': '2.0.0'},
            'paths': {}
        }
        for rule in app.url_map.iter_rules():
            if rule.endpoint == 'static':
                continue
            methods = sorted([m for m in rule.methods if m in {'GET','POST','PUT','DELETE','PATCH'}])
            path = str(rule)
            if path not in spec['paths']:
                spec['paths'][path] = {}
            for m in methods:
                spec['paths'][path][m.lower()] = {
                    'summary': rule.endpoint,
                    'responses': {'200': {'description': 'OK'}}
                }
        return spec

    @app.route('/swagger.json')
    @limiter.exempt
    def swagger_json():
        return jsonify(_generate_openapi_from_map())

    @app.route('/docs')
    @limiter.exempt
    def docs():
        html = """
        <!doctype html>
        <html>
          <head>
            <title>TX API Docs</title>
            <meta charset='utf-8'/>
            <meta name='viewport' content='width=device-width, initial-scale=1'>
            <script src='https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js'></script>
          </head>
          <body>
            <redoc spec-url='/swagger.json'></redoc>
          </body>
        </html>
        """
        return Response(html, mimetype='text/html')

@app.route('/api/provider-health')
@limiter.limit("20 per minute")
def provider_health():
    checks = {}
    # yfinance basic check
    try:
        start = time.time()
        hist = yf.download('AAPL', period='1d', interval='1d', progress=False, auto_adjust=True)
        checks['yfinance'] = {'ok': bool(hist is not None and not hist.empty), 'latency_ms': int((time.time()-start)*1000)}
    except Exception as e:
        checks['yfinance'] = {'ok': False, 'error': str(e)}
    # Finnhub
    try:
        if Config.FINNHUB_API_KEY:
            start = time.time()
            r = httpx.get('https://finnhub.io/api/v1/quote', params={'symbol':'AAPL','token':Config.FINNHUB_API_KEY}, timeout=5.0)
            checks['finnhub'] = {'ok': r.status_code == 200, 'latency_ms': int((time.time()-start)*1000)}
        else:
            checks['finnhub'] = {'ok': False, 'error': 'no_api_key'}
    except Exception as e:
        checks['finnhub'] = {'ok': False, 'error': str(e)}
    # Polygon
    try:
        if Config.POLYGON_API_KEY:
            start = time.time()
            r = httpx.get('https://api.polygon.io/v2/aggs/ticker/AAPL/range/1/day/2024-01-01/2024-01-02', params={'apiKey': Config.POLYGON_API_KEY}, timeout=5.0)
            checks['polygon'] = {'ok': r.status_code in (200,401,403), 'latency_ms': int((time.time()-start)*1000)}
        else:
            checks['polygon'] = {'ok': False, 'error': 'no_api_key'}
    except Exception as e:
        checks['polygon'] = {'ok': False, 'error': str(e)}
    return jsonify({'success': True, 'data': checks, 'timestamp': datetime.now().isoformat()})

@app.route('/api/workers/health')
@limiter.limit("30 per minute")
def workers_health():
    scanning_flag = bool(globals().get('scanning_active'))
    status = globals().get('scanning_status', {})
    return jsonify({'success': True, 'data': {
        'live_scanner_active': scanning_flag,
        'scanning_status': status,
        'background_workers_enabled': bool(Config.ENABLE_BACKGROUND_WORKERS)
    }, 'timestamp': datetime.now().isoformat()})

@app.route('/api/pattern-performance')
@limiter.limit("20 per minute")
def pattern_performance():
    try:
        window_days = int(request.args.get('window', 30))
        pattern = request.args.get('pattern')
        symbol = request.args.get('symbol')
        results = {'overall': {}, 'by_pattern': [], 'by_symbol': []}
        if db_available:
            with Session() as session:
                base_where = " detected_at > NOW() - INTERVAL ':days days' "
                params = {'days': window_days}
                if pattern:
                    base_where += " AND pattern_type = :pattern"
                    params['pattern'] = pattern
                if symbol:
                    base_where += " AND symbol = :symbol"
                    params['symbol'] = symbol
                rows = session.execute(text(f"SELECT pattern_type, COUNT(*) detections, AVG(confidence) avg_conf FROM pattern_detections WHERE {base_where} GROUP BY pattern_type ORDER BY detections DESC"), params).fetchall()
                results['by_pattern'] = [{'pattern': r.pattern_type, 'detections': int(r.detections or 0), 'avg_confidence': float(r.avg_conf or 0)} for r in rows]
                rows2 = session.execute(text(f"SELECT symbol, COUNT(*) detections, AVG(confidence) avg_conf FROM pattern_detections WHERE {base_where} GROUP BY symbol ORDER BY detections DESC LIMIT 25"), params).fetchall()
                results['by_symbol'] = [{'symbol': r.symbol, 'detections': int(r.detections or 0), 'avg_confidence': float(r.avg_conf or 0)} for r in rows2]
        return jsonify({'success': True, 'data': results, 'meta': {'window_days': window_days, 'pattern': pattern, 'symbol': symbol}, 'timestamp': datetime.now().isoformat()})
    except Exception as e:
        logger.error(f"pattern_performance error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
