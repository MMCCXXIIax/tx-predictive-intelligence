"""
Deep Learning Pattern Detector using CNN/LSTM
End-to-end pattern detection from raw OHLCV data without hand-crafted rules.
"""

import os
import logging
import pickle
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from dataclasses import dataclass

import numpy as np
import pandas as pd
import yfinance as yf

# Deep learning
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import Dataset, DataLoader
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logging.warning("PyTorch not available. Deep pattern detector disabled.")

logger = logging.getLogger(__name__)


@dataclass
class PatternPrediction:
    """Deep learning pattern prediction result"""
    symbol: str
    pattern_type: str
    confidence: float
    timestamp: str
    price: float
    volume: int
    metadata: Dict[str, Any]


class OHLCVDataset(Dataset):
    """PyTorch dataset for OHLCV sequences"""
    
    def __init__(self, sequences: np.ndarray, labels: np.ndarray):
        self.sequences = torch.FloatTensor(sequences)
        self.labels = torch.FloatTensor(labels)
    
    def __len__(self):
        return len(self.sequences)
    
    def __getitem__(self, idx):
        return self.sequences[idx], self.labels[idx]


class CNNLSTMPatternDetector(nn.Module):
    """
    Hybrid CNN-LSTM architecture for pattern detection
    - CNN extracts local patterns from OHLCV sequences
    - LSTM captures temporal dependencies
    - Attention mechanism focuses on important time steps
    """
    
    def __init__(self, input_channels=5, sequence_length=50, num_patterns=10, 
                 cnn_filters=64, lstm_hidden=128, dropout=0.3):
        super(CNNLSTMPatternDetector, self).__init__()
        
        self.sequence_length = sequence_length
        self.num_patterns = num_patterns
        
        # 1D CNN for local feature extraction
        self.conv1 = nn.Conv1d(input_channels, cnn_filters, kernel_size=3, padding=1)
        self.conv2 = nn.Conv1d(cnn_filters, cnn_filters * 2, kernel_size=3, padding=1)
        self.pool = nn.MaxPool1d(2)
        self.bn1 = nn.BatchNorm1d(cnn_filters)
        self.bn2 = nn.BatchNorm1d(cnn_filters * 2)
        
        # LSTM for temporal dependencies
        self.lstm = nn.LSTM(
            input_size=cnn_filters * 2,
            hidden_size=lstm_hidden,
            num_layers=2,
            batch_first=True,
            dropout=dropout,
            bidirectional=True
        )
        
        # Attention mechanism
        self.attention = nn.Linear(lstm_hidden * 2, 1)
        
        # Output layers
        self.dropout = nn.Dropout(dropout)
        self.fc1 = nn.Linear(lstm_hidden * 2, 128)
        self.fc2 = nn.Linear(128, num_patterns)
        
        self.relu = nn.ReLU()
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        # x shape: (batch, sequence_length, channels)
        x = x.permute(0, 2, 1)  # (batch, channels, sequence_length)
        
        # CNN layers
        x = self.relu(self.bn1(self.conv1(x)))
        x = self.pool(x)
        x = self.relu(self.bn2(self.conv2(x)))
        x = self.pool(x)
        
        # Prepare for LSTM
        x = x.permute(0, 2, 1)  # (batch, seq_len, features)
        
        # LSTM
        lstm_out, _ = self.lstm(x)  # (batch, seq_len, hidden*2)
        
        # Attention
        attention_weights = torch.softmax(self.attention(lstm_out), dim=1)
        context = torch.sum(attention_weights * lstm_out, dim=1)
        
        # Fully connected
        x = self.dropout(context)
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.sigmoid(self.fc2(x))
        
        return x


