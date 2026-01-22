"""
Real Market Data Testing - Validate ML Models with Actual Cryptocurrency Prices

Tests models against real historical data and ensures predictions are within 0.5% accuracy.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging
import sys
import time
from typing import Dict, List, Tuple
import warnings

warnings.filterwarnings("ignore")

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Import data fetching
try:
    import yfinance as yf

    YFINANCE_AVAILABLE = True
except ImportError:
    logger.error("yfinance not available. Install with: pip install yfinance")
    YFINANCE_AVAILABLE = False

# Import models
try:
    from cryptvault.ml.models.ensemble_predictor import EnhancedEnsemblePredictor
    from cryptvault.ml.models.linear_models import LinearPredictor
    from cryptvault.ml.features.technical_features import TechnicalFeatureExtractor

    MODELS_AVAILABLE = True
except ImportError as e:
    logger.error(f"Failed to import models: {e}")
    MODELS_AVAILABLE = False


def fetch_crypto_data(symbol: str, days: int = 60) -> pd.DataFrame:
    """Fetch real cryptocurrency data from yfinance."""
    if not YFINANCE_AVAILABLE:
        raise RuntimeError("yfinance not available")

    ticker = f"{symbol}-USD"
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    logger.info(f"Fetching {symbol} data from {start_date.date()} to {end_date.date()}...")

    df = yf.download(ticker, start=start_date, end=end_date, progress=False)

    if df.empty:
        raise ValueError(f"No data fetched for {symbol}")

    logger.info(f"Fetched {len(df)} data points for {symbol}")
    return df


def prepare_features(df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Prepare features and targets from price data."""
    close_prices = df["Close"].values

    # Calculate technical indicators as features
    features = []

    for i in range(len(close_prices)):
        if i < 20:
            # Not enough data for full indicators
            ma_5 = float(np.mean(close_prices[: i + 1]))
            ma_10 = float(np.mean(close_prices[: i + 1]))
            ma_20 = float(np.mean(close_prices[: i + 1]))
            std_20 = float(np.std(close_prices[: i + 1])) if i > 0 else 0.01
            momentum = 0.0
            rsi = 50.0
        else:
            # Calculate indicators
            ma_5 = float(np.mean(close_prices[i - 5 : i]))
            ma_10 = float(np.mean(close_prices[i - 10 : i]))
            ma_20 = float(np.mean(close_prices[i - 20 : i]))
            std_20 = float(np.std(close_prices[i - 20 : i]))

            # Momentum
            momentum = (
                float((close_prices[i] - close_prices[i - 1]) / close_prices[i - 1])
                if close_prices[i - 1] != 0
                else 0.0
            )

            # Simple RSI calculation
            deltas = np.diff(close_prices[max(0, i - 14) : i + 1])
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            avg_gain = float(np.mean(gains)) if len(gains) > 0 else 0.0
            avg_loss = float(np.mean(losses)) if len(losses) > 0 else 0.01
            rs = avg_gain / avg_loss if avg_loss != 0 else 0.0
            rsi = float(100 - (100 / (1 + rs)))

        # Feature vector - ensure all are scalars
        feature_vec = [
            float(close_prices[i]),  # Current price
            float(ma_5),
            float(ma_10),
            float(ma_20),
            float(std_20),
            float(momentum),
            float(rsi),
            float((close_prices[i] - ma_20) / ma_20) if ma_20 != 0 else 0.0,  # Distance from MA
            float(i / len(close_prices)),  # Time feature
        ]

        features.append(feature_vec)

    X = np.array(features, dtype=np.float64)
    y = np.array(close_prices, dtype=np.float64)

    return X, y, close_prices


