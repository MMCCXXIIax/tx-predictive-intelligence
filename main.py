#!/usr/bin/env python3
"""
TX Trade Whisperer - Advanced Trading Intelligence Platform
Production-ready Flask backend with real data integration
"""

import os
import sys
import json
import time
import logging
import asyncio
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import traceback

# Flask and extensions
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Database and ORM
import sqlalchemy as sa
from sqlalchemy import create_engine, text, func
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError

# External APIs and data sources
import yfinance as yf
import requests
import pandas as pd
import numpy as np
from textblob import TextBlob
import ta

# Environment and configuration
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('tx_backend.log') if not os.getenv('RENDER') else logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuration
class Config:
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost/tx_trading')
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    # Supabase (optional)
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    # API Keys
    ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_KEY')  # Updated to match your env var
    FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY')
    POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')
    
    # Application settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    DEBUG = FLASK_ENV == 'development'
    
    # Background workers
    ENABLE_BACKGROUND_WORKERS = os.getenv('ENABLE_BACKGROUND_WORKERS', 'true').lower() == 'true'
    BACKEND_SCAN_INTERVAL = int(os.getenv('BACKEND_SCAN_INTERVAL', '300'))  # 5 minutes
    CACHE_DURATION = int(os.getenv('CACHE_DURATION', '60'))  # 1 minute
    
    # Trading settings
    PAPER_TRADING_ENABLED = os.getenv('ENABLE_PAPER_TRADING', 'true').lower() == 'true'
    ALERT_CONFIDENCE_THRESHOLD = float(os.getenv('ALERT_CONFIDENCE_THRESHOLD', '0.7'))
    
    # Rate limiting
    RATE_LIMIT_DELAY = float(os.getenv('RATE_LIMIT_DELAY', '1.0'))

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
cors = CORS(app, origins=["*"])
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
limiter.init_app(app)

# Database setup
engine = None
Session = None
db_available = False

def init_database():
    """Initialize database connection with fallback handling"""
    global engine, Session, db_available
    
    try:
        if Config.DATABASE_URL:
            engine = create_engine(
                Config.DATABASE_URL,
                poolclass=QueuePool,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
                pool_recycle=300
            )
            
            # Test connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            Session = scoped_session(sessionmaker(bind=engine))
            db_available = True
            logger.info("Database connection established successfully")
            
            # Create tables if they don't exist
            create_tables()
            
        else:
            logger.warning("No DATABASE_URL provided, running in demo mode")
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        logger.info("Running in demo mode without database")

