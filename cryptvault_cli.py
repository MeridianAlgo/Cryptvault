#!/usr/bin/env python3
"""
CryptVault - Advanced AI-Powered Cryptocurrency Analysis Platform

A sophisticated cryptocurrency analysis tool that combines:
- Advanced pattern recognition
- Machine learning predictions (LSTM, Ensemble models)
- Real-time data fetching
- Technical analysis
- Risk assessment

Made by the MeridianAlgo Algorithmic Research Team (Quantum Meridian)

Usage:
    python cryptvault_cli.py [TICKER] [DAYS] [INTERVAL]

Examples:
    python cryptvault_cli.py BTC 30 1d     # Bitcoin, 30 days, daily
    python cryptvault_cli.py ETH 14 4h     # Ethereum, 14 days, 4-hour
    python cryptvault_cli.py ADA 7 1h      # Cardano, 7 days, hourly
    
    python cryptvault_cli.py --demo        # Quick demo
    python cryptvault_cli.py --help        # Show help
"""

import sys
import argparse
import logging
from datetime import datetime
from cryptvault.analyzer import PatternAnalyzer

def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.INFO if verbose else logging.ERROR  # Changed to ERROR to suppress warnings
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('cryptvault.log')
        ]
    )



def analyze_cryptocurrency(ticker: str, days: int, interval: str, verbose: bool = False):
    """Analyze cryptocurrency with CryptVault."""
    
    print(f"Analyzing {ticker.upper()} ({days}d, {interval})")
    
    # Initialize analyzer
    analyzer = PatternAnalyzer()
    
    # Perform analysis
    results = analyzer.analyze_ticker(ticker, days=days, interval=interval)
    
    if not results['success']:
        print(f"[ERROR] Analysis failed: {results['error']}")
        if 'suggestions' in results:
            print("\n[SUGGESTIONS]:")
            for suggestion in results['suggestions']:
                print(f"  - {suggestion}")
        return False
    
    # Display results
    print(f"Completed in {results['analysis_time_seconds']:.2f}s | {results['patterns_found']} patterns")
    
    # Market data
    if 'ticker_info' in results:
        ticker_info = results['ticker_info']
        current_price = ticker_info.get('current_price')
        if current_price:
            print(f"Price: ${current_price:,.2f}")
        
        if 'price_change' in ticker_info:
            change = ticker_info['price_change']
            print(f"Change: {change['percentage']:+.2%}")
    
    # ML Predictions
    if results.get('ml_predictions'):
        ml_pred = results['ml_predictions']
        
        if 'trend_forecast' in ml_pred:
            trend = ml_pred['trend_forecast']
            print(f"Trend: {trend['trend_7d']} ({trend['trend_strength']})")
    
    # Top patterns with exact names and detailed info
    if results['patterns_found'] > 0:
        print("Detected Patterns:")
        print("─" * 60)
        for i, pattern in enumerate(results['patterns'][:5], 1):
            pattern_type = pattern.get('type', 'Unknown Pattern')
            confidence = pattern.get('confidence', '0%')
            category = pattern.get('category', 'Unknown')
            
            # Pattern symbols for better visualization
            pattern_symbols = {
                'Double Bottom': '⩗', 'Double Top': '⩘',
                'Triple Bottom': '⫸', 'Triple Top': '⫷',
                'Head and Shoulders': '⩙', 'Inverse Head and Shoulders': '⩚',
                'Ascending Triangle': '△', 'Descending Triangle': '▽',
                'Expanding Triangle': '◇', 'Symmetrical Triangle': '◊',
                'Bull Flag': '⚑', 'Bear Flag': '⚐',
                'Bullish Divergence': '↗', 'Bearish Divergence': '↘',
                'Hidden Bullish Divergence': '⤴', 'Hidden Bearish Divergence': '⤵',
                'Rectangle': '▭', 'Diamond': '◈',
                'Gartley': 'G', 'Butterfly': 'B', 'ABCD': 'A',
                'Hammer': 'H', 'Shooting Star': 'S', 'Doji': '+'
            }
            
            symbol = pattern_symbols.get(pattern_type, '⭐')
            
            # Confidence bar
            conf_value = float(confidence.rstrip('%'))
            conf_bars = int(conf_value / 10)
            conf_bar = '█' * conf_bars + '░' * (10 - conf_bars)
            
            print(f"  {i}. {symbol} {pattern_type:<25} [{category}] [{conf_bar}] {confidence}")
            
            # Add key levels if available
            if 'key_levels' in pattern and pattern['key_levels']:
                key_info = []
                if 'support_level' in pattern['key_levels']:
                    key_info.append(f"Support: ${pattern['key_levels']['support_level']:.2f}")
                if 'resistance_level' in pattern['key_levels']:
                    key_info.append(f"Resistance: ${pattern['key_levels']['resistance_level']:.2f}")
                if 'target_price' in pattern['key_levels']:
                    key_info.append(f"Target: ${pattern['key_levels']['target_price']:.2f}")
                
                if key_info:
                    print(f"      Key Levels: {' | '.join(key_info)}")
        
        if results['patterns_found'] > 5:
            print(f"  ... and {results['patterns_found'] - 5} more patterns")
    
    # Show terminal chart in verbose mode (desktop charts can hang)
    if verbose and 'chart' in results and results['chart']:
        print("\n[CHART] Terminal Chart:")
        print(results['chart'])
    
    return True

