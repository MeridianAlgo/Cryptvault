"""
Advanced System Testing - Target <0.5% MAPE

Tests the advanced predictor with stacking and optimized features.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging
import sys
import warnings

warnings.filterwarnings("ignore")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

try:
    import yfinance as yf

    YFINANCE_AVAILABLE = True
except ImportError:
    logger.error("yfinance not available")
    YFINANCE_AVAILABLE = False

try:
    from cryptvault.ml.preprocessing import DataPreprocessor
    from cryptvault.ml.advanced_predictor import AdvancedPredictor

    COMPONENTS_AVAILABLE = True
except ImportError as e:
    logger.error(f"Failed to import: {e}")
    COMPONENTS_AVAILABLE = False


def fetch_data(symbol: str, days: int = 120) -> pd.DataFrame:
    """Fetch more data for better training."""
    ticker = f"{symbol}-USD"
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    logger.info(f"Fetching {symbol} data...")
    df = yf.download(ticker, start=start_date, end=end_date, progress=False)

    if df.empty:
        raise ValueError(f"No data for {symbol}")

    logger.info(f"Fetched {len(df)} data points")
    return df


def test_symbol(symbol: str, test_days: int = 5, optimize: bool = False):
    """Test advanced system on a cryptocurrency."""
    logger.info(f"\n{'='*100}")
    logger.info(f"Testing {symbol} with Advanced Predictor")
    logger.info(f"{'='*100}\n")

    # Fetch more data
    df = fetch_data(symbol, days=120)

    # Create preprocessor
    preprocessor = DataPreprocessor()

    # Create features
    logger.info("Creating advanced features...")
    features_df = preprocessor.create_features(df)

    # Drop rows with NaN
    features_df = features_df.iloc[50:].copy()
    df = df.iloc[50:].copy()

    logger.info(f"Features shape: {features_df.shape}")
    logger.info(f"Number of features: {features_df.shape[1]}")

    # Prepare target
    target = df["Close"].values

    # Split data
    split_idx = len(features_df) - test_days

    features_train = features_df.iloc[:split_idx]
    target_train = target[:split_idx]

    features_test = features_df.iloc[split_idx:]
    target_test = target[split_idx:]

    logger.info(f"Training samples: {len(features_train)}")
    logger.info(f"Test samples: {len(features_test)}")

    # Preprocess
    logger.info("\nPreprocessing...")
    X_train = preprocessor.fit_transform(features_train)
    y_train = target_train

    # Split for validation
    val_size = int(len(X_train) * 0.15)
    X_train_final = X_train[:-val_size]
    y_train_final = y_train[:-val_size]
    X_val = X_train[-val_size:]
    y_val = y_train[-val_size:]

    logger.info(f"Final training: {len(X_train_final)}, Validation: {len(X_val)}")

    # Transform test
    X_test = preprocessor.transform(features_test)
    y_test = target_test

    # Train advanced model
    logger.info("\nTraining Advanced Predictor...")
    model = AdvancedPredictor(optimize_hyperparams=optimize)

    success = model.train(X_train_final, y_train_final, X_val, y_val)

    if not success:
        logger.error("Training failed")
        return None

    # Predict
    logger.info("\nMaking predictions...")
    predictions = model.predict(X_test)

    logger.info(f"Predictions: {predictions}")
    logger.info(f"Actual: {y_test}")

    # Evaluate
    logger.info("\nEvaluating...")
    metrics = model.evaluate(X_test, y_test)

    # Print results
    print(f"\n{symbol} Results (Advanced Predictor):")
    print(f"{'='*80}")
    print(f"MAPE: {metrics['MAPE']:.3f}%")
    print(f"RMSE: ${metrics['RMSE']:.2f}")
    print(f"MAE: ${metrics['MAE']:.2f}")
    print(f"R2: {metrics['R2']:.4f}")
    print(f"Within 0.5%: {metrics['Within_0.5_Pct']:.1f}%")
    print(f"Within 1.0%: {metrics['Within_1.0_Pct']:.1f}%")
    print(f"Within 2.0%: {metrics['Within_2.0_Pct']:.1f}%")
    print(f"Direction Accuracy: {metrics['Direction_Accuracy']:.1f}%")
    print(f"{'='*80}")

    # Detailed comparison
    print(f"\nDetailed Predictions vs Actual:")
    print(f"{'Date':<12} {'Actual':<12} {'Predicted':<12} {'Error %':<10} {'Status':<10}")
    print(f"{'-'*60}")

    for i, (date, actual, pred) in enumerate(zip(df.index[split_idx:], y_test, predictions)):
        error_pct = abs((actual - pred) / actual) * 100
        status = "PASS" if error_pct <= 0.5 else "CLOSE" if error_pct <= 1.0 else "FAIL"
        print(
            f"{date.strftime('%Y-%m-%d'):<12} ${actual:<11.2f} ${pred:<11.2f} {error_pct:<9.3f}% {status:<10}"
        )

    # Status
    if metrics["MAPE"] <= 0.5:
        print(f"\nPASS: {symbol} meets 0.5% MAPE requirement!")
    elif metrics["MAPE"] <= 1.0:
        print(f"\nCLOSE: {symbol} at {metrics['MAPE']:.3f}% MAPE (target: 0.5%)")
    else:
        print(f"\nNEEDS WORK: {symbol} at {metrics['MAPE']:.3f}% MAPE (target: 0.5%)")

    return metrics


def main():
    """Main testing function."""
    if not YFINANCE_AVAILABLE or not COMPONENTS_AVAILABLE:
        logger.error("Required dependencies not available")
        sys.exit(1)

    # Test cryptocurrencies
    symbols = ["BTC", "ETH", "SOL", "BNB"]

    all_results = {}

    for symbol in symbols:
        try:
            metrics = test_symbol(symbol, test_days=5, optimize=False)
            if metrics:
                all_results[symbol] = metrics
        except Exception as e:
            logger.error(f"Failed to test {symbol}: {e}", exc_info=True)
            continue

    # Summary
    print(f"\n\n{'='*100}")
    print("ADVANCED SYSTEM SUMMARY")
    print(f"{'='*100}")

    if all_results:
        print(
            f"\n{'Symbol':<10} {'MAPE %':<12} {'0.5%':<10} {'1.0%':<10} {'2.0%':<10} {'R2':<10} {'Status':<15}"
        )
        print(f"{'-'*100}")

        for symbol, metrics in all_results.items():
            if metrics["MAPE"] <= 0.5:
                status = "PASS"
            elif metrics["MAPE"] <= 1.0:
                status = "CLOSE"
            else:
                status = "NEEDS WORK"

            print(
                f"{symbol:<10} {metrics['MAPE']:<12.3f} {metrics['Within_0.5_Pct']:<10.1f} "
                f"{metrics['Within_1.0_Pct']:<10.1f} {metrics['Within_2.0_Pct']:<10.1f} "
                f"{metrics['R2']:<10.4f} {status:<15}"
            )

        # Statistics
        mapes = [m["MAPE"] for m in all_results.values()]

        print(f"\n{'='*100}")
        print(f"Average MAPE: {np.mean(mapes):.3f}%")
        print(f"Best MAPE: {np.min(mapes):.3f}%")
        print(f"Worst MAPE: {np.max(mapes):.3f}%")
        print(f"Median MAPE: {np.median(mapes):.3f}%")

        passing = sum(1 for m in mapes if m <= 0.5)
        close = sum(1 for m in mapes if 0.5 < m <= 1.0)

        print(f"\nPassing (<=0.5%): {passing}/{len(mapes)}")
        print(f"Close (0.5-1.0%): {close}/{len(mapes)}")

        if passing == len(mapes):
            print("\nSUCCESS: All symbols meet 0.5% MAPE requirement!")
        elif passing + close == len(mapes):
            print("\nPROGRESS: All symbols within 1.0% MAPE")
        else:
            print("\nCONTINUING OPTIMIZATION...")

    print(f"{'='*100}\n")


if __name__ == "__main__":
    main()