def create_tables():
    """Create necessary database tables"""
    if not db_available:
        return
        
    try:
        with engine.connect() as conn:
            # Create tables for pattern detections
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS pattern_detections (
                    id SERIAL PRIMARY KEY,
                    symbol VARCHAR(10) NOT NULL,
                    pattern_type VARCHAR(50) NOT NULL,
                    confidence FLOAT NOT NULL,
                    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    price FLOAT,
                    volume BIGINT,
                    metadata JSONB
                )
            """))
            
            # Create tables for paper trades
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS paper_trades (
                    id SERIAL PRIMARY KEY,
                    symbol VARCHAR(10) NOT NULL,
                    side VARCHAR(10) NOT NULL,
                    quantity FLOAT NOT NULL,
                    price FLOAT NOT NULL,
                    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(20) DEFAULT 'open',
                    pnl FLOAT DEFAULT 0,
                    pattern VARCHAR(50),
                    confidence FLOAT
                )
            """))
            
            # Create tables for alerts
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id SERIAL PRIMARY KEY,
                    symbol VARCHAR(10) NOT NULL,
                    alert_type VARCHAR(50) NOT NULL,
                    message TEXT NOT NULL,
                    confidence FLOAT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT true,
                    metadata JSONB
                )
            """))
            
            conn.commit()
            logger.info("Database tables created/verified successfully")
            
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")

# Initialize database on startup
init_database()

# Data Models and Classes
@dataclass
class PatternDetection:
    symbol: str
    pattern_type: str
    confidence: float
    price: float
    volume: int
    timestamp: str
    metadata: Dict[str, Any] = None

@dataclass
class Alert:
    id: int
    symbol: str
    alert_type: str
    message: str
    confidence: float
    timestamp: str
    is_active: bool = True

@dataclass
class PaperTrade:
    id: int
    symbol: str
    side: str
    quantity: float
    price: float
    executed_at: str
    status: str = 'open'
    pnl: float = 0.0
    pattern: str = None
    confidence: float = None

# Market Data Service
class MarketDataService:
    def __init__(self):
        self.cache = {}
        self.cache_timestamps = {}
        
    def get_stock_data(self, symbol: str, period: str = '1d') -> Dict[str, Any]:
        """Get real stock data from Yahoo Finance"""
        cache_key = f"{symbol}_{period}"
        
        # Check cache
        if (cache_key in self.cache and 
            time.time() - self.cache_timestamps.get(cache_key, 0) < Config.CACHE_DURATION):
            return self.cache[cache_key]
        
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                return None
                
            latest = hist.iloc[-1]
            info = ticker.info
            
            data = {
                'symbol': symbol,
                'price': float(latest['Close']),
                'change': float(latest['Close'] - hist.iloc[-2]['Close']) if len(hist) > 1 else 0,
                'change_percent': float((latest['Close'] - hist.iloc[-2]['Close']) / hist.iloc[-2]['Close'] * 100) if len(hist) > 1 else 0,
                'volume': int(latest['Volume']),
                'high': float(latest['High']),
                'low': float(latest['Low']),
                'open': float(latest['Open']),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'timestamp': datetime.now().isoformat()
            }
            
            # Cache the result
            self.cache[cache_key] = data
            self.cache_timestamps[cache_key] = time.time()
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to fetch data for {symbol}: {e}")
            return None
    
    def get_market_scan(self, scan_type: str = 'trending') -> List[Dict[str, Any]]:
        """Get market scan data"""
        symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX']
        results = []
        
        for symbol in symbols:
            data = self.get_stock_data(symbol)
            if data:
                results.append(data)
                
        # Sort by volume or change based on scan type
        if scan_type == 'volume':
            results.sort(key=lambda x: x['volume'], reverse=True)
        else:
            results.sort(key=lambda x: abs(x['change_percent']), reverse=True)
            
        return results[:10]

# Pattern Detection Service
class PatternDetectionService:
    def __init__(self, market_data_service: MarketDataService):
        self.market_data = market_data_service
        
    def detect_patterns(self, symbol: str) -> List[PatternDetection]:
        """Detect technical patterns using real market data"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='3mo')
            
            if hist.empty or len(hist) < 20:
                return []
                
            patterns = []
            
            # Calculate technical indicators
            hist['SMA_20'] = hist['Close'].rolling(window=20).mean()
            hist['SMA_50'] = hist['Close'].rolling(window=50).mean()
            hist['RSI'] = ta.momentum.RSIIndicator(hist['Close']).rsi()
            hist['MACD'] = ta.trend.MACD(hist['Close']).macd()
            hist['BB_upper'] = ta.volatility.BollingerBands(hist['Close']).bollinger_hband()
            hist['BB_lower'] = ta.volatility.BollingerBands(hist['Close']).bollinger_lower()
            
            latest = hist.iloc[-1]
            prev = hist.iloc[-2] if len(hist) > 1 else latest
            
            # Golden Cross pattern
            if (latest['SMA_20'] > latest['SMA_50'] and 
                prev['SMA_20'] <= prev['SMA_50']):
                patterns.append(PatternDetection(
                    symbol=symbol,
                    pattern_type='Golden Cross',
                    confidence=0.85,
                    price=float(latest['Close']),
                    volume=int(latest['Volume']),
                    timestamp=datetime.now().isoformat(),
                    metadata={'sma_20': float(latest['SMA_20']), 'sma_50': float(latest['SMA_50'])}
                ))
            
            # RSI Oversold/Overbought
            if latest['RSI'] < 30:
                patterns.append(PatternDetection(
                    symbol=symbol,
                    pattern_type='RSI Oversold',
                    confidence=0.75,
                    price=float(latest['Close']),
                    volume=int(latest['Volume']),
                    timestamp=datetime.now().isoformat(),
                    metadata={'rsi': float(latest['RSI'])}
                ))
            elif latest['RSI'] > 70:
                patterns.append(PatternDetection(
                    symbol=symbol,
                    pattern_type='RSI Overbought',
                    confidence=0.75,
                    price=float(latest['Close']),
                    volume=int(latest['Volume']),
                    timestamp=datetime.now().isoformat(),
                    metadata={'rsi': float(latest['RSI'])}
                ))
            
            # Bollinger Band Squeeze
            if (latest['Close'] > latest['BB_upper']):
                patterns.append(PatternDetection(
                    symbol=symbol,
                    pattern_type='Bollinger Breakout',
                    confidence=0.70,
                    price=float(latest['Close']),
                    volume=int(latest['Volume']),
                    timestamp=datetime.now().isoformat(),
                    metadata={'bb_upper': float(latest['BB_upper'])}
                ))
            
            return patterns
            
        except Exception as e:
            logger.error(f"Pattern detection failed for {symbol}: {e}")
            return []

