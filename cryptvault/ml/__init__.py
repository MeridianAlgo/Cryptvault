"""
Machine Learning Module

This module provides comprehensive ML functionality for cryptocurrency price prediction:
- Feature extraction from technical indicators, patterns, and time data
- Multiple ML models (Linear, LSTM, Ensemble)
- Prediction caching with accuracy tracking
- Clean prediction interface with error handling

Main Components:
- MLPredictor: Main interface for generating predictions
- TechnicalFeatureExtractor: Extract features from technical indicators
- PatternFeatureExtractor: Extract features from chart patterns
- TimeFeatureExtractor: Extract time-based features
- LinearPredictor: Simple linear regression model
- LSTMPredictor: LSTM neural network model (requires PyTorch)
- EnsembleModel: Ensemble combining multiple models
- PredictionCache: Cache predictions with accuracy tracking

Usage:
    from cryptvault.ml import MLPredictor

    predictor = MLPredictor()
    result = predictor.predict(price_data, patterns, horizon=7)
    print(f"Trend: {result['trend_forecast']['trend_7d']}")
"""

from .predictor import MLPredictor
from .features import TechnicalFeatureExtractor, PatternFeatureExtractor, TimeFeatureExtractor
from .models import LinearPredictor, EnsembleModel
from .cache import PredictionCache

__all__ = [
    'MLPredictor',
    'TechnicalFeatureExtractor',
    'PatternFeatureExtractor',
    'TimeFeatureExtractor',
    'LinearPredictor',
    'EnsembleModel',
    'PredictionCache',
]
