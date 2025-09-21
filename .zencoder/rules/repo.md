---
description: Repository Information Overview
alwaysApply: true
---

# TX Trade Whisperer Information

## Summary
TX Trade Whisperer is an advanced trading intelligence platform built with Flask. It provides real-time market data analysis, pattern detection for various financial instruments (stocks, forex, crypto), backtesting capabilities, and paper trading functionality. The platform integrates with external data sources and offers a web-based dashboard for monitoring and strategy building.

## Structure
- **detectors/**: Contains pattern detection algorithms for candlestick patterns
- **services/**: Core business logic modules for data processing, trading, and analysis
- **static/**: Frontend HTML files for the web dashboard
- **migrations/**: Database schema and migration scripts
- **scripts/**: Utility scripts for development and testing

## Language & Runtime
**Language**: Python
**Version**: >=3.11
**Framework**: Flask 3.0.0
**Package Manager**: pip

## Dependencies
**Main Dependencies**:
- Flask 3.0.0 (Web framework)
- SQLAlchemy >=2.0.23 (ORM)
- psycopg >=3.2.2 (PostgreSQL adapter)
- pandas >=2.0.0 (Data analysis)
- yfinance >=0.2.0 (Yahoo Finance data)
- ccxt >=4.4.86 (Cryptocurrency exchange API)
- ta >=0.11.0 (Technical analysis)
- flask-socketio 5.3.0 (WebSocket support)

**Development Dependencies**:
- python-dotenv 1.0.0 (Environment variables)
- waitress 3.0.0 (WSGI server)

## Build & Installation
```bash
pip install -r requirements.txt
```

## Deployment
**Render Configuration**:
- Type: Web service
- Environment: Python
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn -k gthread --threads 4 -w 1 -b 0.0.0.0:$PORT main:app`

**Vercel Configuration**:
- Entry Point: wsgi.py
- Python Runtime: Vercel Python

**Gunicorn Configuration**:
- Worker Class: gevent
- Workers: Dynamic (WEB_CONCURRENCY env var, default 2)
- Preload: Enabled

## Main Files
**Entry Point**: main.py
**WSGI Entry**: wsgi.py
**Configuration**: Environment variables via .env file
**Key Modules**:
- services/data_router.py (Data source management)
- services/alert_engine.py (Trading signals)
- services/backtesting_engine.py (Strategy testing)
- services/paper_trader.py (Simulated trading)
- detectors/*.py (Pattern recognition algorithms)

## Frontend
**Dashboard**: static/tx-dashboard.html
**Backtesting UI**: static/backtesting.html
**Strategy Builder**: static/strategy-builder.html