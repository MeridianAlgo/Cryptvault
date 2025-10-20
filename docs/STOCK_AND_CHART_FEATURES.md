# Stock Support & Pattern Overlay Charts - Quick Reference

## ✨ What's New

CryptVault now supports **129 assets** including stocks, cryptocurrencies, and ETFs, with professional chart generation featuring visual pattern overlays!

## 🚀 Quick Start

### Generate Charts with Pattern Overlays

```bash
# Bitcoin
python generate_chart.py BTC

# Apple Stock
python generate_chart.py AAPL --days 90 --save apple_chart.png

# Tesla with custom settings
python generate_chart.py TSLA --days 120 --interval 1d --save tesla.png

# S&P 500 ETF
python generate_chart.py SPY --days 180 --save sp500.png
```

### Analyze Stocks with CLI

```bash
# Terminal analysis
python cryptvault_cli.py AAPL 60 1d

# With desktop charts
python cryptvault_cli.py TSLA 90 1d --verbose

# Compare multiple stocks
python cryptvault_cli.py --compare AAPL TSLA GOOGL
```

## 📊 Supported Assets (129 Total)

### Cryptocurrencies (50+)
BTC, ETH, SOL, XRP, ADA, DOGE, MATIC, LINK, UNI, AVAX, and more...

### Technology Stocks (20)
AAPL, TSLA, GOOGL, GOOG, MSFT, NVDA, AMZN, META, NFLX, AMD, INTC, CRM, ORCL, ADBE, CSCO, AVGO, QCOM, TXN, INTU, IBM

### Financial Stocks (15)
JPM, BAC, WFC, GS, MS, C, BLK, SCHW, AXP, USB, V, MA, PYPL, SQ, COIN

### Consumer Stocks (10)
WMT, HD, MCD, NKE, SBUX, TGT, COST, LOW, DIS, CMCSA

### Healthcare Stocks (10)
JNJ, UNH, PFE, ABBV, TMO, MRK, ABT, DHR, LLY, BMY

### Energy & Industrial (10)
XOM, CVX, COP, SLB, BA, CAT, GE, MMM, HON, UPS

### Transportation (6)
UBER, LYFT, ABNB, DAL, UAL, AAL

### ETFs (8)
SPY, QQQ, IWM, DIA, VOO, VTI, GLD, SLV

## 🎨 Pattern Overlay Features

### Visualized Patterns
- ✅ Triangles (Ascending, Descending, Symmetrical, Expanding)
- ✅ Rectangles and Channels
- ✅ Wedges (Rising, Falling)
- ✅ Flags and Pennants
- ✅ Head and Shoulders
- ✅ Double/Triple Tops and Bottoms
- ✅ Divergence Patterns
- ✅ Diamond Patterns
- ✅ Harmonic Patterns

### Visual Features
- 🎨 Color-coded by sentiment (bullish/bearish/neutral)
- 📊 Confidence-based transparency
- 🏷️ Clear pattern labels
- 📈 Professional candlestick charts
- 📉 Volume bars
- 🌙 Dark theme optimized for readability

## 💡 Usage Examples

### Example 1: Tech Stock Analysis
```bash
# Analyze NVIDIA
python generate_chart.py NVDA --days 90 --save nvidia.png

# Analyze Apple
python generate_chart.py AAPL --days 120 --save apple.png

# Analyze Tesla
python generate_chart.py TSLA --days 60 --save tesla.png
```

### Example 2: Financial Sector
```bash
# JPMorgan Chase
python generate_chart.py JPM --days 90 --save jpmorgan.png

# Visa
python generate_chart.py V --days 90 --save visa.png

# Coinbase
python generate_chart.py COIN --days 60 --save coinbase.png
```

### Example 3: ETF Analysis
```bash
# S&P 500
python generate_chart.py SPY --days 180 --save sp500.png

# NASDAQ 100
python generate_chart.py QQQ --days 180 --save nasdaq.png

# Gold ETF
python generate_chart.py GLD --days 120 --save gold.png
```

### Example 4: Cryptocurrency Analysis
```bash
# Bitcoin
python generate_chart.py BTC --days 60 --save bitcoin.png

# Ethereum
python generate_chart.py ETH --days 60 --save ethereum.png

# Solana
python generate_chart.py SOL --days 30 --save solana.png
```

### Example 5: Short-term Analysis
```bash
# Hourly Bitcoin data
python generate_chart.py BTC --days 7 --interval 1h --save btc_hourly.png

# 4-hour Ethereum data
python generate_chart.py ETH --days 14 --interval 4h --save eth_4h.png
```

## 🔧 Command-Line Options

```bash
python generate_chart.py SYMBOL [OPTIONS]

Options:
  --days DAYS          Number of days of historical data (default: 30)
  --interval INTERVAL  Data interval: 1h, 4h, 1d, 1w (default: 1d)
  --save FILENAME      Save chart to file instead of displaying
  --help              Show help message
```

