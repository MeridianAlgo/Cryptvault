"""
Comprehensive ML Model Testing and Benchmarking Script

Tests all models rigorously and shows prediction accuracies.
"""

import logging
import sys
import time
from typing import Dict, List, Tuple

import numpy as np

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Import models
try:
    from cryptvault.ml.models.advanced_models import (
        BayesianRidgePredictor,
        CatBoostPredictor,
        QuantileRegressionPredictor,
        get_available_advanced_models,
    )
    from cryptvault.ml.models.ensemble_predictor import EnhancedEnsemblePredictor
    from cryptvault.ml.models.linear_models import ARIMAPredictor, LinearPredictor
    from cryptvault.ml.simple_predictor import SimplePredictor

    MODELS_AVAILABLE = True
except ImportError as e:
    logger.error(f"Failed to import models: {e}")
    MODELS_AVAILABLE = False


def generate_synthetic_data(
    n_samples: int = 1000, trend: str = "bullish"
) -> Tuple[np.ndarray, np.ndarray]:
    """Generate synthetic price data for testing."""
    np.random.seed(42)

    # Generate time series with trend
    t = np.linspace(0, 10, n_samples)

    if trend == "bullish":
        base_trend = 100 + 5 * t
    elif trend == "bearish":
        base_trend = 150 - 3 * t
    else:  # sideways
        base_trend = 100 + np.sin(t) * 2

    # Add noise and volatility
    noise = np.random.normal(0, 2, n_samples)
    volatility = np.random.normal(0, 1, n_samples)

    prices = base_trend + noise + volatility
    prices = np.maximum(prices, 1)  # Ensure positive prices

    # Create features (simple technical indicators)
    features = []
    for i in range(len(prices)):
        if i < 20:
            features.append(
                [
                    prices[i],
                    np.mean(prices[: i + 1]),
                    np.std(prices[: i + 1]) if i > 0 else 0.01,
                    0.0,
                    i / n_samples,
                ]
            )
        else:
            ma_20 = np.mean(prices[i - 20 : i])
            std_20 = np.std(prices[i - 20 : i])
            momentum = (prices[i] - prices[i - 1]) / prices[i - 1] if prices[i - 1] != 0 else 0

            features.append([prices[i], ma_20, std_20, momentum, i / n_samples])

    X = np.array(features)
    y = prices

    return X, y


def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """Calculate comprehensive prediction metrics."""
    # Basic metrics
    mse = np.mean((y_true - y_pred) ** 2)
    rmse = np.sqrt(mse)
    mae = np.mean(np.abs(y_true - y_pred))

    # R-squared
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

    # MAPE (Mean Absolute Percentage Error)
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100

    # Directional accuracy
    y_true_direction = np.sign(np.diff(y_true))
    y_pred_direction = np.sign(np.diff(y_pred))
    directional_accuracy = np.mean(y_true_direction == y_pred_direction) * 100

    # Max error
    max_error = np.max(np.abs(y_true - y_pred))

    return {
        "MSE": mse,
        "RMSE": rmse,
        "MAE": mae,
        "R2": r2,
        "MAPE": mape,
        "Directional_Accuracy": directional_accuracy,
        "Max_Error": max_error,
    }


def test_linear_predictor(X_train, y_train, X_test, y_test) -> Dict:
    """Test Linear Predictor."""
    logger.info("Testing Linear Predictor...")

    start_time = time.time()
    model = LinearPredictor()

    # Train
    train_success = model.train(X_train, y_train)
    train_time = time.time() - start_time

    if not train_success:
        return {"error": "Training failed", "train_time": train_time}

    # Predict
    start_time = time.time()
    y_pred = model.predict(X_test)
    predict_time = time.time() - start_time

    # Calculate metrics
    metrics = calculate_metrics(y_test, y_pred)
    metrics["train_time"] = train_time
    metrics["predict_time"] = predict_time
    metrics["model_name"] = "Linear Predictor"

    return metrics


def test_arima_predictor(y_train, y_test) -> Dict:
    """Test ARIMA Predictor."""
    logger.info("Testing ARIMA Predictor...")

    start_time = time.time()
    model = ARIMAPredictor(p=2, d=1, q=1)

    # Train
    train_success = model.fit(y_train.tolist())
    train_time = time.time() - start_time

    if not train_success:
        return {"error": "Training failed", "train_time": train_time}

    # Predict
    start_time = time.time()
    forecasts = model.forecast(steps=len(y_test))
    predict_time = time.time() - start_time

    # Convert to cumulative predictions
    y_pred = np.array(forecasts)
    if len(y_pred) < len(y_test):
        y_pred = np.pad(y_pred, (0, len(y_test) - len(y_pred)), mode="edge")

    # Calculate metrics
    metrics = calculate_metrics(y_test, y_pred[: len(y_test)])
    metrics["train_time"] = train_time
    metrics["predict_time"] = predict_time
    metrics["model_name"] = "ARIMA"

    return metrics


