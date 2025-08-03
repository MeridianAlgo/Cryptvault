"""Time-based feature extraction for ML models."""

import numpy as np
from typing import List
from datetime import datetime
import logging

from ...data.models import PriceDataFrame


class TimeFeatureExtractor:
    """Extract time-based features for ML models."""
    
    def __init__(self):
        """Initialize time feature extractor."""
        self.logger = logging.getLogger(__name__)
    
    def extract(self, data: PriceDataFrame) -> List[float]:
        """
        Extract time-based features.
        
        Args:
            data: Price data frame
            
        Returns:
            List of time-based features
        """
        try:
            features = []
            
            if not data.data:
                return [0.0] * 10  # Return zeros if no data
            
            # Get the most recent timestamp
            latest_time = data.data[-1].timestamp
            
            # Day of week features (0=Monday, 6=Sunday)
            day_of_week = latest_time.weekday()
            dow_features = [1.0 if i == day_of_week else 0.0 for i in range(7)]
            features.extend(dow_features)
            
            # Hour of day features (normalized)
            hour_of_day = latest_time.hour / 23.0  # Normalize to 0-1
            features.append(hour_of_day)
            
            # Month seasonality
            month = latest_time.month
            month_sin = np.sin(2 * np.pi * month / 12)
            month_cos = np.cos(2 * np.pi * month / 12)
            features.extend([month_sin, month_cos])
            
            # Quarter of year
            quarter = (month - 1) // 3
            quarter_features = [1.0 if i == quarter else 0.0 for i in range(4)]
            features.extend(quarter_features)
            
            # Weekend flag
            is_weekend = 1.0 if day_of_week >= 5 else 0.0
            features.append(is_weekend)
            
            # Market session indicators (assuming UTC times)
            # Asian session: 00:00-08:00 UTC
            # European session: 08:00-16:00 UTC  
            # US session: 16:00-00:00 UTC
            hour = latest_time.hour
            asian_session = 1.0 if 0 <= hour < 8 else 0.0
            european_session = 1.0 if 8 <= hour < 16 else 0.0
            us_session = 1.0 if 16 <= hour < 24 else 0.0
            
            features.extend([asian_session, european_session, us_session])
            
            self.logger.debug(f"Extracted {len(features)} time features")
            return features
            
        except Exception as e:
            self.logger.error(f"Time feature extraction failed: {e}")
            return [0.0] * 18  # Return zeros as fallback
    
    def get_feature_names(self) -> List[str]:
        """Get names of all extracted features."""
        return [
            # Day of week (one-hot encoded)
            'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
            # Hour of day
            'hour_normalized',
            # Month seasonality
            'month_sin', 'month_cos',
            # Quarter (one-hot encoded)
            'q1', 'q2', 'q3', 'q4',
            # Weekend flag
            'is_weekend',
            # Market sessions
            'asian_session', 'european_session', 'us_session'
        ]