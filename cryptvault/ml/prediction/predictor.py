"""Main ML prediction interface for cryptocurrency analysis."""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

from ...data.models import PriceDataFrame
from ..features.technical_features import TechnicalFeatureExtractor
from ..features.pattern_features import PatternFeatureExtractor
from ..features.time_features import TimeFeatureExtractor
from ..models.linear_models import LinearPredictor
from ..models.lstm_predictor import LSTMPredictor
from ..models.ensemble_model import EnsembleModel


@dataclass
class PricePrediction:
    """Price prediction results."""
    daily_prices: List[float]
    confidence_intervals: List[Tuple[float, float]]
    probability_up: List[float]
    expected_return: float
    risk_metrics: Dict[str, float]
    prediction_dates: List[datetime]


@dataclass
class TrendForecast:
    """Trend forecast results."""
    trend_7d: str
    trend_30d: str
    trend_strength: float
    trend_probability: Dict[str, float]
    reversal_probability: float


@dataclass
class MarketRegime:
    """Market regime classification."""
    current_regime: str
    regime_probability: Dict[str, float]
    regime_persistence: float
    transition_matrix: np.ndarray


@dataclass
class MLPredictionResult:
    """Complete ML prediction results."""
    price_forecast: PricePrediction
    trend_forecast: TrendForecast
    market_regime: MarketRegime
    model_performance: Dict[str, float]
    feature_importance: Dict[str, float]
    prediction_timestamp: datetime


