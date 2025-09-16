"""
Desktop Chart Application for CryptVault
Interactive matplotlib-based charts with pattern visualization

Made with ❤️ by the MeridianAlgo Algorithmic Research Team (Quantum Meridian)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import threading
import queue
import logging
from typing import List, Dict, Optional, Any
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from cryptvault.analyzer import PatternAnalyzer
from cryptvault.data.models import PriceDataFrame

logger = logging.getLogger(__name__)

class CryptVaultDesktopCharts:
    """Desktop chart application with interactive pattern visualization."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🚀 CryptVault Desktop Charts - Professional Trading Analysis")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 700)
        # HiDPI scaling for crisper UI on Windows
        try:
            self.root.tk.call('tk', 'scaling', 1.25)
        except Exception:
            pass
        self.root.configure(bg='#0a0e13')
        
        # Set window icon and styling
        try:
            self.root.iconbitmap(default='icon.ico')  # Add if icon exists
        except:
            pass
        
        # Initialize analyzer
        self.analyzer = PatternAnalyzer()
        # Increase pattern sensitivity and quality by default for desktop viz
        try:
            # Initialize variables to prevent NameError
            self._display_patterns = []
            self._pattern_ranges = []
            self._current_symbol = 'BTC'
            self._current_days = 30
            self._current_interval = '1d'
            self.analyzer.set_sensitivity_preset('high')
            # Prefer stricter min confidence per category and filter overlaps
            self.analyzer.update_pattern_settings(max_total_patterns=12, filter_overlapping=True)
        except Exception:
            pass
        
        # Data storage
        self.current_data = None
        self.current_patterns = []
        self.current_symbol = "BTC"
        
        # UI state variables
        self.fig = None
        self.ax_price = None
        self.ax_vol = None
        self.canvas = None
        self._pattern_ranges = []  # list of (start_idx, end_idx)
        self._current_days = 60
        self._current_interval = '1d'
        self._display_patterns = []
        
        # Enhanced pattern colors with better contrast
        self.pattern_colors = {
            'bullish': '#00ff88',    # Bright green
            'bearish': '#ff4444',    # Bright red
            'neutral': '#ffaa00',    # Orange
            'divergence': '#8844ff', # Purple
            'channel': '#00aaff',    # Blue
            'wedge': '#ff8800',      # Dark orange
            'flag': '#ff00ff',       # Magenta
            'triangle': '#88ff00',   # Lime green
            'harmonic': '#aa44ff',
            'candlestick': '#44aaff'
        }
        
        self.pattern_symbols = {
            'Double Bottom': '⩗',
            'Double Top': '⩘',
            'Triple Bottom': '⫸',
            'Triple Top': '⫷',
            'Head and Shoulders': '⩙',
            'Inverse Head and Shoulders': '⩚',
            'Ascending Triangle': '△',
            'Descending Triangle': '▽',
            'Expanding Triangle': '◇',
            'Symmetrical Triangle': '◊',
            'Bull Flag': '⚑',
            'Bear Flag': '⚐',
            'Bullish Divergence': '↗',
            'Bearish Divergence': '↘',
            'Hidden Bullish Divergence': '⤴',
            'Hidden Bearish Divergence': '⤵',
            'Rectangle': '▭',
            'Diamond': '◈',
            'Gartley': 'G',
            'Butterfly': 'B',
            'ABCD': 'A',
            'Hammer': '🔨',
            'Shooting Star': '☄',
            'Doji': '✚'
        }
        
        self.setup_ui()
        # Auto-run first analysis for a better first impression
        self.root.after(100, self.analyze_symbol)
        
    def setup_ui(self):
        """Setup the user interface."""
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', background='#0f1115', foreground='#d0d4dc')
        style.configure('TButton', background='#1b1f27', foreground='#e6e8eb', padding=6)
        style.configure('TEntry', fieldbackground='#1b1f27', foreground='#e6e8eb')
        style.configure('TCombobox', fieldbackground='#1b1f27', foreground='#e6e8eb')
        style.map('TButton', background=[('active', '#2a2f3a')])
        
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control panel
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Symbol input
        ttk.Label(control_frame, text="Symbol:").grid(row=0, column=0, padx=(0, 5))
        self.symbol_var = tk.StringVar(value="BTC")
        symbol_entry = ttk.Entry(control_frame, textvariable=self.symbol_var, width=10)
        symbol_entry.grid(row=0, column=1, padx=(0, 10))
        
        # Days input
        ttk.Label(control_frame, text="Days:").grid(row=0, column=2, padx=(0, 5))
        self.days_var = tk.StringVar(value="60")
        days_entry = ttk.Entry(control_frame, textvariable=self.days_var, width=5)
        days_entry.grid(row=0, column=3, padx=(0, 10))
        
        # Interval selection
        ttk.Label(control_frame, text="Interval:").grid(row=0, column=4, padx=(0, 5))
        self.interval_var = tk.StringVar(value="1d")
        interval_combo = ttk.Combobox(control_frame, textvariable=self.interval_var, 
                                    values=["1h", "4h", "1d", "1w"], width=5)
        interval_combo.grid(row=0, column=5, padx=(0, 10))
        
        # Analyze button
        analyze_btn = ttk.Button(control_frame, text="Analyze", command=self.analyze_symbol)
        analyze_btn.grid(row=0, column=6, padx=(0, 10))

        # Export button
        export_btn = ttk.Button(control_frame, text="Export Chart", command=self.export_chart)
        export_btn.grid(row=0, column=7)

        # Enhanced pattern display toggles with better layout
        self.show_rectangles = tk.BooleanVar(value=True)
        self.show_triangles = tk.BooleanVar(value=True)
        self.show_divergence = tk.BooleanVar(value=True)
        self.show_channels = tk.BooleanVar(value=True)
        self.show_wedges = tk.BooleanVar(value=True)
        self.show_flags = tk.BooleanVar(value=True)
        pattern_frame = ttk.LabelFrame(control_frame, text="Pattern Filters", padding=5)
        pattern_frame.grid(row=0, column=8, columnspan=6, padx=(20, 0), sticky='ew')
        
        ttk.Checkbutton(pattern_frame, text="📊 Rectangles", variable=self.show_rectangles).grid(row=0, column=0, padx=5)
        ttk.Checkbutton(pattern_frame, text="📐 Triangles", variable=self.show_triangles).grid(row=0, column=1, padx=5)
        ttk.Checkbutton(pattern_frame, text="📈 Channels", variable=self.show_channels).grid(row=0, column=2, padx=5)
        ttk.Checkbutton(pattern_frame, text="📉 Wedges", variable=self.show_wedges).grid(row=0, column=3, padx=5)
        ttk.Checkbutton(pattern_frame, text="🚩 Flags", variable=self.show_flags).grid(row=0, column=4, padx=5)
        ttk.Checkbutton(pattern_frame, text="⚡ Divergence", variable=self.show_divergence).grid(row=0, column=5, padx=5)
        
        # Chart frame
        chart_frame = ttk.Frame(main_frame)
        chart_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create enhanced matplotlib figure with modern styling
        self.fig = Figure(figsize=(14, 10), facecolor='#0a0e13', edgecolor='none')
        self.fig.patch.set_facecolor('#0a0e13')
        gs = self.fig.add_gridspec(3, 1, height_ratios=[3, 1, 0.3], hspace=0.1)
        self.ax_price = self.fig.add_subplot(gs[0])
        self.ax_vol = self.fig.add_subplot(gs[1], sharex=self.ax_price)
        self.ax_info = self.fig.add_subplot(gs[2])  # Info panel
        
        # Hide info panel axes and use for status display
        self.ax_info.set_xticks([])
        self.ax_info.set_yticks([])
        self.ax_info.set_facecolor('#0a0e13')
        for spine in self.ax_info.spines.values():
            spine.set_visible(False)
        
        # Modern dark theme styling
        for ax in (self.ax_price, self.ax_vol):
            ax.tick_params(colors='#d0d4dc')
            for spine in ax.spines.values():
                spine.set_color('#2a2f3a')
            ax.grid(True, color='#1b1f27', alpha=0.6, linewidth=0.8, linestyle='--')
        # Hide duplicate x labels on top axis
        self.ax_price.tick_params(labelbottom=False)
        
        # Enhanced canvas with better integration
        self.canvas = FigureCanvasTkAgg(self.fig, chart_frame)
        self.canvas.draw()
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.configure(bg='#0a0e13', highlightthickness=0)
        canvas_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        # Toolbar
        try:
            toolbar = NavigationToolbar2Tk(self.canvas, chart_frame, pack_toolbar=False)
            toolbar.update()
            toolbar.pack(fill=tk.X, side=tk.BOTTOM)
        except Exception:
            pass
        
        # Pattern info frame
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Pattern listbox
        ttk.Label(info_frame, text="Detected Patterns:").pack(anchor=tk.W)
        self.pattern_listbox = tk.Listbox(info_frame, height=6, bg='#1b1f27', fg='#d0d4dc',
                                        selectbackground='#2a2f3a', selectforeground='#e6e8eb', activestyle='none')
        self.pattern_listbox.pack(fill=tk.X, pady=(5, 0))
        self.pattern_listbox.bind('<<ListboxSelect>>', self._on_pattern_select)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready - Enter symbol and click Analyze")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, pady=(10, 0))
        
        # Bind events
        symbol_entry.bind('<Return>', lambda e: self.analyze_symbol())
        days_entry.bind('<Return>', lambda e: self.analyze_symbol())
        interval_combo.bind('<Return>', lambda e: self.analyze_symbol())
        
    def analyze_symbol(self):
        """Analyze the selected symbol."""
        symbol = self.symbol_var.get().upper().strip()
        if not symbol:
            messagebox.showerror("Error", "Please enter a symbol")
            return
            
        try:
            days = int(self.days_var.get())
            interval = self.interval_var.get()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid days (number)")
            return
    
        self.status_var.set(f"Analyzing {symbol}...")
        self.root.update()
        # Remember current settings for chart fetch
        self._current_days = days
        self._current_interval = interval
        
        # Run analysis in thread to prevent UI freezing
        thread = threading.Thread(target=self._run_analysis, args=(symbol, days, interval))
        thread.daemon = True
        thread.start()
        
    def _run_analysis(self, symbol, days, interval):
        """Run analysis in background thread."""
        try:
            # Perform analysis
            results = self.analyzer.analyze_ticker(symbol, days=days, interval=interval)
            
            if not results['success']:
                self.root.after(0, lambda: self._show_error(f"Analysis failed: {results['error']}"))
                return
            
            # Update UI in main thread
            self.root.after(0, lambda: self._update_chart(results, symbol))
            
        except Exception as e:
            self.root.after(0, lambda: self._show_error(f"Analysis error: {str(e)}"))
    
    def _update_chart(self, results, symbol):
        """Update the chart with analysis results."""
        try:
            # Clear previous chart
            self.ax_price.clear()
            self.ax_vol.clear()
            
            # Enhanced axis styling with modern dark theme
            for ax in (self.ax_price, self.ax_vol):
                ax.set_facecolor('#0f1419')
                ax.tick_params(colors='#e6e8eb', labelsize=10)
                ax.grid(True, color='#1e2329', alpha=0.4, linewidth=0.5, linestyle='-')
                
                # Style spines
                for spine in ax.spines.values():
                    spine.set_color('#2a2f3a')
                    spine.set_linewidth(0.8)
            
            # Remove top and right spines for cleaner look
            self.ax_price.spines['top'].set_visible(False)
            self.ax_price.spines['right'].set_visible(False)
            self.ax_vol.spines['top'].set_visible(False)
            self.ax_vol.spines['right'].set_visible(False)
            
            # Get data
            patterns_raw = results.get('patterns', [])
            # Use a consistent order for overlays and list (sorted by confidence desc)
            self._display_patterns = sorted(
                patterns_raw, key=lambda p: float(p.get('confidence','0').rstrip('%')), reverse=True
            )
            ticker_info = results.get('ticker_info', {})
            current_price = ticker_info.get('current_price', 0)
            
            # Update pattern list
            self._update_pattern_list(self._display_patterns)
            
            # Get historical data for charting
            from cryptvault.data.package_fetcher import PackageDataFetcher
            data_fetcher = PackageDataFetcher()
            raw_data = data_fetcher.fetch_historical_data(symbol, days=self._current_days, interval=self._current_interval)
            
            if not raw_data or len(raw_data.data) < 2:
                self._show_error("Insufficient data for charting")
                return
            
            # Convert to DataFrame for easier plotting
            data_points = raw_data.data
            dates = [point.timestamp for point in data_points]
            opens = [point.open for point in data_points]
            highs = [point.high for point in data_points]
            lows = [point.low for point in data_points]
            closes = [point.close for point in data_points]
            volumes = [getattr(point, 'volume', 0) or 0 for point in data_points]
            
            # Plot candlesticks with enhanced gradient effects
            self._plot_candlesticks(dates, opens, highs, lows, closes)
            
            # Plot volume with enhanced styling
            self._plot_volume(dates, volumes, closes)
            
            # Plot patterns on the chart (main focus - no indicators)
            self._plot_patterns(self._display_patterns, dates, opens, highs, lows, closes)
            
            # Enhanced price line with gradient effect
            self.ax_price.plot(dates, closes, color='#00d4ff', linewidth=2, alpha=0.9, label='💰 Close Price')
            
            # Simplified legend focusing on patterns only
            legend_elements = [
                Line2D([0], [0], color='#00ff88', lw=2, label='📈 Bullish Pattern'),
                Line2D([0], [0], color='#ff4444', lw=2, label='📉 Bearish Pattern'),
                Line2D([0], [0], color='#ffaa00', lw=2, label='🔶 Neutral Pattern')
            ]
            
            self.ax_price.legend(
                handles=legend_elements, 
                loc='upper left', 
                frameon=True, 
                fancybox=True, 
                shadow=True,
                framealpha=0.9,
                facecolor='#1a1f2e',
                edgecolor='#2a2f3a',
                fontsize=9
            )
            
            # Enhanced titles and labels
            self.ax_price.set_title(f'📊 {symbol} - Pattern Analysis', 
                                   fontsize=16, fontweight='bold', color='#00d4ff', pad=20)
            self.ax_price.set_ylabel('Price ($)', fontsize=12, color='#e6e8eb', fontweight='bold')
            self.ax_vol.set_ylabel('Volume', fontsize=10, color='#e6e8eb', fontweight='bold')
            self.ax_vol.set_xlabel('Date', fontsize=12, color='#e6e8eb', fontweight='bold')
            
            # Format x-axis dates
            self.ax_price.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            self.ax_price.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//10)))
            
            # Rotate date labels for better readability
            plt.setp(self.ax_vol.xaxis.get_majorticklabels(), rotation=45, ha='right')
            
            # Add current price indicator
            if current_price > 0:
                price_color = '#00ff88' if closes[-1] >= closes[0] else '#ff4444'
                self.ax_price.axhline(y=current_price, color=price_color, linestyle='--', 
                                     alpha=0.8, linewidth=2, label=f'Current: ${current_price:.2f}')
                
                # Add price annotation
                self.ax_price.annotate(f'${current_price:.2f}', 
                                      xy=(dates[-1], current_price),
                                      xytext=(10, 0), textcoords='offset points',
                                      color=price_color, fontweight='bold', fontsize=11,
                                      bbox=dict(boxstyle='round,pad=0.3', facecolor=price_color, alpha=0.2))
            
            # Tight layout for better spacing
            self.fig.tight_layout()
            
            # Refresh canvas
            self.canvas.draw()
            
            # Update status
            pattern_count = len(self._display_patterns)
            self.status_var.set(f"✅ Found {pattern_count} patterns for {symbol}")
            
        except Exception as e:
            self._show_error(f"Chart update error: {str(e)}")
            logging.error(f"Chart update error: {e}", exc_info=True)

    def _draw_head_shoulders(self, x_range, highs_range, lows_range, color):
        """Draw head and shoulders pattern."""
        try:
            arr = np.array(highs_range)
            if len(arr) < 5:
                return
                
            # Find the head (highest peak)
            peak_idx = int(np.argmax(arr))
            if peak_idx < 2 or peak_idx >= len(arr)-2:
                return  # Not enough points on either side
                
            # Find shoulders (local maxima on either side)
            left_peak = np.argmax(arr[:peak_idx])
            right_peak = peak_idx + 1 + np.argmax(arr[peak_idx+1:])
            
            # Draw neckline (connect the troughs between shoulders and head)
            left_trough = peak_idx - 1 - np.argmin(highs_range[peak_idx-1::-1])
            right_trough = peak_idx + 1 + np.argmin(highs_range[peak_idx+1:])
            
            # Draw the pattern
            self.ax_price.plot(
                [x_range[left_peak], x_range[peak_idx], x_range[right_peak]],
                [highs_range[left_peak], highs_range[peak_idx], highs_range[right_peak]],
                color=color, linestyle='--', linewidth=1.4, alpha=0.7
            )
            
            # Draw neckline
            self.ax_price.plot(
                [x_range[left_trough], x_range[right_trough]],
                [highs_range[left_trough], highs_range[right_trough]],
                color=color, linestyle='-', linewidth=1.2, alpha=0.7
            )
            
            # Label
            self.ax_price.annotate(
                'Head & Shoulders', 
                xy=(x_range[peak_idx], highs_range[peak_idx]), 
                xytext=(0, 30), textcoords='offset points',
                ha='center', color=color
            )
        except Exception as e:
            logging.warning(f"Error drawing head & shoulders: {e}")