def run_demo():
    """Run demo."""
    analyzer = PatternAnalyzer()
    
    print("CryptVault v3.2.0-Public Demo")
    print("=" * 60)
    
    # Test functionality
    search_results = analyzer.search_tickers("bitcoin", limit=3)
    if search_results:
        print("\nSearch Results for 'bitcoin':")
        for result in search_results:
            print(f"  {result['symbol']}: {result['name']}")
    
    # Show comprehensive list of supported assets
    supported = analyzer.get_supported_tickers()
    print(f"\nTotal Supported Assets: {len(supported)}")
    print(f"\nTop Cryptocurrencies (20):")
    crypto_list = [s for s in supported if s in ['BTC', 'ETH', 'USDT', 'BNB', 'SOL', 'XRP', 'USDC', 'ADA', 'AVAX', 'DOGE', 'TRX', 'DOT', 'MATIC', 'LINK', 'TON', 'SHIB', 'LTC', 'BCH', 'UNI', 'ATOM']]
    print(f"  {', '.join(crypto_list)}")
    
    print(f"\nPopular Stocks (10):")
    stock_list = [s for s in supported if s in ['AAPL', 'TSLA', 'GOOGL', 'MSFT', 'NVDA', 'AMZN', 'META', 'NFLX', 'AMD', 'INTC']]
    print(f"  {', '.join(stock_list)}")
    
    print(f"\nAll {len(supported)} supported assets:")
    print(f"  {', '.join(supported)}")
    
    print("\nCurrent Prices:")
    btc_price = analyzer.get_current_price("BTC")
    if btc_price:
        print(f"  BTC: ${btc_price:,.2f}")
    else:
        print("  BTC: Price unavailable")

def show_api_status():
    """Show data source status."""
    analyzer = PatternAnalyzer()
    sources = analyzer.data_fetcher.get_available_sources()
    
    print("Data Sources Status:")
    for source_name, available in sources.items():
        status_icon = "[OK]" if available else "[FAIL]"
        print(f"  {status_icon} {source_name.title()}: {'Available' if available else 'Not installed'}")
    
    # Show installation suggestions for missing packages
    missing = [name for name, available in sources.items() if not available]
    if missing:
        print(f"\nNote: Some packages may have compatibility issues:")
        for package in missing:
            if package == 'yfinance':
                print(f"  pip install yfinance")
            elif package == 'ccxt':
                print(f"  pip install ccxt")
            elif package == 'cryptocompare':
                print(f"  pip install cryptocompare")
            elif package == 'fastquant':
                print(f"  fastquant: May have pandas compatibility issues")

def analyze_portfolio(holdings_str: list):
    """Analyze cryptocurrency portfolio."""
    try:
        from cryptvault.portfolio.analyzer import PortfolioAnalyzer
        
        # Parse holdings
        holdings = {}
        for holding in holdings_str:
            if ':' in holding:
                symbol, amount = holding.split(':')
                holdings[symbol.upper()] = float(amount)
        
        if not holdings:
            print("Invalid portfolio format. Use: BTC:0.5 ETH:10")
            return
        
        print(f"Portfolio: {holdings}")
        
        portfolio_analyzer = PortfolioAnalyzer()
        results = portfolio_analyzer.analyze_portfolio(holdings)
        
        if results['success']:
            # Display results
            portfolio_value = results['portfolio_value']
            print(f"Total Value: ${portfolio_value['total_usd']:,.2f}")
            
            print("Allocation:")
            for symbol, percentage in results['asset_allocation'].items():
                value = portfolio_value['asset_values'].get(symbol, 0)
                print(f"  {symbol}: {percentage:.1f}% (${value:,.2f})")
            
            print(f"Diversification Score: {results['diversification_score']:.1f}/100")
            
            if results['rebalancing_suggestions']:
                print("Suggestions:")
                for suggestion in results['rebalancing_suggestions'][:3]:
                    print(f"  {suggestion}")
        else:
            print(f"Portfolio analysis failed: {results['error']}")
            
    except ImportError:
        print("Portfolio analysis requires pandas: pip install pandas")
    except Exception as e:
        print(f"Portfolio analysis error: {e}")