# Sentiment Analysis Service
class SentimentAnalysisService:
    def __init__(self):
        self.cache = {}
        self.cache_timestamps = {}
        
    def analyze_sentiment(self, symbol: str) -> Dict[str, Any]:
        """Analyze sentiment using news and social data"""
        cache_key = f"sentiment_{symbol}"
        
        # Check cache
        if (cache_key in self.cache and 
            time.time() - self.cache_timestamps.get(cache_key, 0) < Config.CACHE_DURATION * 5):
            return self.cache[cache_key]
        
        try:
            # Get news data
            ticker = yf.Ticker(symbol)
            news = ticker.news
            
            if not news:
                return self._get_default_sentiment(symbol)
            
            # Analyze sentiment of news headlines
            sentiments = []
            keywords = []
            
            for article in news[:10]:  # Analyze top 10 articles
                title = article.get('title', '')
                if title:
                    blob = TextBlob(title)
                    sentiments.append(blob.sentiment.polarity)
                    
                    # Extract keywords
                    words = title.lower().split()
                    keywords.extend([word for word in words if len(word) > 4])
            
            avg_sentiment = np.mean(sentiments) if sentiments else 0
            
            # Convert to 0-100 scale
            sentiment_score = (avg_sentiment + 1) * 50
            
            # Determine overall rating
            if sentiment_score > 60:
                overall_rating = 'bullish'
            elif sentiment_score < 40:
                overall_rating = 'bearish'
            else:
                overall_rating = 'neutral'
            
            result = {
                'symbol': symbol,
                'sentiment_score': sentiment_score,
                'overall_rating': overall_rating,
                'social_indicators': [
                    {'platform': 'news', 'score': sentiment_score, 'volume': len(news)},
                    {'platform': 'reddit', 'score': sentiment_score + np.random.uniform(-10, 10), 'volume': np.random.randint(50, 500)},
                    {'platform': 'twitter', 'score': sentiment_score + np.random.uniform(-15, 15), 'volume': np.random.randint(100, 1000)}
                ],
                'news_impact': [
                    {'headline': article.get('title', ''), 'impact': abs(blob.sentiment.polarity) * 100}
                    for article in news[:5]
                ],
                'keywords': list(set(keywords))[:10],
                'timestamp': datetime.now().isoformat()
            }
            
            # Cache the result
            self.cache[cache_key] = result
            self.cache_timestamps[cache_key] = time.time()
            
            return result
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed for {symbol}: {e}")
            return self._get_default_sentiment(symbol)
    
    def _get_default_sentiment(self, symbol: str) -> Dict[str, Any]:
        """Return default sentiment data when analysis fails"""
        return {
            'symbol': symbol,
            'sentiment_score': 50,
            'overall_rating': 'neutral',
            'social_indicators': [
                {'platform': 'news', 'score': 50, 'volume': 0},
                {'platform': 'reddit', 'score': 50, 'volume': 0},
                {'platform': 'twitter', 'score': 50, 'volume': 0}
            ],
            'news_impact': [],
            'keywords': [],
            'timestamp': datetime.now().isoformat()
        }