# Removed _plot_indicators method to simplify chart display
    
    def _plot_candlesticks(self, dates, opens, highs, lows, closes):
        """Plot candlestick chart with enhanced gradient effects."""
        try:
            import numpy as np
            from matplotlib.patches import Rectangle
            
            # Calculate colors for each candlestick
            colors = ['#00ff88' if close >= open else '#ff4444' for open, close in zip(opens, closes)]
            
            # Plot candlesticks
            for i, (date, open_price, high, low, close, color) in enumerate(zip(dates, opens, highs, lows, closes, colors)):
                # Draw the wick (high-low line)
                self.ax_price.plot([date, date], [low, high], color='#666666', linewidth=1, alpha=0.8)
                
                # Draw the body (rectangle)
                body_height = abs(close - open_price)
                body_bottom = min(open_price, close)
                
                # Create rectangle for candlestick body
                rect = Rectangle((mdates.date2num(date) - 0.3, body_bottom), 0.6, body_height, 
                               facecolor=color, edgecolor=color, alpha=0.8, linewidth=1)
                self.ax_price.add_patch(rect)
                
        except Exception as e:
            logging.error(f"Error plotting candlesticks: {e}")
            # Fallback to simple line plot
            self.ax_price.plot(dates, closes, color='#00d4ff', linewidth=2, alpha=0.9)
    
    def _plot_volume(self, dates, volumes, closes):
        """Plot volume bars with color coding based on price movement."""
        try:
            if not volumes or all(v == 0 for v in volumes):
                return
                
            # Calculate colors based on price movement
            colors = []
            for i in range(len(closes)):
                if i == 0:
                    colors.append('#666666')  # Neutral for first bar
                else:
                    colors.append('#00ff88' if closes[i] >= closes[i-1] else '#ff4444')
            
            # Plot volume bars
            self.ax_vol.bar(dates, volumes, color=colors, alpha=0.6, width=0.8)
            
            # Format volume axis
            self.ax_vol.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M' if x >= 1e6 else f'{x/1e3:.0f}K'))
            
        except Exception as e:
            logging.error(f"Error plotting volume: {e}")

    def _draw_triangle(self, x_range, highs_range, lows_range, color, ptype):
        """Draw triangle pattern."""
        try:
            # Draw upper trend line
            self.ax_price.plot([x_range[0], x_range[-1]], [highs_range[0], highs_range[-1]], 
                             color=color, linestyle='-', linewidth=2, alpha=0.8)
            
            # Draw lower trend line
            self.ax_price.plot([x_range[0], x_range[-1]], [lows_range[0], lows_range[-1]], 
                             color=color, linestyle='-', linewidth=2, alpha=0.8)
            
            # Add pattern label
            mid_x = x_range[len(x_range)//2]
            mid_y = (max(highs_range) + min(lows_range)) / 2
            self.ax_price.annotate(ptype, xy=(mid_x, mid_y), 
                                 xytext=(0, 10), textcoords='offset points',
                                 ha='center', color=color, fontsize=9, fontweight='bold')
        except Exception as e:
            logging.warning(f"Error drawing triangle: {e}")

    def _draw_expanding_triangle(self, x_range, highs_range, lows_range, color):
        """Draw expanding triangle pattern."""
        try:
            # Draw expanding upper trend line
            self.ax_price.plot([x_range[0], x_range[-1]], [highs_range[0], highs_range[-1]], 
                             color=color, linestyle='-', linewidth=2, alpha=0.8)
            
            # Draw expanding lower trend line
            self.ax_price.plot([x_range[0], x_range[-1]], [lows_range[0], lows_range[-1]], 
                             color=color, linestyle='-', linewidth=2, alpha=0.8)
            
            # Add pattern label
            mid_x = x_range[len(x_range)//2]
            mid_y = (max(highs_range) + min(lows_range)) / 2
            self.ax_price.annotate('Expanding Triangle', xy=(mid_x, mid_y), 
                                 xytext=(0, 10), textcoords='offset points',
                                 ha='center', color=color, fontsize=9, fontweight='bold')
        except Exception as e:
            logging.warning(f"Error drawing expanding triangle: {e}")

    def _draw_rectangle(self, x_range, highs_range, lows_range, key_levels, color, ptype):
        """Draw rectangle/channel pattern."""
        try:
            # Draw horizontal support and resistance lines
            support = min(lows_range)
            resistance = max(highs_range)
            
            self.ax_price.axhline(y=support, xmin=0, xmax=1, color=color, linestyle='-', linewidth=2, alpha=0.8)
            self.ax_price.axhline(y=resistance, xmin=0, xmax=1, color=color, linestyle='-', linewidth=2, alpha=0.8)
            
            # Add pattern label
            mid_x = x_range[len(x_range)//2]
            mid_y = (resistance + support) / 2
            self.ax_price.annotate(ptype, xy=(mid_x, mid_y), 
                                 xytext=(0, 0), textcoords='offset points',
                                 ha='center', color=color, fontsize=9, fontweight='bold')
        except Exception as e:
            logging.warning(f"Error drawing rectangle: {e}")

    def _draw_channel(self, x_range, highs_range, lows_range, color, ptype):
        """Draw channel pattern."""
        try:
            # Draw parallel trend lines
            self.ax_price.plot([x_range[0], x_range[-1]], [highs_range[0], highs_range[-1]], 
                             color=color, linestyle='-', linewidth=2, alpha=0.8)
            self.ax_price.plot([x_range[0], x_range[-1]], [lows_range[0], lows_range[-1]], 
                             color=color, linestyle='-', linewidth=2, alpha=0.8)
            
            # Add pattern label
            mid_x = x_range[len(x_range)//2]
            mid_y = (max(highs_range) + min(lows_range)) / 2
            self.ax_price.annotate(ptype, xy=(mid_x, mid_y), 
                                 xytext=(0, 10), textcoords='offset points',
                                 ha='center', color=color, fontsize=9, fontweight='bold')
        except Exception as e:
            logging.warning(f"Error drawing channel: {e}")

    def _draw_wedge(self, x_range, highs_range, lows_range, color, ptype):
        """Draw wedge pattern."""
        try:
            # Draw converging trend lines
            self.ax_price.plot([x_range[0], x_range[-1]], [highs_range[0], highs_range[-1]], 
                             color=color, linestyle='-', linewidth=2, alpha=0.8)
            self.ax_price.plot([x_range[0], x_range[-1]], [lows_range[0], lows_range[-1]], 
                             color=color, linestyle='-', linewidth=2, alpha=0.8)
            
            # Add pattern label
            mid_x = x_range[len(x_range)//2]
            mid_y = (max(highs_range) + min(lows_range)) / 2
            self.ax_price.annotate(ptype, xy=(mid_x, mid_y), 
                                 xytext=(0, 10), textcoords='offset points',
                                 ha='center', color=color, fontsize=9, fontweight='bold')
        except Exception as e:
            logging.warning(f"Error drawing wedge: {e}")

    def _draw_flag(self, x_range, highs_range, lows_range, color, ptype):
        """Draw flag/pennant pattern."""
        try:
            # Draw flag pole (initial strong move)
            pole_end = len(x_range) // 3
            if 'bull' in ptype.lower():
                self.ax_price.plot([x_range[0], x_range[pole_end]], [lows_range[0], highs_range[pole_end]], 
                                 color=color, linestyle='-', linewidth=3, alpha=0.9)
            else:
                self.ax_price.plot([x_range[0], x_range[pole_end]], [highs_range[0], lows_range[pole_end]], 
                                 color=color, linestyle='-', linewidth=3, alpha=0.9)
            
            # Draw flag (consolidation)
            flag_start = pole_end
            self.ax_price.plot([x_range[flag_start], x_range[-1]], [highs_range[flag_start], highs_range[-1]], 
                             color=color, linestyle='--', linewidth=2, alpha=0.8)
            self.ax_price.plot([x_range[flag_start], x_range[-1]], [lows_range[flag_start], lows_range[-1]], 
                             color=color, linestyle='--', linewidth=2, alpha=0.8)
            
            # Add pattern label
            mid_x = x_range[len(x_range)//2]
            mid_y = (max(highs_range) + min(lows_range)) / 2
            self.ax_price.annotate(ptype, xy=(mid_x, mid_y), 
                                 xytext=(0, 10), textcoords='offset points',
                                 ha='center', color=color, fontsize=9, fontweight='bold')
        except Exception as e:
            logging.warning(f"Error drawing flag: {e}")

    def _draw_head_and_shoulders(self, x_range, highs_range, lows_range, color):
        """Draw head and shoulders pattern."""
        try:
            # Find the three peaks (left shoulder, head, right shoulder)
            if len(highs_range) >= 3:
                # Draw neckline
                neckline_level = min(lows_range)
                self.ax_price.axhline(y=neckline_level, xmin=0, xmax=1, color=color, linestyle='--', linewidth=2, alpha=0.8)
                
                # Mark the peaks
                for i, (x, high) in enumerate(zip(x_range[::len(x_range)//3], highs_range[::len(highs_range)//3])):
                    if i < 3:  # Only mark first 3 peaks
                        peak_names = ['Left Shoulder', 'Head', 'Right Shoulder']
                        self.ax_price.plot(x, high, 'o', color=color, markersize=8, alpha=0.8)
                        self.ax_price.annotate(peak_names[i], xy=(x, high), 
                                             xytext=(0, 15), textcoords='offset points',
                                             ha='center', color=color, fontsize=8)
        except Exception as e:
            logging.warning(f"Error drawing head and shoulders: {e}")
                            
    def _plot_patterns(self, patterns, dates, opens, highs, lows, closes):
        """Overlay key pattern shapes on the price chart using time ranges and levels."""
        if not patterns or not dates:
            logging.info(f"No patterns to plot: patterns={len(patterns) if patterns else 0}, dates={len(dates) if dates else 0}")
            return
        
        logging.info(f"Plotting {len(patterns)} patterns on chart")
        for i, p in enumerate(patterns[:3]):  # Log first 3 patterns for debugging
            logging.info(f"Pattern {i}: {p.get('type', 'Unknown')} - {p.get('start_time', 'No start')} to {p.get('end_time', 'No end')}")

        # Helper to find nearest index for a datetime
        def find_index(ts):
            try:
                if ts is None:
                    return None
                # Convert timestamp to comparable format
                if hasattr(ts, 'timestamp'):
                    target_ts = ts.timestamp()
                elif isinstance(ts, (int, float)):
                    target_ts = ts
                else:
                    return None
                    
                # Convert dates to timestamps for comparison
                date_timestamps = []
                for d in dates:
                    if hasattr(d, 'timestamp'):
                        date_timestamps.append(d.timestamp())
                    elif isinstance(d, (int, float)):
                        date_timestamps.append(d)
                    else:
                        date_timestamps.append(0)
                
                return max(0, min(len(dates) - 1, 
                    min(range(len(dates)), key=lambda i: abs(date_timestamps[i] - target_ts))))
            except Exception as e:
                logging.debug(f"Error in find_index: {e}")
                return None

        for pattern in patterns:
            if not isinstance(pattern, dict):
                continue
                
            ptype = pattern.get('type', 'Unknown')
            if not ptype:
                continue

            # Respect pattern filter toggles
            if (
                ('rectangle' in ptype.lower() and not self.show_rectangles.get()) or
                ('triangle' in ptype.lower() and not self.show_triangles.get()) or
                ('channel' in ptype.lower() and not self.show_channels.get()) or
                ('wedge' in ptype.lower() and not self.show_wedges.get()) or
                ('flag' in ptype.lower() and not self.show_flags.get()) or
                ('pennant' in ptype.lower() and not self.show_flags.get()) or
                ('divergence' in ptype.lower() and not self.show_divergence.get())
            ):
                self._pattern_ranges.append((0, len(dates)-1))
                continue

            # Enhanced color selection based on pattern type
            color = self.pattern_colors['neutral']  # default
            if 'divergence' in ptype.lower():
                color = self.pattern_colors['divergence']
            elif 'channel' in ptype.lower():
                color = self.pattern_colors['channel']
            elif 'wedge' in ptype.lower():
                color = self.pattern_colors['wedge']
            elif 'flag' in ptype.lower() or 'pennant' in ptype.lower():
                color = self.pattern_colors['flag']
            elif 'triangle' in ptype.lower():
                color = self.pattern_colors['triangle']
            elif 'bull' in ptype.lower():
                color = self.pattern_colors['bullish']
            elif 'bear' in ptype.lower():
                color = self.pattern_colors['bearish']

            # Enhanced datetime parsing with multiple format support
            try:
                start_ts = pattern.get('start_time')
                end_ts = pattern.get('end_time')
                start_dt = end_dt = None
                
                # Try multiple datetime formats
                datetime_formats = [
                    '%Y-%m-%d %H:%M:%S',
                    '%Y-%m-%d',
                    '%Y-%m-%dT%H:%M:%S',
                    '%Y-%m-%dT%H:%M:%SZ',
                    '%Y-%m-%d %H:%M:%S.%f'
                ]
                    
                if start_ts:
                    if isinstance(start_ts, str):
                        for fmt in datetime_formats:
                            try:
                                start_dt = datetime.strptime(start_ts, fmt)
                                break
                            except ValueError:
                                continue
                        if start_dt is None:
                            logging.warning(f"Could not parse start_time: {start_ts}")
                    elif hasattr(start_ts, 'strftime'):
                        start_dt = start_ts
                    elif isinstance(start_ts, (int, float)):
                        start_dt = datetime.fromtimestamp(start_ts)
                    
                if end_ts:
                    if isinstance(end_ts, str):
                        for fmt in datetime_formats:
                            try:
                                end_dt = datetime.strptime(end_ts, fmt)
                                break
                            except ValueError:
                                continue
                        if end_dt is None:
                            logging.warning(f"Could not parse end_time: {end_ts}")
                    elif hasattr(end_ts, 'strftime'):
                        end_dt = end_ts
                    elif isinstance(end_ts, (int, float)):
                        end_dt = datetime.fromtimestamp(end_ts)
                
                # Get indices with bounds checking
                s_idx = find_index(start_dt) if start_dt else 0
                e_idx = find_index(end_dt) if end_dt else len(dates) - 1
                
                # If we couldn't parse dates, use pattern index-based approach
                if start_dt is None and end_dt is None:
                    # Use pattern index if available, otherwise use last 20% of data
                    pattern_idx = pattern.get('index', len(dates) - 1)
                    if isinstance(pattern_idx, (int, float)):
                        pattern_idx = int(pattern_idx)
                        s_idx = max(0, pattern_idx - 10)
                        e_idx = min(len(dates) - 1, pattern_idx + 10)
                    else:
                        # Default to last 20% of data for pattern visualization
                        data_len = len(dates)
                        s_idx = max(0, int(data_len * 0.8))
                        e_idx = data_len - 1
                    logging.info(f"Using index-based range for {ptype}: {s_idx} to {e_idx}")
                
                # Ensure valid range with better validation
                if (s_idx is None or e_idx is None or 
                    s_idx >= len(dates) or e_idx >= len(dates) or 
                    s_idx >= e_idx or e_idx - s_idx < 2):  # Need at least 3 points for pattern
                    
                    logging.warning(f"Invalid range for {ptype}: s_idx={s_idx}, e_idx={e_idx}, dates_len={len(dates)}")
                    # Enhanced fallback: place a visible marker with pattern info
                    try:
                        x = dates[-1]
                        y = closes[-1]
                        # Make fallback markers more visible
                        self.ax_price.scatter(
                            x, y, s=120, c=color, marker='*', 
                            alpha=0.9, edgecolors='#ffffff', linewidth=2,
                            zorder=10
                        )
                        # Add pattern label
                        self.ax_price.annotate(
                            f"📍 {ptype}",
                            xy=(x, y),
                            xytext=(20, 20),
                            textcoords='offset points',
                            color=color,
                            fontweight='bold',
                            bbox=dict(boxstyle='round,pad=0.3', facecolor=color, alpha=0.3, edgecolor=color),
                            zorder=11
                        )
                        self._pattern_ranges.append((len(dates)-5, len(dates)-1))
                        logging.info(f"Drew fallback marker for {ptype} at end of chart")
                    except Exception as e:
                        logging.warning(f"Failed to draw fallback marker: {e}")
                    continue
                
                # Ensure we have a minimum range for pattern visualization
                if e_idx - s_idx < 5:
                    # Expand range to at least 5 points
                    center = (s_idx + e_idx) // 2
                    s_idx = max(0, center - 5)
                    e_idx = min(len(dates) - 1, center + 5)
                    logging.info(f"Expanded pattern range for {ptype}: {s_idx} to {e_idx}")

                # Get the data range for this pattern
                try:
                    x_range = dates[s_idx:e_idx+1]
                    highs_range = highs[s_idx:e_idx+1]
                    lows_range = lows[s_idx:e_idx+1]
                    
                    if (not len(x_range) or not len(highs_range) or not len(lows_range) or
                        len(x_range) < 2 or len(highs_range) < 2 or len(lows_range) < 2):
                        logging.warning(f"Insufficient data for {ptype}: x={len(x_range)}, h={len(highs_range)}, l={len(lows_range)}")
                        continue
                    
                    self._pattern_ranges.append((s_idx, e_idx))
                    key_levels = pattern.get('key_levels', {}) or {}

                    # Pattern-specific drawing logic with error handling
                    logging.info(f"Drawing pattern: {ptype} from {s_idx} to {e_idx}")
                    
                    if 'rectangle' in ptype.lower():
                        self._draw_rectangle(x_range, highs_range, lows_range, key_levels, color, ptype)
                    elif 'expanding triangle' in ptype.lower():
                        self._draw_expanding_triangle(x_range, highs_range, lows_range, color)
                    elif 'triangle' in ptype.lower():
                        self._draw_triangle(x_range, highs_range, lows_range, color, ptype)
                    elif 'channel' in ptype.lower():
                        self._draw_channel(x_range, highs_range, lows_range, color, ptype)
                    elif 'wedge' in ptype.lower():
                        self._draw_wedge(x_range, highs_range, lows_range, color, ptype)
                    elif 'flag' in ptype.lower() or 'pennant' in ptype.lower():
                        self._draw_flag(x_range, highs_range, lows_range, color, ptype)
                    elif 'head and shoulders' in ptype.lower():
                        self._draw_head_and_shoulders(x_range, highs_range, lows_range, color)
                    elif 'divergence' in ptype.lower():
                        self._draw_divergence(x_range, highs_range, lows_range, color, ptype)
                    else:
                        # Enhanced default pattern drawing - always draw something visible
                        try:
                            logging.info(f"Drawing default pattern visualization for {ptype}")
                            # Draw pattern boundary with more visibility
                            self.ax_price.fill_between(
                                x_range, highs_range, lows_range, 
                                color=color, alpha=0.25, linewidth=0, zorder=5
                            )
                            # Draw trend lines with better visibility
                            self.ax_price.plot(x_range, highs_range, color=color, linewidth=2.5, alpha=0.95, zorder=6)
                            self.ax_price.plot(x_range, lows_range, color=color, linewidth=2.5, alpha=0.95, zorder=6)
                            
                            # Add start and end markers
                            self.ax_price.scatter([x_range[0], x_range[-1]], [highs_range[0], highs_range[-1]], 
                                                s=80, c=color, marker='o', alpha=0.9, edgecolors='white', linewidth=2, zorder=7)
                            
                            # Enhanced annotation with better positioning
                            mid_price = (highs_range[-1] + lows_range[-1]) / 2
                            self.ax_price.annotate(
                                f"🎯 {ptype}",
                                xy=(x_range[-1], mid_price),
                                xytext=(-100, 20),
                                textcoords='offset points',
                                color='white',
                                fontweight='bold',
                                fontsize=10,
                                bbox=dict(boxstyle='round,pad=0.4', facecolor=color, alpha=0.8, edgecolor='white'),
                                zorder=8
                            )
                            logging.info(f"Successfully drew default pattern for {ptype}")
                        except Exception as e:
                            logging.warning(f"Error drawing default pattern {ptype}: {e}")
                            # Ultimate fallback - just draw a simple line
                            try:
                                self.ax_price.plot(x_range, closes[s_idx:e_idx+1], color=color, linewidth=3, alpha=0.8, zorder=5)
                                logging.info(f"Drew fallback line for {ptype}")
                            except Exception as e2:
                                logging.error(f"Even fallback line failed for {ptype}: {e2}")
                            
                except Exception as e:
                    logging.error(f"Error drawing pattern {ptype}: {e}")
                    # Try to draw at least a marker to show the pattern exists
                    try:
                        x = dates[len(dates)//2]
                        y = closes[len(closes)//2]
                        self.ax_price.scatter(x, y, s=100, c=color, marker='X', alpha=0.8, edgecolors='white', linewidth=2)
                        self.ax_price.annotate(f"⚠️ {ptype}", xy=(x, y), xytext=(10, 10), textcoords='offset points', color=color)
                        logging.info(f"Drew error marker for {ptype}")
                    except:
                        pass
                    continue
            
            except (ValueError, TypeError) as e:
                logging.warning(f"Error parsing pattern dates: {e}")
                continue

            else:
                try:
                    # Generic marker and label
                    x = x_range[-1]
                    y = closes[e_idx]
                    self.ax_price.scatter(x, y, s=80, c=color, marker='o', 
                                        alpha=0.6, edgecolors='#c9d1d9', linewidth=1)
                    self.ax_price.annotate(ptype, xy=(x, y), 
                                         xytext=(-40, 20), textcoords='offset points', 
                                         color=color)
                except Exception as e:
                    logging.warning(f"Error drawing generic pattern: {e}")

    def _on_pattern_select(self, event):
        """Zoom/highlight selected pattern range on the chart."""
        if not self._pattern_ranges:
            return
        try:
            sel = self.pattern_listbox.curselection()
            if not sel:
                return
            idx = sel[0]
            s_idx, e_idx = self._pattern_ranges[min(idx, len(self._pattern_ranges)-1)]
            if self.current_data is None:
                return
            dates = [p.timestamp for p in self.current_data.data]
            self.ax_price.set_xlim(dates[max(0, s_idx-3)], dates[min(len(dates)-1, e_idx+3)])
            self.canvas.draw_idle()
        except Exception as e:
            logging.warning(f"Error selecting pattern: {e}")
            pass
    
    def _update_pattern_list(self, patterns):
        """Update the pattern listbox with enhanced pattern display."""
        try:
            self.pattern_listbox.delete(0, tk.END)
            
            if not patterns:
                self.pattern_listbox.insert(tk.END, "🔍 No patterns detected")
                return
                
            for i, pattern in enumerate(patterns):
                ptype = pattern.get('type', 'Unknown')
                confidence = pattern.get('confidence', '0%')
                direction = pattern.get('direction', 'neutral')
                
                # Enhanced pattern symbols with emojis
                symbol_map = {
                    'rectangle': '📊', 'triangle': '📐', 'channel': '📈',
                    'wedge': '📉', 'flag': '🚩', 'pennant': '🎯',
                    'divergence': '⚡', 'head and shoulders': '👤',
                    'double top': '⛰️', 'double bottom': '🏔️'
                }
                
                symbol = '◆'  # default
                for key, emoji in symbol_map.items():
                    if key in ptype.lower():
                        symbol = emoji
                        break
                
                # Direction indicators
                dir_indicator = {
                    'bullish': '🟢', 'bearish': '🔴', 'neutral': '🟡'
                }.get(direction.lower(), '⚪')
                
                # Confidence bar
                conf_num = float(confidence.rstrip('%'))
                conf_bars = '█' * int(conf_num / 10) + '░' * (10 - int(conf_num / 10))
                
                # Enhanced display text
                display_text = f"{symbol} {ptype:<20} {dir_indicator} [{conf_bars}] {confidence}"
                self.pattern_listbox.insert(tk.END, display_text)
                
        except Exception as e:
            logging.warning(f"Error updating pattern list: {e}")
            self.pattern_listbox.insert(tk.END, "❌ Error loading patterns")

    def export_chart(self):
        """Export chart as image."""
        if not self.current_data:
            messagebox.showwarning("Warning", "No chart to export")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf"), ("SVG files", "*.svg")],
            title="Save Chart As"
        )
        
        if filename:
            try:
                self.fig.savefig(filename, facecolor='#1e1e1e', edgecolor='none', dpi=300)
                messagebox.showinfo("Success", f"Chart saved as {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save chart: {str(e)}")
    
    def _show_error(self, message):
        """Show enhanced error message with better formatting."""
        try:
            # Clear chart and show error state
            if hasattr(self, 'ax_price') and self.ax_price:
                self.ax_price.clear()
                self.ax_price.text(0.5, 0.5, f'❌ Error: {message}', 
                                 transform=self.ax_price.transAxes, 
                                 ha='center', va='center', 
                                 color='#ff4444', fontsize=14, fontweight='bold')
                self.ax_price.set_facecolor('#0f1419')
                self.canvas.draw()
            
            # Also show messagebox
            messagebox.showerror("🚨 CryptVault Error", f"An error occurred:\n\n{message}\n\nPlease try again or check your internet connection.")
        except Exception as e:
            logging.error(f"Error showing error message: {e}")
            messagebox.showerror("Error", message)  # Fallback}")

    def run(self):
        """Start the application."""
        self.root.mainloop()

def main():
    """Main function for standalone execution."""
    app = CryptVaultDesktopCharts()
    app.run()

if __name__ == "__main__":
    main()
