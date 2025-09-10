#!/usr/bin/env python3
"""
Advanced CryptVault Terminal Charts
Minimalist, colorful, professional crypto analysis with enhanced patterns

Made with ❤️ by the MeridianAlgo Algorithmic Research Team (Quantum Meridian)
"""

import sys
import os
import numpy as np
import time
import threading
import argparse
from datetime import datetime, timedelta
from colorama import init, Fore, Back, Style

# Initialize colorama for cross-platform colors
init(autoreset=True)

# Add CryptVault to path
sys.path.append('.')

from cryptvault.analyzer import PatternAnalyzer
import logging

# Suppress INFO logs - only show warnings and errors
logging.getLogger('cryptvault').setLevel(logging.WARNING)

class AdvancedCryptoCharts:
    """Advanced minimalist terminal charts with enhanced patterns and time-based bias"""
    
    def __init__(self, verbose=False):
        self.analyzer = PatternAnalyzer()
        self.verbose = verbose
        
        # Enhanced pattern library with 50+ patterns
        self.patterns = {
            # Reversal Patterns
            'Double Bottom': {'symbol': '⩗', 'bias': 'bullish', 'strength': 0.8},
            'Double Top': {'symbol': '⩘', 'bias': 'bearish', 'strength': 0.8},
            'Triple Bottom': {'symbol': '⫸', 'bias': 'bullish', 'strength': 0.9},
            'Triple Top': {'symbol': '⫷', 'bias': 'bearish', 'strength': 0.9},
            'Head and Shoulders': {'symbol': '⩙', 'bias': 'bearish', 'strength': 0.85},
            'Inverse Head and Shoulders': {'symbol': '⩚', 'bias': 'bullish', 'strength': 0.85},
            'Cup and Handle': {'symbol': '⌒', 'bias': 'bullish', 'strength': 0.75},
            'Inverted Cup and Handle': {'symbol': '⌓', 'bias': 'bearish', 'strength': 0.75},
            'Rounding Bottom': {'symbol': '⌒', 'bias': 'bullish', 'strength': 0.7},
            'Rounding Top': {'symbol': '⌓', 'bias': 'bearish', 'strength': 0.7},
            'V-Bottom': {'symbol': 'V', 'bias': 'bullish', 'strength': 0.6},
            'Inverted V-Top': {'symbol': 'Λ', 'bias': 'bearish', 'strength': 0.6},
            
            # Triangle Patterns
            'Ascending Triangle': {'symbol': '△', 'bias': 'bullish', 'strength': 0.7},
            'Descending Triangle': {'symbol': '▽', 'bias': 'bearish', 'strength': 0.7},
            'Expanding Triangle': {'symbol': '◇', 'bias': 'neutral', 'strength': 0.5},
            'Symmetrical Triangle': {'symbol': '◊', 'bias': 'neutral', 'strength': 0.6},
            'Right Triangle': {'symbol': '⊿', 'bias': 'neutral', 'strength': 0.55},
            
            # Wedge Patterns
            'Rising Wedge': {'symbol': '⟋', 'bias': 'bearish', 'strength': 0.75},
            'Falling Wedge': {'symbol': '⟍', 'bias': 'bullish', 'strength': 0.75},
            'Rising Wedge Reversal': {'symbol': '⟋', 'bias': 'bearish', 'strength': 0.8},
            'Falling Wedge Reversal': {'symbol': '⟍', 'bias': 'bullish', 'strength': 0.8},
            
            # Channel Patterns
            'Rising Channel': {'symbol': '║', 'bias': 'bullish', 'strength': 0.6},
            'Falling Channel': {'symbol': '║', 'bias': 'bearish', 'strength': 0.6},
            'Horizontal Channel': {'symbol': '═', 'bias': 'neutral', 'strength': 0.5},
            
            # Rectangle Patterns
            'Rectangle': {'symbol': '▭', 'bias': 'neutral', 'strength': 0.5},
            'Rectangle Bullish': {'symbol': '▭', 'bias': 'bullish', 'strength': 0.7},
            'Rectangle Bearish': {'symbol': '▭', 'bias': 'bearish', 'strength': 0.7},
            
            # Flag and Pennant Patterns
            'Bull Flag': {'symbol': '⚑', 'bias': 'bullish', 'strength': 0.8},
            'Bear Flag': {'symbol': '⚐', 'bias': 'bearish', 'strength': 0.8},
            'Pennant': {'symbol': '⚐', 'bias': 'neutral', 'strength': 0.6},
            'Bull Pennant': {'symbol': '⚑', 'bias': 'bullish', 'strength': 0.75},
            'Bear Pennant': {'symbol': '⚐', 'bias': 'bearish', 'strength': 0.75},
            
            # Diamond Patterns
            'Diamond': {'symbol': '◈', 'bias': 'neutral', 'strength': 0.6},
            'Diamond Top': {'symbol': '◈', 'bias': 'bearish', 'strength': 0.75},
            'Diamond Bottom': {'symbol': '◈', 'bias': 'bullish', 'strength': 0.75},
            
            # Divergence Patterns
            'Bullish Divergence': {'symbol': '↗', 'bias': 'bullish', 'strength': 0.8},
            'Bearish Divergence': {'symbol': '↘', 'bias': 'bearish', 'strength': 0.8},
            'Hidden Bullish Divergence': {'symbol': '⤴', 'bias': 'bullish', 'strength': 0.7},
            'Hidden Bearish Divergence': {'symbol': '⤵', 'bias': 'bearish', 'strength': 0.7},
            
            # Harmonic Patterns
            'ABCD': {'symbol': 'A', 'bias': 'neutral', 'strength': 0.7},
            'AB=CD': {'symbol': '=', 'bias': 'neutral', 'strength': 0.65},
            'Gartley': {'symbol': 'G', 'bias': 'neutral', 'strength': 0.8},
            'Butterfly': {'symbol': 'B', 'bias': 'neutral', 'strength': 0.75},
            'Bat': {'symbol': 'b', 'bias': 'neutral', 'strength': 0.75},
            'Crab': {'symbol': 'C', 'bias': 'neutral', 'strength': 0.8},
            'Shark': {'symbol': 'S', 'bias': 'neutral', 'strength': 0.75},
            'Cypher': {'symbol': 'Y', 'bias': 'neutral', 'strength': 0.7},
            'Three Drives': {'symbol': '3', 'bias': 'neutral', 'strength': 0.7},
            
            # Support/Resistance
            'Support': {'symbol': '─', 'bias': 'bullish', 'strength': 0.6},
            'Resistance': {'symbol': '─', 'bias': 'bearish', 'strength': 0.6},
            'Support Break': {'symbol': '⚡', 'bias': 'bearish', 'strength': 0.8},
            'Resistance Break': {'symbol': '⚡', 'bias': 'bullish', 'strength': 0.8},
            
            # Gap Patterns
            'Breakaway Gap': {'symbol': '⟐', 'bias': 'neutral', 'strength': 0.7},
            'Runaway Gap': {'symbol': '⟐', 'bias': 'neutral', 'strength': 0.6},
            'Exhaustion Gap': {'symbol': '⟐', 'bias': 'neutral', 'strength': 0.5},
            'Common Gap': {'symbol': '⟐', 'bias': 'neutral', 'strength': 0.3},
            
            # Candlestick Patterns
            'Doji': {'symbol': '✚', 'bias': 'neutral', 'strength': 0.5},
            'Hammer': {'symbol': '🔨', 'bias': 'bullish', 'strength': 0.7},
            'Shooting Star': {'symbol': '☄', 'bias': 'bearish', 'strength': 0.7},
            'Engulfing Bull': {'symbol': '🟢', 'bias': 'bullish', 'strength': 0.75},
            'Engulfing Bear': {'symbol': '🔴', 'bias': 'bearish', 'strength': 0.75},
        }
        
        # Color scheme
        self.colors = {
            'bullish': Fore.GREEN,
            'bearish': Fore.RED,
            'neutral': Fore.YELLOW,
            'info': Fore.CYAN,
            'warning': Fore.YELLOW,
            'error': Fore.RED,
            'success': Fore.GREEN,
            'price': Fore.WHITE + Style.BRIGHT,
            'chart': Fore.BLUE,
            'pattern': Fore.MAGENTA,
            'confidence': Fore.CYAN
        }
    
    def log(self, level, message):
        """Colored logging with verbose control"""
        if not self.verbose and level in ['info', 'warning']:
            return
        
        color = self.colors.get(level, Fore.WHITE)
        prefix = {
            'info': '💡',
            'warning': '⚠️ ',
            'error': '❌',
            'success': '✅'
        }.get(level, '')
        
        print(f"{color}{prefix} {message}{Style.RESET_ALL}")
    
    def loading_animation(self, text, duration=2):
        """Loading animation with spinner"""
        spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        start_time = time.time()
        i = 0
        
        while time.time() - start_time < duration:
            print(f"\r{Fore.CYAN}{spinner[i % len(spinner)]} {text}...{Style.RESET_ALL}", end='', flush=True)
            time.sleep(0.1)
            i += 1
        
        # Clear the line and print completion
        print(f"\r{' ' * (len(text) + 20)}", end='')  # Clear the line
        print(f"\r{Fore.GREEN}✓ {text} complete{Style.RESET_ALL}")
        print()  # Add newline
    
    def calculate_time_bias(self, patterns, prices=None):
        """Calculate bias for different time horizons based on patterns"""
        if not patterns:
            return {'short': 'neutral', 'medium': 'neutral', 'long': 'neutral'}
        
        # Analyze patterns by type and confidence
        bullish_score = 0
        bearish_score = 0
        total_weight = 0
        
        for pattern in patterns:
            pattern_type = pattern.get('type', '')
            confidence = float(pattern.get('confidence', '50').rstrip('%')) / 100
            
            # Get pattern info
            pattern_info = self.patterns.get(pattern_type, {'bias': 'neutral', 'strength': 0.5})
            bias = pattern_info['bias']
            strength = pattern_info['strength']
            
            # Calculate weighted score
            weight = confidence * strength
            total_weight += weight
            
            if bias == 'bullish':
                bullish_score += weight
            elif bias == 'bearish':
                bearish_score += weight
        
        # Calculate net bias
        if total_weight == 0:
            net_bias = 0
        else:
            net_bias = (bullish_score - bearish_score) / total_weight
        
        def bias_to_text(bias_score):
            if bias_score > 0.15:  # More sensitive thresholds
                return 'bullish'
            elif bias_score < -0.15:
                return 'bearish'
            else:
                return 'neutral'
        
        # For different timeframes, apply different sensitivity
        short_bias = net_bias * 1.2  # More sensitive for short term
        medium_bias = net_bias * 1.0  # Normal sensitivity
        long_bias = net_bias * 0.8   # Less sensitive for long term
        
        return {
            'short': bias_to_text(short_bias),
            'medium': bias_to_text(medium_bias),
            'long': bias_to_text(long_bias)
        }
    
    def create_minimalist_chart(self, symbol, patterns, current_price, bias_analysis):
        """Create minimalist chart display with uniform box formatting"""
        # Fixed width for consistent box
        box_width = 50
        content_width = box_width - 4  # Account for borders and padding
        
        # Create header
        header = f" {symbol} Analysis "
        header_padding = box_width - len(header)
        left_pad = header_padding // 2
        right_pad = header_padding - left_pad
        
        print(f"\n{Fore.WHITE + Style.BRIGHT}╭{'─' * left_pad}{header}{'─' * right_pad}╮{Style.RESET_ALL}")
        
        # Price display
        price_color = self.colors['price']
        price_text = f"${current_price:,.2f}"
        print(f"│ {price_color}{price_text:<{content_width}}{Style.RESET_ALL} │")
        
        # Bias lines with consistent formatting
        short_bias = bias_analysis['short'].upper()
        medium_bias = bias_analysis['medium'].upper()
        long_bias = bias_analysis['long'].upper()
        
        # Color the bias values, keep labels white
        short_color = self.colors.get(bias_analysis['short'].lower(), Fore.WHITE)
        medium_color = self.colors.get(bias_analysis['medium'].lower(), Fore.WHITE)
        long_color = self.colors.get(bias_analysis['long'].lower(), Fore.WHITE)
        
        # Format bias lines with proper spacing
        print(f"│ Short: {short_color}{short_bias}{Style.RESET_ALL}{' ' * (content_width - len(f'Short: {short_bias}'))} │")
        print(f"│ Medium: {medium_color}{medium_bias}{Style.RESET_ALL}{' ' * (content_width - len(f'Medium: {medium_bias}'))} │")
        print(f"│ Long: {long_color}{long_bias}{Style.RESET_ALL}{' ' * (content_width - len(f'Long: {long_bias}'))} │")
        
        # Patterns section
        print(f"│ Patterns:{' ' * (content_width - 9)} │")
        
        if patterns:
            # Sort by confidence and show top 5
            sorted_patterns = sorted(patterns, key=lambda p: float(p.get('confidence', '0').rstrip('%')), reverse=True)
            
            for pattern in sorted_patterns[:5]:
                ptype = pattern.get('type', 'Unknown')
                confidence = pattern.get('confidence', '0%')
                
                pattern_info = self.patterns.get(ptype, {'symbol': '*', 'bias': 'neutral'})
                symbol_char = pattern_info['symbol']
                bias = pattern_info['bias']
                
                # Color code by bias
                bias_color = self.colors[bias]
                conf_value = float(confidence.rstrip('%'))
                
                # Confidence indicator
                if conf_value >= 80:
                    conf_indicator = '●'
                elif conf_value >= 60:
                    conf_indicator = '◐'
                elif conf_value >= 40:
                    conf_indicator = '◑'
                else:
                    conf_indicator = '○'
                
                # Format pattern line with consistent spacing
                pattern_name = ptype[:20] if len(ptype) > 20 else ptype
                pattern_line = f"{symbol_char} {pattern_name} {confidence} {conf_indicator}"
                padding = content_width - len(pattern_line)
                
                print(f"│ {bias_color}{pattern_line}{Style.RESET_ALL}{' ' * padding} │")
        else:
            no_patterns_text = "No patterns detected"
            padding = content_width - len(no_patterns_text)
            print(f"│ {Fore.YELLOW}{no_patterns_text}{Style.RESET_ALL}{' ' * padding} │")
        
        # Close the box with consistent width
        print(f"{Fore.WHITE + Style.BRIGHT}╰{'─' * box_width}╯{Style.RESET_ALL}")
    
    def analyze_crypto(self, symbol, days=60, interval='1d'):
        """Analyze cryptocurrency with loading animation"""
        print(f"\n{Fore.CYAN + Style.BRIGHT}🚀 CryptVault - Crypto & Stock Analysis{Style.RESET_ALL}")
        print(f"{Fore.WHITE}═" * 50 + Style.RESET_ALL)
        
        # Simple loading indicator
        print(f"{Fore.CYAN}⚡ Analyzing {symbol.upper()}...{Style.RESET_ALL}", end='', flush=True)
        
        try:
            # Perform analysis
            results = self.analyzer.analyze_ticker(symbol, days=days, interval=interval)
            
            # Clear loading line
            print(f"\r{' ' * 30}", end='')
            print(f"\r{Fore.GREEN}✓ Analysis complete{Style.RESET_ALL}")
            
            if not results['success']:
                self.log('error', f"Analysis failed: {results['error']}")
                return False
            
            # Extract data
            patterns = results.get('patterns', [])
            ticker_info = results.get('ticker_info', {})
            ml_predictions = results.get('ml_predictions', {})
            existing_chart = results.get('chart', '')
            
            current_price = ticker_info.get('current_price', 0)
            
            # Calculate time-based bias with enhanced analysis
            bias_analysis = self.calculate_time_bias(patterns)
            
            # Enhance bias with price momentum if available
            if ticker_info.get('price_change'):
                price_change = ticker_info['price_change']
                if 'percentage' in price_change:
                    change_pct = price_change['percentage']
                    if change_pct > 0.02:  # +2% or more
                        if bias_analysis['short'] == 'neutral':
                            bias_analysis['short'] = 'bullish'
                    elif change_pct < -0.02:  # -2% or more
                        if bias_analysis['short'] == 'neutral':
                            bias_analysis['short'] = 'bearish'
            
            # Display minimalist chart
            self.create_minimalist_chart(symbol.upper(), patterns, current_price, bias_analysis)
            
            # Open desktop chart instead of terminal chart
            try:
                from cryptvault.visualization.desktop_charts import CryptVaultDesktopCharts
                print(f"\n{Fore.BLUE}📊 Opening desktop chart window...{Style.RESET_ALL}")
                app = CryptVaultDesktopCharts()
                # Pre-populate with current analysis
                app.current_data = raw_data
                app.current_patterns = patterns
                app.current_symbol = symbol.upper()
                app._update_chart(results, symbol.upper())
                app.run()
            except ImportError as e:
                self.log('warning', f"Desktop charts not available: {e}")
                # Fallback to terminal chart
                if existing_chart:
                    print(f"\n{Fore.BLUE}📊 Chart Analysis:{Style.RESET_ALL}")
                    print(existing_chart)
            except Exception as e:
                self.log('warning', f"Desktop chart error: {e}")
                # Fallback to terminal chart
                if existing_chart:
                    print(f"\n{Fore.BLUE}📊 Chart Analysis:{Style.RESET_ALL}")
                    print(existing_chart)
            
            # Show additional detailed analysis in verbose mode
            if self.verbose:
                self._show_detailed_analysis(patterns, ml_predictions)
            
            # Enhanced ML predictions
            ml_forecast = self.interpret_ml_predictions(ml_predictions, patterns, current_price)
            if ml_forecast:
                forecast_color = self.colors.get(ml_forecast['trend'].lower(), Fore.WHITE)
                print(f"\n{Fore.CYAN}🧠 ML Forecast:{Style.RESET_ALL} {forecast_color}{ml_forecast['trend'].upper()}{Style.RESET_ALL} ({ml_forecast['confidence']}% confidence)")
                
                if ml_forecast.get('target_price'):
                    print(f"{Fore.CYAN}🎯 Target Price:{Style.RESET_ALL} ${ml_forecast['target_price']:,.2f}")
            
            # Performance metrics
            analysis_time = results.get('analysis_time_seconds', 0)
            self.log('success', f"Analysis completed in {analysis_time:.2f}s | {len(patterns)} patterns found")
            
            return True
            
        except Exception as e:
            self.log('error', f"Analysis failed: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return False
    
    def analyze_multiple(self, symbols, days=60, interval='1d'):
        """Analyze multiple cryptocurrencies"""
        print(f"\n{Fore.CYAN + Style.BRIGHT}🎯 Multi-Asset Analysis{Style.RESET_ALL}")
        print(f"{Fore.WHITE}═" * 60 + Style.RESET_ALL)
        
        results = []
        for symbol in symbols:
            success = self.analyze_crypto(symbol, days, interval)
            results.append((symbol, success))
            
            if symbol != symbols[-1]:  # Not the last one
                print(f"\n{Fore.WHITE}─" * 50 + Style.RESET_ALL)
        
        # Summary
        successful = sum(1 for _, success in results if success)
        print(f"\n{Fore.CYAN}📊 Summary:{Style.RESET_ALL} {successful}/{len(symbols)} analyses completed")
        
        return results
    
    def interpret_ml_predictions(self, ml_predictions, patterns, current_price):
        """Enhanced ML predictions with ensemble methods and pattern integration"""
        if not ml_predictions:
            return None
        
        # Get ensemble ML predictions
        trend_forecast = ml_predictions.get('trend_forecast', {})
        base_trend = trend_forecast.get('trend_7d', 'sideways')
        base_strength = trend_forecast.get('trend_strength', '60.0%')
        ensemble_confidence = ml_predictions.get('ensemble_confidence', 0.6)
        
        # Parse strength percentage
        try:
            strength_value = float(base_strength.rstrip('%'))
        except:
            strength_value = 60.0
        
        # Enhanced pattern integration
        pattern_score = 0.0
        pattern_weight = 0.0
        
        if patterns:
            bullish_weight = 0
            bearish_weight = 0
            
            for pattern in patterns:
                pattern_type = pattern.get('type', '')
                confidence = float(pattern.get('confidence', '50').rstrip('%'))
                pattern_info = self.patterns.get(pattern_type, {'bias': 'neutral'})
                
                # Weight patterns by confidence and type
                weight = confidence / 100.0
                
                if pattern_info['bias'] == 'bullish':
                    bullish_weight += weight
                elif pattern_info['bias'] == 'bearish':
                    bearish_weight += weight
                
                pattern_weight += weight
            
            # Calculate pattern bias (-1 to 1)
            if pattern_weight > 0:
                pattern_score = (bullish_weight - bearish_weight) / pattern_weight
        
        # Combine ML and pattern signals with advanced logic
        ml_score = 0.0
        if base_trend == 'bullish':
            ml_score = 0.5
        elif base_trend == 'bearish':
            ml_score = -0.5
        
        # Weighted combination (70% ML, 30% patterns)
        combined_score = (0.7 * ml_score) + (0.3 * pattern_score)
        
        # Enhanced confidence calculation
        base_confidence = strength_value
        pattern_boost = min(20, abs(pattern_score) * 25)  # Up to 20% boost from patterns
        ensemble_boost = (ensemble_confidence - 0.5) * 30  # Ensemble quality boost
        
        final_confidence = min(95, max(55, base_confidence + pattern_boost + ensemble_boost))
        
        # Determine final trend with improved thresholds
        if combined_score > 0.15:
            final_trend = 'bullish'
        elif combined_score < -0.15:
            final_trend = 'bearish'
        elif abs(combined_score) > 0.05:
            final_trend = 'neutral'
        else:
            final_trend = 'sideways'
        
        # Dynamic target price calculation
        target_price = None
        if final_trend in ['bullish', 'bearish']:
            # More sophisticated target calculation
            volatility_factor = min(0.15, abs(combined_score) * 0.2)  # Max 15% move
            confidence_factor = final_confidence / 100.0
            
            price_change = volatility_factor * confidence_factor
            
            if final_trend == 'bullish':
                target_price = current_price * (1 + price_change)
            else:  # bearish
                target_price = current_price * (1 - price_change)
        
        return {
            'trend': final_trend,
            'confidence': int(final_confidence),
            'target_price': target_price,
            'ml_score': ml_score,
            'pattern_score': pattern_score,
            'combined_score': combined_score,
            'ensemble_confidence': ensemble_confidence
        }
    
    def _show_detailed_analysis(self, patterns, ml_predictions):
        """Show detailed analysis in verbose mode"""
        print(f"\n{Fore.CYAN}📈 Detailed Pattern Analysis:{Style.RESET_ALL}")
        
        if patterns:
            # Group patterns by type
            pattern_groups = {}
            for pattern in patterns:
                ptype = pattern.get('type', 'Unknown')
                if ptype not in pattern_groups:
                    pattern_groups[ptype] = []
                pattern_groups[ptype].append(pattern)
            
            # Show pattern details
            for ptype, group in pattern_groups.items():
                pattern_info = self.patterns.get(ptype, {'symbol': '*', 'bias': 'neutral'})
                symbol = pattern_info['symbol']
                bias_color = self.colors[pattern_info['bias']]
                
                print(f"  {bias_color}{symbol} {ptype}:{Style.RESET_ALL}")
                for pattern in group:
                    confidence = pattern.get('confidence', '0%')
                    if 'target_price' in pattern:
                        print(f"    Target: ${pattern['target_price']:.2f} | Confidence: {confidence}")
                    if 'description' in pattern:
                        desc = pattern['description'][:60] + "..." if len(pattern['description']) > 60 else pattern['description']
                        print(f"    {desc}")
        
        # ML model details
        if ml_predictions:
            print(f"\n{Fore.CYAN}🤖 ML Model Details:{Style.RESET_ALL}")
            if 'ensemble_accuracy' in ml_predictions:
                accuracy = ml_predictions['ensemble_accuracy']
                print(f"  Ensemble Accuracy: {accuracy:.1%}")
            
            if 'model_weights' in ml_predictions:
                weights = ml_predictions['model_weights']
                print(f"  Active Models:")
                for model, weight in weights.items():
                    if weight > 0.01:
                        print(f"    {model}: {weight:.1%}")
    
    def create_tradingview_style_chart(self, data, patterns, symbol, width=70, height=16):
        """Create unified TradingView-style ASCII chart with proper alignment"""
        if not data or len(data.data) < 2:
            return "Insufficient data for chart"
        
        # Extract OHLCV data
        data_points = data.data[-60:]  # Last 60 data points for clarity
        closes = [point.close for point in data_points]
        highs = [point.high for point in data_points]
        lows = [point.low for point in data_points]
        dates = [point.timestamp for point in data_points]
        
        # Calculate price range with padding
        min_price = min(lows)
        max_price = max(highs)
        price_range = max_price - min_price
        
        if price_range == 0:
            price_range = max_price * 0.01
        
        # Add 5% padding to price range
        padding = price_range * 0.05
        min_price -= padding
        max_price += padding
        price_range = max_price - min_price
        
        # Create unified chart grid
        chart = [[' ' for _ in range(width)] for _ in range(height)]
        
        # Draw price line (unified and smooth)
        for i in range(1, len(closes)):
            x1 = int(((i-1) / (len(closes) - 1)) * (width - 1))
            x2 = int((i / (len(closes) - 1)) * (width - 1))
            
            y1 = int(((closes[i-1] - min_price) / price_range) * (height - 1))
            y2 = int(((closes[i] - min_price) / price_range) * (height - 1))
            
            # Ensure coordinates are within bounds
            x1, x2 = max(0, min(width-1, x1)), max(0, min(width-1, x2))
            y1, y2 = max(0, min(height-1, y1)), max(0, min(height-1, y2))
            
            # Draw line between points
            if x1 == x2:  # Vertical line
                start_y, end_y = min(y1, y2), max(y1, y2)
                for y in range(start_y, end_y + 1):
                    chart[height - 1 - y][x1] = '│'
            else:  # Diagonal or horizontal line
                # Simple line drawing algorithm
                dx = abs(x2 - x1)
                dy = abs(y2 - y1)
                
                if dx > dy:  # More horizontal
                    for x in range(min(x1, x2), max(x1, x2) + 1):
                        if x1 != x2:
                            y = y1 + int((y2 - y1) * (x - x1) / (x2 - x1))
                            y = max(0, min(height - 1, y))
                            chart[height - 1 - y][x] = '─'
                else:  # More vertical
                    for y in range(min(y1, y2), max(y1, y2) + 1):
                        if y1 != y2:
                            x = x1 + int((x2 - x1) * (y - y1) / (y2 - y1))
                            x = max(0, min(width - 1, x))
                            chart[height - 1 - y][x] = '│'
        
        # Add pattern markers (unified positioning)
        if patterns:
            sorted_patterns = sorted(patterns, key=lambda p: float(p.get('confidence', '0').rstrip('%')), reverse=True)
            
            for i, pattern in enumerate(sorted_patterns[:3]):  # Top 3 patterns only
                pattern_type = pattern.get('type', 'Unknown')
                pattern_info = self.patterns.get(pattern_type, {'symbol': '*', 'bias': 'neutral'})
                symbol_char = pattern_info['symbol']
                confidence = float(pattern.get('confidence', '0').rstrip('%'))
                
                # Position markers at different heights to avoid overlap
                marker_y = height - 3 - i
                marker_y = max(1, min(height - 2, marker_y))
                
                # Place marker at 1/4, 1/2, 3/4 positions
                marker_positions = [width // 4, width // 2, 3 * width // 4]
                marker_x = marker_positions[i % 3]
                marker_x = max(0, min(width - 1, marker_x))
                
                # Choose confidence indicator
                if confidence >= 80:
                    conf_char = '●'
                elif confidence >= 60:
                    conf_char = '◐'
                else:
                    conf_char = '○'
                
                # Place pattern marker if space is available
                if chart[marker_y][marker_x] == ' ':
                    chart[marker_y][marker_x] = symbol_char
                
                # Place confidence indicator nearby
                if marker_x + 1 < width and chart[marker_y][marker_x + 1] == ' ':
                    chart[marker_y][marker_x + 1] = conf_char
        
        # Convert chart to string with clean formatting
        chart_lines = []
        
        # Add title (centered and clean)
        title = f"Chart Analysis - {symbol} (1d)"
        title_padding = (width - len(title)) // 2
        chart_lines.append(f"{' ' * (10 + title_padding)}{Fore.WHITE + Style.BRIGHT}{title}{Style.RESET_ALL}")
        
        # Add price labels and chart rows
        for i, row in enumerate(chart):
            price_at_row = min_price + (price_range * (height - 1 - i) / (height - 1))
            price_label = f"{price_at_row:9.2f}"
            
            # Clean row rendering
            row_content = ''.join(row)
            chart_lines.append(f"{Fore.CYAN}{price_label}{Style.RESET_ALL} │{row_content}│")
        
        # Add bottom border
        chart_lines.append(f"         └{'─' * width}┘")
        
        # Add date labels (clean and aligned)
        if dates:
            start_date = dates[0].strftime("%m/%d %H:%M")
            end_date = dates[-1].strftime("%m/%d %H:%M")
            date_spacing = width - len(start_date) - len(end_date)
            date_line = f"          {start_date}{' ' * max(0, date_spacing)}{end_date}"
            chart_lines.append(date_line)
        
        # Add volume bars (TradingView style)
        if volumes:
            chart_lines.append("")
            chart_lines.append(f"{Fore.CYAN}📊 Volume Profile:{Style.RESET_ALL}")
            
            max_volume = max(volumes) if volumes else 1
            volume_bar_width = 30
            
            # Show last 5 volume bars
            for i in range(max(0, len(volumes) - 5), len(volumes)):
                vol_ratio = volumes[i] / max_volume if max_volume > 0 else 0
                bar_length = int(vol_ratio * volume_bar_width)
                
                # Color code volume bars
                if i > 0 and closes[i] >= closes[i-1]:
                    vol_color = Fore.GREEN
                else:
                    vol_color = Fore.RED
                
                volume_bar = '█' * bar_length + '░' * (volume_bar_width - bar_length)
                date_str = dates[i].strftime("%m/%d") if i < len(dates) else f"#{i+1}"
                
                chart_lines.append(f"  {date_str}: {vol_color}{volume_bar}{Style.RESET_ALL} {volumes[i]:,.0f}")
        
        # Add current price and change
        if len(closes) >= 2:
            current_price = closes[-1]
            prev_price = closes[-2]
            change = current_price - prev_price
            change_pct = (change / prev_price) * 100 if prev_price != 0 else 0
            
            change_color = Fore.GREEN if change >= 0 else Fore.RED
            change_symbol = "▲" if change >= 0 else "▼"
            
            chart_lines.append("")
            chart_lines.append(f"{Fore.WHITE + Style.BRIGHT}💰 Current: ${current_price:,.2f} {change_color}{change_symbol} ${abs(change):.2f} ({change_pct:+.2f}%){Style.RESET_ALL}")
        
        # Add technical analysis summary
        if len(closes) >= 20:
            ma20 = sum(closes[-20:]) / 20
            ma_trend = "Above MA20" if current_price > ma20 else "Below MA20"
            ma_color = Fore.GREEN if current_price > ma20 else Fore.RED
            
            chart_lines.append(f"{Fore.CYAN}📈 MA20: ${ma20:.2f} | Price is {ma_color}{ma_trend}{Style.RESET_ALL}")
        
        # Add pattern legend
        if patterns:
            chart_lines.append("")
            chart_lines.append(f"{Fore.MAGENTA}🎯 Pattern Legend:{Style.RESET_ALL}")
            
            pattern_legend = []
            for pattern in patterns[:3]:  # Top 3 patterns
                ptype = pattern.get('type', 'Unknown')
                pattern_info = self.patterns.get(ptype, {'symbol': '*', 'bias': 'neutral'})
                symbol = pattern_info['symbol']
                bias_color = self.colors[pattern_info['bias']]
                confidence = pattern.get('confidence', '0%')
                
                pattern_legend.append(f"{bias_color}{symbol} {ptype} ({confidence}){Style.RESET_ALL}")
            
            chart_lines.append("  " + " | ".join(pattern_legend))
        
        return '\n'.join(chart_lines)
    
    def _add_tradingview_patterns(self, chart, patterns, width, height, min_price, price_range):
        """Add clean pattern overlays without fragmentation"""
        # This function is now integrated into the main chart creation
        # to avoid overlay conflicts and ensure unified rendering
        pass
    
    def _add_technical_indicators(self, chart, prices, width, height, min_price, price_range):
        """Add clean technical indicators without chart fragmentation"""
        # Technical indicators are now integrated into the main chart
        # to maintain visual coherence and prevent overlapping elements
        pass

def main():
    """Main function with enhanced argument parsing"""
    parser = argparse.ArgumentParser(
        description="Advanced CryptVault Terminal Charts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python advanced_crypto_charts.py BTC              # Quick Bitcoin analysis
  python advanced_crypto_charts.py ETH 30 4h       # Ethereum 30 days, 4h intervals
  python advanced_crypto_charts.py -m BTC ETH ADA  # Multi-asset analysis
  python advanced_crypto_charts.py BTC -v          # Verbose mode with detailed charts
        """
    )
    
    parser.add_argument('symbol', nargs='?', default='BTC', help='Cryptocurrency symbol')
    parser.add_argument('days', nargs='?', type=int, default=60, help='Number of days (default: 60)')
    parser.add_argument('interval', nargs='?', default='1d', help='Data interval (default: 1d)')
    parser.add_argument('-m', '--multiple', nargs='+', help='Analyze multiple symbols')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output with detailed charts')
    parser.add_argument('--quick', action='store_true', help='Quick analysis mode')
    
    args = parser.parse_args()
    
    # Initialize charts
    charts = AdvancedCryptoCharts(verbose=args.verbose)
    
    try:
        if args.multiple:
            # Multi-asset analysis
            charts.analyze_multiple(args.multiple, args.days, args.interval)
        else:
            # Single asset analysis
            charts.analyze_crypto(args.symbol, args.days, args.interval)
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️  Analysis interrupted{Style.RESET_ALL}")
    except Exception as e:
        charts.log('error', f"Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()