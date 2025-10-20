# Stock Support and Pattern Overlay Charts

CryptVault now provides comprehensive support for stock market analysis alongside cryptocurrency analysis, with professional chart generation featuring visual pattern overlays.

## Table of Contents

1. [Stock Ticker Support](#stock-ticker-support)
2. [Pattern Overlay Charts](#pattern-overlay-charts)
3. [Usage Examples](#usage-examples)
4. [Supported Patterns](#supported-patterns)
5. [Technical Details](#technical-details)

## Stock Ticker Support

CryptVault supports **120+ assets** including:

### Cryptocurrencies (50+)
All major cryptocurrencies including BTC, ETH, SOL, XRP, ADA, DOGE, and many more.

### Stock Categories (70+)

#### Technology Stocks
- **FAANG+**: AAPL, AMZN, NFLX, GOOGL, GOOG, META
- **Semiconductors**: NVDA, AMD, INTC, QCOM, AVGO, TXN
- **Software**: MSFT, CRM, ORCL, ADBE, INTU
- **Hardware**: AAPL, IBM, CSCO

#### Financial Stocks
- **Banks**: JPM, BAC, WFC, C, USB
- **Investment**: GS, MS, BLK, SCHW
- **Payments**: V, MA, PYPL, SQ, AXP
- **Crypto**: COIN

#### Consumer Stocks
- **Retail**: WMT, TGT, COST, HD, LOW
- **Food & Beverage**: MCD, SBUX
- **Entertainment**: DIS, CMCSA
- **Apparel**: NKE

#### Healthcare Stocks
- **Pharma**: JNJ, PFE, MRK, ABBV, LLY, BMY
- **Biotech**: TMO, DHR, ABT
- **Insurance**: UNH

#### Energy & Industrial
- **Energy**: XOM, CVX, COP, SLB
- **Aerospace**: BA
- **Industrial**: CAT, GE, MMM, HON, UPS

#### Transportation & Services
- **Rideshare**: UBER, LYFT
- **Hospitality**: ABNB
- **Airlines**: DAL, UAL, AAL

#### ETFs
- **Broad Market**: SPY, QQQ, IWM, DIA, VOO, VTI
- **Commodities**: GLD, SLV

## Pattern Overlay Charts

The new `generate_chart.py` script creates professional matplotlib charts with visual pattern overlays.

### Key Features

1. **Professional Candlestick Charts**
   - High-quality candlestick visualization
   - Color-coded volume bars
   - Dark theme optimized for readability

2. **Visual Pattern Overlays**
   - Patterns drawn directly on the chart
   - Color-coded by sentiment (bullish/bearish/neutral)
   - Confidence-based transparency
   - Clear pattern labels

3. **Export Capabilities**
   - Save as high-resolution PNG images
   - Perfect for reports and presentations
   - Customizable dimensions

4. **Automatic Analysis**
   - Detects 50+ chart patterns
   - Calculates technical indicators
   - Provides pattern confidence scores

### Color Scheme

- **Bullish Patterns**: Green (#00ff88)
- **Bearish Patterns**: Red (#ff4444)
- **Neutral Patterns**: Orange (#ffaa00)
- **Divergence Patterns**: Purple (#8844ff)

## Usage Examples

### Basic Usage

```bash
# Analyze Bitcoin with default settings (30 days, 1d interval)
python generate_chart.py BTC

# Analyze Apple stock
python generate_chart.py AAPL

# Analyze Tesla with 60 days of data
python generate_chart.py TSLA --days 60
```

### Advanced Usage

```bash
# Generate chart with custom interval
python generate_chart.py NVDA --days 90 --interval 1d

# Save chart to file
python generate_chart.py GOOGL --days 120 --save google_analysis.png

# Analyze ETF
python generate_chart.py SPY --days 180 --interval 1d --save spy_chart.png

# Short-term analysis with hourly data
python generate_chart.py BTC --days 7 --interval 1h --save btc_hourly.png
```

### Integration with CLI

You can also use the standard CLI for analysis:

```bash
# CLI analysis (terminal output)
python cryptvault_cli.py AAPL 60 1d

# Generate visual chart for the same analysis
python generate_chart.py AAPL --days 60 --save aapl_analysis.png
```

## Supported Patterns

The pattern overlay system visualizes the following pattern types:

### Triangle Patterns
- **Ascending Triangle**: Flat resistance, rising support
- **Descending Triangle**: Declining resistance, flat support
- **Symmetrical Triangle**: Converging trendlines
- **Expanding Triangle**: Diverging trendlines (diamond-like)

### Rectangle and Channel Patterns
- **Rectangle**: Horizontal support and resistance
- **Rising Channel**: Parallel upward trendlines
- **Falling Channel**: Parallel downward trendlines

### Wedge Patterns
- **Rising Wedge**: Converging upward trendlines
- **Falling Wedge**: Converging downward trendlines

### Flag and Pennant Patterns
- **Bull Flag**: Strong upward move followed by consolidation
- **Bear Flag**: Strong downward move followed by consolidation
- **Pennants**: Small symmetrical triangles after strong moves

### Reversal Patterns
- **Head and Shoulders**: Three peaks with middle peak highest
- **Inverse Head and Shoulders**: Three troughs with middle lowest
- **Double Top**: Two peaks at similar levels
- **Double Bottom**: Two troughs at similar levels
- **Triple Top/Bottom**: Three peaks/troughs at similar levels

### Divergence Patterns
- **Bullish Divergence**: Price makes lower lows, indicator makes higher lows
- **Bearish Divergence**: Price makes higher highs, indicator makes lower highs
- **Hidden Divergence**: Continuation divergence patterns

### Other Patterns
- **Diamond**: Expanding then contracting price action
- **Cup and Handle**: Rounded bottom with small consolidation
- **Harmonic Patterns**: Gartley, Butterfly, Bat, Crab, ABCD

## Technical Details

### Pattern Overlay Implementation

The pattern overlay system uses matplotlib to draw patterns directly on candlestick charts:

```python
from cryptvault.visualization.pattern_overlay import PatternOverlay

# Create overlay instance
overlay = PatternOverlay(ax)

# Draw pattern on chart
overlay.draw_pattern(pattern, dates, opens, highs, lows, closes)
```

### Drawing Methods

Each pattern type has a specialized drawing method:

- `_draw_triangle_pattern()`: Draws trendlines for triangle patterns
- `_draw_rectangle_pattern()`: Draws horizontal support/resistance
- `_draw_wedge_pattern()`: Draws converging trendlines
- `_draw_flag_pattern()`: Draws pole and flag consolidation
- `_draw_head_shoulders()`: Draws peaks and neckline
- `_draw_double_triple_pattern()`: Marks extrema points
- `_draw_divergence_pattern()`: Draws trend lines with arrows
- `_draw_diamond_pattern()`: Draws expanding/contracting lines

### Customization

You can customize the pattern overlay appearance:

```python
# Adjust pattern colors
overlay.pattern_colors = {
    'bullish': '#00ff88',
    'bearish': '#ff4444',
    'neutral': '#ffaa00',
    'divergence': '#8844ff'
}

# Patterns automatically adjust transparency based on confidence
# Higher confidence = more opaque (alpha: 0.4 to 0.8)
```

### Data Sources

CryptVault uses multiple data sources:

1. **yfinance**: Primary source for both stocks and cryptocurrencies
   - Stocks: Direct ticker symbols (AAPL, TSLA, etc.)
   - Crypto: Ticker with -USD suffix (BTC-USD, ETH-USD)

2. **ccxt**: Fallback for cryptocurrency data
   - Uses Binance exchange
   - Ticker format: BTC/USDT

### Supported Intervals

- `1h`: Hourly data (good for short-term analysis)
- `4h`: 4-hour data (medium-term analysis)
- `1d`: Daily data (default, best for most analysis)
- `1w`: Weekly data (long-term trends)

## Best Practices

### For Stock Analysis

1. **Use daily intervals** for most stock analysis
2. **60-120 days** provides good pattern visibility
3. **Save charts** for documentation and comparison
4. **Compare multiple timeframes** for confirmation

```bash
# Good stock analysis workflow
python generate_chart.py AAPL --days 90 --save aapl_90d.png
python generate_chart.py AAPL --days 180 --save aapl_180d.png
```

### For Cryptocurrency Analysis

1. **Shorter timeframes** work well due to 24/7 trading
2. **Hourly data** useful for day trading
3. **Daily data** for swing trading
4. **Weekly data** for long-term holds

```bash
# Crypto analysis workflow
python generate_chart.py BTC --days 7 --interval 1h --save btc_hourly.png
python generate_chart.py BTC --days 30 --interval 1d --save btc_daily.png
python generate_chart.py BTC --days 180 --interval 1w --save btc_weekly.png
```

### Pattern Interpretation

1. **Check confidence scores**: Higher confidence = more reliable
2. **Look for volume confirmation**: Patterns with volume support are stronger
3. **Consider multiple patterns**: Confluence increases probability
4. **Use with other indicators**: Combine with RSI, MACD, etc.

## Troubleshooting

### Common Issues

**Issue**: "Insufficient data for charting"
- **Solution**: Try a longer time period or different interval

**Issue**: "No patterns detected"
- **Solution**: Adjust sensitivity settings or try different timeframe

**Issue**: "Symbol not found"
- **Solution**: Verify ticker symbol is correct and supported

**Issue**: Chart looks cluttered
- **Solution**: Reduce time period or filter pattern types

### Getting Help

1. Check the [Developer Guide](DEVELOPER_GUIDE.md)
2. Review [CLI vs Core](CLI_VS_CORE.md) documentation
3. See [Main README](main_README.md) for comprehensive overview
4. Open an issue on GitHub for bugs or feature requests

## Examples Gallery

### Stock Analysis Examples

```bash
# Tech stock analysis
python generate_chart.py NVDA --days 90 --save nvidia_analysis.png
python generate_chart.py TSLA --days 120 --save tesla_analysis.png

# Financial sector
python generate_chart.py JPM --days 90 --save jpmorgan_analysis.png
python generate_chart.py V --days 90 --save visa_analysis.png

# ETF analysis
python generate_chart.py SPY --days 180 --save sp500_analysis.png
python generate_chart.py QQQ --days 180 --save nasdaq_analysis.png
```

### Cryptocurrency Examples

```bash
# Major cryptocurrencies
python generate_chart.py BTC --days 60 --save bitcoin_analysis.png
python generate_chart.py ETH --days 60 --save ethereum_analysis.png
python generate_chart.py SOL --days 60 --save solana_analysis.png

# Altcoins
python generate_chart.py DOGE --days 90 --save dogecoin_analysis.png
python generate_chart.py ADA --days 90 --save cardano_analysis.png
```

## Future Enhancements

Planned improvements for stock and chart features:

1. **More Stock Exchanges**: Support for international stocks
2. **Real-time Data**: Live price updates and streaming
3. **Custom Indicators**: User-defined technical indicators
4. **Pattern Backtesting**: Historical pattern performance
5. **Multi-asset Comparison**: Side-by-side chart comparison
6. **Interactive Charts**: Web-based interactive visualizations
7. **Alert System**: Pattern detection alerts and notifications

## Contributing

We welcome contributions to improve stock support and charting:

1. Add support for more stock exchanges
2. Improve pattern detection algorithms
3. Enhance chart visualization
4. Add new pattern types
5. Improve documentation

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## License

CryptVault is released under the MIT License. See [LICENSE](../LICENSE) for details.

---

**Made with ❤️ by the MeridianAlgo Algorithmic Research Team (Quantum Meridian)**


---

## Related Documentation

### Getting Started
- [Main README](../README.md) - Project overview
- [Quick Guide](../QUICK_GUIDE.md) - Fast reference
- [Setup Guide](setup/SETUP_GUIDE.md) - Installation instructions

### Chart Features
- [Interactive Chart Guide](INTERACTIVE_CHART_GUIDE.md) - Using interactive windows
- [Matplotlib Toolbar Guide](MATPLOTLIB_TOOLBAR_GUIDE.md) - Toolbar controls
- [Interactive Features Summary](INTERACTIVE_FEATURES_SUMMARY.md) - Quick reference
- [Chart Generation Results](CHART_GENERATION_RESULTS.md) - Example outputs

### Core Features
- [CLI vs Core](CLI_VS_CORE.md) - Understanding entry points
- [Developer Guide](DEVELOPER_GUIDE.md) - Development documentation
- [Platform Support](PLATFORM_SUPPORT.md) - OS compatibility

### Reference
- [Documentation Index](INDEX.md) - Complete documentation index
- [Changelog - Stock Support](CHANGELOG_STOCK_SUPPORT.md) - Stock feature updates
- [Contributing](../CONTRIBUTING.md) - Contribution guidelines

---

[📚 Documentation Index](INDEX.md) | [🏠 Main README](../README.md) | [⚡ Quick Guide](../QUICK_GUIDE.md)