def compare_assets(symbols: list):
    """Compare multiple cryptocurrency assets."""
    try:
        from cryptvault.portfolio.analyzer import PortfolioAnalyzer
        
        portfolio_analyzer = PortfolioAnalyzer()
        results = portfolio_analyzer.compare_assets([s.upper() for s in symbols])
        
        if results['success']:
            print("Asset Comparison (30 days):")
            for symbol, data in results['comparison_data'].items():
                print(f"{symbol}: ${data['current_price']:,.2f} | {data['period_return']:+.1f}% | Vol: {data['volatility']:.1f}%")
            
            if results['best_performer']:
                best = results['best_performer']
                print(f"Best Performer: {best[0]} ({best[1]['period_return']:+.1f}%)")
        else:
            print(f"Comparison failed: {results['error']}")
            
    except ImportError:
        print("Asset comparison requires pandas: pip install pandas")
    except Exception as e:
        print(f"Comparison error: {e}")

def start_live_analysis(symbol: str):
    """Start live analysis."""
    try:
        from cryptvault.data.websocket_stream import LiveAnalyzer
        
        live_analyzer = LiveAnalyzer()
        live_analyzer.start_live_analysis(symbol.upper())
        
    except ImportError:
        print("Live analysis requires websockets: pip install websockets")
    except Exception as e:
        print(f"Live analysis error: {e}")

def open_desktop_charts():
    """Open desktop charts in a new window."""
    try:
        from cryptvault.visualization.desktop_charts import CryptVaultDesktopCharts
        
        print("[LAUNCH] Opening CryptVault Desktop Charts...")
        print("[INFO] A new window will open with interactive charts")
        print("[TIP] Use the interface to analyze different cryptocurrencies")
        
        app = CryptVaultDesktopCharts()
        app.run()
        
    except ImportError as e:
        print("Desktop charts require additional packages:")
        print("  pip install tkinter matplotlib numpy pandas")
        print(f"Missing: {e}")
    except Exception as e:
        print(f"Desktop charts error: {e}")
        import traceback
        traceback.print_exc()

def show_prediction_accuracy():
    """Show ML prediction accuracy report."""
    try:
        from cryptvault.ml.prediction.predictor import MLPredictor
        
        print("[ML] CryptVault ML Prediction Accuracy Report")
        print("=" * 60)
        
        predictor = MLPredictor()
        
        # Get accuracy report for last 30 days
        report = predictor.get_prediction_accuracy_report(30)
        
        if 'error' in report:
            print(f"[ERROR] Error generating report: {report['error']}")
            return
        
        if report.get('total_predictions', 0) == 0:
            print("[INFO] No verified predictions found in the last 30 days")
            print("[TIP] Make some predictions first, then check back in a week!")
            return
        
        # Overall statistics
        print(f"[ACCURACY] Overall Accuracy: {report['overall_accuracy']:.1%}")
        print(f"[STATS] Total Predictions: {report['total_predictions']}")
        print(f"[STATS] Accurate Predictions: {report['accurate_predictions']}")
        print(f"[STATS] Average Error: {report['average_error']:.1%}")
        print()
        
        # Accuracy by symbol
        if report.get('accuracy_by_symbol'):
            print("[ACCURACY] Accuracy by Symbol:")
            for symbol, data in report['accuracy_by_symbol'].items():
                accuracy = data['accuracy_rate']
                total = data['total']
                confidence = data['avg_confidence']
                print(f"  {symbol}: {accuracy:.1%} ({total} predictions, avg confidence: {confidence:.1%})")
            print()
        
        # Recent predictions
        if report.get('recent_predictions'):
            print("[RECENT] Recent Predictions:")
            for pred in report['recent_predictions']:
                symbol = pred['symbol']
                predicted = pred['predicted']
                actual = pred['actual']
                accuracy = pred['accuracy']
                date = pred['date']
                
                status = "[OK]" if accuracy >= 0.9 else "[FAIL]"
                print(f"  {status} {symbol} on {date}: Predicted ${predicted:.2f}, Actual ${actual:.2f} (Score: {accuracy:.1%})")
        
        # Cache statistics
        cache_stats = predictor.prediction_cache.get_cache_stats()
        print()
        print("[CACHE] Cache Statistics:")
        print(f"  Total Predictions: {cache_stats['total_predictions']}")
        print(f"  Verified: {cache_stats['verified_predictions']}")
        print(f"  Pending: {cache_stats['pending_predictions']}")
        print(f"  Recent (7 days): {cache_stats['recent_predictions_7d']}")
        print(f"  Cache Size: {cache_stats['cache_size_mb']:.2f} MB")
        
    except ImportError:
        print("[ERROR] ML prediction modules not available")
    except Exception as e:
        print(f"[ERROR] Error showing accuracy report: {e}")
        import traceback
        traceback.print_exc()

