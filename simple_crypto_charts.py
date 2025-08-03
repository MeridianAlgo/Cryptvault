#!/usr/bin/env python3
"""
Simple CryptVault Desktop Charts
A simplified version that focuses on working charts
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from datetime import datetime
import threading

# Import CryptVault components
from cryptvault.analyzer import PatternAnalyzer

class SimpleCryptoCharts:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CryptVault - Crypto Charts")
        self.root.geometry("1200x800")
        self.root.configure(bg='white')
        
        # Initialize analyzer
        self.analyzer = PatternAnalyzer()
        
        # Data storage
        self.current_data = None
        self.current_patterns = []
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Control panel
        control_frame = tk.Frame(self.root, bg='white', pady=10)
        control_frame.pack(fill=tk.X, padx=10)
        
        # Symbol input
        tk.Label(control_frame, text="Symbol:", bg='white', font=('Arial', 11)).pack(side=tk.LEFT, padx=(0, 5))
        self.symbol_var = tk.StringVar(value="BTC")
        symbol_entry = tk.Entry(control_frame, textvariable=self.symbol_var, width=8, font=('Arial', 11))
        symbol_entry.pack(side=tk.LEFT, padx=(0, 15))
        
        # Days input
        tk.Label(control_frame, text="Days:", bg='white', font=('Arial', 11)).pack(side=tk.LEFT, padx=(0, 5))
        self.days_var = tk.StringVar(value="60")
        days_entry = tk.Entry(control_frame, textvariable=self.days_var, width=6, font=('Arial', 11))
        days_entry.pack(side=tk.LEFT, padx=(0, 15))
        
        # Analyze button
        analyze_btn = tk.Button(control_frame, text="📊 Analyze Crypto", 
                              command=self.analyze_crypto, bg='#0078d4', fg='white',
                              font=('Arial', 11, 'bold'), padx=20, pady=5)
        analyze_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        # Status
        self.status_var = tk.StringVar(value="Ready to analyze")
        status_label = tk.Label(control_frame, textvariable=self.status_var, 
                              bg='white', font=('Arial', 10), fg='#666666')
        status_label.pack(side=tk.RIGHT)
        
        # Chart area
        chart_frame = tk.Frame(self.root, bg='white')
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(12, 6), facecolor='white')
        
        # Create main chart
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('white')
        self.ax.grid(True, alpha=0.3)
        
        # Embed in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Info panel
        info_frame = tk.Frame(self.root, bg='white')
        info_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.info_text = tk.Text(info_frame, height=8, bg='#f8f9fa', fg='#333333',
                               font=('Consolas', 9), relief='solid', borderwidth=1)
        self.info_text.pack(fill=tk.X)
        
        # Load initial data
        self.show_welcome_message()
    
    def show_welcome_message(self):
        """Show welcome message"""
        self.ax.clear()
        self.ax.text(0.5, 0.5, '📊 CryptVault Charts\n\nEnter a symbol (BTC, ETH, ADA) and click Analyze', 
                    ha='center', va='center', transform=self.ax.transAxes,
                    fontsize=16, color='#666666')
        self.ax.set_title('Welcome to CryptVault Desktop Charts', fontsize=18, fontweight='bold', color='#333333')
        self.canvas.draw()
        
        welcome_text = """
🚀 Welcome to CryptVault Desktop Charts!

📈 Features:
• Real-time cryptocurrency price charts
• Advanced pattern recognition
• ML-powered predictions
• Professional visualization

💡 How to use:
1. Enter a cryptocurrency symbol (BTC, ETH, ADA, etc.)
2. Choose number of days (30-90 recommended)
3. Click "Analyze Crypto" to generate charts

