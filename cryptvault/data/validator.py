"""Data validation utilities."""

from typing import Dict, Any, List
from .models import PriceDataFrame


class DataValidator:
    """Validate price data quality."""
    
    def validate_price_dataframe(self, data_frame: PriceDataFrame) -> Dict[str, Any]:
        """Validate price data frame."""
        errors = []
        warnings = []
        
        if len(data_frame) == 0:
            errors.append("Empty data frame")
            return {
                'is_valid': False,
                'errors': errors,
                'warnings': warnings,
                'suggestions': ['Provide price data'],
                'statistics': {}
            }
        
        # Check for invalid prices
        for i, point in enumerate(data_frame.data):
            if point.high < point.low:
                errors.append(f"Invalid price at index {i}: high < low")
            if point.close < 0 or point.open < 0:
                errors.append(f"Negative price at index {i}")
            if point.volume < 0:
                errors.append(f"Negative volume at index {i}")
        
        # Calculate statistics
        closes = data_frame.get_closes()
        volumes = data_frame.get_volumes()
        
        statistics = {
            'data_points': len(data_frame),
            'price_range': {
                'min': min(closes),
                'max': max(closes),
                'current': closes[-1] if closes else 0
            },
            'volume': {
                'avg': sum(volumes) / len(volumes) if volumes else 0,
                'total': sum(volumes)
            }
        }
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'suggestions': [] if len(errors) == 0 else ['Fix data quality issues'],
            'statistics': statistics
        }