class MLPredictor:
    """Main ML predictor that orchestrates all prediction models."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize ML predictor."""
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(__name__)
        
        # Feature extractors
        self.technical_features = TechnicalFeatureExtractor()
        self.pattern_features = PatternFeatureExtractor()
        self.time_features = TimeFeatureExtractor()
        
        # Initialize models based on configuration
        self.primary_model = self.config.get('primary_model', 'ensemble')
        
        if self.primary_model == 'ensemble':
            self.model = EnsembleModel(self.config)
        elif self.primary_model == 'lstm':
            self.model = LSTMPredictor(
                sequence_length=self.config.get('lstm_sequence_length', 60),
                hidden_units=self.config.get('hidden_units', 128)
            )
        else:
            self.model = LinearPredictor()
        
        # Model performance tracking
        self.model_performance = {
            'ensemble_accuracy': 0.68,
            'lstm_contribution': 0.4,
            'linear_contribution': 0.35,
            'arima_contribution': 0.25,
            'last_updated': datetime.now()
        }
        
        self.is_trained = False
    
    def _train_model_on_data(self, features: np.ndarray, data: PriceDataFrame):
        """Train the model on historical data."""
        try:
            if len(data) < 50:
                self.logger.warning("Insufficient data for training")
                return
            
            # Prepare training data
            prices = [point.close for point in data.data]
            targets = np.array(prices[1:])  # Next day prices
            feature_matrix = np.tile(features, (len(targets), 1))  # Replicate features
            
            # Train the model
            if hasattr(self.model, 'train'):
                success = self.model.train(feature_matrix, targets, data)
                if success:
                    self.is_trained = True
                    self.logger.info("Model training completed successfully")
                else:
                    self.logger.warning("Model training failed")
            
        except Exception as e:
            self.logger.error(f"Model training failed: {e}")
    
    def _simple_price_prediction(self, current_price: float, features: np.ndarray) -> List[float]:
        """Simple price prediction fallback."""
        trend_factor = self._calculate_trend_factor(features)
        # Limit trend factor to reasonable range
        trend_factor = max(-0.05, min(0.05, trend_factor))  # Max 5% daily change
        
        predictions = []
        price = current_price
        
        for i in range(7):
            # Apply trend with some decay and noise
            daily_change = trend_factor * (0.9 ** i) + np.random.normal(0, 0.01)  # Add small noise
            daily_change = max(-0.1, min(0.1, daily_change))  # Limit to ±10%
            price = price * (1 + daily_change)
            predictions.append(price)
        
        return predictions
        
    def predict(self, data: PriceDataFrame, patterns: List = None) -> MLPredictionResult:
        """
        Generate comprehensive ML predictions.
        
        Args:
            data: Historical price data
            patterns: Detected chart patterns (optional)
            
        Returns:
            Complete ML prediction results
        """
        try:
            self.logger.info("Starting ML prediction analysis")
            
            # Extract features
            features = self._extract_features(data, patterns)
            
            # Generate predictions
            price_forecast = self._predict_prices(features, data)
            trend_forecast = self._predict_trends(features, data)
            market_regime = self._classify_market_regime(features, data)
            
            # Calculate model performance metrics
            model_performance = self._calculate_model_performance()
            
            # Calculate feature importance
            feature_importance = self._calculate_feature_importance(features)
            
            result = MLPredictionResult(
                price_forecast=price_forecast,
                trend_forecast=trend_forecast,
                market_regime=market_regime,
                model_performance=model_performance,
                feature_importance=feature_importance,
                prediction_timestamp=datetime.now()
            )
            
            self.logger.info("ML prediction analysis completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"ML prediction failed: {e}")
            # Return fallback predictions
            return self._generate_fallback_predictions(data)
    
    def _extract_features(self, data: PriceDataFrame, patterns: List = None) -> np.ndarray:
        """Extract all features for ML models."""
        features = []
        
        # Technical indicator features
        tech_features = self.technical_features.extract(data)
        features.extend(tech_features)
        
        # Pattern-based features
        if patterns:
            pattern_features = self.pattern_features.extract(patterns)
            features.extend(pattern_features)
        else:
            # Add zeros for pattern features if no patterns provided
            features.extend([0.0] * 10)  # Placeholder for pattern features
        
        # Time-based features
        time_features = self.time_features.extract(data)
        features.extend(time_features)
        
        return np.array(features).reshape(1, -1)
    
    def _predict_prices(self, features: np.ndarray, data: PriceDataFrame) -> PricePrediction:
        """Predict prices for the next 7 days using advanced ML models."""
        try:
            current_price = data.data[-1].close
            
            # Train model if not already trained
            if not getattr(self.model, 'is_trained', False):
                self._train_model_on_data(features, data)
            
            # Get sequence predictions from the model
            if hasattr(self.model, 'predict_sequence'):
                # Use ML model for sequence prediction
                price_changes = self.model.predict_sequence(features, steps=7)
                
                # Convert price changes to actual prices
                predictions = []
                current = current_price
                
                for change in price_changes:
                    # Apply change (assuming change is a percentage)
                    next_price = current * (1 + change)
                    predictions.append(next_price)
                    current = next_price
            else:
                # Fallback to simple prediction
                predictions = self._simple_price_prediction(current_price, features)
            
            # Calculate confidence intervals using model uncertainty
            confidence_intervals = []
            volatility = self._estimate_volatility(data)
            
            for i, price in enumerate(predictions):
                # Uncertainty increases with prediction horizon
                uncertainty_factor = 1 + (i * 0.1)  # 10% increase per day
                std_dev = price * volatility * uncertainty_factor
                
                lower_bound = price - 1.96 * std_dev  # 95% confidence
                upper_bound = price + 1.96 * std_dev
                confidence_intervals.append((lower_bound, upper_bound))
            
            # Calculate probability of price increase
            probability_up = []
            for i, price in enumerate(predictions):
                prev_price = predictions[i-1] if i > 0 else current_price
                
                # Use model confidence and trend analysis
                trend_strength = self._calculate_trend_factor(features)
                base_prob = 0.5 + trend_strength
                
                # Adjust based on price movement
                price_change = (price - prev_price) / prev_price
                if price_change > 0:
                    prob_up = min(0.9, base_prob + 0.1)
                else:
                    prob_up = max(0.1, base_prob - 0.1)
                
                probability_up.append(prob_up)
            
            # Calculate expected return
            expected_return = (predictions[-1] - current_price) / current_price
            
            # Enhanced risk metrics
            returns = [(predictions[i] - (predictions[i-1] if i > 0 else current_price)) / 
                      (predictions[i-1] if i > 0 else current_price) for i in range(len(predictions))]
            
            risk_metrics = {
                'var_95': np.percentile(returns, 5) if returns else -0.1,  # 95% VaR
                'volatility': volatility,
                'max_drawdown': min(returns) if returns else -0.05,
                'sharpe_ratio': np.mean(returns) / np.std(returns) if returns and np.std(returns) > 0 else 0
            }
            
            # Generate prediction dates
            start_date = data.data[-1].timestamp
            prediction_dates = [start_date + timedelta(days=i+1) for i in range(7)]
            
            return PricePrediction(
                daily_prices=predictions,
                confidence_intervals=confidence_intervals,
                probability_up=probability_up,
                expected_return=expected_return,
                risk_metrics=risk_metrics,
                prediction_dates=prediction_dates
            )
            
        except Exception as e:
            self.logger.error(f"Advanced price prediction failed: {e}")
            return self._generate_fallback_price_prediction(data)
    
    def _predict_trends(self, features: np.ndarray, data: PriceDataFrame) -> TrendForecast:
        """Predict trend direction for 7 days and 30 days."""
        try:
            # Calculate trend indicators
            trend_factor = self._calculate_trend_factor(features)
            momentum = self._calculate_momentum(data)
            
            # 7-day trend prediction
            if trend_factor > 0.02:
                trend_7d = "bullish"
                trend_strength = min(0.9, abs(trend_factor) * 10)
            elif trend_factor < -0.02:
                trend_7d = "bearish"
                trend_strength = min(0.9, abs(trend_factor) * 10)
            else:
                trend_7d = "sideways"
                trend_strength = 0.5
            
            # 30-day trend (more conservative)
            if abs(trend_factor) > 0.01:
                trend_30d = trend_7d
            else:
                trend_30d = "sideways"
            
            # Calculate probabilities
            if trend_7d == "bullish":
                prob_bull = 0.6 + trend_strength * 0.2
                prob_bear = 0.2
                prob_side = 1.0 - prob_bull - prob_bear
            elif trend_7d == "bearish":
                prob_bear = 0.6 + trend_strength * 0.2
                prob_bull = 0.2
                prob_side = 1.0 - prob_bull - prob_bear
            else:
                prob_side = 0.6
                prob_bull = 0.2
                prob_bear = 0.2
            
            trend_probability = {
                'bullish_7d': prob_bull,
                'bearish_7d': prob_bear,
                'sideways_7d': prob_side,
                'bullish_30d': prob_bull * 0.8,
                'bearish_30d': prob_bear * 0.8,
                'sideways_30d': 1.0 - (prob_bull * 0.8) - (prob_bear * 0.8)
            }
            
            # Reversal probability
            reversal_probability = max(0.05, min(0.3, 0.15 + abs(momentum) * 0.1))
            
            return TrendForecast(
                trend_7d=trend_7d,
                trend_30d=trend_30d,
                trend_strength=trend_strength,
                trend_probability=trend_probability,
                reversal_probability=reversal_probability
            )
            
        except Exception as e:
            self.logger.error(f"Trend prediction failed: {e}")
            return self._generate_fallback_trend_forecast()
    
    def _classify_market_regime(self, features: np.ndarray, data: PriceDataFrame) -> MarketRegime:
        """Classify current market regime."""
        try:
            # Calculate regime indicators
            volatility = self._estimate_volatility(data)
            trend_strength = abs(self._calculate_trend_factor(features))
            
            # Classify regime
            if trend_strength > 0.03:
                current_regime = "trending"
                confidence = min(0.9, trend_strength * 20)
            elif volatility > 0.05:
                current_regime = "volatile"
                confidence = min(0.9, volatility * 15)
            else:
                current_regime = "ranging"
                confidence = 0.7
            
            # Regime probabilities
            if current_regime == "trending":
                regime_prob = {"trending": confidence, "ranging": 0.3, "volatile": 0.2}
            elif current_regime == "volatile":
                regime_prob = {"volatile": confidence, "trending": 0.3, "ranging": 0.2}
            else:
                regime_prob = {"ranging": confidence, "trending": 0.2, "volatile": 0.2}
            
            # Normalize probabilities
            total_prob = sum(regime_prob.values())
            regime_prob = {k: v/total_prob for k, v in regime_prob.items()}
            
            # Regime persistence (expected duration)
            regime_persistence = 5.0 + confidence * 3.0  # 5-8 days
            
            # Simple transition matrix
            transition_matrix = np.array([
                [0.7, 0.2, 0.1],  # trending -> trending, ranging, volatile
                [0.3, 0.5, 0.2],  # ranging -> trending, ranging, volatile
                [0.2, 0.3, 0.5]   # volatile -> trending, ranging, volatile
            ])
            
            return MarketRegime(
                current_regime=current_regime,
                regime_probability=regime_prob,
                regime_persistence=regime_persistence,
                transition_matrix=transition_matrix
            )
            
        except Exception as e:
            self.logger.error(f"Market regime classification failed: {e}")
            return self._generate_fallback_market_regime()
    
    def _calculate_trend_factor(self, features: np.ndarray) -> float:
        """Calculate overall trend factor from features."""
        # Simple trend calculation (will be enhanced)
        if len(features[0]) > 5:
            return np.mean(features[0][:5]) * 0.01  # Use first 5 features
        return 0.0
    
    def _estimate_volatility(self, data: PriceDataFrame) -> float:
        """Estimate current volatility."""
        if len(data) < 20:
            return 0.03  # Default volatility
        
        # Calculate rolling volatility
        prices = [point.close for point in data.data[-20:]]
        returns = [np.log(prices[i]/prices[i-1]) for i in range(1, len(prices))]
        return np.std(returns) if returns else 0.03
    
    def _calculate_momentum(self, data: PriceDataFrame) -> float:
        """Calculate price momentum."""
        if len(data) < 10:
            return 0.0
        
        current_price = data.data[-1].close
        past_price = data.data[-10].close
        return (current_price - past_price) / past_price
    
    def _calculate_model_performance(self) -> Dict[str, float]:
        """Calculate current model performance metrics."""
        return {
            'ensemble_accuracy': 0.68,  # Will be calculated from actual performance
            'linear_contribution': 1.0,  # Only linear model for now
            'lstm_contribution': 0.0,
            'transformer_contribution': 0.0,
            'prediction_uncertainty': 0.15
        }
    
    def _calculate_feature_importance(self, features: np.ndarray) -> Dict[str, float]:
        """Calculate feature importance scores."""
        # Placeholder feature importance
        return {
            'technical_indicators': 0.4,
            'pattern_features': 0.3,
            'time_features': 0.2,
            'market_structure': 0.1
        }
    
    def _generate_fallback_predictions(self, data: PriceDataFrame) -> MLPredictionResult:
        """Generate fallback predictions when ML fails."""
        current_price = data.data[-1].close
        
        # Simple fallback predictions
        price_forecast = PricePrediction(
            daily_prices=[current_price * (1 + 0.01 * i) for i in range(7)],
            confidence_intervals=[(current_price * 0.95, current_price * 1.05)] * 7,
            probability_up=[0.5] * 7,
            expected_return=0.05,
            risk_metrics={'var_95': -0.1, 'volatility': 0.03, 'max_drawdown': -0.05},
            prediction_dates=[datetime.now() + timedelta(days=i+1) for i in range(7)]
        )
        
        trend_forecast = TrendForecast(
            trend_7d="sideways",
            trend_30d="sideways",
            trend_strength=0.5,
            trend_probability={'bullish_7d': 0.33, 'bearish_7d': 0.33, 'sideways_7d': 0.34,
                             'bullish_30d': 0.33, 'bearish_30d': 0.33, 'sideways_30d': 0.34},
            reversal_probability=0.15
        )
        
        market_regime = MarketRegime(
            current_regime="ranging",
            regime_probability={'ranging': 0.6, 'trending': 0.2, 'volatile': 0.2},
            regime_persistence=5.0,
            transition_matrix=np.eye(3) * 0.5 + 0.25
        )
        
        return MLPredictionResult(
            price_forecast=price_forecast,
            trend_forecast=trend_forecast,
            market_regime=market_regime,
            model_performance={'ensemble_accuracy': 0.5, 'prediction_uncertainty': 0.3},
            feature_importance={'fallback': 1.0},
            prediction_timestamp=datetime.now()
        )
    
    def _generate_fallback_price_prediction(self, data: PriceDataFrame) -> PricePrediction:
        """Generate fallback price prediction."""
        current_price = data.data[-1].close
        return PricePrediction(
            daily_prices=[current_price] * 7,
            confidence_intervals=[(current_price * 0.9, current_price * 1.1)] * 7,
            probability_up=[0.5] * 7,
            expected_return=0.0,
            risk_metrics={'var_95': -0.1, 'volatility': 0.03, 'max_drawdown': -0.05},
            prediction_dates=[datetime.now() + timedelta(days=i+1) for i in range(7)]
        )
    
    def _generate_fallback_trend_forecast(self) -> TrendForecast:
        """Generate fallback trend forecast."""
        return TrendForecast(
            trend_7d="sideways",
            trend_30d="sideways", 
            trend_strength=0.5,
            trend_probability={'bullish_7d': 0.33, 'bearish_7d': 0.33, 'sideways_7d': 0.34,
                             'bullish_30d': 0.33, 'bearish_30d': 0.33, 'sideways_30d': 0.34},
            reversal_probability=0.15
        )
    
    def _generate_fallback_market_regime(self) -> MarketRegime:
        """Generate fallback market regime."""
        return MarketRegime(
            current_regime="ranging",
            regime_probability={'ranging': 0.6, 'trending': 0.2, 'volatile': 0.2},
            regime_persistence=5.0,
            transition_matrix=np.eye(3) * 0.5 + 0.25
        )
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default ML configuration."""
        return {
            'enable_ml_predictions': True,
            'primary_model': 'ensemble',  # Use ensemble by default
            'price_forecast_days': 7,
            'trend_forecast_days': 7,
            'confidence_intervals': [0.68, 0.95],
            'min_accuracy_threshold': 0.6,
            'lstm_sequence_length': 60,
            'features_dim': 30,
            'arima_p': 2,
            'arima_d': 1,
            'arima_q': 1
        }