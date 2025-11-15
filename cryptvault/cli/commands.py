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
        cache_stats = predictor.prediction_cache.get_cache_stats()
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
    Generate chart with pattern overlays.

    Args:
        ticker: Ticker symbol
        days: Number of days
        interval: Data interval
        save_path: Path to save chart (if provided)
        verbose: Enable verbose output
    """
    try:
        from cryptvault.visualization.desktop_charts import CryptVaultDesktopCharts
        from cryptvault.core.analyzer import PatternAnalyzer
        from cryptvault.config.manager import ConfigManager

        if save_path:
            print(format_info(f"Generating chart and saving to {save_path}..."))
            # For saving to file, use candlestick chart generator
            from cryptvault.visualization.candlestick_charts import CandlestickChartGenerator
            config = ConfigManager()
            analyzer = PatternAnalyzer(config)
            result = analyzer.analyze_ticker(ticker, days=days, interval=interval)
            
            if result.success:
                from cryptvault.data.fetchers import DataFetcher
                fetcher = DataFetcher()
                data = fetcher.fetch(ticker, days=days, interval=interval)
                
                if data and len(data) > 0:
                    chart_gen = CandlestickChartGenerator()
                    patterns_dict = []
                    for pattern in result.patterns:
                        if isinstance(pattern, dict):
                            patterns_dict.append(pattern)
                        else:
                            patterns_dict.append({
                                'type': getattr(pattern, 'pattern_type', 'Unknown'),
                                'confidence': f"{getattr(pattern, 'confidence', 0):.1%}",
                                'category': str(getattr(pattern, 'category', 'Unknown'))
                            })
                    
                    chart_output = chart_gen.generate_candlestick_chart(
                        data, ticker, patterns=patterns_dict
                    )
                    
                    with open(save_path, 'w', encoding='utf-8') as f:
                        f.write(chart_output)
                    print(format_success(f"Chart saved to: {save_path}"))
                else:
                    print(format_warning("Could not generate chart: no data available"))
            else:
                print(format_warning("Could not generate chart: analysis failed"))
        else:
            # For interactive display, use matplotlib directly
            print(format_info("Generating interactive chart with pattern overlays..."))
            print(format_info("Chart window will open - use toolbar to zoom/pan"))
            
            try:
                import matplotlib.pyplot as plt
                import matplotlib.dates as mdates
                from datetime import datetime
                import numpy as np
                
                # Set dark mode style
                plt.style.use('dark_background')
                fig = plt.figure(figsize=(12, 8), facecolor='#1e1e1e')
                
                # Get data for chart
                from cryptvault.data.fetchers import DataFetcher
                fetcher = DataFetcher()
                data = fetcher.fetch(ticker, days=days, interval=interval)
                
                if data and len(data) > 0:
                    # Extract data
                    dates = [point.timestamp for point in data]
                    opens = [point.open for point in data]
                    highs = [point.high for point in data]
                    lows = [point.low for point in data]
                    closes = [point.close for point in data]
                    
                    print(format_info(f"Chart data: {len(data)} points from {dates[0].strftime('%Y-%m-%d')} to {dates[-1].strftime('%Y-%m-%d')}"))
                    
                    # Create subplots
                    ax1 = plt.subplot2grid((4, 1), (0, 0), rowspan=3)
                    ax2 = plt.subplot2grid((4, 1), (3, 0))
                    
                    # Plot candlesticks properly
                    for i in range(len(dates)):
                        color = '#00ff88' if closes[i] >= opens[i] else '#ff4444'
                        # High-low line
                        ax1.plot([i, i], [lows[i], highs[i]], color='white', linewidth=1, alpha=0.8)
                        # Open-close bar
                        ax1.bar(i, abs(closes[i] - opens[i]), 
                               bottom=min(opens[i], closes[i]), 
                               color=color, alpha=0.8, width=0.6)
                    
                    # Calculate and plot moving averages using pandas for reliability
                    try:
                        import pandas as pd
                        closes_series = pd.Series(closes)
                        
                        # MA20
                        if len(closes) >= 20:
                            ma20 = closes_series.rolling(window=20, min_periods=1).mean()
                            ax1.plot(range(len(ma20)), ma20, color='#ffa500', linewidth=2, alpha=0.7, label='MA20')
                            print(format_info("MA20 plotted successfully"))
                        
                        # MA50 - Always plot if we have any data, even if less than 50 points
                        if len(closes) >= 1:
                            if len(closes) >= 50:
                                ma50 = closes_series.rolling(window=50, min_periods=1).mean()
                            else:
                                # For less than 50 points, use available data
                                ma50 = closes_series.rolling(window=len(closes), min_periods=1).mean()
                            ax1.plot(range(len(ma50)), ma50, color='#00bfff', linewidth=2, alpha=0.7, label='MA50')
                            print(format_info(f"MA50 plotted successfully ({len(closes)} points)"))
                            
                    except ImportError:
                        # Fallback to manual calculation
                        print(format_warning("Pandas not available, using manual MA calculation"))
                        
                        # MA20
                        if len(closes) >= 20:
                            ma20 = []
                            for i in range(len(closes)):
                                if i >= 19:
                                    ma20.append(np.mean(closes[i-19:i+1]))
                                else:
                                    ma20.append(np.mean(closes[:i+1]) if i >= 0 else closes[0])
                            ax1.plot(range(len(ma20)), ma20, color='#ffa500', linewidth=2, alpha=0.7, label='MA20')
                        
                        # MA50
                        if len(closes) >= 1:
                            ma50 = []
                            window = min(50, len(closes))
                            for i in range(len(closes)):
                                if i >= window - 1:
                                    ma50.append(np.mean(closes[i-window+1:i+1]))
                                else:
                                    ma50.append(np.mean(closes[:i+1]) if i >= 0 else closes[0])
                            ax1.plot(range(len(ma50)), ma50, color='#00bfff', linewidth=2, alpha=0.7, label='MA50')
                    
                    # Plot volume
                    volumes = [point.volume for point in data]
                    max_volume = max(volumes) if volumes else 1
                    colors = ['#00ff88' if c >= o else '#ff4444' for c, o in zip(closes, opens)]
                    ax2.bar(range(len(volumes)), volumes, color=colors, alpha=0.6)
                    
                    # Formatting
                    ax1.set_title(f'{ticker} Chart - {interval}', fontsize=16, fontweight='bold', color='white')
                    ax1.set_ylabel('Price ($)', fontsize=12, color='white')
                    ax1.grid(True, alpha=0.2, color='gray')
                    ax1.set_facecolor('#2a2a2a')
                    
                    ax2.set_ylabel('Volume', fontsize=12, color='white')
                    ax2.set_xlabel('Time', fontsize=12, color='white')
                    ax2.grid(True, alpha=0.2, color='gray')
                    ax2.set_facecolor('#2a2a2a')
                    
                    # Format x-axis
                    ax1.set_xlim(-1, len(dates))
                    ax2.set_xlim(-1, len(dates))
                    
                    # Set x-axis labels
                    step = max(1, len(dates) // 10)
                    x_ticks = list(range(0, len(dates), step))
                    x_labels = [dates[i].strftime('%m-%d') for i in x_ticks]
                    ax1.set_xticks(x_ticks)
                    ax1.set_xticklabels(x_labels, rotation=45)
                    ax2.set_xticks(x_ticks)
                    ax2.set_xticklabels(x_labels, rotation=45)
                    
                    # Add pattern annotations if available
                    config = ConfigManager()
                    analyzer = PatternAnalyzer(config)
                    result = analyzer.analyze_ticker(ticker, days=days, interval=interval)
                    
                    if result.success and result.patterns:
                        print(format_info(f"Plotting {len(result.patterns)} detected patterns..."))
                        for idx, pattern in enumerate(result.patterns):
                            # Debug: print pattern attributes
                            print(format_info(f"Pattern {idx+1} type: {type(pattern)}"))
                            if hasattr(pattern, '__dict__'):
                                print(format_info(f"  Attributes: {list(pattern.__dict__.keys())}"))
                                for key, value in pattern.__dict__.items():
                                    print(format_info(f"    {key}: {value}"))
                            
                            # Try different attribute names
                            pattern_type = None
                            confidence = 0
                            start_time = None
                            end_time = None
                            
                            # Try various attribute names
                            for attr in ['pattern_type', 'type', 'name', 'pattern_name']:
                                if hasattr(pattern, attr):
                                    pattern_type = getattr(pattern, attr)
                                    break
                            
                            for attr in ['confidence', 'confidence_score', 'score']:
                                if hasattr(pattern, attr):
                                    confidence = getattr(pattern, attr)
                                    break
                            
                            for attr in ['start_time', 'start', 'begin_time', 'begin']:
                                if hasattr(pattern, attr):
                                    start_time = getattr(pattern, attr)
                                    break
                            
                            for attr in ['end_time', 'end', 'finish_time', 'finish']:
                                if hasattr(pattern, attr):
                                    end_time = getattr(pattern, attr)
                                    break
                            
                            # If pattern is a dict, try dict keys
                            if isinstance(pattern, dict):
                                pattern_type = pattern.get('pattern_type', pattern.get('type', 'Unknown'))
                                confidence = pattern.get('confidence', pattern.get('confidence_score', 0))
                                start_time = pattern.get('start_time', pattern.get('start', None))
                                end_time = pattern.get('end_time', pattern.get('end', None))
                            
                            print(format_info(f"Pattern {idx+1}: {pattern_type} - Confidence: {confidence}"))
                            print(format_info(f"  Start: {start_time}, End: {end_time}"))
                            
                            # Find the closest indices for pattern start and end
                            start_idx = None
                            end_idx = None
                            
                            if start_time and end_time:
                                # Convert to datetime if they are strings and normalize timezone
                                if isinstance(start_time, str):
                                    try:
                                        from datetime import datetime
                                        start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                                    except:
                                        pass
                                
                                if isinstance(end_time, str):
                                    try:
                                        from datetime import datetime
                                        end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                                    except:
                                        pass
                                
                                # Make pattern datetimes timezone-naive to match chart datetimes
                                if hasattr(start_time, 'tzinfo') and start_time.tzinfo is not None:
                                    start_time = start_time.replace(tzinfo=None)
                                if hasattr(end_time, 'tzinfo') and end_time.tzinfo is not None:
                                    end_time = end_time.replace(tzinfo=None)
                                
                                # Also make chart datetimes timezone-naive
                                normalized_dates = []
                                for date in dates:
                                    if hasattr(date, 'tzinfo') and date.tzinfo is not None:
                                        normalized_dates.append(date.replace(tzinfo=None))
                                    else:
                                        normalized_dates.append(date)
                                
                                # Find start index
                                min_start_diff = float('inf')
                                for i, date in enumerate(normalized_dates):
                                    diff = abs((date - start_time).total_seconds())
                                    if diff < min_start_diff:
                                        min_start_diff = diff
                                        start_idx = i
                                
                                # Find end index
                                min_end_diff = float('inf')
                                for i, date in enumerate(normalized_dates):
                                    diff = abs((date - end_time).total_seconds())
                                    if diff < min_end_diff:
                                        min_end_diff = diff
                                        end_idx = i
                                
                                print(format_info(f"  Found indices: start={start_idx}, end={end_idx} (total points: {len(dates)})"))
                                
                                # Plot pattern if we found valid indices
                                if start_idx is not None and end_idx is not None and start_idx < len(dates) and end_idx < len(dates):
                                    # Ensure end_idx >= start_idx
                                    if end_idx < start_idx:
                                        start_idx, end_idx = end_idx, start_idx
                                    
                                    # Add colored background for pattern region
                                    pattern_color = '#ffff00' if 'Bullish' in str(pattern_type) else '#00ffff' if 'Bearish' in str(pattern_type) else '#ff00ff'
                                    confidence_str = f"{confidence:.1f}%" if isinstance(confidence, (int, float)) else f"{confidence}%"
                                    ax1.axvspan(start_idx, end_idx, 
                                              alpha=0.2, color=pattern_color, 
                                              label=f"{pattern_type} ({confidence_str})")
                                    
                                    # Draw pattern-specific shapes
                                    if 'Wedge' in str(pattern_type):
                                        # Draw wedge pattern lines
                                        pattern_highs = [highs[i] for i in range(start_idx, min(end_idx+1, len(highs)))]
                                        pattern_lows = [lows[i] for i in range(start_idx, min(end_idx+1, len(lows)))]
                                        pattern_x = list(range(start_idx, min(end_idx+1, len(highs))))
                                        
                                        if len(pattern_highs) >= 3 and len(pattern_lows) >= 3:
                                            # Falling wedge - upper line slopes down, lower line slopes down more steeply
                                            if 'Falling' in str(pattern_type):
                                                # Upper trendline (resistance)
                                                z_high = np.polyfit(pattern_x[:len(pattern_x)//2], pattern_highs[:len(pattern_highs)//2], 1)
                                                p_high = np.poly1d(z_high)
                                                ax1.plot(pattern_x[:len(pattern_x)//2], p_high(pattern_x[:len(pattern_x)//2]), 
                                                       color=pattern_color, linewidth=2, linestyle='--', alpha=0.8)
                                                
                                                # Lower trendline (support)
                                                z_low = np.polyfit(pattern_x[len(pattern_x)//2:], pattern_lows[len(pattern_lows)//2:], 1)
                                                p_low = np.poly1d(z_low)
                                                ax1.plot(pattern_x[len(pattern_x)//2:], p_low(pattern_x[len(pattern_x)//2:]), 
                                                       color=pattern_color, linewidth=2, linestyle='--', alpha=0.8)
                                            
                                            # Rising wedge - lower line slopes up, upper line slopes up more steeply
                                            elif 'Rising' in str(pattern_type):
                                                # Lower trendline (support)
                                                z_low = np.polyfit(pattern_x[:len(pattern_x)//2], pattern_lows[:len(pattern_lows)//2], 1)
                                                p_low = np.poly1d(z_low)
                                                ax1.plot(pattern_x[:len(pattern_x)//2], p_low(pattern_x[:len(pattern_x)//2]), 
                                                       color=pattern_color, linewidth=2, linestyle='--', alpha=0.8)
                                                
                                                # Upper trendline (resistance)
                                                z_high = np.polyfit(pattern_x[len(pattern_x)//2:], pattern_highs[len(pattern_highs)//2:], 1)
                                                p_high = np.poly1d(z_high)
                                                ax1.plot(pattern_x[len(pattern_x)//2:], p_high(pattern_x[len(pattern_x)//2:]), 
                                                       color=pattern_color, linewidth=2, linestyle='--', alpha=0.8)
                                    
                                    elif 'Triangle' in str(pattern_type):
                                        # Draw triangle pattern
                                        pattern_highs = [highs[i] for i in range(start_idx, min(end_idx+1, len(highs)))]
                                        pattern_lows = [lows[i] for i in range(start_idx, min(end_idx+1, len(lows)))]
                                        pattern_x = list(range(start_idx, min(end_idx+1, len(highs))))
                                        
                                        if len(pattern_highs) >= 3:
                                            # Ascending triangle - horizontal top, rising bottom
                                            if 'Ascending' in str(pattern_type):
                                                # Horizontal resistance line
                                                max_high = max(pattern_highs[:len(pattern_highs)//2])
                                                ax1.plot([pattern_x[0], pattern_x[len(pattern_x)//2]], [max_high, max_high], 
                                                       color=pattern_color, linewidth=2, linestyle='--', alpha=0.8)
                                                
                                                # Rising support line
                                                z_low = np.polyfit(pattern_x[:len(pattern_x)//2], pattern_lows[:len(pattern_lows)//2], 1)
                                                p_low = np.poly1d(z_low)
                                                ax1.plot(pattern_x[:len(pattern_x)//2], p_low(pattern_x[:len(pattern_x)//2]), 
                                                       color=pattern_color, linewidth=2, linestyle='--', alpha=0.8)
                                    
                                    elif 'Head' in str(pattern_type) and 'Shoulders' in str(pattern_type):
                                        # Draw head and shoulders pattern
                                        pattern_highs = [highs[i] for i in range(start_idx, min(end_idx+1, len(highs)))]
                                        pattern_lows = [lows[i] for i in range(start_idx, min(end_idx+1, len(lows)))]
                                        pattern_x = list(range(start_idx, min(end_idx+1, len(highs))))
                                        
                                        if len(pattern_highs) >= 5:
                                            # Find peaks (head and shoulders)
                                            from scipy.signal import find_peaks
                                            peaks, _ = find_peaks(pattern_highs, distance=2)
                                            
                                            if len(peaks) >= 3:
                                                # Mark the head and shoulders
                                                for i, peak_idx in enumerate(peaks[:3]):
                                                    actual_idx = start_idx + peak_idx
                                                    ax1.plot(actual_idx, pattern_highs[peak_idx], 'o', 
                                                           color=pattern_color, markersize=8, alpha=0.8)
                                                    
                                                    # Label: L-S-H-S-R (Left Shoulder, Head, Right Shoulder)
                                                    labels = ['LS', 'H', 'RS']
                                                    if i < len(labels):
                                                        ax1.text(actual_idx, pattern_highs[peak_idx] * 1.02, labels[i], 
                                                               color=pattern_color, fontsize=8, ha='center', fontweight='bold')
                                    
                                    # Add pattern label at the bottom of the chart
                                    mid_idx = (start_idx + end_idx) // 2
                                    price_at_pattern = np.mean([lows[mid_idx], highs[mid_idx]])
                                    confidence_str = f"{confidence:.1f}%" if isinstance(confidence, (int, float)) else f"{confidence}%"
                                    ax1.text(mid_idx, price_at_pattern * 0.95, 
                                           f"{pattern_type}\n{confidence_str}", 
                                           color='white', fontsize=8, ha='center',
                                           bbox=dict(boxstyle='round,pad=0.3', facecolor=pattern_color, alpha=0.7))
                                    
                                    print(format_info(f"  ✓ Plotted {pattern_type} from {dates[start_idx].strftime('%Y-%m-%d')} to {dates[end_idx].strftime('%Y-%m-%d')}"))
                                else:
                                    print(format_warning(f"  ✗ Could not plot {pattern_type} - invalid indices"))
                            else:
                                print(format_warning(f"  ✗ Pattern {pattern_type} missing start/end time"))
                    else:
                        print(format_warning("No patterns detected or pattern analysis failed"))
                        
                        # Try to plot a simple pattern manually for testing
                        if len(dates) >= 10:
                            # Create a fake pattern region for testing
                            start_idx = len(dates) // 3
                            end_idx = 2 * len(dates) // 3
                            ax1.axvspan(start_idx, end_idx, 
                                      alpha=0.2, color='yellow', 
                                      label='Test Pattern Region')
                            ax1.text((start_idx + end_idx) // 2, np.mean(lows[start_idx:end_idx]), 
                                   'Test Pattern', 
                                   color='white', fontsize=8, ha='center',
                                   bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
                            print(format_info("Added test pattern region for visualization"))
                    
                    # Update legend
                    if result.success and result.patterns:
                        handles, labels = ax1.get_legend_handles_labels()
                        if handles:
                            ax1.legend(handles[:5], labels[:5], loc='upper left', facecolor='#2a2a2a', edgecolor='gray', fontsize=9)
                    
                    plt.tight_layout()
                    plt.show()
                    
                else:
                    print(format_warning("Could not generate chart: no data available"))
                    
            except ImportError:
                print(format_warning("Matplotlib not available for interactive charts"))
                # Fallback to terminal chart
                from cryptvault.visualization.candlestick_charts import CandlestickChartGenerator
                config = ConfigManager()
                analyzer = PatternAnalyzer(config)
                result = analyzer.analyze_ticker(ticker, days=days, interval=interval)
                
                if result.success:
                    from cryptvault.data.fetchers import DataFetcher
                    fetcher = DataFetcher()
                    data = fetcher.fetch(ticker, days=days, interval=interval)
                    
                    if data and len(data) > 0:
                        chart_gen = CandlestickChartGenerator()
                        patterns_dict = []
                        for pattern in result.patterns:
                            if isinstance(pattern, dict):
                                patterns_dict.append(pattern)
                            else:
                                patterns_dict.append({
                                    'type': getattr(pattern, 'pattern_type', 'Unknown'),
                                    'confidence': f"{getattr(pattern, 'confidence', 0):.1%}",
                                    'category': str(getattr(pattern, 'category', 'Unknown'))
                                })
                        
                        chart_output = chart_gen.generate_candlestick_chart(
                            data, ticker, patterns=patterns_dict
                        )
                        print(chart_output)
                    else:
                        print(format_warning("Could not generate chart: no data available"))
                else:
                    print(format_warning("Could not generate chart: analysis failed"))
            except Exception as e:
                print(format_warning(f"Could not generate interactive chart: {e}"))
                # Fallback to terminal chart
                from cryptvault.visualization.candlestick_charts import CandlestickChartGenerator
                config = ConfigManager()
                analyzer = PatternAnalyzer(config)
                result = analyzer.analyze_ticker(ticker, days=days, interval=interval)
                
                if result.success:
                    from cryptvault.data.fetchers import DataFetcher
                    fetcher = DataFetcher()
                    data = fetcher.fetch(ticker, days=days, interval=interval)
                    
                    if data and len(data) > 0:
                        chart_gen = CandlestickChartGenerator()
                        patterns_dict = []
                        for pattern in result.patterns:
                            if isinstance(pattern, dict):
                                patterns_dict.append(pattern)
                            else:
                                patterns_dict.append({
                                    'type': getattr(pattern, 'pattern_type', 'Unknown'),
                                    'confidence': f"{getattr(pattern, 'confidence', 0):.1%}",
                                    'category': str(getattr(pattern, 'category', 'Unknown'))
                                })
                        
                        chart_output = chart_gen.generate_candlestick_chart(
                            data, ticker, patterns=patterns_dict
                        )
                        print(chart_output)
                    else:
                        print(format_warning("Could not generate chart: no data available"))
                else:
                    print(format_warning("Could not generate chart: analysis failed"))

    except Exception as e:
        logger.exception("Error generating chart")
        print(format_error(f"Chart generation failed: {e}"))
        if verbose:
            import traceback
            traceback.print_exc()
