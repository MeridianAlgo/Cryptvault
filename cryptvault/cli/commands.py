"""
CLI Commands Module

This module provides command implementations for the CryptVault CLI,
handling the core functionality for analyzing cryptocurrencies, portfolios,
and other operations.

Functions:
    - analyze_ticker: Analyze a single ticker symbol
    - analyze_portfolio: Analyze a portfolio of holdings
    - compare_assets: Compare multiple assets
    - show_demo: Show demo information
    - show_api_status: Show data source status
    - show_prediction_accuracy: Show ML prediction accuracy
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from cryptvault.core.analyzer import PatternAnalyzer
from .formatters import (
    format_analysis_results,
    format_portfolio_results,
    format_comparison_results,
    format_success,
    format_error,
    format_info,
    format_warning,
    create_progress_indicator
)
from .validators import (
    validate_ticker,
    validate_days,
    validate_interval,
    validate_portfolio_holdings,
    validate_file_path,
    ValidationError
)


logger = logging.getLogger(__name__)


def analyze_ticker(
    ticker: str,
    days: int = 30,
    interval: str = '1d',
    verbose: bool = False,
    generate_chart: bool = True,
    save_chart_path: Optional[str] = None,
    no_chart: bool = False
) -> bool:
    """
    Analyze a cryptocurrency or stock ticker.

    Args:
        ticker: Ticker symbol to analyze
        days: Number of days of historical data
        interval: Data interval (1h, 4h, 1d, etc.)
        verbose: Enable verbose output
        generate_chart: Whether to generate chart
        save_chart_path: Path to save chart (if provided)
        no_chart: Disable chart generation

    Returns:
        True if analysis succeeded, False otherwise

    Example:
        >>> analyze_ticker('BTC', days=60, interval='1d')
        True
    """
    try:
        # Initialize analyzer
        analyzer = PatternAnalyzer()

        # Validate inputs
        supported_tickers = analyzer.get_supported_tickers()
        ticker = validate_ticker(ticker, supported_tickers)
        days = validate_days(days)
        interval = validate_interval(interval)

        if save_chart_path:
            save_chart_path = validate_file_path(save_chart_path)

        # Disable chart if explicitly requested
        if no_chart:
            generate_chart = False

        # Show progress indicator
        progress = create_progress_indicator(f"Analyzing {ticker}")
        progress.start()

        # Perform analysis
        try:
            results = analyzer.analyze_ticker(ticker, days=days, interval=interval)
        finally:
            progress.stop()

        # Convert AnalysisResult to dict if needed
        if hasattr(results, 'to_dict'):
            results_dict = results.to_dict()
        elif isinstance(results, dict):
            results_dict = results
        else:
            # Fallback: create dict from object attributes
            results_dict = {
                'success': getattr(results, 'success', False),
                'symbol': getattr(results, 'symbol', 'Unknown'),
                'patterns_found': len(getattr(results, 'patterns', [])),
                'patterns': getattr(results, 'patterns', []),
                'pattern_summary': getattr(results, 'pattern_summary', {}),
                'technical_indicators': getattr(results, 'technical_indicators', {}),
                'ml_predictions': getattr(results, 'ml_predictions', None),
                'ticker_info': getattr(results, 'ticker_info', {}),
                'analysis_time_seconds': getattr(results, 'analysis_time', 0),
                'errors': getattr(results, 'errors', []),
                'warnings': getattr(results, 'warnings', [])
            }

        # Format and display results
        output = format_analysis_results(results_dict, verbose=verbose)
        print(output)

        if not results_dict.get('success', False):
            return False

        # Generate chart if requested
        if generate_chart or save_chart_path:
            _generate_chart(ticker, days, interval, save_chart_path, verbose)

        return True

    except ValidationError as e:
        print(format_error(str(e)))
        return False
    except Exception as e:
        logger.exception("Error analyzing ticker")
        print(format_error(f"Analysis failed: {e}"))
        if verbose:
            import traceback
            traceback.print_exc()
        return False


def analyze_portfolio(holdings_str: List[str], verbose: bool = False) -> bool:
    """
    Analyze a cryptocurrency portfolio.

    Args:
        holdings_str: List of holdings in format ['BTC:0.5', 'ETH:10']
        verbose: Enable verbose output

    Returns:
        True if analysis succeeded, False otherwise

    Example:
        >>> analyze_portfolio(['BTC:0.5', 'ETH:10'])
        True
    """
    try:
        # Validate and parse holdings
        holdings = validate_portfolio_holdings(holdings_str)

        print(format_info(f"Analyzing portfolio with {len(holdings)} assets"))

        # Import portfolio analyzer
        try:
            from cryptvault.portfolio.analyzer import PortfolioAnalyzer, PortfolioAsset
        except ImportError:
            print(format_error("Portfolio analysis requires pandas: pip install pandas"))
            return False

        # Convert holdings dict to PortfolioAsset objects
        portfolio_assets = []
        total_value = sum(holdings.values())
        
        for symbol, amount in holdings.items():
            # Convert monetary amount to allocation percentage
            allocation = amount / total_value if total_value > 0 else 0
            portfolio_assets.append(PortfolioAsset(symbol=symbol, allocation=allocation))

        # Show progress
        progress = create_progress_indicator("Analyzing portfolio")
        progress.start()

        try:
            portfolio_analyzer = PortfolioAnalyzer()
            results = portfolio_analyzer.analyze_portfolio(portfolio_assets)
        finally:
            progress.stop()

        # Format and display results
        output = format_portfolio_results(results)
        print(output)

        return results.get('success', False)

    except ValidationError as e:
        print(format_error(str(e)))
        return False
    except Exception as e:
        logger.exception("Error analyzing portfolio")
        print(format_error(f"Portfolio analysis failed: {e}"))
        if verbose:
            import traceback
            traceback.print_exc()
        return False


def compare_assets(symbols: List[str], verbose: bool = False) -> bool:
    """
    Compare multiple cryptocurrency assets.

    Args:
        symbols: List of ticker symbols to compare
        verbose: Enable verbose output

    Returns:
        True if comparison succeeded, False otherwise

    Example:
        >>> compare_assets(['BTC', 'ETH', 'ADA'])
        True
    """
    try:
        # Validate symbols
        analyzer = PatternAnalyzer()
        supported_tickers = analyzer.get_supported_tickers()

        validated_symbols = []
        for symbol in symbols:
            validated_symbols.append(validate_ticker(symbol, supported_tickers))

        print(format_info(f"Comparing {len(validated_symbols)} assets"))

        # Import portfolio analyzer for comparison
        try:
            from cryptvault.portfolio.analyzer import PortfolioAnalyzer
        except ImportError:
            print(format_error("Asset comparison requires pandas: pip install pandas"))
            return False

        # Show progress
        progress = create_progress_indicator("Comparing assets")
        progress.start()

        try:
            portfolio_analyzer = PortfolioAnalyzer()
            results = portfolio_analyzer.compare_assets(validated_symbols)
        finally:
            progress.stop()

        # Format and display results
        output = format_comparison_results(results)
        print(output)

        return results.get('success', False)

    except ValidationError as e:
        print(format_error(str(e)))
        return False
    except Exception as e:
        logger.exception("Error comparing assets")
        print(format_error(f"Asset comparison failed: {e}"))
        if verbose:
            import traceback
            traceback.print_exc()
        return False


def show_demo() -> None:
    """
    Show demo information including supported tickers and current prices.

    Example:
        >>> show_demo()
    """
    try:
        analyzer = PatternAnalyzer()

        print("\n" + "=" * 70)
        print("CryptVault v4.0.0 Demo")
        print("=" * 70)

        # Search functionality demo
        search_results = analyzer.search_tickers("bitcoin", limit=3)
        if search_results:
            print("\nSearch Results for 'bitcoin':")
            for result in search_results:
                print(f"  • {result['symbol']}: {result['name']}")

        # Show supported assets
        supported = analyzer.get_supported_tickers()
        print(f"\nTotal Supported Assets: {len(supported)}")

        # Top cryptocurrencies
        print("\nTop Cryptocurrencies (20):")
        crypto_list = [
            s for s in supported
            if s in ['BTC', 'ETH', 'USDT', 'BNB', 'SOL', 'XRP', 'USDC', 'ADA',
                    'AVAX', 'DOGE', 'TRX', 'DOT', 'MATIC', 'LINK', 'TON', 'SHIB',
                    'LTC', 'BCH', 'UNI', 'ATOM']
        ]
        print(f"  {', '.join(crypto_list)}")

        # Popular stocks
        print("\nPopular Stocks (10):")
        stock_list = [
            s for s in supported
            if s in ['AAPL', 'TSLA', 'GOOGL', 'MSFT', 'NVDA', 'AMZN', 'META',
                    'NFLX', 'AMD', 'INTC']
        ]
        print(f"  {', '.join(stock_list)}")

        # Current price example
        print("\nCurrent Prices:")
        btc_price = analyzer.get_current_price("BTC")
        if btc_price:
            print(f"  BTC: ${btc_price:,.2f}")
        else:
            print("  BTC: Price unavailable")

        print("\n" + "=" * 70)
        print("Try: python cryptvault_cli.py BTC 60 1d")
        print("=" * 70 + "\n")

    except Exception as e:
        logger.exception("Error showing demo")
        print(format_error(f"Demo failed: {e}"))


def show_api_status() -> None:
    """
    Show data source status and availability.

    Example:
        >>> show_api_status()
    """
    try:
        analyzer = PatternAnalyzer()
        sources = analyzer.data_fetcher.get_available_sources()

        print("\n" + "=" * 70)
        print("Data Sources Status")
        print("=" * 70)

        for source_name, available in sources.items():
            if available:
                status = format_success(f"{source_name.title()}: Available")
            else:
                status = format_warning(f"{source_name.title()}: Not installed")
            print(f"  {status}")

        # Show installation suggestions for missing packages
        missing = [name for name, available in sources.items() if not available]
        if missing:
            print("\nInstallation suggestions:")
            for package in missing:
                if package == 'yfinance':
                    print(f"  pip install yfinance")
                elif package == 'ccxt':
                    print(f"  pip install ccxt")
                elif package == 'cryptocompare':
                    print(f"  pip install cryptocompare")

        print("=" * 70 + "\n")

    except Exception as e:
        logger.exception("Error showing API status")
        print(format_error(f"Failed to get API status: {e}"))


def show_prediction_accuracy(days: int = 30, verbose: bool = False) -> None:
    """
    Show ML prediction accuracy report.

    Args:
        days: Number of days to include in report
        verbose: Enable verbose output

    Example:
        >>> show_prediction_accuracy(30)
    """
    try:
        from cryptvault.ml.predictor import MLPredictor

        print("\n" + "=" * 70)
        print("ML Prediction Accuracy Report")
        print("=" * 70)

        predictor = MLPredictor()

        # Get accuracy report
        progress = create_progress_indicator("Generating accuracy report")
        progress.start()

        try:
            report = predictor.get_prediction_accuracy_report(days)
        finally:
            progress.stop()

        if 'error' in report:
            print(format_error(f"Error generating report: {report['error']}"))
            return

        if report.get('total_predictions', 0) == 0:
            print(format_info("No verified predictions found in the specified period"))
            print(format_info("Make some predictions first, then check back later!"))
            return

        # Overall statistics
        print(f"\nOverall Accuracy: {report['overall_accuracy']:.1%}")
        print(f"Total Predictions: {report['total_predictions']}")
        print(f"Accurate Predictions: {report['accurate_predictions']}")
        print(f"Average Error: {report['average_error']:.1%}")

        # Accuracy by symbol
        if report.get('accuracy_by_symbol'):
            print("\nAccuracy by Symbol:")
            for symbol, data in report['accuracy_by_symbol'].items():
                accuracy = data['accuracy_rate']
                total = data['total']
                confidence = data['avg_confidence']
                print(f"  {symbol}: {accuracy:.1%} ({total} predictions, "
                     f"avg confidence: {confidence:.1%})")

        # Recent predictions (if verbose)
        if verbose and report.get('recent_predictions'):
            print("\nRecent Predictions:")
            for pred in report['recent_predictions'][:10]:
                symbol = pred['symbol']
                predicted = pred['predicted']
                actual = pred['actual']
                accuracy = pred['accuracy']
                date = pred['date']

                if accuracy >= 0.9:
                    status = format_success("Accurate")
                else:
                    status = format_warning("Inaccurate")

                print(f"  {status} {symbol} on {date}: "
                     f"Predicted ${predicted:.2f}, Actual ${actual:.2f} "
                     f"(Score: {accuracy:.1%})")

        # Cache statistics
        cache_stats = predictor.cache.get_cache_stats()
        print("\nCache Statistics:")
        print(f"  Total Predictions: {cache_stats['total_predictions']}")
        print(f"  Verified: {cache_stats['verified_predictions']}")
        print(f"  Pending: {cache_stats['pending_predictions']}")
        print(f"  Cache Size: {cache_stats['cache_size_mb']:.2f} MB")

        print("=" * 70 + "\n")

    except ImportError:
        print(format_error("ML prediction modules not available"))
    except Exception as e:
        logger.exception("Error showing prediction accuracy")
        print(format_error(f"Failed to generate accuracy report: {e}"))
        if verbose:
            import traceback
            traceback.print_exc()


def start_live_analysis(symbol: str, verbose: bool = False) -> None:
    """
    Start live analysis for a symbol.

    Args:
        symbol: Ticker symbol to analyze
        verbose: Enable verbose output

    Example:
        >>> start_live_analysis('BTC')
    """
    try:
        # Validate symbol
        analyzer = PatternAnalyzer()
        supported_tickers = analyzer.get_supported_tickers()
        symbol = validate_ticker(symbol, supported_tickers)

        from cryptvault.data.websocket_stream import LiveAnalyzer

        print(format_info(f"Starting live analysis for {symbol}"))
        print(format_info("Press Ctrl+C to stop"))

        live_analyzer = LiveAnalyzer()
        live_analyzer.start_live_analysis(symbol)

    except ValidationError as e:
        print(format_error(str(e)))
    except ImportError:
        print(format_error("Live analysis requires websockets: pip install websockets"))
    except KeyboardInterrupt:
        print(format_info("\nLive analysis stopped"))
    except Exception as e:
        logger.exception("Error in live analysis")
        print(format_error(f"Live analysis failed: {e}"))
        if verbose:
            import traceback
            traceback.print_exc()


def open_desktop_charts(verbose: bool = False) -> None:
    """
    Open desktop charts in a new window.

    Args:
        verbose: Enable verbose output

    Example:
        >>> open_desktop_charts()
    """
    try:
        from cryptvault.visualization.desktop_charts import CryptVaultDesktopCharts

        print(format_info("Opening CryptVault Desktop Charts..."))
        print(format_info("A new window will open with interactive charts"))

        app = CryptVaultDesktopCharts()
        app.run()

    except ImportError as e:
        print(format_error("Desktop charts require additional packages:"))
        print("  pip install tkinter matplotlib numpy pandas")
        print(f"Missing: {e}")
    except Exception as e:
        logger.exception("Error opening desktop charts")
        print(format_error(f"Desktop charts failed: {e}"))
        if verbose:
            import traceback
            traceback.print_exc()


def _generate_chart(
    ticker: str,
    days: int,
    interval: str,
    save_path: Optional[str],
    verbose: bool
) -> None:
    """
    Generate chart with pattern overlays using the new ChartGenerator.

    Args:
        ticker: Ticker symbol
        days: Number of days
        interval: Data interval
        save_path: Path to save chart (if provided)
        verbose: Enable verbose output
    """
    try:
        from cryptvault.visualization.chart_generator import ChartGenerator
        from cryptvault.patterns.scanner import PatternScanner
        from cryptvault.ml.simple_predictor import SimplePredictor
        from cryptvault.data.fetchers import DataFetcher
        import pandas as pd
        
        # Fetch data
        print(format_info(f"Fetching {ticker} data for chart..."))
        fetcher = DataFetcher()
        data = fetcher.fetch(ticker, days=days, interval=interval)
        
        if not data or len(data) == 0:
            print(format_warning("Could not generate chart: no data available"))
            return
        
        # Convert to DataFrame
        df = pd.DataFrame({
            'Date': [point.timestamp for point in data],
            'Open': [point.open for point in data],
            'High': [point.high for point in data],
            'Low': [point.low for point in data],
            'Close': [point.close for point in data],
            'Volume': [point.volume for point in data]
        })
        
        # Scan for patterns
        print(format_info("Scanning for patterns..."))
        scanner = PatternScanner(window=5)
        patterns = scanner.scan(df)
        pattern_list = scanner.to_dict_list()
        
        if patterns:
            print(format_success(f"Found {len(patterns)} patterns"))
            # Show diverse patterns (not all the same type)
            diverse = []
            seen_types = set()
            
            for p in patterns:
                ptype = p.pattern_type
                # Add if new type or if we have less than 3 patterns
                if ptype not in seen_types or len(diverse) < 3:
                    diverse.append(p)
                    seen_types.add(ptype)
                if len(diverse) >= 5:
                    break
            
            for i, p in enumerate(diverse, 1):
                print(format_info(f"  {i}. {p.pattern_type} ({p.confidence:.0f}%) - {p.direction}"))
        
        # Generate prediction
        predictor = SimplePredictor()
        prediction = predictor.predict(df, pattern_list)
        prediction_dict = {
            'direction': prediction.direction,
            'confidence': prediction.confidence
        }
        
        # Generate chart
        chart_gen = ChartGenerator()
        
        if save_path:
            print(format_info(f"Saving chart to {save_path}..."))
            chart_gen.generate(
                df, pattern_list, 
                symbol=f"{ticker}-USD",
                prediction=prediction_dict,
                save_path=save_path
            )
            print(format_success(f"Chart saved to: {save_path}"))
        else:
            print(format_info("Generating interactive chart..."))
            chart_gen.generate(
                df, pattern_list,
                symbol=f"{ticker}-USD", 
                prediction=prediction_dict,
                save_path=None  # Display interactively
            )
            
    except ImportError as e:
        print(format_warning(f"Chart generation requires additional packages: {e}"))
        print(format_info("Install with: pip install matplotlib pandas numpy"))
    except Exception as e:
        logger.exception("Error generating chart")
        print(format_error(f"Chart generation failed: {e}"))
        if verbose:
            import traceback
            traceback.print_exc()