🎯 Supported symbols: BTC, ETH, ADA, DOT, LINK, LTC, XRP, BCH, BNB, SOL
        """
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, welcome_text)
    
    def analyze_crypto(self):
        """Analyze cryptocurrency"""
        thread = threading.Thread(target=self._analyze_thread)
        thread.daemon = True
        thread.start()
    
    def _analyze_thread(self):
        """Background analysis thread"""
        try:
            symbol = self.symbol_var.get().upper()
            days = int(self.days_var.get())
            
            print(f"Starting analysis for {symbol} with {days} days")
            
            # Update status
            self.root.after(0, lambda: self.status_var.set(f"Analyzing {symbol}..."))
            
            # Perform analysis
            print("Calling analyzer.analyze_ticker...")
            results = self.analyzer.analyze_ticker(symbol, days=days, interval='1d')
            print(f"Analysis results: {results}")
            
            if not results['success']:
                error_msg = results.get('error', 'Unknown error')
                print(f"Analysis failed: {error_msg}")
                self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
                self.root.after(0, lambda: self.status_var.set("Analysis failed"))
                return
            
            # Store results
            self.current_data = results.get('price_data')
            self.current_patterns = results.get('patterns', [])
            
            print(f"Data points: {len(self.current_data.data) if self.current_data else 0}")
            print(f"Patterns found: {len(self.current_patterns)}")
            
            # Update UI
            self.root.after(0, self.update_chart)
            self.root.after(0, lambda: self.status_var.set(f"✅ Analysis complete - {len(self.current_patterns)} patterns found"))
            
        except Exception as e:
            print(f"Exception in analysis thread: {e}")
            import traceback
            traceback.print_exc()
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.root.after(0, lambda: self.status_var.set("Analysis failed"))
    
    def update_chart(self):
        """Update the chart with current data"""
        print("update_chart called")
        
        if not self.current_data:
            print("No current_data available")
            return
            
        if len(self.current_data.data) == 0:
            print("current_data.data is empty")
            return
        
        print(f"Updating chart with {len(self.current_data.data)} data points")
        
        # Clear chart
        self.ax.clear()
        
        # Extract data
        data_points = self.current_data.data
        dates = [point.timestamp for point in data_points]
        prices = [point.close for point in data_points]
        
        print(f"Dates range: {dates[0]} to {dates[-1]}")
        print(f"Price range: ${min(prices):.2f} to ${max(prices):.2f}")
        
        # Plot main price line
        self.ax.plot(dates, prices, color='#0078d4', linewidth=2, label='Price')
        self.ax.fill_between(dates, prices, alpha=0.2, color='#0078d4')
        
        # Add pattern highlights
        colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57']
        for i, pattern in enumerate(self.current_patterns[:5]):
            if 'start_index' in pattern and 'end_index' in pattern:
                start_idx = max(0, min(pattern['start_index'], len(dates)-1))
                end_idx = max(0, min(pattern['end_index'], len(dates)-1))
                
                color = colors[i % len(colors)]
                self.ax.axvspan(dates[start_idx], dates[end_idx], 
                              alpha=0.3, color=color, label=pattern['type'])
        
        # Styling
        symbol = self.symbol_var.get().upper()
        current_price = prices[-1] if prices else 0
        
        self.ax.set_title(f'{symbol} Price Chart - ${current_price:,.2f}', 
                         fontsize=16, fontweight='bold', color='#333333')
        self.ax.set_ylabel('Price ($)', fontsize=12, color='#333333')
        self.ax.grid(True, alpha=0.3)
        self.ax.legend(loc='upper left')
        
        # Format dates
        self.fig.autofmt_xdate()
        
        # Tight layout
        self.fig.tight_layout()
        self.canvas.draw()
        
        # Update info
        self.update_info()
    
    def update_info(self):
        """Update information panel"""
        self.info_text.delete(1.0, tk.END)
        
        symbol = self.symbol_var.get().upper()
        
        if not self.current_data:
            self.info_text.insert(tk.END, "No data available")
            return
        
        # Basic info
        data_points = self.current_data.data
        current_price = data_points[-1].close if data_points else 0
        
        info_text = f"📊 {symbol} ANALYSIS RESULTS\n"
        info_text += "=" * 50 + "\n\n"
        info_text += f"💰 Current Price: ${current_price:,.2f}\n"
        info_text += f"📈 Data Points: {len(data_points)}\n"
        info_text += f"🔍 Patterns Found: {len(self.current_patterns)}\n\n"
        
        # Pattern details
        if self.current_patterns:
            info_text += "🎯 DETECTED PATTERNS:\n"
            info_text += "-" * 30 + "\n"
            
            for i, pattern in enumerate(self.current_patterns[:8], 1):
                confidence = pattern.get('confidence', 'Unknown')
                ptype = pattern.get('type', 'Unknown')
                
                # Pattern emoji
                if 'Bullish' in ptype or 'Bottom' in ptype:
                    emoji = "🟢"
                elif 'Bearish' in ptype or 'Top' in ptype:
                    emoji = "🔴"
                else:
                    emoji = "🟡"
                
                info_text += f"{i:2d}. {emoji} {ptype:<20} [{confidence:>6}]\n"
                
                if 'target_price' in pattern:
                    info_text += f"     → Target: ${pattern['target_price']:.2f}\n"
                
                info_text += "\n"
        else:
            info_text += "No patterns detected in current timeframe.\n"
            info_text += "Try increasing the number of days for better pattern detection.\n"
        
        self.info_text.insert(tk.END, info_text)
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    """Main function"""
    try:
        print("🚀 Starting CryptVault Desktop Charts...")
        app = SimpleCryptoCharts()
        app.run()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()