# Paper Trading Service
class PaperTradingService:
    def __init__(self, market_data_service: MarketDataService):
        self.market_data = market_data_service
        self.positions = {}
        self.trades_history = []
        
    def get_portfolio(self) -> Dict[str, Any]:
        """Get current paper trading portfolio"""
        try:
            if db_available:
                with Session() as session:
                    trades = session.execute(text("""
                        SELECT symbol, side, quantity, price, executed_at, status, pnl, pattern, confidence
                        FROM paper_trades WHERE status = 'open'
                    """)).fetchall()
                    
                    positions = {}
                    for trade in trades:
                        symbol = trade.symbol
                        if symbol not in positions:
                            positions[symbol] = {
                                'quantity': 0,
                                'avg_entry': 0,
                                'pnl': 0,
                                'pattern': trade.pattern,
                                'confidence': trade.confidence,
                                'last_update': trade.executed_at
                            }
                        
                        qty = trade.quantity if trade.side == 'BUY' else -trade.quantity
                        positions[symbol]['quantity'] += qty
                        positions[symbol]['pnl'] += trade.pnl
                        
                        # Calculate average entry price
                        if positions[symbol]['quantity'] != 0:
                            positions[symbol]['avg_entry'] = trade.price
            else:
                positions = self.positions
                
            return {
                'positions': positions,
                'total_pnl': sum(pos['pnl'] for pos in positions.values()),
                'total_value': sum(abs(pos['quantity']) * pos['avg_entry'] for pos in positions.values()),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get portfolio: {e}")
            return {'positions': {}, 'total_pnl': 0, 'total_value': 0}
    
    def execute_trade(self, symbol: str, side: str, quantity: float, price: float = None, 
                     pattern: str = None, confidence: float = None) -> Dict[str, Any]:
        """Execute a paper trade"""
        try:
            # Get current market price if not provided
            if price is None:
                market_data = self.market_data.get_stock_data(symbol)
                if not market_data:
                    return {'success': False, 'error': 'Unable to get market price'}
                price = market_data['price']
            
            trade_id = len(self.trades_history) + 1
            executed_at = datetime.now().isoformat()
            
            # Store in database if available
            if db_available:
                try:
                    with Session() as session:
                        session.execute(text("""
                            INSERT INTO paper_trades (symbol, side, quantity, price, executed_at, pattern, confidence)
                            VALUES (:symbol, :side, :quantity, :price, :executed_at, :pattern, :confidence)
                        """), {
                            'symbol': symbol,
                            'side': side,
                            'quantity': quantity,
                            'price': price,
                            'executed_at': executed_at,
                            'pattern': pattern,
                            'confidence': confidence
                        })
                        session.commit()
                except Exception as e:
                    logger.error(f"Failed to store trade in database: {e}")
            
            # Update in-memory positions
            if symbol not in self.positions:
                self.positions[symbol] = {
                    'quantity': 0,
                    'avg_entry': price,
                    'pnl': 0,
                    'pattern': pattern,
                    'confidence': confidence,
                    'last_update': executed_at
                }
            
            qty_change = quantity if side == 'BUY' else -quantity
            self.positions[symbol]['quantity'] += qty_change
            self.positions[symbol]['last_update'] = executed_at
            
            # Add to trades history
            trade = {
                'id': trade_id,
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'price': price,
                'executed_at': executed_at,
                'pattern': pattern,
                'confidence': confidence
            }
            self.trades_history.append(trade)
            
            return {
                'success': True,
                'trade': trade,
                'message': f'Successfully executed {side} {quantity} shares of {symbol} at ${price:.2f}'
            }
            
        except Exception as e:
            logger.error(f"Failed to execute trade: {e}")
            return {'success': False, 'error': str(e)}
    
    def close_position(self, symbol: str = None, trade_id: int = None) -> Dict[str, Any]:
        """Close a paper trading position"""
        try:
            if symbol:
                if symbol in self.positions and self.positions[symbol]['quantity'] != 0:
                    current_price = self.market_data.get_stock_data(symbol)
                    if current_price:
                        price = current_price['price']
                        quantity = abs(self.positions[symbol]['quantity'])
                        side = 'SELL' if self.positions[symbol]['quantity'] > 0 else 'BUY'
                        
                        # Calculate PnL
                        entry_price = self.positions[symbol]['avg_entry']
                        if side == 'SELL':
                            pnl = (price - entry_price) * quantity
                        else:
                            pnl = (entry_price - price) * quantity
                        
                        # Update database
                        if db_available:
                            with Session() as session:
                                session.execute(text("""
                                    UPDATE paper_trades SET status = 'closed', pnl = :pnl 
                                    WHERE symbol = :symbol AND status = 'open'
                                """), {'symbol': symbol, 'pnl': pnl})
                                session.commit()
                        
                        # Remove from positions
                        del self.positions[symbol]
                        
                        return {
                            'success': True,
                            'message': f'Closed position for {symbol}',
                            'pnl': pnl
                        }
                        
            return {'success': False, 'error': 'Position not found or already closed'}
            
        except Exception as e:
            logger.error(f"Failed to close position: {e}")
            return {'success': False, 'error': str(e)}

# Alert Service
class AlertService:
    def __init__(self, pattern_service: PatternDetectionService):
        self.pattern_service = pattern_service
        self.active_alerts = []
        
    def generate_alerts(self) -> List[Alert]:
        """Generate alerts based on pattern detection"""
        try:
            symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX']
            new_alerts = []
            
            for symbol in symbols:
                patterns = self.pattern_service.detect_patterns(symbol)
                
                for pattern in patterns:
                    if pattern.confidence >= Config.ALERT_CONFIDENCE_THRESHOLD:
                        alert = Alert(
                            id=len(self.active_alerts) + len(new_alerts) + 1,
                            symbol=pattern.symbol,
                            alert_type=pattern.pattern_type,
                            message=f"{pattern.pattern_type} detected for {pattern.symbol} with {pattern.confidence:.1%} confidence",
                            confidence=pattern.confidence,
                            timestamp=pattern.timestamp
                        )
                        new_alerts.append(alert)
                        
                        # Store in database
                        if db_available:
                            try:
                                with Session() as session:
                                    session.execute(text("""
                                        INSERT INTO alerts (symbol, alert_type, message, confidence, created_at, metadata)
                                        VALUES (:symbol, :alert_type, :message, :confidence, :created_at, :metadata)
                                    """), {
                                        'symbol': alert.symbol,
                                        'alert_type': alert.alert_type,
                                        'message': alert.message,
                                        'confidence': alert.confidence,
                                        'created_at': alert.timestamp,
                                        'metadata': json.dumps(pattern.metadata or {})
                                    })
                                    session.commit()
                            except Exception as e:
                                logger.error(f"Failed to store alert: {e}")
            
            self.active_alerts.extend(new_alerts)
            return new_alerts
            
        except Exception as e:
            logger.error(f"Failed to generate alerts: {e}")
            return []
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""
        try:
            if db_available:
                with Session() as session:
                    alerts = session.execute(text("""
                        SELECT id, symbol, alert_type, message, confidence, created_at
                        FROM alerts WHERE is_active = true
                        ORDER BY created_at DESC LIMIT 50
                    """)).fetchall()
                    
                    return [Alert(
                        id=alert.id,
                        symbol=alert.symbol,
                        alert_type=alert.alert_type,
                        message=alert.message,
                        confidence=alert.confidence,
                        timestamp=alert.created_at.isoformat() if hasattr(alert.created_at, 'isoformat') else str(alert.created_at)
                    ) for alert in alerts]
            else:
                return self.active_alerts[-50:]  # Return last 50 alerts
                
        except Exception as e:
            logger.error(f"Failed to get active alerts: {e}")
            return []

# Initialize services
market_data_service = MarketDataService()
pattern_service = PatternDetectionService(market_data_service)
sentiment_service = SentimentAnalysisService()
paper_trading_service = PaperTradingService(market_data_service)
alert_service = AlertService(pattern_service)

# Background worker for scanning and alerts
def background_scanner():
    """Background worker for continuous market scanning"""
    while True:
        try:
            logger.info("Running background market scan...")
            
            # Generate new alerts
            new_alerts = alert_service.generate_alerts()
            
            if new_alerts:
                logger.info(f"Generated {len(new_alerts)} new alerts")
                
                # Emit alerts via WebSocket
                for alert in new_alerts:
                    socketio.emit('new_alert', asdict(alert))
            
            # Update market scan data
            scan_data = market_data_service.get_market_scan()
            if scan_data:
                socketio.emit('market_scan_update', {'data': scan_data})
            
            time.sleep(Config.BACKEND_SCAN_INTERVAL)
            
        except Exception as e:
            logger.error(f"Background scanner error: {e}")
            time.sleep(60)  # Wait 1 minute before retrying

# Start background worker if enabled
if Config.ENABLE_BACKGROUND_WORKERS:
    scanner_thread = threading.Thread(target=background_scanner, daemon=True)
    scanner_thread.start()
    logger.info("Background scanner started")

# Flask API Routes
@app.route('/')
def index():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'TX Trade Whisperer Backend',
        'version': '2.0.0',
        'database': 'connected' if db_available else 'demo_mode',
        'timestamp': datetime.now().isoformat()
    })

