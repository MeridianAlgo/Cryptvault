"""Advanced ML models for enhanced prediction accuracy."""

import logging
import warnings
from typing import Any, Dict, List, Optional

import numpy as np

warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)

# Try importing advanced libraries
try:
    from catboost import CatBoostRegressor

    CATBOOST_AVAILABLE = True
except ImportError:
    CATBOOST_AVAILABLE = False

try:
    from sklearn.ensemble import BaggingRegressor, StackingRegressor
    from sklearn.linear_model import Ridge

    STACKING_AVAILABLE = True
except ImportError:
    STACKING_AVAILABLE = False


class CatBoostPredictor:
    """CatBoost gradient boosting predictor with categorical feature support."""

    def __init__(self):
        self.model = None
        self.is_trained = False
        self.logger = logging.getLogger(__name__)

        if CATBOOST_AVAILABLE:
            self.model = CatBoostRegressor(
                iterations=200,
                depth=7,
                learning_rate=0.05,
                l2_leaf_reg=3,
                random_seed=42,
                verbose=False,
                thread_count=-1,
            )

    def train(self, X: np.ndarray, y: np.ndarray) -> bool:
        """Train CatBoost model."""
        if not CATBOOST_AVAILABLE or self.model is None:
            return False

        try:
            self.model.fit(X, y, verbose=False)
            self.is_trained = True
            self.logger.info("CatBoost model trained successfully")
            return True
        except Exception as e:
            self.logger.error(f"CatBoost training failed: {e}")
            return False

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions."""
        if not self.is_trained or self.model is None:
            return np.zeros(X.shape[0])

        try:
            return self.model.predict(X)
        except Exception as e:
            self.logger.error(f"CatBoost prediction failed: {e}")
            return np.zeros(X.shape[0])

    def get_feature_importance(self) -> Optional[np.ndarray]:
        """Get feature importance scores."""
        if self.is_trained and self.model is not None:
            try:
                return self.model.get_feature_importance()
            except:
                return None
        return None


class StackedEnsemblePredictor:
    """Stacked ensemble combining multiple base models."""

    def __init__(self, base_models: List[Any]):
        self.base_models = base_models
        self.meta_model = None
        self.is_trained = False
        self.logger = logging.getLogger(__name__)

        if STACKING_AVAILABLE:
            self.meta_model = Ridge(alpha=1.0)

    def train(self, X: np.ndarray, y: np.ndarray) -> bool:
        """Train stacked ensemble."""
        if not STACKING_AVAILABLE or not self.base_models:
            return False

        try:
            # Train base models
            base_predictions = []
            for model in self.base_models:
                try:
                    model.fit(X, y)
                    pred = model.predict(X)
                    base_predictions.append(pred)
                except Exception as e:
                    self.logger.warning(f"Base model training failed: {e}")
                    continue

            if not base_predictions:
                return False

            # Stack predictions
            X_meta = np.column_stack(base_predictions)

            # Train meta model
            self.meta_model.fit(X_meta, y)
            self.is_trained = True
            self.logger.info(f"Stacked ensemble trained with {len(base_predictions)} base models")
            return True

        except Exception as e:
            self.logger.error(f"Stacked ensemble training failed: {e}")
            return False

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions using stacked ensemble."""
        if not self.is_trained:
            return np.zeros(X.shape[0])

        try:
            # Get base model predictions
            base_predictions = []
            for model in self.base_models:
                try:
                    pred = model.predict(X)
                    base_predictions.append(pred)
                except:
                    continue

            if not base_predictions:
                return np.zeros(X.shape[0])

            # Stack and predict with meta model
            X_meta = np.column_stack(base_predictions)
            return self.meta_model.predict(X_meta)

        except Exception as e:
            self.logger.error(f"Stacked ensemble prediction failed: {e}")
            return np.zeros(X.shape[0])


