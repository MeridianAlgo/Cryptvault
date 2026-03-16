"""
Test Ultimate ML System

Tests the best-of-everything predictor with all optimizations.
"""

import logging
import sys
from datetime import datetime, timedelta

import numpy as np
import yfinance as yf

sys.path.insert(0, ".")

from cryptvault.ml.preprocessing import DataPreprocessor, split_train_val_test
from cryptvault.ml.ultimate_predictor import UltimatePredictor

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_ultimate_system(symbol: str, days: int = 150):
    """Test ultimate ML system."""
    logger.info(f"\n{'='*80}")
    logger.info(f"Testing Ultimate System: {symbol}")
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
    logger.info(f"Created {len(features.columns)} features")

    # Target
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

    # Split with more training data
    X_train, y_train, X_val, y_val, X_test, y_test = split_train_val_test(
        X, y, train_ratio=0.75, val_ratio=0.15
    )

    logger.info(f"Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")

    # Walk-forward validation
    logger.info("\nPerforming walk-forward validation...")
    predictor = UltimatePredictor(
        enable_feature_selection=True,
        n_features_to_select=45,
        enable_hyperopt=False,  # Disable for speed
        use_lstm=False,
    )
    
    mean_mape, std_mape = predictor.walk_forward_validation(
        np.vstack([X_train, X_val]),
        np.concatenate([y_train, y_val]),
        n_splits=5
    )

    # Train ultimate predictor
    logger.info("\nTraining Ultimate Predictor...")
    success = predictor.train(X_train, y_train, X_val, y_val)

    if not success:
        logger.error("Training failed")
        return None

    # Predict with confidence
    test_pred, lower, upper = predictor.predict_with_confidence(X_test)

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

    within_05pct = np.mean(np.abs((y_test - test_pred) / y_test) < 0.005) * 100
    within_1pct = np.mean(np.abs((y_test - test_pred) / y_test) < 0.01) * 100
    within_2pct = np.mean(np.abs((y_test - test_pred) / y_test) < 0.02) * 100
    within_5pct = np.mean(np.abs((y_test - test_pred) / y_test) < 0.05) * 100

    logger.info(f"\n{'='*80}")
    logger.info(f"ULTIMATE SYSTEM RESULTS FOR {symbol}")
    logger.info(f"{'='*80}")
    logger.info(f"Walk-Forward CV:     {mean_mape:.4f}% ± {std_mape:.4f}%")
    logger.info(f"Test MAPE:           {mape:.4f}%")
    logger.info(f"RMSE:                ${rmse:.2f}")
    logger.info(f"MAE:                 ${mae:.2f}")
    logger.info(f"R²:                  {r2:.4f}")
    logger.info(f"Direction Accuracy:  {direction_accuracy:.2f}%")
    logger.info(f"Within 0.5%:         {within_05pct:.2f}%")
    logger.info(f"Within 1%:           {within_1pct:.2f}%")
    logger.info(f"Within 2%:           {within_2pct:.2f}%")
    logger.info(f"Within 5%:           {within_5pct:.2f}%")
    logger.info(f"{'='*80}\n")

    # Sample predictions
    logger.info("Sample Predictions (last 5):")
    logger.info(f"{'Actual':<12} {'Predicted':<12} {'Lower':<12} {'Upper':<12} {'Error %':<10}")
    logger.info("-" * 60)
    for i in range(max(0, len(y_test) - 5), len(y_test)):
        actual = y_test[i]
        pred = test_pred[i]
        low = lower[i]
        up = upper[i]
        error = abs((actual - pred) / actual) * 100
        logger.info(
            f"${actual:<11.2f} ${pred:<11.2f} ${low:<11.2f} ${up:<11.2f} {error:<9.3f}%"
        )

    # Model performance
    logger.info("\nModel Performance:")
    perf = predictor.get_model_performance()
    for name, metrics in perf.items():
        if "mape" in metrics:
            logger.info(
                f"{name:<15} MAPE: {metrics['mape']:.4f}%, "
                f"R²: {metrics['r2']:.4f}, Weight: {predictor.model_weights[name]:.4f}"
            )

    return {
        "symbol": symbol,
        "cv_mape": mean_mape,
        "cv_std": std_mape,
        "test_mape": mape,
        "rmse": rmse,
        "mae": mae,
        "r2": r2,
        "direction_accuracy": direction_accuracy,
        "within_05pct": within_05pct,
        "within_1pct": within_1pct,
        "within_2pct": within_2pct,
        "within_5pct": within_5pct,
        "test_samples": len(y_test),
    }


def main():
    """Test ultimate system on multiple cryptocurrencies."""
    symbols = ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD"]
    results = []

    for symbol in symbols:
        result = test_ultimate_system(symbol, days=150)
        if result:
            results.append(result)

    if results:
        logger.info(f"\n{'='*80}")
        logger.info("ULTIMATE SYSTEM SUMMARY")
        logger.info(f"{'='*80}")
        logger.info(
            f"{'Symbol':<10} {'CV MAPE':<12} {'Test MAPE':<12} {'R²':<10} {'Dir Acc':<12} {'Within 1%':<12}"
        )
        logger.info("-" * 80)

        for r in results:
            logger.info(
                f"{r['symbol']:<10} {r['cv_mape']:<12.4f} {r['test_mape']:<12.4f} "
                f"{r['r2']:<10.4f} {r['direction_accuracy']:<12.2f} {r['within_1pct']:<12.2f}"
            )

        avg_cv_mape = np.mean([r["cv_mape"] for r in results])
        avg_test_mape = np.mean([r["test_mape"] for r in results])
        avg_r2 = np.mean([r["r2"] for r in results])
        avg_dir = np.mean([r["direction_accuracy"] for r in results])
        avg_within_1 = np.mean([r["within_1pct"] for r in results])

        logger.info("-" * 80)
        logger.info(
            f"{'AVERAGE':<10} {avg_cv_mape:<12.4f} {avg_test_mape:<12.4f} "
            f"{avg_r2:<10.4f} {avg_dir:<12.2f} {avg_within_1:<12.2f}"
        )
        logger.info(f"{'='*80}\n")

        # Compare with baseline
        baseline_mape = 2.225
        improvement = ((baseline_mape - avg_test_mape) / baseline_mape) * 100

        if avg_test_mape < baseline_mape:
            logger.info(f"IMPROVEMENT: {improvement:.2f}% better than baseline ({baseline_mape:.3f}%)")
        else:
            logger.info(f"REGRESSION: {-improvement:.2f}% worse than baseline ({baseline_mape:.3f}%)")

        if avg_test_mape < 0.5:
            logger.info("TARGET ACHIEVED: Average MAPE < 0.5%")
        elif avg_test_mape < 1.0:
            logger.info("EXCELLENT: Average MAPE < 1.0%")
        elif avg_test_mape < 2.0:
            logger.info("GOOD: Average MAPE < 2.0%")


if __name__ == "__main__":
    main()