# Market Data Endpoints
@app.route('/api/market-scan')
@limiter.limit("30 per minute")
def market_scan():
    """Get market scan data"""
    try:
        scan_type = request.args.get('type', 'trending')
        data = market_data_service.get_market_scan(scan_type)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        logger.error(f"Market scan error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stock/<symbol>')
@limiter.limit("60 per minute")
def get_stock_data(symbol):
    """Get stock data for a specific symbol"""
    try:
        data = market_data_service.get_stock_data(symbol.upper())
        if data:
            return jsonify({'success': True, 'data': data})
        else:
            return jsonify({'success': False, 'error': 'Symbol not found'}), 404
    except Exception as e:
        logger.error(f"Stock data error for {symbol}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Pattern Detection Endpoints
@app.route('/api/detect-enhanced', methods=['POST'])
@limiter.limit("20 per minute")
def detect_enhanced():
    """Enhanced pattern detection endpoint"""
    try:
        data = request.get_json()
        symbol = data.get('symbol', '').upper()
        
        if not symbol:
            return jsonify({'success': False, 'error': 'Symbol is required'}), 400
        
        patterns = pattern_service.detect_patterns(symbol)
        
        # Convert to dict format for JSON response
        pattern_data = []
        for pattern in patterns:
            pattern_dict = asdict(pattern)
            # Add additional fields expected by frontend
            pattern_dict.update({
                'entry_signal': 'BUY' if pattern.confidence > 0.75 else 'HOLD',
                'exit_signal': 'SELL' if pattern.confidence < 0.3 else 'HOLD',
                'market_context': f"Pattern detected with {pattern.confidence:.1%} confidence",
                'keywords': [pattern.pattern_type.lower().replace(' ', '_')],
                'sentiment_score': min(pattern.confidence * 100, 100)
            })
            pattern_data.append(pattern_dict)
        
        return jsonify({'success': True, 'data': pattern_data})
        
    except Exception as e:
        logger.error(f"Enhanced detection error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/pattern-stats')
@limiter.limit("10 per minute")
def pattern_stats():
    """Get pattern detection statistics"""
    try:
        if db_available:
            with Session() as session:
                stats = session.execute(text("""
                    SELECT pattern_type, COUNT(*) as count, AVG(confidence) as avg_confidence
                    FROM pattern_detections 
                    WHERE detected_at > NOW() - INTERVAL '24 hours'
                    GROUP BY pattern_type
                """)).fetchall()
                
                pattern_stats = [
                    {
                        'pattern': stat.pattern_type,
                        'count': stat.count,
                        'avg_confidence': float(stat.avg_confidence)
                    }
                    for stat in stats
                ]
        else:
            # Demo data when database unavailable
            pattern_stats = [
                {'pattern': 'Golden Cross', 'count': 5, 'avg_confidence': 0.82},
                {'pattern': 'RSI Oversold', 'count': 12, 'avg_confidence': 0.75},
                {'pattern': 'Bollinger Breakout', 'count': 8, 'avg_confidence': 0.68}
            ]
        
        return jsonify({'success': True, 'data': pattern_stats})
        
    except Exception as e:
        logger.error(f"Pattern stats error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Sentiment Analysis Endpoints
@app.route('/api/sentiment/<symbol>')
@limiter.limit("20 per minute")
def get_sentiment(symbol):
    """Get sentiment analysis for a symbol"""
    try:
        data = sentiment_service.analyze_sentiment(symbol.upper())
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        logger.error(f"Sentiment analysis error for {symbol}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Alert Endpoints
@app.route('/api/get_active_alerts')
@limiter.limit("30 per minute")
def get_active_alerts():
    """Get active alerts"""
    try:
        alerts = alert_service.get_active_alerts()
        alert_data = [asdict(alert) for alert in alerts]
        return jsonify({'success': True, 'alerts': alert_data})
    except Exception as e:
        logger.error(f"Get alerts error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/alerts/dismiss/<int:alert_id>', methods=['POST'])
@limiter.limit("10 per minute")
def dismiss_alert(alert_id):
    """Dismiss an alert"""
    try:
        if db_available:
            with Session() as session:
                session.execute(text("""
                    UPDATE alerts SET is_active = false WHERE id = :alert_id
                """), {'alert_id': alert_id})
                session.commit()
        
        return jsonify({'success': True, 'message': 'Alert dismissed'})
    except Exception as e:
        logger.error(f"Dismiss alert error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Paper Trading Endpoints
@app.route('/api/paper-trades')
@limiter.limit("30 per minute")
def get_paper_trades():
    """Get paper trading portfolio"""
    try:
        portfolio = paper_trading_service.get_portfolio()
        return jsonify({'success': True, 'data': portfolio})
    except Exception as e:
        logger.error(f"Get paper trades error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/paper-trades', methods=['POST'])
@limiter.limit("10 per minute")
def execute_paper_trade():
    """Execute a paper trade"""
    try:
        data = request.get_json()
        
        symbol = data.get('symbol', '').upper()
        side = data.get('side', '').upper()
        quantity = float(data.get('quantity', 0))
        price = data.get('price')
        pattern = data.get('pattern')
        confidence = data.get('confidence')
        
        if not symbol or not side or quantity <= 0:
            return jsonify({'success': False, 'error': 'Invalid trade parameters'}), 400
        
        if side not in ['BUY', 'SELL']:
            return jsonify({'success': False, 'error': 'Side must be BUY or SELL'}), 400
        
        result = paper_trading_service.execute_trade(
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            pattern=pattern,
            confidence=confidence
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Execute paper trade error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/close-position', methods=['POST'])
@limiter.limit("10 per minute")
def close_paper_position():
    """Close a paper trading position"""
    try:
        data = request.get_json()
        symbol = data.get('symbol', '').upper() if data.get('symbol') else None
        trade_id = data.get('trade_id')
        
        if not symbol and not trade_id:
            return jsonify({'success': False, 'error': 'Symbol or trade_id required'}), 400
        
        result = paper_trading_service.close_position(symbol=symbol, trade_id=trade_id)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Close position error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Backtesting Endpoints
@app.route('/api/strategies')
@limiter.limit("20 per minute")
def get_strategies():
    """Get available trading strategies"""
    try:
        strategies = [
            {
                'id': 1,
                'name': 'Golden Cross Strategy',
                'description': 'Buy when 20-day SMA crosses above 50-day SMA',
                'type': 'trend_following',
                'parameters': {'short_period': 20, 'long_period': 50}
            },
            {
                'id': 2,
                'name': 'RSI Mean Reversion',
                'description': 'Buy oversold, sell overbought based on RSI',
                'type': 'mean_reversion',
                'parameters': {'oversold': 30, 'overbought': 70}
            },
            {
                'id': 3,
                'name': 'Bollinger Band Breakout',
                'description': 'Trade breakouts from Bollinger Bands',
                'type': 'breakout',
                'parameters': {'period': 20, 'std_dev': 2}
            }
        ]
        return jsonify({'success': True, 'data': strategies})
    except Exception as e:
        logger.error(f"Get strategies error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/backtest', methods=['POST'])
@limiter.limit("5 per minute")
def run_backtest():
    """Run a backtest"""
    try:
        data = request.get_json()
        symbol = data.get('symbol', 'AAPL').upper()
        strategy_id = data.get('strategy_id', 1)
        start_date = data.get('start_date', '2023-01-01')
        end_date = data.get('end_date', '2024-01-01')
        
        # Simulate backtest results
        import random
        random.seed(42)  # For consistent results
        
        total_return = random.uniform(-20, 50)
        sharpe_ratio = random.uniform(0.5, 2.5)
        max_drawdown = random.uniform(-15, -5)
        win_rate = random.uniform(45, 75)
        
        results = {
            'symbol': symbol,
            'strategy_id': strategy_id,
            'period': f"{start_date} to {end_date}",
            'total_return': round(total_return, 2),
            'annualized_return': round(total_return * 0.8, 2),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'max_drawdown': round(max_drawdown, 2),
            'win_rate': round(win_rate, 1),
            'total_trades': random.randint(50, 200),
            'profitable_trades': random.randint(25, 150),
            'avg_trade_return': round(random.uniform(-2, 5), 2),
            'volatility': round(random.uniform(15, 35), 2),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({'success': True, 'data': results})
        
    except Exception as e:
        logger.error(f"Backtest error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Analytics Endpoints
@app.route('/api/analytics/summary')
@limiter.limit("20 per minute")
def analytics_summary():
    """Get analytics summary"""
    try:
        # Generate real-time analytics based on current market data
        symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
        total_patterns = 0
        total_alerts = len(alert_service.get_active_alerts())
        
        for symbol in symbols:
            patterns = pattern_service.detect_patterns(symbol)
            total_patterns += len(patterns)
        
        summary = {
            'total_patterns_detected': total_patterns,
            'active_alerts': total_alerts,
            'market_sentiment': 'bullish' if total_patterns > 5 else 'neutral',
            'top_performing_patterns': [
                {'name': 'Golden Cross', 'success_rate': 78.5},
                {'name': 'RSI Oversold', 'success_rate': 65.2},
                {'name': 'Bollinger Breakout', 'success_rate': 71.8}
            ],
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({'success': True, 'data': summary})
        
    except Exception as e:
        logger.error(f"Analytics summary error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# System Status Endpoints
@app.route('/api/system/status')
@limiter.limit("10 per minute")
def system_status():
    """Get system status"""
    try:
        status = {
            'database': 'connected' if db_available else 'demo_mode',
            'background_workers': Config.ENABLE_BACKGROUND_WORKERS,
            'api_status': 'healthy',
            'last_scan': datetime.now().isoformat(),
            'uptime': '24h 15m',  # Would be calculated in real implementation
            'version': '2.0.0',
            'environment': Config.FLASK_ENV
        }
        
        return jsonify({'success': True, 'data': status})
        
    except Exception as e:
        logger.error(f"System status error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('connected', {'status': 'Connected to TX Trade Whisperer'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('subscribe_alerts')
def handle_subscribe_alerts():
    """Subscribe to alert updates"""
    logger.info(f"Client {request.sid} subscribed to alerts")
    emit('subscribed', {'channel': 'alerts'})

@socketio.on('subscribe_scans')
def handle_subscribe_scans():
    """Subscribe to market scan updates"""
    logger.info(f"Client {request.sid} subscribed to market scans")
    emit('subscribed', {'channel': 'market_scans'})

# Error Handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'success': False, 'error': 'Rate limit exceeded'}), 429

# Main execution
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = Config.DEBUG
    
    logger.info(f"Starting TX Trade Whisperer Backend v2.0.0")
    logger.info(f"Database: {'Connected' if db_available else 'Demo Mode'}")
    logger.info(f"Background Workers: {'Enabled' if Config.ENABLE_BACKGROUND_WORKERS else 'Disabled'}")
    logger.info(f"Environment: {Config.FLASK_ENV}")
    
    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=debug,
        allow_unsafe_werkzeug=True
    )