class BayesianRidgePredictor:
    """Bayesian Ridge Regression with uncertainty quantification."""

    def __init__(self):
        self.model = None
        self.is_trained = False
        self.logger = logging.getLogger(__name__)

        try:
            from sklearn.linear_model import BayesianRidge

            self.model = BayesianRidge(
                n_iter=300, alpha_1=1e-6, alpha_2=1e-6, lambda_1=1e-6, lambda_2=1e-6
            )
        except ImportError:
            pass

    def train(self, X: np.ndarray, y: np.ndarray) -> bool:
        """Train Bayesian Ridge model."""
        if self.model is None:
            return False

        try:
            self.model.fit(X, y)
            self.is_trained = True
            self.logger.info("Bayesian Ridge model trained successfully")
            return True
        except Exception as e:
            self.logger.error(f"Bayesian Ridge training failed: {e}")
            return False

    def predict(self, X: np.ndarray, return_std: bool = False) -> np.ndarray:
        """Make predictions with optional uncertainty estimates."""
        if not self.is_trained or self.model is None:
            if return_std:
                return np.zeros(X.shape[0]), np.ones(X.shape[0])
            return np.zeros(X.shape[0])

        try:
            if return_std:
                return self.model.predict(X, return_std=True)
            return self.model.predict(X)
        except Exception as e:
            self.logger.error(f"Bayesian Ridge prediction failed: {e}")
            if return_std:
                return np.zeros(X.shape[0]), np.ones(X.shape[0])
            return np.zeros(X.shape[0])


class QuantileRegressionPredictor:
    """Quantile regression for prediction intervals."""

    def __init__(self, quantiles: List[float] = [0.1, 0.5, 0.9]):
        self.quantiles = quantiles
        self.models = {}
        self.is_trained = False
        self.logger = logging.getLogger(__name__)

        try:
            from sklearn.ensemble import GradientBoostingRegressor

            for q in quantiles:
                self.models[q] = GradientBoostingRegressor(
                    loss="quantile",
                    alpha=q,
                    n_estimators=100,
                    max_depth=5,
                    learning_rate=0.1,
                    random_state=42,
                )
        except ImportError:
            pass

    def train(self, X: np.ndarray, y: np.ndarray) -> bool:
        """Train quantile regression models."""
        if not self.models:
            return False

        try:
            for q, model in self.models.items():
                model.fit(X, y)

            self.is_trained = True
            self.logger.info(f"Quantile regression trained for {len(self.quantiles)} quantiles")
            return True
        except Exception as e:
            self.logger.error(f"Quantile regression training failed: {e}")
            return False

    def predict(self, X: np.ndarray) -> Dict[float, np.ndarray]:
        """Make predictions for all quantiles."""
        if not self.is_trained:
            return {q: np.zeros(X.shape[0]) for q in self.quantiles}

        try:
            predictions = {}
            for q, model in self.models.items():
                predictions[q] = model.predict(X)
            return predictions
        except Exception as e:
            self.logger.error(f"Quantile regression prediction failed: {e}")
            return {q: np.zeros(X.shape[0]) for q in self.quantiles}

    def get_prediction_interval(self, X: np.ndarray, confidence: float = 0.8) -> tuple:
        """Get prediction interval for given confidence level."""
        predictions = self.predict(X)

        lower_q = (1 - confidence) / 2
        upper_q = 1 - lower_q

        # Find closest quantiles
        lower_pred = predictions.get(min(self.quantiles, key=lambda x: abs(x - lower_q)))
        upper_pred = predictions.get(min(self.quantiles, key=lambda x: abs(x - upper_q)))
        median_pred = predictions.get(0.5, predictions[self.quantiles[len(self.quantiles) // 2]])

        return lower_pred, median_pred, upper_pred


def get_available_advanced_models() -> Dict[str, bool]:
    """Check which advanced models are available."""
    return {
        "catboost": CATBOOST_AVAILABLE,
        "stacking": STACKING_AVAILABLE,
    }