def train_and_predict(model, X_train, y_train, X_test, n_predictions=5):
    """Train model and make predictions."""
    # Train
    train_start = time.time()
    success = model.train(X_train, y_train)
    train_time = time.time() - train_start

    if not success:
        return None, train_time, 0

    # Predict
    pred_start = time.time()

    # Make predictions for next N days
    predictions = []
    current_features = X_test[-1].copy()

    for i in range(n_predictions):
        # Predict next value
        pred_result = model.predict(current_features.reshape(1, -1))

        # Extract prediction value
        if isinstance(pred_result, dict):
            if "ensemble_prediction" in pred_result:
                pred_value = pred_result["ensemble_prediction"]
            elif "individual_predictions" in pred_result:
                preds = list(pred_result["individual_predictions"].values())
                pred_value = np.mean(preds) if preds else 0
            else:
                pred_value = 0
        elif isinstance(pred_result, np.ndarray):
            pred_value = pred_result[0] if len(pred_result) > 0 else 0
        else:
            pred_value = float(pred_result)

        predictions.append(pred_value)

        # Update features for next prediction (simple approach)
        # In reality, this would use the predicted value to update indicators
        current_features[0] = pred_value  # Update current price

    pred_time = time.time() - pred_start

    return np.array(predictions), train_time, pred_time


def calculate_accuracy_metrics(actual_prices, predicted_prices):
    """Calculate detailed accuracy metrics."""
    # Percentage errors
    pct_errors = np.abs((actual_prices - predicted_prices) / actual_prices) * 100

    # Mean Absolute Percentage Error
    mape = np.mean(pct_errors)

    # Max percentage error
    max_pct_error = np.max(pct_errors)

    # Within 0.5% accuracy count
    within_half_pct = np.sum(pct_errors <= 0.5)
    within_half_pct_ratio = within_half_pct / len(pct_errors) * 100

    # Within 1% accuracy count
    within_1_pct = np.sum(pct_errors <= 1.0)
    within_1_pct_ratio = within_1_pct / len(pct_errors) * 100

    # Direction accuracy
    if len(actual_prices) > 1:
        actual_direction = np.sign(np.diff(actual_prices))
        pred_direction = np.sign(np.diff(predicted_prices))
        direction_accuracy = np.mean(actual_direction == pred_direction) * 100
    else:
        direction_accuracy = 0

    return {
        "MAPE": mape,
        "Max_Error_Pct": max_pct_error,
        "Within_0.5_Pct": within_half_pct_ratio,
        "Within_1_Pct": within_1_pct_ratio,
        "Direction_Accuracy": direction_accuracy,
        "Individual_Errors": pct_errors,
    }


def test_crypto_symbol(symbol: str, test_days: int = 30):
    """Test models on a specific cryptocurrency."""
    logger.info(f"\n{'='*100}")
    logger.info(f"Testing {symbol}")
    logger.info(f"{'='*100}")

    # Fetch data
    try:
        df = fetch_crypto_data(symbol, days=60)
    except Exception as e:
        logger.error(f"Failed to fetch data for {symbol}: {e}")
        return None

    # Prepare features
    X, y, prices = prepare_features(df)

    # Split: Use first 30 days for training, predict next 5 days, compare with actual
    split_idx = len(X) - test_days
    test_split = split_idx + 5  # Predict 5 days ahead

    X_train = X[:split_idx]
    y_train = y[:split_idx]
    X_test = X[split_idx:test_split]
    y_test = y[split_idx:test_split]

    logger.info(f"Training samples: {len(X_train)}, Test samples: {len(y_test)}")
    logger.info(f"Training period: {df.index[0].date()} to {df.index[split_idx-1].date()}")
    logger.info(f"Test period: {df.index[split_idx].date()} to {df.index[test_split-1].date()}")
    logger.info(f"Actual prices in test period: {y_test}")

    results = []

    # Test Linear Predictor
    logger.info("\n--- Testing Linear Predictor ---")
    try:
        model = LinearPredictor()
        predictions, train_time, pred_time = train_and_predict(
            model, X_train, y_train, X_test, n_predictions=len(y_test)
        )

        if predictions is not None:
            logger.info(f"Predictions: {predictions}")
            metrics = calculate_accuracy_metrics(y_test, predictions)
            metrics["model"] = "Linear Predictor"
            metrics["train_time"] = train_time
            metrics["pred_time"] = pred_time
            results.append(metrics)

            logger.info(f"MAPE: {metrics['MAPE']:.2f}%")
            logger.info(f"Within 0.5%: {metrics['Within_0.5_Pct']:.1f}%")
            logger.info(f"Within 1.0%: {metrics['Within_1_Pct']:.1f}%")
    except Exception as e:
        logger.error(f"Linear Predictor failed: {e}")

    # Test Enhanced Ensemble
    logger.info("\n--- Testing Enhanced Ensemble ---")
    try:
        model = EnhancedEnsemblePredictor(enable_deep_learning=False)
        predictions, train_time, pred_time = train_and_predict(
            model, X_train, y_train, X_test, n_predictions=len(y_test)
        )

        if predictions is not None:
            logger.info(f"Predictions: {predictions}")
            metrics = calculate_accuracy_metrics(y_test, predictions)
            metrics["model"] = "Enhanced Ensemble"
            metrics["train_time"] = train_time
            metrics["pred_time"] = pred_time
            results.append(metrics)

            logger.info(f"MAPE: {metrics['MAPE']:.2f}%")
            logger.info(f"Within 0.5%: {metrics['Within_0.5_Pct']:.1f}%")
            logger.info(f"Within 1.0%: {metrics['Within_1_Pct']:.1f}%")
    except Exception as e:
        logger.error(f"Enhanced Ensemble failed: {e}")

    return results


