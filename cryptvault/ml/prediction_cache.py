"""
Advanced Prediction Cache System
Stores predictions with timestamps and tracks accuracy over time
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class PredictionRecord:
    """Individual prediction record with metadata"""
    symbol: str
    prediction_date: datetime
    prediction_type: str  # 'price', 'trend', 'pattern'
    predicted_value: Any
    actual_value: Optional[Any] = None
    confidence: float = 0.0
    timeframe: str = '1d'
    target_date: datetime = None
    accuracy_score: Optional[float] = None
    verified: bool = False
    model_version: str = '2.0'
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        # Convert datetime objects to ISO strings
        data['prediction_date'] = self.prediction_date.isoformat()
        if self.target_date:
            data['target_date'] = self.target_date.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PredictionRecord':
        """Create from dictionary"""
        # Convert ISO strings back to datetime objects
        data['prediction_date'] = datetime.fromisoformat(data['prediction_date'])
        if data.get('target_date'):
            data['target_date'] = datetime.fromisoformat(data['target_date'])
        return cls(**data)


class PredictionCache:
    """Advanced prediction caching system with accuracy tracking"""
    
    def __init__(self, cache_dir: str = '.cryptvault_predictions'):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
        # Cache files
        self.predictions_file = self.cache_dir / 'predictions.json'
        self.accuracy_file = self.cache_dir / 'accuracy_stats.json'
        
        # Load existing data
        self.predictions: List[PredictionRecord] = self._load_predictions()
        self.accuracy_stats = self._load_accuracy_stats()
    
    def store_prediction(self, symbol: str, prediction_type: str, 
                        predicted_value: Any, confidence: float = 0.0,
                        timeframe: str = '1d', days_ahead: int = 7) -> str:
        """Store a new prediction"""
        
        prediction_date = datetime.now()
        target_date = prediction_date + timedelta(days=days_ahead)
        
        record = PredictionRecord(
            symbol=symbol.upper(),
            prediction_date=prediction_date,
            prediction_type=prediction_type,
            predicted_value=predicted_value,
            confidence=confidence,
            timeframe=timeframe,
            target_date=target_date
        )
        
        self.predictions.append(record)
        self._save_predictions()
        
        prediction_id = f"{symbol}_{prediction_type}_{prediction_date.strftime('%Y%m%d_%H%M%S')}"
        self.logger.info(f"Stored prediction {prediction_id}: {predicted_value} (confidence: {confidence:.1%})")
        
        return prediction_id
    
    def verify_predictions(self, current_prices: Dict[str, float]) -> Dict[str, Any]:
        """Verify predictions against actual prices and update accuracy"""
        
        verification_results = {
            'verified_count': 0,
            'accurate_predictions': 0,
            'total_error': 0.0,
            'accuracy_by_symbol': {},
            'accuracy_by_timeframe': {}
        }
        
        now = datetime.now()
        
        for prediction in self.predictions:
            # Skip if already verified or target date not reached
            if prediction.verified or not prediction.target_date or now < prediction.target_date:
                continue
            
            # Skip if we don't have current price data
            if prediction.symbol not in current_prices:
                continue
            
            actual_price = current_prices[prediction.symbol]
            
            # Verify price predictions
            if prediction.prediction_type == 'price':
                predicted_price = float(prediction.predicted_value)
                error_percentage = abs(predicted_price - actual_price) / actual_price
                
                # Consider prediction accurate if within 10% of actual price
                is_accurate = error_percentage <= 0.10
                
                prediction.actual_value = actual_price
                prediction.accuracy_score = 1.0 - error_percentage if error_percentage <= 1.0 else 0.0
                prediction.verified = True
                
                verification_results['verified_count'] += 1
                verification_results['total_error'] += error_percentage
                
                if is_accurate:
                    verification_results['accurate_predictions'] += 1
                
                # Track by symbol
                symbol = prediction.symbol
                if symbol not in verification_results['accuracy_by_symbol']:
                    verification_results['accuracy_by_symbol'][symbol] = {'correct': 0, 'total': 0}
                
                verification_results['accuracy_by_symbol'][symbol]['total'] += 1
                if is_accurate:
                    verification_results['accuracy_by_symbol'][symbol]['correct'] += 1
                
                # Track by timeframe
                tf = prediction.timeframe
                if tf not in verification_results['accuracy_by_timeframe']:
                    verification_results['accuracy_by_timeframe'][tf] = {'correct': 0, 'total': 0}
                
                verification_results['accuracy_by_timeframe'][tf]['total'] += 1
                if is_accurate:
                    verification_results['accuracy_by_timeframe'][tf]['correct'] += 1
        
        # Update accuracy stats
        if verification_results['verified_count'] > 0:
            self._update_accuracy_stats(verification_results)
            self._save_predictions()
        
        return verification_results
    
    def get_accuracy_report(self, days_back: int = 30) -> Dict[str, Any]:
        """Generate comprehensive accuracy report"""
        
        cutoff_date = datetime.now() - timedelta(days=days_back)
        recent_predictions = [p for p in self.predictions 
                            if p.prediction_date >= cutoff_date and p.verified]
        
        if not recent_predictions:
            return {'error': 'No verified predictions in the specified period'}
        
        # Calculate overall accuracy
        accurate_count = sum(1 for p in recent_predictions if p.accuracy_score and p.accuracy_score >= 0.9)
        total_count = len(recent_predictions)
        overall_accuracy = accurate_count / total_count if total_count > 0 else 0.0
        
        # Average error
        avg_error = sum(1 - p.accuracy_score for p in recent_predictions if p.accuracy_score) / total_count
        
        # Accuracy by symbol
        symbol_accuracy = {}
        for prediction in recent_predictions:
            symbol = prediction.symbol
            if symbol not in symbol_accuracy:
                symbol_accuracy[symbol] = {'correct': 0, 'total': 0, 'avg_confidence': 0.0}
            
            symbol_accuracy[symbol]['total'] += 1
            symbol_accuracy[symbol]['avg_confidence'] += prediction.confidence
            
            if prediction.accuracy_score and prediction.accuracy_score >= 0.9:
                symbol_accuracy[symbol]['correct'] += 1
        
        # Calculate percentages
        for symbol_data in symbol_accuracy.values():
            symbol_data['accuracy_rate'] = symbol_data['correct'] / symbol_data['total']
            symbol_data['avg_confidence'] /= symbol_data['total']
        
        return {
            'period_days': days_back,
            'total_predictions': total_count,
            'accurate_predictions': accurate_count,
            'overall_accuracy': overall_accuracy,
            'average_error': avg_error,
            'accuracy_by_symbol': symbol_accuracy,
            'recent_predictions': [
                {
                    'symbol': p.symbol,
                    'predicted': p.predicted_value,
                    'actual': p.actual_value,
                    'accuracy': p.accuracy_score,
                    'date': p.prediction_date.strftime('%Y-%m-%d')
                }
                for p in recent_predictions[-10:]  # Last 10 predictions
            ]
        }
    
    def cleanup_old_predictions(self, days_to_keep: int = 90):
        """Remove old predictions to keep cache size manageable"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        original_count = len(self.predictions)
        self.predictions = [p for p in self.predictions if p.prediction_date >= cutoff_date]
        removed_count = original_count - len(self.predictions)
        
        if removed_count > 0:
            self._save_predictions()
            self.logger.info(f"Cleaned up {removed_count} old predictions")
        
        return removed_count
    
    def _load_predictions(self) -> List[PredictionRecord]:
        """Load predictions from cache file"""
        if not self.predictions_file.exists():
            return []
        
        try:
            with open(self.predictions_file, 'r') as f:
                data = json.load(f)
                return [PredictionRecord.from_dict(record) for record in data]
        except Exception as e:
            self.logger.error(f"Error loading predictions: {e}")
            return []
    
    def _save_predictions(self):
        """Save predictions to cache file"""
        try:
            data = [record.to_dict() for record in self.predictions]
            with open(self.predictions_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving predictions: {e}")
    
    def _load_accuracy_stats(self) -> Dict:
        """Load accuracy statistics"""
        if not self.accuracy_file.exists():
            return {'total_predictions': 0, 'accurate_predictions': 0, 'last_updated': None}
        
        try:
            with open(self.accuracy_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading accuracy stats: {e}")
            return {'total_predictions': 0, 'accurate_predictions': 0, 'last_updated': None}
    
    def _update_accuracy_stats(self, verification_results: Dict):
        """Update overall accuracy statistics"""
        self.accuracy_stats['total_predictions'] += verification_results['verified_count']
        self.accuracy_stats['accurate_predictions'] += verification_results['accurate_predictions']
        self.accuracy_stats['last_updated'] = datetime.now().isoformat()
        
        # Save updated stats
        try:
            with open(self.accuracy_file, 'w') as f:
                json.dump(self.accuracy_stats, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving accuracy stats: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_predictions = len(self.predictions)
        verified_predictions = sum(1 for p in self.predictions if p.verified)
        pending_predictions = total_predictions - verified_predictions
        
        # Recent activity (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_predictions = sum(1 for p in self.predictions if p.prediction_date >= week_ago)
        
        return {
            'total_predictions': total_predictions,
            'verified_predictions': verified_predictions,
            'pending_predictions': pending_predictions,
            'recent_predictions_7d': recent_predictions,
            'cache_size_mb': self._get_cache_size(),
            'oldest_prediction': min(p.prediction_date for p in self.predictions) if self.predictions else None,
            'newest_prediction': max(p.prediction_date for p in self.predictions) if self.predictions else None
        }
    
    def _get_cache_size(self) -> float:
        """Get cache size in MB"""
        total_size = 0
        for file_path in self.cache_dir.glob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size / (1024 * 1024)  # Convert to MB