## 📚 Documentation

- **[Stock Support & Charts Guide](docs/STOCK_SUPPORT_AND_CHARTS.md)** - Comprehensive guide
- **[Changelog](CHANGELOG_STOCK_SUPPORT.md)** - Detailed changes
- **[Main README](README.md)** - Project overview
- **[Quick Guide](QUICK_GUIDE.md)** - Quick reference
- **[Developer Guide](docs/DEVELOPER_GUIDE.md)** - For developers

## 🎯 Key Features

### 1. Professional Charts
- High-quality candlestick visualization
- Color-coded volume bars
- Dark theme optimized for readability
- Export as PNG images

### 2. Pattern Detection
- 50+ chart patterns
- Automatic detection
- Confidence scoring
- Visual overlays

### 3. Multi-Asset Support
- Cryptocurrencies
- US Stocks
- ETFs
- Multiple timeframes

### 4. Easy to Use
- Simple command-line interface
- No configuration required
- Works out of the box
- Cross-platform (Windows, macOS, Linux)

## 🔍 Pattern Examples

### Ascending Triangle
```
     Resistance (flat) ─────────────
    /                              
   /  Support (rising)             
  /                                
```

### Head and Shoulders
```
        Head
       /    \
      /      \
  Left        Right
Shoulder    Shoulder
─────────────────────── Neckline
```

### Double Bottom
```
    \     /
     \   /
      \ /
       V    V
```

## 💻 Integration Example

```python
from cryptvault.analyzer import PatternAnalyzer
from cryptvault.data.package_fetcher import PackageDataFetcher
from cryptvault.visualization.pattern_overlay import PatternOverlay

# Fetch data
fetcher = PackageDataFetcher()
data = fetcher.fetch_historical_data('AAPL', days=60, interval='1d')

# Analyze patterns
analyzer = PatternAnalyzer()
results = analyzer.analyze_dataframe(data)

# Create chart with pattern overlays
# (See examples/pattern_overlay_example.py for full code)
```

## 🎓 Best Practices

### For Stocks
1. Use daily intervals (1d) for most analysis
2. 60-120 days provides good pattern visibility
3. Save charts for documentation
4. Compare multiple timeframes

### For Cryptocurrencies
1. Shorter timeframes work well (24/7 trading)
2. Hourly data useful for day trading
3. Daily data for swing trading
4. Weekly data for long-term holds

### Pattern Interpretation
1. Check confidence scores (higher = more reliable)
2. Look for volume confirmation
3. Consider multiple patterns (confluence)
4. Use with other indicators (RSI, MACD)

## 🐛 Troubleshooting

**Issue**: "Insufficient data for charting"
- Try a longer time period or different interval

**Issue**: "No patterns detected"
- Adjust sensitivity or try different timeframe

**Issue**: "Symbol not found"
- Verify ticker symbol is correct and supported

**Issue**: Chart looks cluttered
- Reduce time period or filter pattern types

## 🚀 What's Next?

Future enhancements:
- Real-time data streaming
- Interactive web charts
- Custom indicator overlays
- Pattern backtesting
- Multi-asset comparison
- Alert system
- International exchanges

## 📞 Support

- **GitHub**: https://github.com/MeridianAlgo/Cryptvault
- **Issues**: https://github.com/MeridianAlgo/Cryptvault/issues
- **Docs**: See `docs/` folder

## 📄 License

MIT License - See [LICENSE](LICENSE) for details

---

**Made with ❤️ by the MeridianAlgo Algorithmic Research Team (Quantum Meridian)**

**Version**: 3.3.0  
**Last Updated**: 2025


---

## Related Documentation

### Chart Features
- [Stock Support & Charts](STOCK_SUPPORT_AND_CHARTS.md) - Complete stock guide
- [Interactive Chart Guide](INTERACTIVE_CHART_GUIDE.md) - Interactive windows
- [Matplotlib Toolbar Guide](MATPLOTLIB_TOOLBAR_GUIDE.md) - Toolbar controls
- [Chart Generation Results](CHART_GENERATION_RESULTS.md) - Example outputs

### Getting Started
- [Main README](../README.md) - Project overview
- [Quick Guide](../QUICK_GUIDE.md) - Fast reference
- [Setup Complete](../SETUP_COMPLETE.md) - Setup summary

### Core Features
- [CLI vs Core](CLI_VS_CORE.md) - Understanding entry points
- [Developer Guide](DEVELOPER_GUIDE.md) - Development documentation

### Reference
- [Documentation Index](INDEX.md) - Complete documentation index
- [Changelog - Stock Support](CHANGELOG_STOCK_SUPPORT.md) - Stock feature updates

---

[📚 Documentation Index](INDEX.md) | [🏠 Main README](../README.md) | [🎨 Stock & Charts Guide](STOCK_SUPPORT_AND_CHARTS.md)
