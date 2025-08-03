"""
CryptVault Desktop Charting Platform
Advanced interactive charts with pattern visualization
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import threading
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from cryptvault.analyzer import PatternAnalyzer
from cryptvault.data.package_fetcher import PackageDataFetcher

class CryptVaultDesktopCharts:
    """Desktop charting application for CryptVault"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CryptVault - Advanced Crypto Charts")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize analyzer
        self.analyzer = PatternAnalyzer()
        self.data_fetcher = PackageDataFetcher()
        
        # Current data
        self.current_data = None
        self.current_patterns = []
        self.current_predictions = None
        
        # Setup UI
        self.setup_ui()
        
        # Style configuration
        self.setup_styles()
        
    def setup_styles(self):
        """Setup modern professional theme styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure professional theme
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', foreground='#333333', font=('Arial', 10))
        style.configure('TButton', background='#0078d4', foreground='white', font=('Arial', 10, 'bold'))
        style.configure('TCombobox', background='white', foreground='#333333')
        style.configure('TEntry', background='white', foreground='#333333')
        
        # Button hover effects
        style.map('TButton',
                 background=[('active', '#106ebe'),
                           ('pressed', '#005a9e')])
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control panel
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Symbol input
        ttk.Label(control_frame, text="Symbol:").pack(side=tk.LEFT, padx=(0, 5))
        self.symbol_var = tk.StringVar(value="BTC")
        symbol_entry = ttk.Entry(control_frame, textvariable=self.symbol_var, width=10)
        symbol_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # Days input
        ttk.Label(control_frame, text="Days:").pack(side=tk.LEFT, padx=(0, 5))
        self.days_var = tk.StringVar(value="60")
        days_entry = ttk.Entry(control_frame, textvariable=self.days_var, width=8)
        days_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # Interval selection
        ttk.Label(control_frame, text="Interval:").pack(side=tk.LEFT, padx=(0, 5))
        self.interval_var = tk.StringVar(value="1d")
        interval_combo = ttk.Combobox(control_frame, textvariable=self.interval_var, 
                                    values=["1h", "4h", "1d"], width=8, state="readonly")
        interval_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        # Analyze button
        analyze_btn = ttk.Button(control_frame, text="🚀 Analyze", 
                               command=self.analyze_crypto)
        analyze_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(control_frame, textvariable=self.status_var)
        status_label.pack(side=tk.RIGHT)
        
        # Chart container
        chart_frame = ttk.Frame(main_frame)
        chart_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create matplotlib figure with professional styling
        self.fig = Figure(figsize=(14, 8), facecolor='white')
        self.fig.patch.set_facecolor('white')
        
        # Create subplots with better spacing
        self.ax_main = self.fig.add_subplot(2, 2, 1)  # Main price chart
        self.ax_volume = self.fig.add_subplot(2, 2, 2)  # Volume
        self.ax_patterns = self.fig.add_subplot(2, 2, 3)  # Pattern analysis
        self.ax_ml = self.fig.add_subplot(2, 2, 4)  # ML predictions
        
        # Configure professional subplot styles
        for ax in [self.ax_main, self.ax_volume, self.ax_patterns, self.ax_ml]:
            ax.set_facecolor('white')
            ax.tick_params(colors='#333333', labelsize=9)
            ax.spines['bottom'].set_color('#cccccc')
            ax.spines['top'].set_color('#cccccc')
            ax.spines['right'].set_color('#cccccc')
            ax.spines['left'].set_color('#cccccc')
            ax.grid(True, alpha=0.3, color='#cccccc')
        
        # Embed matplotlib in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add toolbar
        toolbar = NavigationToolbar2Tk(self.canvas, chart_frame)
        toolbar.update()
        
        # Info panel
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Pattern info with professional styling
        self.pattern_text = tk.Text(info_frame, height=6, bg='white', fg='#333333',
                                  font=('Consolas', 9), relief='solid', borderwidth=1)
        self.pattern_text.pack(fill=tk.X)
        
    def analyze_crypto(self):
        """Analyze cryptocurrency in a separate thread"""
        # Start analysis in background thread
        thread = threading.Thread(target=self._analyze_crypto_thread)
        thread.daemon = True
        thread.start()
        
    def _analyze_crypto_thread(self):
        """Background thread for crypto analysis"""
        try:
            symbol = self.symbol_var.get().upper()
            days = int(self.days_var.get())
            interval = self.interval_var.get()
            
            # Update status
            self.root.after(0, lambda: self.status_var.set(f"Analyzing {symbol}..."))
            
            # Fetch data
            self.root.after(0, lambda: self.status_var.set("Fetching data..."))
            data = self.data_fetcher.fetch_data(symbol, days=days, interval=interval)
            
            if not data or len(data.data) < 20:
                self.root.after(0, lambda: messagebox.showerror("Error", "Insufficient data"))
                return
            
            # Perform analysis
            self.root.after(0, lambda: self.status_var.set("Running analysis..."))
            results = self.analyzer.analyze_ticker(symbol, days=days, interval=interval)
            
            if not results['success']:
                self.root.after(0, lambda: messagebox.showerror("Error", results['error']))
                return
            
            # Store results
            self.current_data = data
            self.current_patterns = results.get('patterns', [])
            self.current_predictions = results.get('ml_predictions', {})
            
            # Update charts on main thread
            self.root.after(0, self.update_charts)
            self.root.after(0, lambda: self.status_var.set(f"Analysis complete - {len(self.current_patterns)} patterns found"))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.root.after(0, lambda: self.status_var.set("Analysis failed"))
    
    def update_charts(self):
        """Update all charts with current data"""
        if not self.current_data:
            print("No data available for charting")
            return
        
        print(f"Updating charts with {len(self.current_data.data)} data points")
        
        # Clear all subplots
        for ax in [self.ax_main, self.ax_volume, self.ax_patterns, self.ax_ml]:
            ax.clear()
            ax.set_facecolor('white')
            ax.tick_params(colors='#333333', labelsize=9)
            ax.grid(True, alpha=0.3, color='#cccccc')
        
        # Prepare data
        data_points = self.current_data.data
        dates = [point.timestamp for point in data_points]
        prices = [point.close for point in data_points]
        volumes = [point.volume for point in data_points]
        highs = [point.high for point in data_points]
        lows = [point.low for point in data_points]
        opens = [point.open for point in data_points]
        
        # 1. Main Price Chart with professional colors
        self.ax_main.plot(dates, prices, color='#0078d4', linewidth=2, label='Price')
        self.ax_main.fill_between(dates, prices, alpha=0.2, color='#0078d4')
        
        # Add candlestick-like visualization with professional colors
        for i, (date, open_p, high, low, close) in enumerate(zip(dates, opens, highs, lows, prices)):
            color = '#107c10' if close >= open_p else '#d13438'  # Green for up, red for down
            self.ax_main.plot([date, date], [low, high], color=color, alpha=0.7, linewidth=1)
        
        # Add pattern markers
        for pattern in self.current_patterns[:5]:  # Show top 5 patterns
            if 'start_index' in pattern and 'end_index' in pattern:
                start_idx = max(0, min(pattern['start_index'], len(dates)-1))
                end_idx = max(0, min(pattern['end_index'], len(dates)-1))
                
                pattern_color = self.get_pattern_color(pattern['type'])
                self.ax_main.axvspan(dates[start_idx], dates[end_idx], 
                                   alpha=0.2, color=pattern_color)
                
                # Add pattern label
                mid_idx = (start_idx + end_idx) // 2
                if mid_idx < len(dates):
                    self.ax_main.annotate(pattern['type'], 
                                        xy=(dates[mid_idx], prices[mid_idx]),
                                        xytext=(10, 10), textcoords='offset points',
                                        color=pattern_color, fontsize=8,
                                        bbox=dict(boxstyle='round,pad=0.3', 
                                                facecolor=pattern_color, alpha=0.7))
        
        self.ax_main.set_title(f'{self.symbol_var.get()} Price Chart', color='#333333', fontsize=14, fontweight='bold')
        self.ax_main.set_ylabel('Price ($)', color='#333333', fontsize=11)
        self.ax_main.legend(loc='upper left')
        
        # Format price labels
        current_price = prices[-1] if prices else 0
        self.ax_main.text(0.02, 0.98, f'Current: ${current_price:,.2f}', 
                         transform=self.ax_main.transAxes, fontsize=12, fontweight='bold',
                         verticalalignment='top', bbox=dict(boxstyle='round', facecolor='#0078d4', alpha=0.8, edgecolor='none'),
                         color='white')
        
        # 2. Volume Chart with professional styling
        self.ax_volume.bar(dates, volumes, color='#605e5c', alpha=0.7, width=0.8)
        self.ax_volume.set_title('Trading Volume', color='#333333', fontsize=12, fontweight='bold')
        self.ax_volume.set_ylabel('Volume', color='#333333', fontsize=11)
        
        # Format volume labels
        avg_volume = np.mean(volumes) if volumes else 0
        self.ax_volume.text(0.02, 0.98, f'Avg: {avg_volume:,.0f}', 
                           transform=self.ax_volume.transAxes, fontsize=10,
                           verticalalignment='top', bbox=dict(boxstyle='round', facecolor='#605e5c', alpha=0.8),
                           color='white')
        
        # 3. Pattern Analysis Chart
        pattern_types = {}
        for pattern in self.current_patterns:
            ptype = pattern['type']
            confidence = float(pattern['confidence'].rstrip('%'))
            if ptype not in pattern_types:
                pattern_types[ptype] = []
            pattern_types[ptype].append(confidence)
        
        if pattern_types:
            pattern_names = list(pattern_types.keys())[:8]  # Top 8 patterns
            avg_confidences = [np.mean(pattern_types[name]) for name in pattern_names]
            
            bars = self.ax_patterns.barh(pattern_names, avg_confidences, 
                                       color=['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', 
                                             '#feca57', '#ff9ff3', '#54a0ff', '#5f27cd'][:len(pattern_names)])
            
            # Add confidence labels
            for i, (bar, conf) in enumerate(zip(bars, avg_confidences)):
                self.ax_patterns.text(conf + 1, i, f'{conf:.1f}%', 
                                    va='center', color='white', fontsize=9)
        
        self.ax_patterns.set_title('Pattern Confidence', color='white', fontsize=12)
        self.ax_patterns.set_xlabel('Confidence (%)', color='white')
        self.ax_patterns.set_xlim(0, 100)
        self.ax_patterns.grid(True, alpha=0.3)
        
        # 4. ML Predictions Chart
        if self.current_predictions and 'trend_forecast' in self.current_predictions:
            trend_data = self.current_predictions['trend_forecast']
            
            # Create prediction visualization
            future_dates = [dates[-1] + timedelta(days=i) for i in range(1, 8)]
            
            # Simple trend projection based on current trend
            last_price = prices[-1]
            trend_strength = float(trend_data.get('trend_strength', '50').rstrip('%')) / 100
            trend_direction = 1 if trend_data.get('trend_7d', 'sideways') == 'bullish' else -1 if trend_data.get('trend_7d', 'sideways') == 'bearish' else 0
            
            predicted_prices = []
            for i in range(7):
                # Simple prediction model
                change = trend_direction * trend_strength * 0.02 * (i + 1)  # 2% max change per day
                predicted_price = last_price * (1 + change)
                predicted_prices.append(predicted_price)
            
            # Plot historical prices
            self.ax_ml.plot(dates[-30:], prices[-30:], color='#00ff88', linewidth=2, label='Historical')
            
            # Plot predictions
            all_dates = dates[-1:] + future_dates
            all_prices = prices[-1:] + predicted_prices
            self.ax_ml.plot(all_dates, all_prices, color='#ff6b6b', linewidth=2, 
                          linestyle='--', label='Prediction')
            
            # Add confidence band
            confidence_band = [p * 0.05 for p in predicted_prices]  # 5% confidence band
            upper_band = [p + c for p, c in zip(predicted_prices, confidence_band)]
            lower_band = [p - c for p, c in zip(predicted_prices, confidence_band)]
            
            self.ax_ml.fill_between(future_dates, upper_band, lower_band, 
                                  alpha=0.3, color='#ff6b6b')
        
        self.ax_ml.set_title('ML Predictions (7 days)', color='white', fontsize=12)
        self.ax_ml.set_ylabel('Price ($)', color='white')
        self.ax_ml.legend()
        self.ax_ml.grid(True, alpha=0.3)
        
        # Adjust layout
        self.fig.tight_layout()
        self.canvas.draw()
        
        # Update pattern info text
        self.update_pattern_info()
    
    def get_pattern_color(self, pattern_type):
        """Get color for pattern type"""
        color_map = {
            'Double Bottom': '#00ff88',
            'Double Top': '#ff4444',
            'Triple Bottom': '#00ff88',
            'Triple Top': '#ff4444',
            'Head and Shoulders': '#ff4444',
            'Inverse Head and Shoulders': '#00ff88',
            'Ascending Triangle': '#4488ff',
            'Descending Triangle': '#ff8844',
            'Expanding Triangle': '#8844ff',
            'Bullish Divergence': '#00ff88',
            'Bearish Divergence': '#ff4444',
            'Hidden Bullish Divergence': '#44ff88',
            'Hidden Bearish Divergence': '#ff8888'
        }
        return color_map.get(pattern_type, '#ffffff')
    
    def update_pattern_info(self):
        """Update pattern information text"""
        self.pattern_text.delete(1.0, tk.END)
        
        if not self.current_patterns:
            self.pattern_text.insert(tk.END, "No patterns detected.")
            return
        
        info_text = f"📊 PATTERN ANALYSIS - {len(self.current_patterns)} patterns found\n"
        info_text += "=" * 60 + "\n\n"
        
        for i, pattern in enumerate(self.current_patterns[:10], 1):
            confidence = pattern['confidence']
            ptype = pattern['type']
            
            # Pattern emoji
            emoji = "🔺" if "Bullish" in ptype or "Bottom" in ptype else "🔻" if "Bearish" in ptype or "Top" in ptype else "⚡"
            
            info_text += f"{i:2d}. {emoji} {ptype:<25} [{confidence:>6}]\n"
            
            if 'target_price' in pattern:
                info_text += f"     Target: ${pattern['target_price']:.2f}\n"
            
            if 'description' in pattern:
                info_text += f"     {pattern['description'][:50]}...\n"
            
            info_text += "\n"
        
        # Add ML predictions info
        if self.current_predictions:
            info_text += "\n🧠 ML PREDICTIONS\n"
            info_text += "=" * 30 + "\n"
            
            if 'trend_forecast' in self.current_predictions:
                trend = self.current_predictions['trend_forecast']
                info_text += f"7-day Trend: {trend.get('trend_7d', 'Unknown')}\n"
                info_text += f"Strength: {trend.get('trend_strength', 'Unknown')}\n"
            
            if 'ensemble_accuracy' in self.current_predictions:
                accuracy = self.current_predictions['ensemble_accuracy']
                info_text += f"Model Accuracy: {accuracy:.1%}\n"
        
        self.pattern_text.insert(tk.END, info_text)
    
    def run(self):
        """Start the desktop application"""
        # Load initial data
        self.analyze_crypto()
        
        # Start main loop
        self.root.mainloop()

def main():
    """Main function to run desktop charts"""
    try:
        app = CryptVaultDesktopCharts()
        app.run()
    except Exception as e:
        print(f"Error starting desktop charts: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()