# Overview

TX is a trading intelligence assistant that provides AI-driven candlestick pattern recognition, real-time market analysis, and paper trading simulation for cryptocurrency, stock, and forex markets. The system operates as an educational and analytical tool, detecting trading patterns and providing insights without offering financial advice.

## Import Status: COMPLETED ✅
- **Imported from GitHub**: September 14, 2025
- **Replit Setup**: Fully configured and operational
- **Current Status**: Live trading intelligence system with real-time pattern detection

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend Architecture
- **Flask Web Framework**: RESTful API server with CORS support for cross-origin requests
- **Modular Service Layer**: Separate services for data routing, paper trading, alert management, and database operations
- **Pattern Detection Engine**: Centralized registry system with 20+ candlestick pattern detectors (hammer, doji, engulfing patterns, etc.)
- **Multi-Asset Data Router**: Unified interface handling crypto, stock, and forex data from different sources

## Data Management
- **PostgreSQL Database**: Primary data storage using SQLAlchemy ORM with connection pooling
- **Supabase Integration**: Secondary database option with service role authentication
- **File-based Logging**: CSV and text file logging for trade history and alert tracking
- **In-memory Caching**: JSON-based caching system for real-time market data

## Real-time Data Pipeline
- **CryptoDataService**: CoinGecko API integration with background threading for crypto data
- **AlphaDataService**: Alpha Vantage API for stock and forex market data
- **Threaded Data Updates**: Automatic background refresh with configurable intervals
- **Rate Limiting**: Built-in API rate limiting and error handling

## Trading Simulation
- **Paper Trading Engine**: Thread-safe simulation system with position tracking
- **Risk Management**: Configurable stop-loss and take-profit percentages
- **Trade Execution**: Simulated buy/sell operations with comprehensive logging
- **Portfolio Tracking**: Real-time P&L calculation and position management

## Alert System
- **Pattern-based Alerts**: Confidence threshold filtering for pattern detections
- **Multi-channel Notifications**: Support for various alert delivery methods
- **Alert History**: Persistent logging of all triggered alerts

## Deployment Architecture
- **Multi-platform Support**: Railway, Vercel, and Docker deployment configurations
- **WSGI Integration**: Gunicorn and Waitress server options
- **Environment Management**: Comprehensive environment variable configuration
- **Static Asset Serving**: Built-in client application serving

# External Dependencies

## Market Data APIs
- **CoinGecko API**: Real-time cryptocurrency OHLC data with free tier access
- **Alpha Vantage API**: Stock and forex market data requiring API key authentication

## Database Services
- **PostgreSQL**: Primary relational database for structured data storage
- **Supabase**: Cloud PostgreSQL service with built-in authentication and real-time features

## Infrastructure
- **Railway**: Primary cloud deployment platform with automated builds
- **Vercel**: Alternative serverless deployment option
- **Flask-CORS**: Cross-origin resource sharing for frontend integration

## Python Libraries
- **SQLAlchemy 2.0+**: Database ORM with connection pooling
- **Requests**: HTTP client for external API communications
- **Threading**: Built-in Python threading for concurrent data processing
- **CSV/JSON**: Standard library modules for data serialization and logging

## Development Tools
- **python-dotenv**: Environment variable management
- **Gunicorn/Waitress**: Production WSGI servers
- **psycopg2**: PostgreSQL adapter for Python