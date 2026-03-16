"""
Test ML System with Alternative Data Sources

Integrates sentiment, on-chain metrics, and other alternative data.
"""

import logging
import sys
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import yfinance as yf

sys.path.insert(0, ".")

from cryptvault.data.alternative_data import AlternativeDataFetcher, merge_alternative_data
from cryptvault.ml.preprocessing import DataPreprocessor, split_train_val_test
from cryptvault.ml.production_predictor import ProductionPredictor

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_with_alternative_data(symbol: str, days: int = 120):
    """Test ML system with alternative data sources."""
    logger.info(f"\n{'='*80}")
    logger.info(f"Testing with Alternative Data: {symbol}")
    logger.info(f"{'='*80}\n")

    # Fetch price data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    try:
        df = yf.download(symbol, start=start_date, end=end_date, progress=False)
    except Exception as e:
        logger.error(f"Failed to fetch price data: {e}")
        return None

    if df.empty or len(df) < 50:
        logger.error(f"Insufficient data for {symbol}")
        return None

    logger.info(f"Downloaded {len(df)} price data points")

    # Fetch alternative data
    logger.info("Fetching alternative data sources...")
    alt_fetcher = AlternativeDataFetcher()
    alt_data = alt_fetcher.fetch_all_alternative_data(symbol, days=days)

    logger.info(f"Fetched {len(alt_data)} alternative data sources:")
    for source, data in alt_data.items():
        if data is not None:
            logger.info(f"  - {source}: {len(data)} records, {len(data.columns)} features")

    # Create base features
    preprocessor = DataPreprocessor()
    features = preprocessor.create_features(df)
    logger.info(f"Created {len(features.columns)} base features")

    # Merge alternative data
    if alt_data:
        features = merge_alternative_data(features, alt_data)
        logger.info(f"Total features after merge: {len(features.columns)}")

    # Prepare target
    target = df["Close"].shift(-1).values[:-1]
    features = features.iloc[:-1]

    # Remove NaN
    valid_mask = ~np.isnan(target)
    features = features[valid_mask]
    target = target[valid_mask]

    logger.info(f"Valid samples: {len(target)}")

    # Transform
    try:
        X = preprocessor.fit_transform(features)
        y = target
    except Exception as e:
        logger.error(f"Preprocessing failed: {e}")
        return None

    # Split
    X_train, y_train, X_val, y_val, X_test, y_test = split_train_val_test(
        X, y, train_ratio=0.7, val_ratio=0.15
    )

    logger.info(f"Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")

    # Train
    logger.info("\nTraining with alternative data...")
    predictor = ProductionPredictor()
    success = predictor.train(X_train, y_train, X_val, y_val)

    if not success:
        logger.error("Training failed")
        return None

    # Predict
    test_pred = predictor.predict(X_test)

    # Metrics
    mape = np.mean(np.abs((y_test - test_pred) / y_test)) * 100
    rmse = np.sqrt(np.mean((y_test - test_pred) ** 2))
    mae = np.mean(np.abs(y_test - test_pred))

    ss_res = np.sum((y_test - test_pred) ** 2)
    ss_tot = np.sum((y_test - np.mean(y_test)) ** 2)
    r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

    actual_direction = np.sign(np.diff(y_test))
    pred_direction = np.sign(np.diff(test_pred))
    direction_accuracy = np.mean(actual_direction == pred_direction) * 100

    within_1pct = np.mean(np.abs((y_test - test_pred) / y_test) < 0.01) * 100
    within_2pct = np.mean(np.abs((y_test - test_pred) / y_test) < 0.02) * 100
    within_5pct = np.mean(np.abs((y_test - test_pred) / y_test) < 0.05) * 100

    logger.info(f"\n{'='*80}")
    logger.info(f"RESULTS FOR {symbol} (WITH ALTERNATIVE DATA)")
    logger.info(f"{'='*80}")
    logger.info(f"Features Used:       {len(features.columns)} (base + alternative)")
    logger.info(f"MAPE:                {mape:.4f}%")
    logger.info(f"RMSE:                ${rmse:.2f}")
    logger.info(f"MAE:                 ${mae:.2f}")
    logger.info(f"R²:                  {r2:.4f}")
    logger.info(f"Direction Accuracy:  {direction_accuracy:.2f}%")
    logger.info(f"Within 1%:           {within_1pct:.2f}%")
    logger.info(f"Within 2%:           {within_2pct:.2f}%")
    logger.info(f"Within 5%:           {within_5pct:.2f}%")
    logger.info(f"{'='*80}\n")

    # Sample predictions
    logger.info("Sample Predictions (last 5):")
    logger.info(f"{'Actual':<12} {'Predicted':<12} {'Error %':<10}")
    logger.info("-" * 40)
    for i in range(max(0, len(y_test) - 5), len(y_test)):
        actual = y_test[i]
        pred = test_pred[i]
        error = abs((actual - pred) / actual) * 100
        logger.info(f"${actual:<11.2f} ${pred:<11.2f} {error:<9.3f}%")

    return {
        "symbol": symbol,
        "num_features": len(features.columns),
        "mape": mape,
        "rmse": rmse,
        "mae": mae,
        "r2": r2,
        "direction_accuracy": direction_accuracy,
        "within_1pct": within_1pct,
        "within_2pct": within_2pct,
        "within_5pct": within_5pct,
        "test_samples": len(y_test),
    }


def main():
    """Test on multiple cryptocurrencies with alternative data."""
    symbols = ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD"]
    results = []

    for symbol in symbols:
        result = test_with_alternative_data(symbol, days=120)
        if result:
            results.append(result)

    if results:
        logger.info(f"\n{'='*80}")
        logger.info("SUMMARY - WITH ALTERNATIVE DATA")
        logger.info(f"{'='*80}")
        logger.info(
            f"{'Symbol':<10} {'Features':<10} {'MAPE':<10} {'R²':<10} {'Dir Acc':<12} {'Within 2%':<12}"
        )
        logger.info("-" * 80)

        for r in results:
            logger.info(
                f"{r['symbol']:<10} {r['num_features']:<10} {r['mape']:<10.4f} "
                f"{r['r2']:<10.4f} {r['direction_accuracy']:<12.2f} {r['within_2pct']:<12.2f}"
            )

        avg_mape = np.mean([r["mape"] for r in results])
        avg_r2 = np.mean([r["r2"] for r in results])
        avg_dir = np.mean([r["direction_accuracy"] for r in results])
        avg_within_2 = np.mean([r["within_2pct"] for r in results])

        logger.info("-" * 80)
        logger.info(
            f"{'AVERAGE':<10} {'':<10} {avg_mape:<10.4f} "
            f"{avg_r2:<10.4f} {avg_dir:<12.2f} {avg_within_2:<12.2f}"
        )
        logger.info(f"{'='*80}\n")

        # Compare with baseline
        baseline_mape = 2.225  # From previous tests
        improvement = ((baseline_mape - avg_mape) / baseline_mape) * 100

        if avg_mape < baseline_mape:
            logger.info(f"IMPROVEMENT: {improvement:.2f}% better than baseline ({baseline_mape:.3f}%)")
        else:
            logger.info(f"REGRESSION: {-improvement:.2f}% worse than baseline ({baseline_mape:.3f}%)")

        if avg_mape < 0.5:
            logger.info("TARGET ACHIEVED: Average MAPE < 0.5%")
        elif avg_mape < 1.0:
            logger.info("EXCELLENT: Average MAPE < 1.0%")
        elif avg_mape < 2.0:
            logger.info("GOOD: Average MAPE < 2.0%")


if __name__ == "__main__":
    main()