def test_ensemble_predictor(X_train, y_train, X_test, y_test) -> Dict:
    """Test Enhanced Ensemble Predictor."""
    logger.info("Testing Enhanced Ensemble Predictor...")

    start_time = time.time()
    model = EnhancedEnsemblePredictor(enable_deep_learning=False)

    # Train
    train_success = model.train(X_train, y_train)
    train_time = time.time() - start_time

    if not train_success:
        return {"error": "Training failed", "train_time": train_time}

    # Predict
    start_time = time.time()
    result = model.predict(X_test)
    predict_time = time.time() - start_time

    # Extract predictions
    if isinstance(result, dict) and "individual_predictions" in result:
        # Get ensemble prediction or average of individual predictions
        if "ensemble_prediction" in result:
            y_pred = np.array([result["ensemble_prediction"]] * len(y_test))
        else:
            preds = list(result["individual_predictions"].values())
            y_pred = np.array([np.mean(preds)] * len(y_test))
    else:
        return {"error": "Invalid prediction format", "train_time": train_time}

    # Calculate metrics
    metrics = calculate_metrics(y_test, y_pred)
    metrics["train_time"] = train_time
    metrics["predict_time"] = predict_time
    metrics["model_name"] = "Enhanced Ensemble"
    metrics["num_models"] = len(model.models)

    return metrics


def test_catboost_predictor(X_train, y_train, X_test, y_test) -> Dict:
    """Test CatBoost Predictor."""
    logger.info("Testing CatBoost Predictor...")

    try:
        start_time = time.time()
        model = CatBoostPredictor()

        if model.model is None:
            return {"error": "CatBoost not available", "train_time": 0}

        # Train
        train_success = model.train(X_train, y_train)
        train_time = time.time() - start_time

        if not train_success:
            return {"error": "Training failed", "train_time": train_time}

        # Predict
        start_time = time.time()
        y_pred = model.predict(X_test)
        predict_time = time.time() - start_time

        # Calculate metrics
        metrics = calculate_metrics(y_test, y_pred)
        metrics["train_time"] = train_time
        metrics["predict_time"] = predict_time
        metrics["model_name"] = "CatBoost"

        return metrics
    except Exception as e:
        return {"error": str(e), "model_name": "CatBoost"}


def test_bayesian_ridge_predictor(X_train, y_train, X_test, y_test) -> Dict:
    """Test Bayesian Ridge Predictor."""
    logger.info("Testing Bayesian Ridge Predictor...")

    try:
        start_time = time.time()
        model = BayesianRidgePredictor()

        if model.model is None:
            return {"error": "Bayesian Ridge not available", "train_time": 0}

        # Train
        train_success = model.train(X_train, y_train)
        train_time = time.time() - start_time

        if not train_success:
            return {"error": "Training failed", "train_time": train_time}

        # Predict with uncertainty
        start_time = time.time()
        y_pred, y_std = model.predict(X_test, return_std=True)
        predict_time = time.time() - start_time

        # Calculate metrics
        metrics = calculate_metrics(y_test, y_pred)
        metrics["train_time"] = train_time
        metrics["predict_time"] = predict_time
        metrics["model_name"] = "Bayesian Ridge"
        metrics["mean_uncertainty"] = np.mean(y_std)

        return metrics
    except Exception as e:
        return {"error": str(e), "model_name": "Bayesian Ridge"}


def test_quantile_regression_predictor(X_train, y_train, X_test, y_test) -> Dict:
    """Test Quantile Regression Predictor."""
    logger.info("Testing Quantile Regression Predictor...")

    try:
        start_time = time.time()
        model = QuantileRegressionPredictor(quantiles=[0.1, 0.5, 0.9])

        if not model.models:
            return {"error": "Quantile Regression not available", "train_time": 0}

        # Train
        train_success = model.train(X_train, y_train)
        train_time = time.time() - start_time

        if not train_success:
            return {"error": "Training failed", "train_time": train_time}

        # Predict
        start_time = time.time()
        predictions = model.predict(X_test)
        predict_time = time.time() - start_time

        # Use median prediction
        y_pred = predictions.get(0.5, list(predictions.values())[0])

        # Calculate metrics
        metrics = calculate_metrics(y_test, y_pred)
        metrics["train_time"] = train_time
        metrics["predict_time"] = predict_time
        metrics["model_name"] = "Quantile Regression"

        # Calculate prediction interval width
        if 0.1 in predictions and 0.9 in predictions:
            interval_width = np.mean(predictions[0.9] - predictions[0.1])
            metrics["prediction_interval_width"] = interval_width

        return metrics
    except Exception as e:
        return {"error": str(e), "model_name": "Quantile Regression"}


