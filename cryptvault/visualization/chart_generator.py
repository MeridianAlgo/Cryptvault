"""
CryptVault Chart Generator - Professional Charts with Pattern Overlays

Creates beautiful charts with:
- Candlestick visualization
- Pattern overlays (properly drawn!)
- Support/resistance lines
- Technical indicators
- Volume bars
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle, FancyBboxPatch
import numpy as np
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Set dark theme
plt.style.use('dark_background')


class ChartGenerator:
    """Generate professional charts with pattern overlays."""
    
    def __init__(self):
        self.colors = {
            'bullish': '#26a69a',      # Teal green
            'bearish': '#ef5350',      # Red
            'neutral': '#ffa726',      # Orange
            'volume_up': '#26a69a44',  # Transparent teal
            'volume_down': '#ef535044', # Transparent red
            'background': '#1e222d',   # Dark blue-gray
            'grid': '#2a2e39',         # Slightly lighter
            'text': '#d1d4dc',         # Light gray
            'pattern_bullish': '#00ff88',  # Bright green for patterns
            'pattern_bearish': '#ff4466',  # Bright red for patterns
            'pattern_neutral': '#ffaa00'   # Bright orange for patterns
        }
    
    def generate(self, df: pd.DataFrame, patterns: List[Dict], 
                symbol: str, prediction: Dict = None,
                save_path: str = None) -> None:
        """
        Generate chart with pattern overlays.
        
        Args:
            df: DataFrame with OHLCV data
            patterns: List of detected patterns
            symbol: Asset symbol
            prediction: Optional prediction data
            save_path: Path to save chart (None = display)
        """
        # Normalize columns
        df = self._normalize_columns(df)
        
        # Create figure
        fig = plt.figure(figsize=(16, 10), facecolor=self.colors['background'])
        
        # Create subplots
        gs = fig.add_gridspec(4, 1, height_ratios=[3, 1, 1, 0.5], hspace=0.05)
        ax_price = fig.add_subplot(gs[0])
        ax_volume = fig.add_subplot(gs[1], sharex=ax_price)
        ax_rsi = fig.add_subplot(gs[2], sharex=ax_price)
        ax_macd = fig.add_subplot(gs[3], sharex=ax_price)
        
        # Get dates
        if 'Date' in df.columns:
            dates = pd.to_datetime(df['Date'])
        elif df.index.name == 'Date' or isinstance(df.index, pd.DatetimeIndex):
            dates = df.index
        else:
            dates = pd.date_range(end=datetime.now(), periods=len(df), freq='D')
        
        # Plot candlesticks
        self._plot_candlesticks(ax_price, dates, df)
        
        # Plot patterns
        self._plot_patterns(ax_price, dates, df, patterns)
        
        # Plot volume
        self._plot_volume(ax_volume, dates, df)
        
        # Plot RSI
        self._plot_rsi(ax_rsi, dates, df)
        
        # Plot MACD
        self._plot_macd(ax_macd, dates, df)
        
        # Add title and styling
        self._style_chart(fig, ax_price, ax_volume, ax_rsi, ax_macd, 
                         symbol, prediction, patterns)
        
        # Format x-axis with date labels on bottom plot
        self._format_xaxis_dates(ax_macd, dates, len(df))
        
        # Save or show
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight', 
                       facecolor=self.colors['background'], edgecolor='none')
            logger.info(f"Chart saved to: {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def _normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize column names."""
        column_map = {
            'open': 'Open', 'high': 'High', 'low': 'Low',
            'close': 'Close', 'volume': 'Volume',
            'OPEN': 'Open', 'HIGH': 'High', 'LOW': 'Low',
            'CLOSE': 'Close', 'VOLUME': 'Volume'
        }
        return df.rename(columns=column_map)
    
    def _plot_candlesticks(self, ax, dates, df):
        """Plot candlestick chart using integer indices for proper alignment."""
        width = 0.6  # Slightly thinner candles
        
        # Use integer indices for x-axis
        indices = np.arange(len(df))
        
        for i in indices:
            open_price = df['Open'].iloc[i]
            close_price = df['Close'].iloc[i]
            high_price = df['High'].iloc[i]
            low_price = df['Low'].iloc[i]
            
            color = self.colors['bullish'] if close_price >= open_price else self.colors['bearish']
            
            # Draw wick (high-low line) - thinner
            ax.plot([i, i], [low_price, high_price], 
                   color=color, linewidth=1, alpha=0.6, zorder=1)
            
            # Draw body (open-close rectangle)
            body_bottom = min(open_price, close_price)
            body_height = abs(close_price - open_price)
            if body_height < 0.001:  # Doji
                body_height = high_price * 0.001
            
            rect = Rectangle(
                (i - width/2, body_bottom),
                width, body_height,
                facecolor=color, edgecolor=color, alpha=1.0, zorder=2,
                linewidth=0
            )
            ax.add_patch(rect)
        
        # Set x-axis limits to show all data
        ax.set_xlim(-1, len(df))
        ax.set_ylabel('Price (USD)', color=self.colors['text'], fontsize=10, fontweight='bold')
    
    def _plot_patterns(self, ax, dates, df, patterns):
        """Plot pattern overlays on chart with proper shapes - show more patterns."""
        if not patterns:
            return

        # Get diverse patterns (not all the same type) - increased limit
        diverse_patterns = []
        seen_types = set()
        
        # Sort by confidence
        sorted_patterns = sorted(patterns, key=lambda x: x.get('confidence', 0), reverse=True)
        
        # Pick top patterns with diversity - increased from 5 to 10
        for pattern in sorted_patterns:
            ptype = pattern.get('pattern_type', 'Unknown')
            # Allow up to 2 of each type
            type_count = sum(1 for p in diverse_patterns if p.get('pattern_type') == ptype)
            if type_count < 2 or len(diverse_patterns) < 5:
                diverse_patterns.append(pattern)
                seen_types.add(ptype)
            if len(diverse_patterns) >= 10:  # Increased from 5
                break
        
        for pattern in diverse_patterns:
            start_idx = pattern.get('start_index', 0)
            end_idx = pattern.get('end_index', len(df) - 1)
            pattern_type = pattern.get('pattern_type', 'Unknown')
            confidence = pattern.get('confidence', 50)
            direction = pattern.get('direction', 'neutral')
            
            # Ensure valid indices
            start_idx = max(0, min(start_idx, len(df) - 1))
            end_idx = max(start_idx + 1, min(end_idx, len(df) - 1))
            
            # Get color based on direction
            if direction == 'bullish':
                color = self.colors['pattern_bullish']
            elif direction == 'bearish':
                color = self.colors['pattern_bearish']
            else:
                color = self.colors['pattern_neutral']
            
            # Get pattern data
            pattern_highs = df['High'].iloc[start_idx:end_idx+1]
            pattern_lows = df['Low'].iloc[start_idx:end_idx+1]
            
            if len(pattern_highs) < 2:
                continue
            
            # Draw pattern based on type with VERY visible styling
            pattern_type_lower = pattern_type.lower()
            
            if 'triangle' in pattern_type_lower or 'wedge' in pattern_type_lower:
                self._draw_triangle_wedge(ax, start_idx, end_idx, pattern_highs, pattern_lows, color)
            elif 'rectangle' in pattern_type_lower or 'channel' in pattern_type_lower:
                self._draw_rectangle_channel(ax, start_idx, end_idx, pattern_highs, pattern_lows, color)
            elif 'flag' in pattern_type_lower or 'pennant' in pattern_type_lower:
                self._draw_flag_pennant(ax, start_idx, end_idx, pattern_highs, pattern_lows, color)
            elif 'head' in pattern_type_lower and 'shoulder' in pattern_type_lower:
                self._draw_head_shoulders(ax, start_idx, end_idx, pattern_highs, pattern_lows, color)
            elif 'double' in pattern_type_lower:
                self._draw_double_pattern(ax, start_idx, end_idx, pattern_highs, pattern_lows, color)
            else:
                # Default: draw trendlines
                self._draw_trendlines(ax, start_idx, end_idx, pattern_highs, pattern_lows, color)
            
            # Add label with BOLD styling
            mid_idx = (start_idx + end_idx) // 2
            mid_price = (pattern_highs.max() + pattern_lows.min()) / 2
            
            # Larger, bolder label
            label_text = f"{pattern_type}\n{confidence:.0f}%"
            ax.text(mid_idx, mid_price, label_text,
                   ha='center', va='center', fontsize=9, color='white',
                   fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor=color, 
                            edgecolor='white', linewidth=1.5, alpha=0.95),
                   zorder=10)  # Higher z-order to be on top
    
    def _draw_triangle_wedge(self, ax, start_idx, end_idx, highs, lows, color):
        """Draw triangle or wedge pattern - VERY VISIBLE."""
        # Upper trendline - VERY thick and bright
        ax.plot([start_idx, end_idx], 
               [highs.iloc[0], highs.iloc[-1]],
               color=color, linestyle='-', linewidth=4, alpha=1.0, zorder=5)
        
        # Lower trendline - VERY thick and bright
        ax.plot([start_idx, end_idx],
               [lows.iloc[0], lows.iloc[-1]],
               color=color, linestyle='-', linewidth=4, alpha=1.0, zorder=5)
        
        # Fill area with more opacity
        ax.fill_between([start_idx, end_idx],
                       [highs.iloc[0], highs.iloc[-1]],
                       [lows.iloc[0], lows.iloc[-1]],
                       color=color, alpha=0.2, zorder=2)
    
    def _draw_rectangle_channel(self, ax, start_idx, end_idx, highs, lows, color):
        """Draw rectangle or channel pattern - VERY VISIBLE."""
        # Horizontal resistance - VERY thick
        resistance = highs.max()
        ax.plot([start_idx, end_idx], [resistance, resistance],
               color=color, linestyle='-', linewidth=4, alpha=1.0, zorder=5)
        
        # Horizontal support - VERY thick
        support = lows.min()
        ax.plot([start_idx, end_idx], [support, support],
               color=color, linestyle='-', linewidth=4, alpha=1.0, zorder=5)
        
        # Fill area with more opacity
        ax.fill_between([start_idx, end_idx],
                       [resistance, resistance],
                       [support, support],
                       color=color, alpha=0.2, zorder=2)
    
    def _draw_flag_pennant(self, ax, start_idx, end_idx, highs, lows, color):
        """Draw flag or pennant pattern."""
        # Flagpole (first 1/3)
        pole_end = start_idx + (end_idx - start_idx) // 3
        
        # Draw pole
        ax.plot([start_idx, pole_end], 
               [lows.iloc[0], highs.iloc[len(highs)//3]],
               color=color, linestyle='-', linewidth=3, alpha=0.9, zorder=3)
        
        # Draw flag (converging lines)
        ax.plot([pole_end, end_idx], 
               [highs.iloc[len(highs)//3], highs.iloc[-1]],
               color=color, linestyle='--', linewidth=2, alpha=0.7, zorder=3)
        ax.plot([pole_end, end_idx],
               [lows.iloc[len(lows)//3], lows.iloc[-1]],
               color=color, linestyle='--', linewidth=2, alpha=0.7, zorder=3)
    
    def _draw_head_shoulders(self, ax, start_idx, end_idx, highs, lows, color):
        """Draw head and shoulders pattern with better visibility."""
        # Find key points (left shoulder, head, right shoulder)
        length = len(highs)
        if length < 5:
            self._draw_trendlines(ax, start_idx, end_idx, highs, lows, color)
            return
        
        left_shoulder_idx = start_idx + length // 4
        head_idx = start_idx + length // 2
        right_shoulder_idx = start_idx + 3 * length // 4
        
        # Draw shoulders and head - thicker lines
        points_x = [start_idx, left_shoulder_idx, head_idx, right_shoulder_idx, end_idx]
        points_y = [lows.iloc[0], highs.iloc[length//4], highs.iloc[length//2], 
                   highs.iloc[3*length//4], lows.iloc[-1]]
        
        ax.plot(points_x, points_y, color=color, linestyle='-', 
               linewidth=3, alpha=0.9, marker='o', markersize=8, zorder=3)
        
        # Neckline - thicker
        neckline = (lows.iloc[length//4] + lows.iloc[3*length//4]) / 2
        ax.plot([start_idx, end_idx], [neckline, neckline],
               color=color, linestyle='--', linewidth=2.5, alpha=0.7, zorder=3)
    
    def _draw_double_pattern(self, ax, start_idx, end_idx, highs, lows, color):
        """Draw double top/bottom pattern."""
        length = len(highs)
        if length < 3:
            self._draw_trendlines(ax, start_idx, end_idx, highs, lows, color)
            return
        
        # Find two peaks/troughs
        first_peak_idx = start_idx + length // 3
        second_peak_idx = start_idx + 2 * length // 3
        
        # Draw peaks
        peak_level = (highs.iloc[length//3] + highs.iloc[2*length//3]) / 2
        ax.plot([first_peak_idx, first_peak_idx], [lows.min(), peak_level],
               color=color, linestyle='-', linewidth=2, alpha=0.7, zorder=3)
        ax.plot([second_peak_idx, second_peak_idx], [lows.min(), peak_level],
               color=color, linestyle='-', linewidth=2, alpha=0.7, zorder=3)
        
        # Connect peaks
        ax.plot([first_peak_idx, second_peak_idx], [peak_level, peak_level],
               color=color, linestyle='--', linewidth=2, alpha=0.6, zorder=3)
    
    def _draw_trendlines(self, ax, start_idx, end_idx, highs, lows, color):
        """Draw simple trendlines - VERY VISIBLE."""
        # Upper trendline - VERY thick
        ax.plot([start_idx, end_idx], 
               [highs.iloc[0], highs.iloc[-1]],
               color=color, linestyle='-', linewidth=4, alpha=1.0, zorder=5)
        
        # Lower trendline - VERY thick
        ax.plot([start_idx, end_idx],
               [lows.iloc[0], lows.iloc[-1]],
               color=color, linestyle='-', linewidth=4, alpha=1.0, zorder=5)
    
    def _plot_volume(self, ax, dates, df):
        """Plot volume bars using integer indices."""
        indices = np.arange(len(df))
        colors = [self.colors['volume_up'] if df['Close'].iloc[i] >= df['Open'].iloc[i] 
                 else self.colors['volume_down'] for i in range(len(df))]
        
        ax.bar(indices, df['Volume'], color=colors, width=0.6, linewidth=0)
        ax.set_xlim(-1, len(df))
        ax.set_ylabel('Volume', color=self.colors['text'], fontsize=9, fontweight='bold')
        ax.set_facecolor(self.colors['background'])
        ax.ticklabel_format(style='plain', axis='y')
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M' if x >= 1e6 else f'{x/1e3:.0f}K'))
    
    def _plot_rsi(self, ax, dates, df):
        """Plot RSI indicator using integer indices."""
        indices = np.arange(len(df))
        rsi = self._calculate_rsi(df['Close'].values)
        
        ax.plot(indices, rsi, color='#9c27b0', linewidth=2, label='RSI(14)')
        ax.axhline(y=70, color=self.colors['bearish'], linestyle='--', alpha=0.4, linewidth=1)
        ax.axhline(y=30, color=self.colors['bullish'], linestyle='--', alpha=0.4, linewidth=1)
        ax.axhline(y=50, color=self.colors['text'], linestyle=':', alpha=0.2, linewidth=1)
        
        ax.fill_between(indices, 70, rsi, where=(rsi >= 70), 
                       color=self.colors['bearish'], alpha=0.2)
        ax.fill_between(indices, 30, rsi, where=(rsi <= 30), 
                       color=self.colors['bullish'], alpha=0.2)
        
        ax.set_xlim(-1, len(df))
        ax.set_ylabel('RSI', color=self.colors['text'], fontsize=9, fontweight='bold')
        ax.set_ylim(0, 100)
        ax.set_facecolor(self.colors['background'])
    
    def _plot_macd(self, ax, dates, df):
        """Plot MACD indicator using integer indices."""
        indices = np.arange(len(df))
        macd, signal, hist = self._calculate_macd(df['Close'].values)
        
        ax.plot(indices, macd, color='#2196f3', linewidth=1.5, label='MACD')
        ax.plot(indices, signal, color='#ff9800', linewidth=1.5, label='Signal')
        
        colors = [self.colors['bullish'] if h >= 0 else self.colors['bearish'] for h in hist]
        ax.bar(indices, hist, color=colors, alpha=0.4, width=0.6, linewidth=0)
        
        ax.axhline(y=0, color=self.colors['text'], linestyle='-', alpha=0.2, linewidth=1)
        ax.set_xlim(-1, len(df))
        ax.set_ylabel('MACD', color=self.colors['text'], fontsize=9, fontweight='bold')
        ax.set_facecolor(self.colors['background'])
    
    def _calculate_rsi(self, prices, period=14):
        """Calculate RSI."""
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        rsi = np.zeros(len(prices))
        rsi[:period] = 50
        
        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])
        
        for i in range(period, len(prices) - 1):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            
            if avg_loss == 0:
                rsi[i + 1] = 100
            else:
                rsi[i + 1] = 100 - (100 / (1 + avg_gain / avg_loss))
        
        return rsi
    
    def _calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """Calculate MACD."""
        def ema(data, period):
            result = np.zeros(len(data))
            multiplier = 2 / (period + 1)
            result[0] = data[0]
            for i in range(1, len(data)):
                result[i] = (data[i] - result[i-1]) * multiplier + result[i-1]
            return result
        
        ema_fast = ema(prices, fast)
        ema_slow = ema(prices, slow)
        macd_line = ema_fast - ema_slow
        signal_line = ema(macd_line, signal)
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    def _style_chart(self, fig, ax_price, ax_volume, ax_rsi, ax_macd, 
                    symbol, prediction, patterns):
        """Apply styling to chart with proper date formatting."""
        # Title with better formatting
        title = f'{symbol} Technical Analysis'
        if prediction:
            direction = prediction.get('direction', 'neutral')
            confidence = prediction.get('confidence', 50)
            emoji = "🟢" if direction == 'bullish' else "🔴" if direction == 'bearish' else "🟡"
            title += f' | {emoji} {direction.upper()} ({confidence:.0f}%)'
        
        ax_price.set_title(title, color=self.colors['text'], fontsize=16, 
                          fontweight='bold', pad=20)
        
        # Pattern count badge - smaller and cleaner
        if patterns:
            pattern_text = f'{len(patterns)} patterns'
            ax_price.text(0.02, 0.97, pattern_text, transform=ax_price.transAxes,
                         fontsize=9, color='white', verticalalignment='top',
                         fontweight='bold',
                         bbox=dict(boxstyle='round,pad=0.5', facecolor='#2a2e39',
                                  edgecolor='#404552', linewidth=1, alpha=0.9))
        
        # Style all axes with cleaner grid
        for ax in [ax_price, ax_volume, ax_rsi, ax_macd]:
            ax.set_facecolor(self.colors['background'])
            ax.tick_params(colors=self.colors['text'], labelsize=8)
            ax.grid(True, alpha=0.08, color=self.colors['grid'], linestyle='-', linewidth=0.5)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_color(self.colors['grid'])
            ax.spines['left'].set_color(self.colors['grid'])
        
        # Hide x-axis labels for upper plots
        for ax in [ax_price, ax_volume, ax_rsi]:
            plt.setp(ax.get_xticklabels(), visible=False)
        
        plt.tight_layout()
    
    def _format_xaxis_dates(self, ax, dates, n_points):
        """Format x-axis with date labels."""
        # Convert dates to list if it's a Series or Index
        if hasattr(dates, 'tolist'):
            date_list = dates.tolist()
        elif hasattr(dates, 'to_pydatetime'):
            date_list = dates.to_pydatetime()
        else:
            date_list = list(dates)
        
        # Select evenly spaced date labels
        n_labels = min(8, n_points)  # Show max 8 date labels
        step = max(1, n_points // n_labels)
        
        tick_positions = list(range(0, n_points, step))
        tick_labels = []
        
        for i in tick_positions:
            if i < len(date_list):
                date_obj = date_list[i]
                if isinstance(date_obj, str):
                    tick_labels.append(date_obj[:10])  # Take first 10 chars (YYYY-MM-DD)
                elif hasattr(date_obj, 'strftime'):
                    tick_labels.append(date_obj.strftime('%Y-%m-%d'))
                else:
                    tick_labels.append(str(date_obj)[:10])
            else:
                tick_labels.append('')
        
        ax.set_xticks(tick_positions)
        ax.set_xticklabels(tick_labels, rotation=45, ha='right')
        ax.set_xlabel('Date', color=self.colors['text'], fontsize=10)
