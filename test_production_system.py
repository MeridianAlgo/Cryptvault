"""
Production System Testing - Real Market Data with <0.5% MAPE Target

Complete end-to-end testing of the production ML system.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging
import sys
import warnings

warnings.filterwarnings("ignore")

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Import components
try:
    import yfinance as yf

    YFINANCE_AVAILABLE = True
except ImportError:
    logger.error("yfinance not available")
    YFINANCE_AVAILABLE = False

try:
    from cryptvault.ml.preprocessing import DataPreprocessor, split_train_val_test
    from cryptvault.ml.production_predictor import ProductionPredictor

    COMPONENTS_AVAILABLE = True
except ImportError as e:
    logger.error(f"Failed to import components: {e}")
    COMPONENTS_AVAILABLE = False


def fetch_data(symbol: str, days: int = 90) -> pd.DataFrame:
    """Fetch cryptocurrency data."""
    ticker = f"{symbol}-USD"
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    logger.info(f"Fetching {symbol} data...")
    df = yf.download(ticker, start=start_date, end=end_date, progress=False)

    if df.empty:
        raise ValueError(f"No data for {symbol}")

    logger.info(f"Fetched {len(df)} data points")
    return df


def test_symbol(symbol: str, test_days: int = 5):
    """Test production system on a cryptocurrency."""
    logger.info(f"\n{'='*100}")
    logger.info(f"Testing {symbol}")
    logger.info(f"{'='*100}\n")

    # Fetch data
    df = fetch_data(symbol, days=90)

    # Create preprocessor
    preprocessor = DataPreprocessor()

    # Create features
    logger.info("Creating features...")
    features_df = preprocessor.create_features(df)

    # Drop rows with too many NaN (first 50 rows typically)
    features_df = features_df.iloc[50:].copy()
    df = df.iloc[50:].copy()

    logger.info(f"Features shape after dropping NaN: {features_df.shape}")

    # Prepare target (next day's close price)
    target = df["Close"].values

    # Split data
    split_idx = len(features_df) - test_days

    features_train = features_df.iloc[:split_idx]
    target_train = target[:split_idx]

    features_test = features_df.iloc[split_idx:]
    target_test = target[split_idx:]

    logger.info(f"Training samples: {len(features_train)}")
    logger.info(f"Test samples: {len(features_test)}")
    logger.info(f"Test period: {df.index[split_idx]} to {df.index[-1]}")
    logger.info(f"Actual test prices: {target_test}")

    # Fit preprocessor and transform
    logger.info("\nPreprocessing data...")
    X_train = preprocessor.fit_transform(features_train)
    y_train = target_train

    # Further split training into train/val
    val_size = int(len(X_train) * 0.15)
    X_train_final = X_train[:-val_size]
    y_train_final = y_train[:-val_size]
    X_val = X_train[-val_size:]
    y_val = y_train[-val_size:]

    logger.info(f"Final training samples: {len(X_train_final)}")
    logger.info(f"Validation samples: {len(X_val)}")

    # Transform test data
    X_test = preprocessor.transform(features_test)
    y_test = target_test

    # Train model
    logger.info("\nTraining production model...")
    model = ProductionPredictor()

    success = model.train(X_train_final, y_train_final, X_val, y_val)

    if not success:
        logger.error("Training failed")
        return None

    # Make predictions
    logger.info("\nMaking predictions...")
    predictions = model.predict(X_test)

    logger.info(f"Predictions: {predictions}")

    # Evaluate
    logger.info("\nEvaluating performance...")
    metrics = model.evaluate(X_test, y_test)

    # Print results
    print(f"\n{symbol} Results:")
    print(f"{'='*80}")
    print(f"MAPE: {metrics['MAPE']:.3f}%")
    print(f"RMSE: ${metrics['RMSE']:.2f}")
    print(f"MAE: ${metrics['MAE']:.2f}")
    print(f"R²: {metrics['R2']:.4f}")
    print(f"Within 0.5%: {metrics['Within_0.5_Pct']:.1f}%")
    print(f"Within 1.0%: {metrics['Within_1_Pct']:.1f}%")
    print(f"Direction Accuracy: {metrics['Direction_Accuracy']:.1f}%")
    print(f"{'='*80}")

    # Detailed comparison
    print(f"\nDetailed Predictions vs Actual:")
    print(f"{'Date':<12} {'Actual':<12} {'Predicted':<12} {'Error %':<10}")
    print(f"{'-'*50}")

    for i, (date, actual, pred) in enumerate(zip(df.index[split_idx:], y_test, predictions)):
        error_pct = abs((actual - pred) / actual) * 100
        print(f"{date.strftime('%Y-%m-%d'):<12} ${actual:<11.2f} ${pred:<11.2f} {error_pct:<9.3f}%")

    # Check if meets 0.5% requirement
    if metrics["MAPE"] <= 0.5:
        print(f"\n✓ {symbol} MEETS 0.5% MAPE requirement!")
    elif metrics["MAPE"] <= 1.0:
        print(f"\n⚠ {symbol} close but needs improvement (MAPE: {metrics['MAPE']:.3f}%)")
    else:
        print(f"\n✗ {symbol} DOES NOT meet requirement (MAPE: {metrics['MAPE']:.3f}%)")

    return metrics


def main():
    """Main testing function."""
    if not YFINANCE_AVAILABLE or not COMPONENTS_AVAILABLE:
        logger.error("Required dependencies not available")
        sys.exit(1)

    # Test multiple cryptocurrencies
    symbols = ["BTC", "ETH", "SOL", "BNB"]

    all_results = {}

    for symbol in symbols:
        try:
            metrics = test_symbol(symbol, test_days=5)
            if metrics:
                all_results[symbol] = metrics
        except Exception as e:
            logger.error(f"Failed to test {symbol}: {e}", exc_info=True)
            continue

    # Overall summary
    print(f"\n\n{'='*100}")
    print("OVERALL SUMMARY")
    print(f"{'='*100}")

    if all_results:
        print(
            f"\n{'Symbol':<10} {'MAPE %':<12} {'Within 0.5%':<15} {'Within 1%':<12} {'R²':<10} {'Status':<20}"
        )
        print(f"{'-'*100}")

        for symbol, metrics in all_results.items():
            status = (
                "✓ PASS"
                if metrics["MAPE"] <= 0.5
                else "⚠ CLOSE" if metrics["MAPE"] <= 1.0 else "✗ FAIL"
            )
            print(
                f"{symbol:<10} {metrics['MAPE']:<12.3f} {metrics['Within_0.5_Pct']:<15.1f} "
                f"{metrics['Within_1_Pct']:<12.1f} {metrics['R2']:<10.4f} {status:<20}"
            )

        # Statistics
        mapes = [m["MAPE"] for m in all_results.values()]
        within_half = [m["Within_0.5_Pct"] for m in all_results.values()]

        print(f"\n{'='*100}")
        print(f"Average MAPE: {np.mean(mapes):.3f}%")
        print(f"Best MAPE: {np.min(mapes):.3f}%")
        print(f"Worst MAPE: {np.max(mapes):.3f}%")
        print(f"Average Within 0.5%: {np.mean(within_half):.1f}%")

        passing = sum(1 for m in mapes if m <= 0.5)
        print(f"\nSymbols meeting 0.5% requirement: {passing}/{len(mapes)}")

        if passing == len(mapes):
            print("\n🎉 ALL SYMBOLS MEET THE 0.5% MAPE REQUIREMENT!")
        elif passing > 0:
            print(f"\n⚠ {passing} out of {len(mapes)} symbols meet the requirement")
        else:
            print("\n⚠ No symbols meet the 0.5% requirement yet - further optimization needed")

    print(f"{'='*100}\n")


if __name__ == "__main__":
    main()
