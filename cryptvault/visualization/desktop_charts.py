"""
Desktop Chart Application for CryptVault
Interactive matplotlib-based charts with pattern visualization

Made with ❤️ by the MeridianAlgo Algorithmic Research Team (Quantum Meridian)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
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
        self.root.title("CryptVault Desktop Charts")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1e1e1e')
        
        # Initialize analyzer
        self.analyzer = PatternAnalyzer()
        
        # Data storage
        self.current_data = None
        self.current_patterns = []
        self.current_symbol = "BTC"
        
        # Pattern colors and symbols
        self.pattern_colors = {
            'bullish': '#00ff88',
            'bearish': '#ff4444', 
            'neutral': '#ffaa00',
            'divergence': '#00aaff',
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
        
    def setup_ui(self):
        """Setup the user interface."""
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', background='#1e1e1e', foreground='white')
        style.configure('TButton', background='#333333', foreground='white')
        style.configure('TEntry', fieldbackground='#333333', foreground='white')
        style.configure('TCombobox', fieldbackground='#333333', foreground='white')
        
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
        
        # Chart frame
        chart_frame = ttk.Frame(main_frame)
        chart_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(12, 8), facecolor='#1e1e1e')
        self.ax = self.fig.add_subplot(111, facecolor='#1e1e1e')
        self.ax.tick_params(colors='white')
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['top'].set_color('white')
        self.ax.spines['right'].set_color('white')
        self.ax.spines['left'].set_color('white')
        
        # Canvas
        self.canvas = FigureCanvasTkAgg(self.fig, chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Pattern info frame
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Pattern listbox
        ttk.Label(info_frame, text="Detected Patterns:").pack(anchor=tk.W)
        self.pattern_listbox = tk.Listbox(info_frame, height=6, bg='#333333', fg='white',
                                        selectbackground='#555555')
        self.pattern_listbox.pack(fill=tk.X, pady=(5, 0))
        
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
            self.ax.clear()
            self.ax.set_facecolor('#1e1e1e')
            self.ax.tick_params(colors='white')
            
            # Get data
            patterns = results.get('patterns', [])
            ticker_info = results.get('ticker_info', {})
            current_price = ticker_info.get('current_price', 0)
            
            # Update pattern list
            self._update_pattern_list(patterns)
            
            # Get historical data for charting
            from cryptvault.data.package_fetcher import PackageDataFetcher
            data_fetcher = PackageDataFetcher()
            raw_data = data_fetcher.fetch_historical_data(symbol, days=60, interval='1d')
            
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
            volumes = [point.volume for point in data_points] if hasattr(data_points[0], 'volume') else [0] * len(data_points)
            
            # Plot candlestick chart
            self._plot_candlesticks(dates, opens, highs, lows, closes)
            
            # Plot patterns
            if patterns:
                self._plot_patterns(patterns, dates, closes)
            
            # Add price line
            self.ax.plot(dates, closes, color='#00aaff', linewidth=1, alpha=0.7, label='Price')
            
            # Format chart
            self.ax.set_title(f"{symbol} - {len(patterns)} Patterns Detected", 
                            color='white', fontsize=14, fontweight='bold')
            self.ax.set_xlabel("Date", color='white')
            self.ax.set_ylabel("Price (USD)", color='white')
            
            # Format x-axis
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            self.ax.xaxis.set_major_locator(mdates.DayLocator(interval=7))
            self.fig.autofmt_xdate()
            
            # Add legend
            self.ax.legend(loc='upper left', facecolor='#333333', edgecolor='white')
            
            # Add current price annotation
            if current_price > 0:
                self.ax.annotate(f'${current_price:,.2f}', 
                               xy=(dates[-1], current_price),
                               xytext=(10, 10), textcoords='offset points',
                               bbox=dict(boxstyle='round,pad=0.3', facecolor='#333333', edgecolor='white'),
                               color='white', fontweight='bold')
            
            # Update canvas
            self.canvas.draw()
            
            # Update status
            analysis_time = results.get('analysis_time_seconds', 0)
            self.status_var.set(f"Analysis complete - {len(patterns)} patterns found in {analysis_time:.2f}s")
            
            # Store current data
            self.current_data = raw_data
            self.current_patterns = patterns
            self.current_symbol = symbol
            
        except Exception as e:
            self._show_error(f"Chart update error: {str(e)}")
    
    def _plot_candlesticks(self, dates, opens, highs, lows, closes):
        """Plot candlestick chart."""
        for i, (date, open_price, high, low, close) in enumerate(zip(dates, opens, highs, lows, closes)):
            # Determine color
            color = '#00ff88' if close >= open_price else '#ff4444'
            
            # Draw wick
            self.ax.plot([date, date], [low, high], color='white', linewidth=1, alpha=0.8)
            
            # Draw body
            body_height = abs(close - open_price)
            body_bottom = min(open_price, close)
            
            if body_height > 0:
                rect = plt.Rectangle((date - timedelta(hours=6), body_bottom), 
                                   timedelta(hours=12), body_height,
                                   facecolor=color, edgecolor='white', alpha=0.8)
                self.ax.add_patch(rect)
            else:
                # Doji - draw horizontal line
                self.ax.plot([date - timedelta(hours=6), date + timedelta(hours=6)], 
                           [close, close], color='white', linewidth=2)
    
    def _plot_patterns(self, patterns, dates, closes):
        """Plot pattern overlays on the chart."""
        for i, pattern in enumerate(patterns):
            pattern_type = pattern.get('type', 'Unknown')
            confidence = float(pattern.get('confidence', '0').rstrip('%')) / 100
            
            # Get pattern color
            if 'bullish' in pattern_type.lower():
                color = self.pattern_colors['bullish']
            elif 'bearish' in pattern_type.lower():
                color = self.pattern_colors['bearish']
            elif 'divergence' in pattern_type.lower():
                color = self.pattern_colors['divergence']
            elif any(harmonic in pattern_type.lower() for harmonic in ['gartley', 'butterfly', 'abcd']):
                color = self.pattern_colors['harmonic']
            else:
                color = self.pattern_colors['neutral']
            
            # Get pattern symbol
            symbol = self.pattern_symbols.get(pattern_type, '⭐')
            
            # Calculate position (spread patterns across the chart)
            if len(patterns) > 1:
                x_pos = len(dates) // (len(patterns) + 1) * (i + 1)
            else:
                x_pos = len(dates) // 2
            
            if x_pos < len(dates):
                y_pos = closes[x_pos]
                
                # Add pattern marker
                self.ax.scatter(dates[x_pos], y_pos, s=200, c=color, marker='o', 
                              alpha=0.8, edgecolors='white', linewidth=2)
                
                # Add pattern symbol
                self.ax.annotate(symbol, xy=(dates[x_pos], y_pos), 
                               xytext=(0, 20), textcoords='offset points',
                               ha='center', va='bottom', fontsize=16, color=color,
                               bbox=dict(boxstyle='round,pad=0.3', facecolor='#333333', 
                                       edgecolor=color, alpha=0.8))
                
                # Add pattern name and confidence
                label = f"{pattern_type}\n{confidence:.1%}"
                self.ax.annotate(label, xy=(dates[x_pos], y_pos), 
                               xytext=(0, -40), textcoords='offset points',
                               ha='center', va='top', fontsize=10, color='white',
                               bbox=dict(boxstyle='round,pad=0.3', facecolor='#333333', 
                                       edgecolor=color, alpha=0.8))
    
    def _update_pattern_list(self, patterns):
        """Update the pattern listbox."""
        self.pattern_listbox.delete(0, tk.END)
        
        if not patterns:
            self.pattern_listbox.insert(tk.END, "No patterns detected")
            return
        
        # Sort patterns by confidence
        sorted_patterns = sorted(patterns, key=lambda p: float(p.get('confidence', '0').rstrip('%')), reverse=True)
        
        for pattern in sorted_patterns:
            pattern_type = pattern.get('type', 'Unknown')
            confidence = pattern.get('confidence', '0%')
            symbol = self.pattern_symbols.get(pattern_type, '⭐')
            
            # Format pattern entry
            entry = f"{symbol} {pattern_type} - {confidence}"
            self.pattern_listbox.insert(tk.END, entry)
    
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
        """Show error message."""
        self.status_var.set(f"Error: {message}")
        messagebox.showerror("Error", message)
    
    def run(self):
        """Start the application."""
        self.root.mainloop()

def main():
    """Main function for standalone execution."""
    app = CryptVaultDesktopCharts()
    app.run()

if __name__ == "__main__":
    main()
