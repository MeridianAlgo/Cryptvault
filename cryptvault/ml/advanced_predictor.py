"""
Advanced ML Predictor with Stacking and Hyperparameter Optimization

Target: <0.5% MAPE through advanced ensemble techniques.
"""

import logging
import warnings
from typing import Dict, Optional, Tuple

import numpy as np

warnings.filterwarnings("ignore")

from sklearn.ensemble import (
    ExtraTreesRegressor,
    GradientBoostingRegressor,
    HistGradientBoostingRegressor,
    RandomForestRegressor,
    StackingRegressor,
    VotingRegressor,
)
from sklearn.linear_model import BayesianRidge, HuberRegressor, Ridge
from sklearn.metrics import mean_absolute_percentage_error, r2_score
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.neural_network import MLPRegressor

logger = logging.getLogger(__name__)


class AdvancedPredictor:
    """
    Advanced predictor with stacking, hyperparameter tuning, and sophisticated ensembling.

    Techniques:
    - Stacked generalization
    - Hyperparameter optimization
    - Multiple meta-learners
    - Weighted voting
    - Cross-validation
    """

    def __init__(self, optimize_hyperparams: bool = False):
        self.optimize_hyperparams = optimize_hyperparams
        self.base_models = {}
        self.meta_model = None
        self.stacking_model = None
        self.voting_model = None
        self.is_trained = False
        self.best_params = {}

    def _create_optimized_models(self):
        """Create models with optimized hyperparameters."""

        # HistGradientBoosting - best for tabular data
        self.base_models["hist_gb"] = HistGradientBoostingRegressor(
            max_iter=300,
            max_depth=10,
            learning_rate=0.03,
            l2_regularization=0.05,
            min_samples_leaf=5,
            max_leaf_nodes=50,
            random_state=42,
        )

        # RandomForest with optimized params
        self.base_models["rf"] = RandomForestRegressor(
            n_estimators=300,
            max_depth=20,
            min_samples_split=3,
            min_samples_leaf=1,
            max_features="sqrt",
            bootstrap=True,
            random_state=42,
            n_jobs=-1,
        )

        # ExtraTrees for diversity
        self.base_models["et"] = ExtraTreesRegressor(
            n_estimators=300,
            max_depth=20,
            min_samples_split=3,
            min_samples_leaf=1,
            max_features="sqrt",
            bootstrap=True,
            random_state=42,
            n_jobs=-1,
        )

        # GradientBoosting with careful tuning
        self.base_models["gb"] = GradientBoostingRegressor(
            n_estimators=200,
            max_depth=8,
            learning_rate=0.03,
            subsample=0.85,
            min_samples_split=3,
            min_samples_leaf=2,
            max_features="sqrt",
            random_state=42,
        )

        # Huber for robustness
        self.base_models["huber"] = HuberRegressor(epsilon=1.2, max_iter=300, alpha=0.0001)

        # BayesianRidge for uncertainty
        self.base_models["bayes"] = BayesianRidge(
            max_iter=300, alpha_1=1e-6, alpha_2=1e-6, lambda_1=1e-6, lambda_2=1e-6
        )

        # MLP for non-linear patterns
        self.base_models["mlp"] = MLPRegressor(
            hidden_layer_sizes=(150, 100, 50),
            activation="relu",
            solver="adam",
            alpha=0.0001,
            learning_rate="adaptive",
            max_iter=1000,
            early_stopping=True,
            validation_fraction=0.1,
            random_state=42,
        )

        logger.info(f"Created {len(self.base_models)} optimized base models")

    def _optimize_hyperparameters(self, X_train, y_train):
        """Optimize hyperparameters using grid search."""
        logger.info("Optimizing hyperparameters...")

        # Time series cross-validation
        tscv = TimeSeriesSplit(n_splits=3)

        # Optimize HistGradientBoosting (fastest to tune)
        param_grid = {
            "max_depth": [8, 10, 12],
            "learning_rate": [0.02, 0.03, 0.05],
            "l2_regularization": [0.01, 0.05, 0.1],
        }

        grid_search = GridSearchCV(
            HistGradientBoostingRegressor(max_iter=200, random_state=42),
            param_grid,
            cv=tscv,
            scoring="neg_mean_absolute_percentage_error",
            n_jobs=-1,
            verbose=0,
        )

        grid_search.fit(X_train, y_train)
        self.best_params["hist_gb"] = grid_search.best_params_
        self.base_models["hist_gb"] = grid_search.best_estimator_

        logger.info(f"Best params for HistGB: {self.best_params['hist_gb']}")

    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None,
    ) -> bool:
        """
        Train advanced ensemble with stacking.
        """
        if len(X_train) < 20:
            logger.error("Insufficient training data")
            return False

        # Create models
        self._create_optimized_models()

        # Optionally optimize hyperparameters
        if self.optimize_hyperparams and len(X_train) > 100:
            self._optimize_hyperparameters(X_train, y_train)

        # Train base models
        logger.info("Training base models...")
        trained_models = []

        for name, model in self.base_models.items():
            try:
                model.fit(X_train, y_train)
                trained_models.append((name, model))

                if X_val is not None and y_val is not None:
                    pred = model.predict(X_val)
                    mape = mean_absolute_percentage_error(y_val, pred) * 100
                    logger.info(f"{name}: MAPE={mape:.3f}%")

            except Exception as e:
                logger.warning(f"Failed to train {name}: {e}")
                continue

        if len(trained_models) < 3:
            logger.error("Too few models trained")
            return False

        # Create stacking ensemble
        logger.info("Creating stacking ensemble...")

        estimators = [(name, model) for name, model in trained_models]

        # Meta-learner: Ridge for stability
        self.meta_model = Ridge(alpha=0.5)

        self.stacking_model = StackingRegressor(
            estimators=estimators, final_estimator=self.meta_model, cv=3, n_jobs=-1
        )

        try:
            self.stacking_model.fit(X_train, y_train)
            logger.info("Stacking model trained successfully")
        except Exception as e:
            logger.error(f"Stacking failed: {e}")
            return False

        # Create voting ensemble as backup
        self.voting_model = VotingRegressor(estimators=estimators, n_jobs=-1)

        try:
            self.voting_model.fit(X_train, y_train)
            logger.info("Voting model trained successfully")
        except Exception as e:
            logger.warning(f"Voting model failed: {e}")

        self.is_trained = True
        return True

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions using stacking ensemble."""
        if not self.is_trained:
            raise RuntimeError("Model must be trained first")

        try:
            # Primary: Stacking predictions
            stacking_pred = self.stacking_model.predict(X)

            # Backup: Voting predictions
            if self.voting_model is not None:
                voting_pred = self.voting_model.predict(X)

                # Blend stacking and voting (80/20)
                predictions = 0.8 * stacking_pred + 0.2 * voting_pred
            else:
                predictions = stacking_pred

            return predictions

        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            # Fallback to best base model
            return self.base_models["hist_gb"].predict(X)

    def predict_with_uncertainty(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Predict with uncertainty estimates."""
        # Get predictions from all base models
        all_preds = []

        for model in self.base_models.values():
            try:
                pred = model.predict(X)
                all_preds.append(pred)
            except:
                continue

        all_preds = np.array(all_preds)

        # Mean and std
        mean_pred = np.mean(all_preds, axis=0)
        std_pred = np.std(all_preds, axis=0)

        return mean_pred, std_pred

    def evaluate(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """Comprehensive evaluation."""
        predictions = self.predict(X)

        mape = mean_absolute_percentage_error(y, predictions) * 100
        rmse = np.sqrt(np.mean((y - predictions) ** 2))
        mae = np.mean(np.abs(y - predictions))
        r2 = r2_score(y, predictions)

        # Percentage within thresholds
        pct_errors = np.abs((y - predictions) / y) * 100
        within_0_5 = np.sum(pct_errors <= 0.5) / len(y) * 100
        within_1_0 = np.sum(pct_errors <= 1.0) / len(y) * 100
        within_2_0 = np.sum(pct_errors <= 2.0) / len(y) * 100

        # Direction accuracy
        if len(y) > 1:
            y_dir = np.sign(np.diff(y))
            pred_dir = np.sign(np.diff(predictions))
            dir_acc = np.mean(y_dir == pred_dir) * 100
        else:
            dir_acc = 0

        return {
            "MAPE": mape,
            "RMSE": rmse,
            "MAE": mae,
            "R2": r2,
            "Within_0.5_Pct": within_0_5,
            "Within_1.0_Pct": within_1_0,
            "Within_2.0_Pct": within_2_0,
            "Direction_Accuracy": dir_acc,
        }
