"""LSTM Neural Network for cryptocurrency price prediction using PyTorch."""

import numpy as np
from typing import List, Tuple, Optional, Dict
import logging
import warnings

# Suppress warnings
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, TensorDataset
    
    # Suppress PyTorch warnings
    torch.set_warn_always(False)
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False

from ...data.models import PriceDataFrame


class LSTMNet(nn.Module):
    """PyTorch LSTM Network."""
    
    def __init__(self, input_size: int, hidden_size: int = 128, num_layers: int = 2):
        super(LSTMNet, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=0.2)
        self.fc = nn.Linear(hidden_size, 1)
        
    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])


class LSTMPredictor:
    """LSTM predictor using PyTorch."""
    
    def __init__(self, sequence_length: int = 60, hidden_units: int = 128):
        self.sequence_length = sequence_length
        self.hidden_units = hidden_units
        self.logger = logging.getLogger(__name__)
        
        self.model = None
        self.scaler = None
        self.is_trained = False
        
        if not PYTORCH_AVAILABLE:
            self.logger.warning("PyTorch not available. LSTM will use fallback.")
    
    def train(self, features: np.ndarray, targets: np.ndarray) -> bool:
        """Train LSTM model."""
        if not PYTORCH_AVAILABLE:
            return self._fallback_training(features, targets)
        
        try:
            if len(features) < self.sequence_length + 10:
                # Insufficient data - use fallback silently
                return False
            
            # Prepare sequences
            X, y = self._prepare_sequences(features, targets)
            if len(X) < 10:
                return False
            
            # Create model
            input_size = X.shape[2]
            self.model = LSTMNet(input_size, self.hidden_units)
            
            # Convert to tensors
            X_tensor = torch.FloatTensor(X)
            y_tensor = torch.FloatTensor(y).unsqueeze(1)
            
            # Training setup
            criterion = nn.MSELoss()
            optimizer = optim.Adam(self.model.parameters(), lr=0.001)
            
            # Simple training loop
            self.model.train()
            for epoch in range(50):
                optimizer.zero_grad()
                outputs = self.model(X_tensor)
                loss = criterion(outputs, y_tensor)
                loss.backward()
                optimizer.step()
            
            self.is_trained = True
            return True
            
        except Exception as e:
            self.logger.error(f"LSTM training failed: {e}")
            return self._fallback_training(features, targets)
    
    def predict(self, features: np.ndarray) -> np.ndarray:
        """Make predictions."""
        if not PYTORCH_AVAILABLE or not self.is_trained:
            return self._fallback_predictions(features)
        
        try:
            # Prepare input
            if len(features.shape) == 1:
                features = features.reshape(1, -1)
            
            # Create sequence
            if len(features) >= self.sequence_length:
                X = features[-self.sequence_length:].reshape(1, self.sequence_length, -1)
            else:
                # Pad if needed
                pad_size = self.sequence_length - len(features)
                padding = np.zeros((pad_size, features.shape[1]))
                X = np.vstack([padding, features]).reshape(1, self.sequence_length, -1)
            
            # Predict
            self.model.eval()
            with torch.no_grad():
                X_tensor = torch.FloatTensor(X)
                prediction = self.model(X_tensor).numpy()
            
            return prediction.flatten()
            
        except Exception as e:
            self.logger.error(f"LSTM prediction failed: {e}")
            return self._fallback_predictions(features)
    
    def predict_sequence(self, features: np.ndarray, steps: int = 7) -> List[float]:
        """Predict sequence of future values."""
        if not PYTORCH_AVAILABLE or not self.is_trained:
            return self._fallback_sequence(steps)
        
        try:
            predictions = []
            current_features = features.copy()
            
            for _ in range(steps):
                pred = self.predict(current_features)
                predictions.append(float(pred[0]))
                
                # Update features (simple approach)
                if len(current_features) > 0:
                    current_features = np.roll(current_features, -1, axis=0)
                    current_features[-1] = pred[0] * 0.01  # Small change
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Sequence prediction failed: {e}")
            return self._fallback_sequence(steps)
    
    def _prepare_sequences(self, features: np.ndarray, targets: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare sequences for LSTM."""
        X, y = [], []
        
        for i in range(self.sequence_length, len(features)):
            X.append(features[i-self.sequence_length:i])
            y.append(targets[i])
        
        return np.array(X), np.array(y)
    
    def _fallback_training(self, features: np.ndarray, targets: np.ndarray) -> bool:
        """Fallback training."""
        self.trend = np.mean(np.diff(targets)) if len(targets) > 1 else 0.0
        self.is_trained = True
        return True
    
    def _fallback_predictions(self, features: np.ndarray) -> np.ndarray:
        """Fallback predictions."""
        trend = getattr(self, 'trend', 0.01)
        n_samples = len(features) if len(features.shape) > 1 else 1
        return np.array([trend] * n_samples)
    
    def _fallback_sequence(self, steps: int) -> List[float]:
        """Fallback sequence predictions."""
        trend = getattr(self, 'trend', 0.01)
        return [trend * (i + 1) * 0.1 for i in range(steps)]