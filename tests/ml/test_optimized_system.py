"""
Test Optimized ML System - Focus on what works

Uses the best-performing configuration from previous tests.
"""

import logging
import sys
from datetime import datetime, timedelta

import numpy as np
import yfinance as yf

sys.path.insert(0, ".")

from cryptvault.ml.production_predictor import ProductionPredictor
from cryptvault.ml.preprocessing import DataPreprocessor, split_train_val_test

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_optimized_system(symbol: str, days: int = 150):
    """Test with optimized configuration."""
    logger.info(f"\n{'='*80}")
    logger.info(f"Testing: {symbol}")
    logger.info(f"{'='*80}\n")

    # Fetch more data for better training
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    try:
        df = yf.download(symbol, start=start_date, end=end_date, progress=False)
    except Exception as e:
        logger.error(f"Failed to fetch data: {e}")
        return None

    if df.empty or len(df) < 50:
        logger.error(f"Insufficient data for {symbol}")
        return None

    logger.info(f"Downloaded {len(df)} data points")

    # Create features
    preprocessor = DataPreprocessor()
    features = preprocessor.create_features(df)
    
    # Target: predict percentage change instead of absolute price
    # This normalizes the problem and makes it easier to learn
    target = df["Close"].pct_change().shift(-1).values[:-1] * 100  # Next day % change
    features = features.iloc[:-1]

    # Remove NaN
    valid_mask = ~np.isnan(target) & ~np.isinf(target)
    features = features[valid_mask]
    target = target[valid_mask]

    logger.info(f"Valid samples: {len(target)}")

    # Transform features
    X = preprocessor.fit_transform(features)
    y = target

    # Split with more training data
    X_train, y_train, X_val, y_val, X_test, y_test = split_train_val_test(
        X, y, train_ratio=0.75, val_ratio=0.15
    )

    logger.info(f"Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")

    # Train
    predictor = ProductionPredictor()
    success = predictor.train(X_train, y_train, X_val, y_val)

    if not success:
        logger.error("Training failed")
        return None

    # Predict
    test_pred = predictor.predict(X_test)

    # Calculate metrics on percentage change
    mape = np.mean(np.abs((y_test - test_pred) / (y_test + 1e-10))) * 100
    rmse = np.sqrt(np.mean((y_test - test_pred) ** 2))
    mae = np.mean(np.abs(y_test - test_pred))
    
    ss_res = np.sum((y_test - test_pred) ** 2)
    ss_tot = np.sum((y_test - np.mean(y_test)) ** 2)
    r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

    # Direction accuracy
    direction_acc = np.mean(np.sign(y_test) == np.sign(test_pred)) * 100

    # Within thresholds (for percentage changes)
    within_01pct = np.mean(np.abs(y_test - test_pred) < 0.1) * 100
    within_05pct = np.mean(np.abs(y_test - test_pred) < 0.5) * 100
    within_1pct = np.mean(np.abs(y_test - test_pred) < 1.0) * 100

    logger.info(f"\n{'='*80}")
    logger.info(f"RESULTS FOR {symbol}")
    logger.info(f"{'='*80}")
    logger.info(f"MAPE (% change):     {mape:.4f}%")
    logger.info(f"RMSE (% change):     {rmse:.4f}%")
    logger.info(f"MAE (% change):      {mae:.4f}%")
    logger.info(f"R²:                  {r2:.4f}")
    logger.info(f"Direction Accuracy:  {direction_acc:.2f}%")
    logger.info(f"Within 0.1%:         {within_01pct:.2f}%")
    logger.info(f"Within 0.5%:         {within_05pct:.2f}%")
    logger.info(f"Within 1.0%:         {within_1pct:.2f}%")
    logger.info(f"{'='*80}\n")

    # Sample predictions
    logger.info("Sample Predictions (last 5 - % change):")
    logger.info(f"{'Actual %':<12} {'Predicted %':<12} {'Error':<10}")
    logger.info("-" * 40)
    for i in range(max(0, len(y_test) - 5), len(y_test)):
        actual = y_test[i]
        pred = test_pred[i]
        error = abs(actual - pred)
        logger.info(f"{actual:<12.3f} {pred:<12.3f} {error:<10.3f}")

    return {
        "symbol": symbol,
        "mape": mape,
        "rmse": rmse,
        "mae": mae,
        "r2": r2,
        "direction_accuracy": direction_acc,
        "within_01pct": within_01pct,
        "within_05pct": within_05pct,
        "within_1pct": within_1pct,
    }


def main():
    """Test on multiple cryptocurrencies."""
    symbols = ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD"]
    results = []

    for symbol in symbols:
        result = test_optimized_system(symbol, days=150)
        if result:
            results.append(result)

    if results:
        logger.info(f"\n{'='*80}")
        logger.info("SUMMARY - OPTIMIZED SYSTEM (% Change Prediction)")
        logger.info(f"{'='*80}")
        logger.info(f"{'Symbol':<10} {'MAPE':<10} {'R²':<10} {'Dir Acc':<12} {'Within 0.5%':<12}")
        logger.info("-" * 80)

        for r in results:
            logger.info(
                f"{r['symbol']:<10} {r['mape']:<10.4f} {r['r2']:<10.4f} "
                f"{r['direction_accuracy']:<12.2f} {r['within_05pct']:<12.2f}"
            )

        avg_mape = np.mean([r["mape"] for r in results])
        avg_r2 = np.mean([r["r2"] for r in results])
        avg_dir = np.mean([r["direction_accuracy"] for r in results])

        logger.info("-" * 80)
        logger.info(
            f"{'AVERAGE':<10} {avg_mape:<10.4f} {avg_r2:<10.4f} {avg_dir:<12.2f}"
        )
        logger.info(f"{'='*80}\n")


if __name__ == "__main__":
    main()