class DeepPatternDetectorSystem:
    """
    End-to-end deep learning pattern detection system
    """
    
    def __init__(self, model_dir: str = 'models/deep_patterns'):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
        self.sequence_length = 50
        self.pattern_names = [
            'DOUBLE_TOP', 'DOUBLE_BOTTOM', 'HEAD_SHOULDERS', 
            'INVERSE_HEAD_SHOULDERS', 'ASCENDING_TRIANGLE', 
            'DESCENDING_TRIANGLE', 'BULL_FLAG', 'BEAR_FLAG',
            'WEDGE_RISING', 'WEDGE_FALLING'
        ]
        
        self.model = None
        self.scaler_mean = None
        self.scaler_std = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        if TORCH_AVAILABLE:
            self._initialize_model()
    
    def _initialize_model(self):
        """Initialize or load model"""
        model_path = os.path.join(self.model_dir, 'cnn_lstm_model.pth')
        scaler_path = os.path.join(self.model_dir, 'scaler.pkl')
        
        if os.path.exists(model_path):
            try:
                self.model = CNNLSTMPatternDetector(
                    input_channels=5,
                    sequence_length=self.sequence_length,
                    num_patterns=len(self.pattern_names)
                ).to(self.device)
                self.model.load_state_dict(torch.load(model_path, map_location=self.device))
                self.model.eval()
                
                with open(scaler_path, 'rb') as f:
                    scaler_data = pickle.load(f)
                    self.scaler_mean = scaler_data['mean']
                    self.scaler_std = scaler_data['std']
                
                logger.info("Deep pattern detector model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                self._create_new_model()
        else:
            self._create_new_model()
    
    def _create_new_model(self):
        """Create new untrained model"""
        self.model = CNNLSTMPatternDetector(
            input_channels=5,
            sequence_length=self.sequence_length,
            num_patterns=len(self.pattern_names)
        ).to(self.device)
        logger.info("Created new deep pattern detector model")
    
    def _prepare_sequences(self, df: pd.DataFrame) -> np.ndarray:
        """Convert OHLCV dataframe to sequences"""
        if len(df) < self.sequence_length:
            return np.array([])
        
        # Extract OHLCV
        ohlcv = df[['open', 'high', 'low', 'close', 'volume']].values
        
        # Normalize if scaler available
        if self.scaler_mean is not None and self.scaler_std is not None:
            ohlcv = (ohlcv - self.scaler_mean) / (self.scaler_std + 1e-8)
        
        # Create sliding windows
        sequences = []
        for i in range(len(ohlcv) - self.sequence_length + 1):
            sequences.append(ohlcv[i:i + self.sequence_length])
        
        return np.array(sequences)
    
    def detect_patterns(self, symbol: str, timeframe: str = '1h') -> List[PatternPrediction]:
        """
        Detect patterns in recent data using deep learning
        """
        if not TORCH_AVAILABLE or self.model is None:
            return []
        
        try:
            # Download data
            df = self._download_data(symbol, timeframe)
            if df.empty or len(df) < self.sequence_length:
                return []
            
            # Prepare sequences
            sequences = self._prepare_sequences(df)
            if len(sequences) == 0:
                return []
            
            # Predict
            self.model.eval()
            with torch.no_grad():
                # Use only the most recent sequence
                recent_seq = torch.FloatTensor(sequences[-1:]).to(self.device)
                predictions = self.model(recent_seq).cpu().numpy()[0]
            
            # Convert to pattern predictions
            results = []
            threshold = 0.5  # Confidence threshold
            
            for idx, confidence in enumerate(predictions):
                if confidence >= threshold:
                    pattern_type = self.pattern_names[idx]
                    latest_candle = df.iloc[-1]
                    
                    results.append(PatternPrediction(
                        symbol=symbol,
                        pattern_type=pattern_type,
                        confidence=float(confidence),
                        timestamp=datetime.now().isoformat(),
                        price=float(latest_candle['close']),
                        volume=int(latest_candle['volume']),
                        metadata={
                            'timeframe': timeframe,
                            'detector': 'deep_cnn_lstm',
                            'sequence_length': self.sequence_length
                        }
                    ))
            
            return results
        
        except Exception as e:
            logger.error(f"Deep pattern detection failed for {symbol}: {e}")
            return []
    
    def _download_data(self, symbol: str, timeframe: str) -> pd.DataFrame:
        """Download OHLCV data"""
        try:
            tf_map = {
                '1m': '1m', '5m': '5m', '15m': '15m', '30m': '30m',
                '1h': '60m', '4h': '240m', '1d': '1d'
            }
            interval = tf_map.get(timeframe, timeframe)
            
            df = yf.download(symbol, period='5d', interval=interval, 
                           progress=False, auto_adjust=True)
            
            if isinstance(df, pd.DataFrame) and not df.empty:
                df.columns = [c.lower() for c in df.columns]
                return df
            
            return pd.DataFrame()
        
        except Exception as e:
            logger.error(f"Data download failed for {symbol}: {e}")
            return pd.DataFrame()
    
    def train(self, training_data: List[Tuple[pd.DataFrame, List[int]]], 
              epochs: int = 50, batch_size: int = 32, learning_rate: float = 0.001):
        """
        Train the deep pattern detector
        training_data: List of (dataframe, labels) where labels is list of pattern indices
        """
        if not TORCH_AVAILABLE:
            logger.error("PyTorch not available for training")
            return {'success': False, 'error': 'PyTorch not installed'}
        
        try:
            # Prepare dataset
            all_sequences = []
            all_labels = []
            
            for df, pattern_labels in training_data:
                sequences = self._prepare_sequences(df)
                if len(sequences) == 0:
                    continue
                
                # Create multi-hot encoded labels
                label_vector = np.zeros(len(self.pattern_names))
                for pattern_idx in pattern_labels:
                    if 0 <= pattern_idx < len(self.pattern_names):
                        label_vector[pattern_idx] = 1.0
                
                all_sequences.append(sequences[-1])  # Use most recent sequence
                all_labels.append(label_vector)
            
            if len(all_sequences) < 10:
                return {'success': False, 'error': 'Insufficient training data'}
            
            # Fit scaler
            all_data = np.concatenate(all_sequences, axis=0)
            self.scaler_mean = np.mean(all_data, axis=0)
            self.scaler_std = np.std(all_data, axis=0)
            
            # Normalize
            normalized_sequences = [
                (seq - self.scaler_mean) / (self.scaler_std + 1e-8)
                for seq in all_sequences
            ]
            
            # Create dataset
            dataset = OHLCVDataset(
                np.array(normalized_sequences),
                np.array(all_labels)
            )
            dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
            
            # Training setup
            criterion = nn.BCELoss()
            optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
            
            # Training loop
            self.model.train()
            for epoch in range(epochs):
                total_loss = 0
                for sequences, labels in dataloader:
                    sequences = sequences.to(self.device)
                    labels = labels.to(self.device)
                    
                    optimizer.zero_grad()
                    outputs = self.model(sequences)
                    loss = criterion(outputs, labels)
                    loss.backward()
                    optimizer.step()
                    
                    total_loss += loss.item()
                
                if (epoch + 1) % 10 == 0:
                    avg_loss = total_loss / len(dataloader)
                    logger.info(f"Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.4f}")
            
            # Save model
            model_path = os.path.join(self.model_dir, 'cnn_lstm_model.pth')
            torch.save(self.model.state_dict(), model_path)
            
            scaler_path = os.path.join(self.model_dir, 'scaler.pkl')
            with open(scaler_path, 'wb') as f:
                pickle.dump({
                    'mean': self.scaler_mean,
                    'std': self.scaler_std
                }, f)
            
            return {
                'success': True,
                'epochs': epochs,
                'samples': len(all_sequences),
                'final_loss': total_loss / len(dataloader)
            }
        
        except Exception as e:
            logger.error(f"Training failed: {e}")
            return {'success': False, 'error': str(e)}


# Singleton instance
_deep_detector = None

def get_deep_detector() -> DeepPatternDetectorSystem:
    """Get or create deep pattern detector instance"""
    global _deep_detector
    if _deep_detector is None:
        _deep_detector = DeepPatternDetectorSystem()
    return _deep_detector


def detect_patterns_deep(symbol: str, timeframe: str = '1h') -> Dict[str, Any]:
    """
    Wrapper function for deep pattern detection
    Returns dict compatible with existing API
    """
    try:
        detector = get_deep_detector()
        predictions = detector.detect_patterns(symbol, timeframe)
        
        return {
            'success': True,
            'symbol': symbol,
            'timeframe': timeframe,
            'patterns': [
                {
                    'pattern_type': p.pattern_type,
                    'confidence': p.confidence,
                    'price': p.price,
                    'volume': p.volume,
                    'timestamp': p.timestamp,
                    'metadata': p.metadata
                }
                for p in predictions
            ],
            'detector': 'deep_cnn_lstm'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
