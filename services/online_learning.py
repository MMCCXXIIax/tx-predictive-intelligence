"""
Online/Incremental Learning System
Updates ML models incrementally as new outcomes arrive without full retraining
Uses Passive-Aggressive algorithms and incremental ensemble methods
"""

import os
import logging
import pickle
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from collections import deque

import numpy as np
import pandas as pd

# Incremental learning algorithms
from sklearn.linear_model import PassiveAggressiveClassifier, SGDClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, accuracy_score

logger = logging.getLogger(__name__)


class IncrementalModel:
    """
    Wrapper for incremental learning model with online updates
    """
    
    def __init__(self, model_type: str = 'passive_aggressive'):
        self.model_type = model_type
        self.model = self._create_model()
        self.scaler = StandardScaler()
        self.is_fitted = False
        self.n_samples_seen = 0
        self.performance_history = deque(maxlen=100)
        self.feature_names = []
        
        # Performance tracking
        self.recent_predictions = deque(maxlen=50)
        self.recent_actuals = deque(maxlen=50)
    
    def _create_model(self):
        """Create incremental learning model"""
        if self.model_type == 'passive_aggressive':
            return PassiveAggressiveClassifier(
                C=0.01,
                max_iter=1,
                warm_start=True,
                random_state=42
            )
        elif self.model_type == 'sgd':
            return SGDClassifier(
                loss='log_loss',
                penalty='l2',
                alpha=0.0001,
                max_iter=1,
                warm_start=True,
                random_state=42
            )
        else:
            return PassiveAggressiveClassifier(C=0.01, max_iter=1, warm_start=True)
    
    def partial_fit(self, X: np.ndarray, y: np.ndarray, classes: Optional[np.ndarray] = None):
        """
        Incrementally update model with new data
        
        Args:
            X: Feature matrix (n_samples, n_features)
            y: Labels (n_samples,)
            classes: Class labels (required for first call)
        """
        try:
            if not self.is_fitted:
                # First fit: initialize scaler
                self.scaler.fit(X)
                self.is_fitted = True
                classes = classes if classes is not None else np.array([0, 1])
            
            # Scale features
            X_scaled = self.scaler.transform(X)
            
            # Partial fit
            if not self.is_fitted:
                self.model.partial_fit(X_scaled, y, classes=classes)
            else:
                self.model.partial_fit(X_scaled, y)
            
            self.n_samples_seen += len(y)
            
            # Track performance
            if len(self.recent_actuals) >= 10:
                try:
                    auc = roc_auc_score(
                        list(self.recent_actuals),
                        list(self.recent_predictions)
                    )
                    self.performance_history.append(auc)
                except:
                    pass
            
            return True
        
        except Exception as e:
            logger.error(f"Partial fit failed: {e}")
            return False
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict probabilities"""
        if not self.is_fitted:
            # Return neutral probabilities if not fitted
            return np.full((len(X), 2), 0.5)
        
        X_scaled = self.scaler.transform(X)
        
        # Some models don't have predict_proba
        if hasattr(self.model, 'predict_proba'):
            return self.model.predict_proba(X_scaled)
        else:
            # Use decision function as proxy
            decision = self.model.decision_function(X_scaled)
            # Convert to probabilities using sigmoid
            proba_positive = 1 / (1 + np.exp(-decision))
            return np.column_stack([1 - proba_positive, proba_positive])
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict class labels"""
        if not self.is_fitted:
            return np.zeros(len(X), dtype=int)
        
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)
    
    def update_with_feedback(self, X: np.ndarray, y_pred: np.ndarray, y_actual: np.ndarray):
        """
        Update model with actual outcomes (feedback loop)
        
        Args:
            X: Features used for prediction
            y_pred: Predicted probabilities
            y_actual: Actual outcomes
        """
        # Store for performance tracking
        for pred, actual in zip(y_pred, y_actual):
            self.recent_predictions.append(pred)
            self.recent_actuals.append(actual)
        
        # Incremental update
        self.partial_fit(X, y_actual)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get recent performance metrics"""
        if len(self.recent_actuals) < 10:
            return {
                'n_samples': self.n_samples_seen,
                'recent_samples': len(self.recent_actuals),
                'status': 'insufficient_data'
            }
        
        try:
            preds = list(self.recent_predictions)
            actuals = list(self.recent_actuals)
            
            binary_preds = [1 if p >= 0.5 else 0 for p in preds]
            
            metrics = {
                'n_samples': self.n_samples_seen,
                'recent_samples': len(actuals),
                'auc': roc_auc_score(actuals, preds),
                'accuracy': accuracy_score(actuals, binary_preds),
                'avg_auc_last_100': np.mean(list(self.performance_history)) if self.performance_history else 0.0,
                'status': 'active'
            }
            return metrics
        except Exception as e:
            return {
                'n_samples': self.n_samples_seen,
                'error': str(e),
                'status': 'error'
            }


class OnlineLearningSystem:
    """
    Manages online learning for multiple models (per asset class, timeframe, etc.)
    """
    
    def __init__(self, model_dir: str = 'models/online'):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
        self.models: Dict[str, IncrementalModel] = {}
        self.update_queue = deque(maxlen=1000)
        
        self._load_models()
    
    def _model_key(self, asset_class: str, timeframe: str, regime: str = 'all') -> str:
        """Generate unique key for model"""
        return f"{asset_class}_{timeframe}_{regime}"
    
    def _load_models(self):
        """Load existing online models"""
        try:
            for filename in os.listdir(self.model_dir):
                if filename.endswith('_online.pkl'):
                    key = filename.replace('_online.pkl', '')
                    filepath = os.path.join(self.model_dir, filename)
                    
                    with open(filepath, 'rb') as f:
                        self.models[key] = pickle.load(f)
                    
                    logger.info(f"Loaded online model: {key}")
        except Exception as e:
            logger.error(f"Failed to load online models: {e}")
    
    def _save_model(self, key: str):
        """Save a specific model"""
        try:
            filepath = os.path.join(self.model_dir, f"{key}_online.pkl")
            with open(filepath, 'wb') as f:
                pickle.dump(self.models[key], f)
        except Exception as e:
            logger.error(f"Failed to save model {key}: {e}")
    
    def get_or_create_model(self, asset_class: str, timeframe: str, 
                           regime: str = 'all') -> IncrementalModel:
        """Get existing model or create new one"""
        key = self._model_key(asset_class, timeframe, regime)
        
        if key not in self.models:
            self.models[key] = IncrementalModel(model_type='passive_aggressive')
            logger.info(f"Created new online model: {key}")
        
        return self.models[key]
    
    def update_model(self, asset_class: str, timeframe: str, regime: str,
                    X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """
        Update model incrementally with new data
        
        Args:
            asset_class: Asset class (equity, crypto, fx)
            timeframe: Timeframe (1h, 4h, 1d)
            regime: Market regime
            X: Feature matrix
            y: Labels
        
        Returns:
            Update result
        """
        try:
            model = self.get_or_create_model(asset_class, timeframe, regime)
            
            success = model.partial_fit(X, y)
            
            if success:
                # Save periodically
                if model.n_samples_seen % 50 == 0:
                    self._save_model(self._model_key(asset_class, timeframe, regime))
                
                return {
                    'success': True,
                    'model_key': self._model_key(asset_class, timeframe, regime),
                    'n_samples_seen': model.n_samples_seen,
                    'performance': model.get_performance_metrics()
                }
            else:
                return {'success': False, 'error': 'Partial fit failed'}
        
        except Exception as e:
            logger.error(f"Model update failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def predict(self, asset_class: str, timeframe: str, regime: str,
               X: np.ndarray) -> Dict[str, Any]:
        """
        Make prediction using online model
        
        Returns:
            Prediction result with probabilities
        """
        try:
            model = self.get_or_create_model(asset_class, timeframe, regime)
            
            if not model.is_fitted:
                return {
                    'success': False,
                    'error': 'Model not yet fitted',
                    'prediction': 0.5
                }
            
            proba = model.predict_proba(X)
            prediction = proba[:, 1]  # Probability of positive class
            
            return {
                'success': True,
                'prediction': float(prediction[0]) if len(prediction) > 0 else 0.5,
                'probabilities': proba.tolist(),
                'model_key': self._model_key(asset_class, timeframe, regime),
                'n_samples_seen': model.n_samples_seen,
                'performance': model.get_performance_metrics()
            }
        
        except Exception as e:
            logger.error(f"Online prediction failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'prediction': 0.5
            }
    
    def queue_update(self, asset_class: str, timeframe: str, regime: str,
                    features: np.ndarray, label: int):
        """
        Queue an update for batch processing
        Useful for real-time systems to avoid blocking
        """
        self.update_queue.append({
            'asset_class': asset_class,
            'timeframe': timeframe,
            'regime': regime,
            'features': features,
            'label': label,
            'timestamp': datetime.now()
        })
    
    def process_update_queue(self, batch_size: int = 10) -> Dict[str, Any]:
        """
        Process queued updates in batches
        
        Returns:
            Processing statistics
        """
        if len(self.update_queue) == 0:
            return {'processed': 0, 'message': 'Queue empty'}
        
        processed = 0
        errors = 0
        
        # Group by model key
        batches = {}
        
        for _ in range(min(batch_size, len(self.update_queue))):
            item = self.update_queue.popleft()
            key = self._model_key(item['asset_class'], item['timeframe'], item['regime'])
            
            if key not in batches:
                batches[key] = {'X': [], 'y': [], 'metadata': item}
            
            batches[key]['X'].append(item['features'])
            batches[key]['y'].append(item['label'])
        
        # Update each model with its batch
        for key, batch in batches.items():
            try:
                X = np.vstack(batch['X'])
                y = np.array(batch['y'])
                
                meta = batch['metadata']
                result = self.update_model(
                    meta['asset_class'],
                    meta['timeframe'],
                    meta['regime'],
                    X, y
                )
                
                if result['success']:
                    processed += len(y)
                else:
                    errors += 1
            
            except Exception as e:
                logger.error(f"Batch update failed for {key}: {e}")
                errors += 1
        
        return {
            'processed': processed,
            'errors': errors,
            'queue_remaining': len(self.update_queue)
        }
    
    def get_all_models_status(self) -> Dict[str, Any]:
        """Get status of all online models"""
        status = {}
        
        for key, model in self.models.items():
            status[key] = {
                'n_samples': model.n_samples_seen,
                'is_fitted': model.is_fitted,
                'performance': model.get_performance_metrics()
            }
        
        return {
            'total_models': len(self.models),
            'models': status,
            'queue_size': len(self.update_queue)
        }


# Singleton instance
_online_system = None

def get_online_learning_system() -> OnlineLearningSystem:
    """Get or create online learning system instance"""
    global _online_system
    if _online_system is None:
        _online_system = OnlineLearningSystem()
    return _online_system
