@app.route('/api/provider-health')
@limiter.limit("20 per minute")
def provider_health():
    checks = {}
    circuit = CircuitBreaker()
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
            r = resilient_http_get('https://finnhub.io/api/v1/quote', params={'symbol':'AAPL','token':Config.FINNHUB_API_KEY}, timeout=5.0, circuit=circuit)
            checks['finnhub'] = {'ok': r.status_code == 200, 'latency_ms': int((time.time()-start)*1000)}
        else:
            checks['finnhub'] = {'ok': False, 'error': 'no_api_key'}
    except Exception as e:
        checks['finnhub'] = {'ok': False, 'error': str(e)}
    # Polygon
    try:
        if Config.POLYGON_API_KEY:
            start = time.time()
            r = resilient_http_get('https://api.polygon.io/v2/aggs/ticker/AAPL/range/1/day/2024-01-01/2024-01-02', params={'apiKey': Config.POLYGON_API_KEY}, timeout=5.0, circuit=circuit)
            checks['polygon'] = {'ok': r.status_code in (200,401,403), 'latency_ms': int((time.time()-start)*1000)}
        else:
            checks['polygon'] = {'ok': False, 'error': 'no_api_key'}
    except Exception as e:
        checks['polygon'] = {'ok': False, 'error': str(e)}
    return jsonify({'success': True, 'data': checks, 'timestamp': datetime.now().isoformat()})