def print_results_table(results: List[Dict]):
    """Print results in a formatted table."""
    print("\n" + "=" * 120)
    print("COMPREHENSIVE MODEL TESTING RESULTS")
    print("=" * 120)

    # Header
    print(
        f"{'Model':<25} {'R²':<10} {'RMSE':<12} {'MAE':<12} {'MAPE %':<12} {'Dir Acc %':<12} {'Train (s)':<12} {'Predict (s)':<12}"
    )
    print("-" * 120)

    # Results
    for result in results:
        if "error" in result:
            print(f"{result.get('model_name', 'Unknown'):<25} ERROR: {result['error']}")
        else:
            print(
                f"{result['model_name']:<25} "
                f"{result.get('R2', 0):<10.4f} "
                f"{result.get('RMSE', 0):<12.4f} "
                f"{result.get('MAE', 0):<12.4f} "
                f"{result.get('MAPE', 0):<12.2f} "
                f"{result.get('Directional_Accuracy', 0):<12.2f} "
                f"{result.get('train_time', 0):<12.4f} "
                f"{result.get('predict_time', 0):<12.4f}"
            )

    print("=" * 120)

    # Summary statistics
    valid_results = [r for r in results if "error" not in r]
    if valid_results:
        print("\nSUMMARY STATISTICS:")
        print(
            f"  Best R² Score: {max(r.get('R2', 0) for r in valid_results):.4f} ({[r['model_name'] for r in valid_results if r.get('R2', 0) == max(r.get('R2', 0) for r in valid_results)][0]})"
        )
        print(
            f"  Best RMSE: {min(r.get('RMSE', float('inf')) for r in valid_results):.4f} ({[r['model_name'] for r in valid_results if r.get('RMSE', float('inf')) == min(r.get('RMSE', float('inf')) for r in valid_results)][0]})"
        )
        print(
            f"  Best Directional Accuracy: {max(r.get('Directional_Accuracy', 0) for r in valid_results):.2f}% ({[r['model_name'] for r in valid_results if r.get('Directional_Accuracy', 0) == max(r.get('Directional_Accuracy', 0) for r in valid_results)][0]})"
        )
        print(
            f"  Fastest Training: {min(r.get('train_time', float('inf')) for r in valid_results):.4f}s ({[r['model_name'] for r in valid_results if r.get('train_time', float('inf')) == min(r.get('train_time', float('inf')) for r in valid_results)][0]})"
        )
        print(
            f"  Fastest Prediction: {min(r.get('predict_time', float('inf')) for r in valid_results):.4f}s ({[r['model_name'] for r in valid_results if r.get('predict_time', float('inf')) == min(r.get('predict_time', float('inf')) for r in valid_results)][0]})"
        )


def main():
    """Main testing function."""
    if not MODELS_AVAILABLE:
        logger.error("Models not available. Please install required dependencies.")
        sys.exit(1)

    logger.info("Starting comprehensive model testing...")

    # Check available advanced models
    available = get_available_advanced_models()
    logger.info(f"Available advanced models: {available}")

    # Generate test data
    logger.info("Generating synthetic test data...")
    X, y = generate_synthetic_data(n_samples=1000, trend="bullish")

    # Split data (80/20)
    split_idx = int(0.8 * len(X))
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    logger.info(f"Training samples: {len(X_train)}, Test samples: {len(X_test)}")

    # Test all models
    results = []

    # 1. Linear Predictor
    try:
        result = test_linear_predictor(X_train, y_train, X_test, y_test)
        results.append(result)
    except Exception as e:
        logger.error(f"Linear Predictor test failed: {e}")
        results.append({"error": str(e), "model_name": "Linear Predictor"})

    # 2. ARIMA Predictor
    try:
        result = test_arima_predictor(y_train, y_test)
        results.append(result)
    except Exception as e:
        logger.error(f"ARIMA Predictor test failed: {e}")
        results.append({"error": str(e), "model_name": "ARIMA"})

    # 3. Enhanced Ensemble Predictor
    try:
        result = test_ensemble_predictor(X_train, y_train, X_test, y_test)
        results.append(result)
    except Exception as e:
        logger.error(f"Enhanced Ensemble test failed: {e}")
        results.append({"error": str(e), "model_name": "Enhanced Ensemble"})

    # 4. CatBoost Predictor
    if available.get("catboost", False):
        try:
            result = test_catboost_predictor(X_train, y_train, X_test, y_test)
            results.append(result)
        except Exception as e:
            logger.error(f"CatBoost test failed: {e}")
            results.append({"error": str(e), "model_name": "CatBoost"})
    else:
        logger.warning("CatBoost not available, skipping...")

    # 5. Bayesian Ridge Predictor
    try:
        result = test_bayesian_ridge_predictor(X_train, y_train, X_test, y_test)
        results.append(result)
    except Exception as e:
        logger.error(f"Bayesian Ridge test failed: {e}")
        results.append({"error": str(e), "model_name": "Bayesian Ridge"})

    # 6. Quantile Regression Predictor
    try:
        result = test_quantile_regression_predictor(X_train, y_train, X_test, y_test)
        results.append(result)
    except Exception as e:
        logger.error(f"Quantile Regression test failed: {e}")
        results.append({"error": str(e), "model_name": "Quantile Regression"})

    # Print results
    print_results_table(results)

    logger.info("Testing complete!")


if __name__ == "__main__":
    main()