def interactive_mode():
    """Interactive CryptVault mode."""
    print("CryptVault Interactive Mode")
    print("Commands: analyze, portfolio, compare, live, desktop, status, help, exit")
    
    while True:
        try:
            command = input("\ncryptvault> ").strip().lower()
            
            if command == 'exit' or command == 'quit':
                break
            elif command == 'help':
                print("Available commands:")
                print("  analyze <SYMBOL> <DAYS> <INTERVAL> - Analyze cryptocurrency")
                print("  portfolio <SYMBOL:AMOUNT> ... - Analyze portfolio")
                print("  compare <SYMBOL> ... - Compare assets")
                print("  live <SYMBOL> - Start live analysis")
                print("  desktop - Open desktop charts window")
                print("  status - Show API status")
                print("  help - Show this help")
                print("  exit - Exit interactive mode")
            elif command == 'status':
                show_api_status()
            elif command.startswith('analyze'):
                parts = command.split()
                if len(parts) >= 2:
                    ticker = parts[1].upper()
                    days = int(parts[2]) if len(parts) > 2 else 30
                    interval = parts[3] if len(parts) > 3 else '1d'
                    analyze_cryptocurrency(ticker, days, interval)
                else:
                    print("Usage: analyze <SYMBOL> [DAYS] [INTERVAL]")
            elif command.startswith('portfolio'):
                parts = command.split()[1:]
                if parts:
                    analyze_portfolio(parts)
                else:
                    print("Usage: portfolio <SYMBOL:AMOUNT> ...")
            elif command.startswith('compare'):
                parts = command.split()[1:]
                if parts:
                    compare_assets(parts)
                else:
                    print("Usage: compare <SYMBOL> ...")
            elif command.startswith('live'):
                parts = command.split()
                if len(parts) >= 2:
                    start_live_analysis(parts[1])
                else:
                    print("Usage: live <SYMBOL>")
            elif command == 'desktop':
                open_desktop_charts()
            else:
                print("Unknown command. Type 'help' for available commands.")
                
        except KeyboardInterrupt:
            print("\nUse 'exit' to quit")
        except Exception as e:
            print(f"Error: {e}")



def main():
    """Main CryptVault CLI function."""
    parser = argparse.ArgumentParser(
        description="CryptVault - Advanced AI-Powered Cryptocurrency Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cryptvault_cli.py BTC 30 1d     # Bitcoin, 30 days, daily
  python cryptvault_cli.py ETH 14 4h     # Ethereum, 14 days, 4-hour
  python cryptvault_cli.py --desktop     # Open desktop charts window
  python cryptvault_cli.py --demo        # Quick demo
        """
    )
    
    parser.add_argument('ticker', nargs='?', default='BTC',
                       help='Cryptocurrency ticker symbol (default: BTC)')
    parser.add_argument('days', nargs='?', type=int, default=30,
                       help='Number of days of data (default: 30)')
    parser.add_argument('interval', nargs='?', default='1d',
                       help='Data interval: 1h, 4h, 1d (default: 1d)')
    
    parser.add_argument('--demo', action='store_true',
                       help='Run quick demo')

    parser.add_argument('--status', action='store_true',
                       help='Show API status')
    parser.add_argument('--portfolio', nargs='+', metavar='SYMBOL:AMOUNT',
                       help='Analyze portfolio: BTC:0.5 ETH:10 ADA:1000')
    parser.add_argument('--compare', nargs='+', metavar='SYMBOL',
                       help='Compare multiple assets: BTC ETH ADA')
    parser.add_argument('--live', metavar='SYMBOL',
                       help='Start live analysis for symbol')
    parser.add_argument('--desktop', '-d', action='store_true',
                       help='Open desktop charts in new window')
    parser.add_argument('--accuracy', action='store_true',
                       help='Show ML prediction accuracy report')
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Interactive mode')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output with detailed charts')
    parser.add_argument('--version', action='version', version='CryptVault 3.2.0-Public')
    
    args = parser.parse_args()
    
    setup_logging(args.verbose)
    
    try:
        if args.demo:
            run_demo()
        elif args.status:
            show_api_status()
        elif args.portfolio:
            analyze_portfolio(args.portfolio)
        elif args.compare:
            compare_assets(args.compare)
        elif args.live:
            start_live_analysis(args.live)
        elif args.desktop:
            open_desktop_charts()
        elif args.accuracy:
            show_prediction_accuracy()
        elif args.interactive:
            interactive_mode()
        else:
            success = analyze_cryptocurrency(
                args.ticker, 
                args.days, 
                args.interval, 
                args.verbose
            )
            if not success:
                sys.exit(1)
                
    except KeyboardInterrupt:
        print("Interrupted")
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()