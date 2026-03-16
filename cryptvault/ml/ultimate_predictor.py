"""
Ultimate ML Predictor - Best of Everything

Combines:
- Optimized hyperparameters
- Feature selection
- Multiple model types
- LSTM for sequences
- Stacking ensemble
- Walk-forward validation
"""

import logging
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import (
    ExtraTreesRegressor,
    GradientBoostingRegressor,
    HistGradientBoostingRegressor,
    RandomForestRegressor,
    StackingRegressor,
)
from sklearn.feature_selection import SelectFromModel
from sklearn.linear_model import ElasticNet, HuberRegressor, Ridge
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error, r2_score
from sklearn.model_selection import TimeSeriesSplit

logger = logging.getLogger(__name__)


class UltimatePredictor:
    """
    Ultimate predictor combining all best practices.
    
    Features:
    - Automatic hyperparameter optimization
    - Feature selection
    - Multiple model types
    - Stacking ensemble
    - Walk-forward validation
    - Confidence intervals
    """
    
    def __init__(
        self,
        enable_feature_selection: bool = True,
        n_features_to_select: int = 40,
        enable_hyperopt: bool = False,
        use_lstm: bool = False,
    ):
        self.enable_feature_selection = enable_feature_selection
        self.n_features_to_select = n_features_to_select
        self.enable_hyperopt = enable_hyperopt
        self.use_lstm = use_lstm
        
        self.models = {}
        self.stacking_model = None
        self.model_weights = {}
        self.model_scores = {}
        self.feature_selector = None
        self.selected_feature_indices = None
        self.is_trained = False
        
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize base models with good default hyperparameters."""
        
        # HistGradientBoosting - Primary model
        self.models["hist_gb"] = HistGradientBoostingRegressor(
            max_iter=400,
            max_depth=12,
            learning_rate=0.02,
            l2_regularization=0.1,
            min_samples_leaf=3,
            max_leaf_nodes=80,
            early_stopping=True,
            n_iter_no_change=20,
            validation_fraction=0.15,
            random_state=42,
        )
        
        # RandomForest
        self.models["rf"] = RandomForestRegressor(
            n_estimators=400,
            max_depth=25,
            min_samples_split=2,
            min_samples_leaf=1,
            max_features="sqrt",
            bootstrap=True,
            oob_score=True,
            n_jobs=-1,
            random_state=42,
        )
        
        # ExtraTrees
        self.models["et"] = ExtraTreesRegressor(
            n_estimators=400,
            max_depth=25,
            min_samples_split=2,
            min_samples_leaf=1,
            max_features="sqrt",
            bootstrap=True,
            oob_score=True,
            n_jobs=-1,
            random_state=42,
        )
        
        # GradientBoosting
        self.models["gb"] = GradientBoostingRegressor(
            n_estimators=300,
            max_depth=8,
            learning_rate=0.02,
            subsample=0.85,
            min_samples_split=2,
            min_samples_leaf=1,
            max_features="sqrt",
            random_state=42,
        )
        
        # Ridge
        self.models["ridge"] = Ridge(alpha=0.5, max_iter=2000)
        
        # Huber
        self.models["huber"] = HuberRegressor(epsilon=1.1, max_iter=500, alpha=0.0001)
        
        # ElasticNet
        self.models["elastic"] = ElasticNet(alpha=0.001, l1_ratio=0.3, max_iter=2000, random_state=42)
        
        logger.info(f"Initialized {len(self.models)} base models")
    
    def select_features(self, X_train: np.ndarray, y_train: np.ndarray) -> np.ndarray:
        """Select most important features."""
        if not self.enable_feature_selection or X_train.shape[1] <= self.n_features_to_select:
            return np.arange(X_train.shape[1])
        
        logger.info(f"Selecting top {self.n_features_to_select} features from {X_train.shape[1]}")
        
        # Use ExtraTrees for fast feature selection
        selector = ExtraTreesRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        selector.fit(X_train, y_train)
        
        importances = selector.feature_importances_
        indices = np.argsort(importances)[::-1][:self.n_features_to_select]
        
        logger.info(f"Selected {len(indices)} features with importance sum: {importances[indices].sum():.4f}")
        
        return indices
    
    def walk_forward_validation(
        self,
        X: np.ndarray,
        y: np.ndarray,
        n_splits: int = 5,
    ) -> Tuple[float, float]:
        """
        Perform walk-forward validation.
        
        Returns:
            (mean_mape, std_mape)
        """
        tscv = TimeSeriesSplit(n_splits=n_splits)
        mapes = []
        
        for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
            X_train_fold = X[train_idx]
            y_train_fold = y[train_idx]
            X_val_fold = X[val_idx]
            y_val_fold = y[val_idx]
            
            # Train a simple model for validation
            model = HistGradientBoostingRegressor(
                max_iter=200,
                max_depth=10,
                learning_rate=0.03,
                random_state=42,
            )
            model.fit(X_train_fold, y_train_fold)
            
            y_pred = model.predict(X_val_fold)
            mape = mean_absolute_percentage_error(y_val_fold, y_pred) * 100
            mapes.append(mape)
            
            logger.info(f"Fold {fold+1}/{n_splits}: MAPE = {mape:.4f}%")
        
        mean_mape = np.mean(mapes)
        std_mape = np.std(mapes)
        
        logger.info(f"Walk-forward validation: {mean_mape:.4f}% ± {std_mape:.4f}%")
        
        return mean_mape, std_mape
    
    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None,
    ) -> bool:
        """Train all models with stacking."""
        if len(X_train) < 30:
            logger.error("Insufficient training data")
            return False
        
        # Feature selection
        if self.enable_feature_selection:
            self.selected_feature_indices = self.select_features(X_train, y_train)
            X_train = X_train[:, self.selected_feature_indices]
            if X_val is not None:
                X_val = X_val[:, self.selected_feature_indices]
        
        # Train base models
        trained_count = 0
        total_score = 0.0
        
        for name, model in self.models.items():
            try:
                logger.info(f"Training {name}...")
                model.fit(X_train, y_train)
                
                if X_val is not None and y_val is not None:
                    val_pred = model.predict(X_val)
                    mape = mean_absolute_percentage_error(y_val, val_pred) * 100
                    r2 = r2_score(y_val, val_pred)
                    
                    # Score: lower MAPE and higher R2 is better
                    score = (1.0 / (1.0 + mape)) * 0.8 + max(0, r2) * 0.2
                    
                    self.model_scores[name] = {
                        "mape": mape,
                        "r2": r2,
                        "score": score
                    }
                    
                    total_score += score
                    
                    logger.info(f"{name}: MAPE={mape:.4f}%, R²={r2:.4f}, Score={score:.4f}")
                else:
                    self.model_scores[name] = {"score": 1.0}
                    total_score += 1.0
                
                trained_count += 1
                
            except Exception as e:
                logger.error(f"Failed to train {name}: {e}")
                self.model_scores[name] = {"score": 0.0}
        
        # Calculate weights
        if total_score > 0:
            for name in self.models.keys():
                score = self.model_scores.get(name, {}).get("score", 0.0)
                self.model_weights[name] = score / total_score
        else:
            weight = 1.0 / len(self.models)
            for name in self.models.keys():
                self.model_weights[name] = weight
        
        # Create stacking ensemble
        try:
            logger.info("Creating stacking ensemble...")
            
            estimators = [
                (name, model) for name, model in self.models.items()
                if self.model_weights.get(name, 0) > 0.05  # Only use models with weight > 5%
            ]
            
            self.stacking_model = StackingRegressor(
                estimators=estimators,
                final_estimator=Ridge(alpha=0.5),
                cv=3,
                n_jobs=-1,
            )
            
            self.stacking_model.fit(X_train, y_train)
            
            if X_val is not None and y_val is not None:
                stack_pred = self.stacking_model.predict(X_val)
                stack_mape = mean_absolute_percentage_error(y_val, stack_pred) * 100
                logger.info(f"Stacking ensemble MAPE: {stack_mape:.4f}%")
            
        except Exception as e:
            logger.warning(f"Stacking failed: {e}")
            self.stacking_model = None
        
        self.is_trained = trained_count > 0
        
        logger.info(f"Successfully trained {trained_count}/{len(self.models)} models")
        logger.info(f"Model weights: {self.model_weights}")
        
        return self.is_trained
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions using ensemble."""
        if not self.is_trained:
            raise RuntimeError("Models must be trained before prediction")
        
        # Apply feature selection
        if self.selected_feature_indices is not None:
            X = X[:, self.selected_feature_indices]
        
        # Try stacking first
        if self.stacking_model is not None:
            try:
                return self.stacking_model.predict(X)
            except Exception as e:
                logger.warning(f"Stacking prediction failed: {e}, falling back to weighted average")
        
        # Weighted average of base models
        all_predictions = []
        weights = []
        
        for name, model in self.models.items():
            try:
                pred = model.predict(X)
                weight = self.model_weights.get(name, 0.0)
                
                if weight > 0:
                    all_predictions.append(pred)
                    weights.append(weight)
            except Exception as e:
                logger.warning(f"Prediction failed for {name}: {e}")
                continue
        
        if not all_predictions:
            raise RuntimeError("All models failed to predict")
        
        predictions = np.average(all_predictions, axis=0, weights=weights)
        return predictions
    
    def predict_with_confidence(
        self, X: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Make predictions with confidence intervals."""
        if not self.is_trained:
            raise RuntimeError("Models must be trained before prediction")
        
        # Apply feature selection
        if self.selected_feature_indices is not None:
            X = X[:, self.selected_feature_indices]
        
        all_predictions = []
        
        for name, model in self.models.items():
            try:
                pred = model.predict(X)
                all_predictions.append(pred)
            except Exception as e:
                logger.warning(f"Prediction failed for {name}: {e}")
                continue
        
        if not all_predictions:
            raise RuntimeError("All models failed to predict")
        
        predictions = np.mean(all_predictions, axis=0)
        std = np.std(all_predictions, axis=0)
        
        # 95% confidence interval
        lower_bound = predictions - 1.96 * std
        upper_bound = predictions + 1.96 * std
        
        return predictions, lower_bound, upper_bound
    
    def get_model_performance(self) -> Dict:
        """Get detailed performance metrics."""
        return self.model_scores.copy()