def print_summary(all_results: Dict[str, List[Dict]]):
    """Print summary of all tests."""
    print("\n" + "=" * 120)
    print("REAL MARKET DATA TESTING SUMMARY")
    print("=" * 120)

    for symbol, results in all_results.items():
        if not results:
            continue

        print(f"\n{symbol}:")
        print(
            f"{'Model':<25} {'MAPE %':<12} {'Max Err %':<12} {'Within 0.5%':<15} {'Within 1%':<12} {'Dir Acc %':<12}"
        )
        print("-" * 120)

        for result in results:
            print(
                f"{result['model']:<25} "
                f"{result['MAPE']:<12.2f} "
                f"{result['Max_Error_Pct']:<12.2f} "
                f"{result['Within_0.5_Pct']:<15.1f} "
                f"{result['Within_1_Pct']:<12.1f} "
                f"{result['Direction_Accuracy']:<12.1f}"
            )

    print("=" * 120)

    # Overall statistics
    all_mapes = []
    all_within_half = []

    for results in all_results.values():
        for result in results:
            all_mapes.append(result["MAPE"])
            all_within_half.append(result["Within_0.5_Pct"])

    if all_mapes:
        print(f"\nOVERALL STATISTICS:")
        print(f"  Average MAPE: {np.mean(all_mapes):.2f}%")
        print(f"  Best MAPE: {np.min(all_mapes):.2f}%")
        print(f"  Worst MAPE: {np.max(all_mapes):.2f}%")
        print(f"  Average Within 0.5%: {np.mean(all_within_half):.1f}%")

        # Check if models meet 0.5% accuracy requirement
        models_meeting_req = sum(1 for mape in all_mapes if mape <= 0.5)
        print(f"\n  Models meeting 0.5% MAPE requirement: {models_meeting_req}/{len(all_mapes)}")

        if models_meeting_req < len(all_mapes):
            print("\n  ⚠️  WARNING: Not all models meet the 0.5% accuracy requirement!")
            print("  Models need improvement to achieve target accuracy.")
        else:
            print("\n  ✓ All models meet the 0.5% accuracy requirement!")


def main():
    """Main testing function."""
    if not YFINANCE_AVAILABLE or not MODELS_AVAILABLE:
        logger.error("Required dependencies not available")
        sys.exit(1)

    # Test multiple cryptocurrencies
    symbols = ["BTC", "ETH", "SOL", "BNB"]

    all_results = {}

    for symbol in symbols:
        try:
            results = test_crypto_symbol(symbol, test_days=30)
            if results:
                all_results[symbol] = results
        except Exception as e:
            logger.error(f"Failed to test {symbol}: {e}")
            continue

    # Print summary
    print_summary(all_results)


if __name__ == "__main__":
    main()
