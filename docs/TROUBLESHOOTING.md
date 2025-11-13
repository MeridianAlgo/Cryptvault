# CryptVault Troubleshooting Guide

## Overview

This guide helps you diagnose and resolve common issues with CryptVault. Issues are organized by category with symptoms, causes, and solutions.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Data Fetching Issues](#data-fetching-issues)
3. [Analysis Issues](#analysis-issues)
4. [Performance Issues](#performance-issues)
5. [Configuration Issues](#configuration-issues)
6. [Display Issues](#display-issues)
7. [ML Prediction Issues](#ml-prediction-issues)
8. [Debugging Tips](#debugging-tips)
9. [FAQ](#faq)
10. [Getting Help](#getting-help)

---

## Installation Issues

### Issue: pip install fails with "No matching distribution found"

**Symptoms**:
```
ERROR: Could not find a version that satisfies the requirement cryptvault
```

**Causes**:
- Python version too old
- pip not updated
- Network connectivity issues

**Solutions**:

1. Check Python version:
```bash
python --version  # Should be 3.8 or higher
```

2. Update pip:
```bash
python -m pip install --upgrade pip
```

3. Install from source:
```bash
git clone https://github.com/yourusername/cryptvault.git
cd cryptvault
pip install -e .
```

### Issue: Import errors after installation

**Symptoms**:
```python
ModuleNotFoundError: No module named 'cryptvault'
```

**Causes**:
- Wrong Python environment
- Installation incomplete
- Virtual environment not activated

**Solutions**:

1. Verify installation:
```bash
pip list | grep cryptvault
```

2. Check Python path:
```bash
python -c "import sys; print(sys.path)"
```

3. Reinstall:
```bash
pip uninstall cryptvault
pip install cryptvault
```

### Issue: Dependency conflicts

**Symptoms**:
```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed
```

**Causes**:
- Conflicting package versions
- Outdated dependencies

**Solutions**:

1. Create fresh virtual environment:
```bash
python -m venv fresh_env
source fresh_env/bin/activate  # On Windows: fresh_env\Scripts\activate
pip install cryptvault
```

2. Use requirements file:
```bash
pip install -r requirements.txt
```

---

## Data Fetching Issues

### Issue: "Failed to fetch data for ticker"

**Symptoms**:
```
DataFetchError: Failed to fetch data for BTC from all sources
```

**Causes**:
- Invalid ticker symbol
- Network connectivity issues
- API rate limiting
- Data source unavailable

**Solutions**:

1. Verify ticker symbol:
```bash
# List supported tickers
cryptvault list-tickers

# Try alternative symbol format
cryptvault analyze BTC-USD  # Instead of BTC
```

2. Check network connectivity:
```bash
# Test internet connection
ping google.com

# Test specific data source
python -c "import yfinance as yf; print(yf.Ticker('BTC-USD').info)"
```

3. Check data source status:
```python
from cryptvault.data.fetchers import DataFetcher

fetcher = DataFetcher()
sources = fetcher.get_available_sources()
print(sources)  # Should show available sources
```

4. Wait and retry (rate limiting):
```bash
# Wait 60 seconds and try again
sleep 60
cryptvault analyze BTC
```

### Issue: "Insufficient data for analysis"

**Symptoms**:
```
InsufficientDataError: Need at least 30 data points, got 15
```

**Causes**:
- Ticker too new
- Interval too large
- Data source limitations

**Solutions**:

1. Reduce days or change interval:
```bash
# Try shorter period
cryptvault analyze NEWTICKER --days 7

# Try smaller interval
cryptvault analyze NEWTICKER --interval 1h
```

2. Check data availability:
```python
from cryptvault.data.fetchers import DataFetcher
from datetime import datetime, timedelta

fetcher = DataFetcher()
data = fetcher.fetch('TICKER', days=365)
print(f"Available data points: {len(data)}")
```

### Issue: API rate limiting

**Symptoms**:
```
RateLimitError: API rate limit exceeded
```

**Causes**:
- Too many requests in short time
- Free tier limitations

**Solutions**:

1. Enable caching:
```yaml
# In config/settings.yaml
data_sources:
  cache_ttl: 600  # 10 minutes
```

2. Add delays between requests:
```python
import time

for ticker in tickers:
    result = analyzer.analyze_ticker(ticker)
    time.sleep(5)  # Wait 5 seconds between requests
```

3. Use API key (if available):
```bash
export CRYPTOCOMPARE_API_KEY=your_key_here
```

---

## Analysis Issues

### Issue: No patterns detected

**Symptoms**:
```
Found 0 patterns
```

**Causes**:
- Sensitivity too high
- Insufficient data
- No clear patterns in data
- Pattern detection disabled

**Solutions**:

1. Lower sensitivity:
```bash
cryptvault analyze BTC --sensitivity 0.3
```

2. Increase data range:
```bash
cryptvault analyze BTC --days 90
```

3. Check pattern configuration:
```yaml
# In config/settings.yaml
patterns:
  enabled_geometric: true
  enabled_reversal: true
  enabled_harmonic: true
```

4. Try different ticker:
```bash
# Some tickers have clearer patterns
cryptvault analyze ETH --days 60
```

### Issue: Analysis takes too long

**Symptoms**:
- Analysis hangs or takes > 30 seconds
- No output for extended period

**Causes**:
- Too much data
- Slow network
- Resource constraints

**Solutions**:

1. Reduce data points:
```yaml
# In config/settings.yaml
analysis:
  max_data_points: 500  # Reduce from 1000
```

2. Disable ML predictions:
```yaml
ml:
  enabled: false
```

3. Use faster interval:
```bash
cryptvault analyze BTC --days 30 --interval 1d
```

### Issue: Analysis fails with error

**Symptoms**:
```
AnalysisError: Analysis failed
```

**Causes**:
- Data quality issues
- Configuration errors
- Component failures

**Solutions**:

1. Enable debug logging:
```bash
export CRYPTVAULT_LOG_LEVEL=DEBUG
cryptvault analyze BTC --days 60
```

2. Check logs:
```bash
tail -f logs/cryptvault.log
```

3. Validate data:
```python
from cryptvault.data.validators import DataValidator
from cryptvault.data.fetchers import DataFetcher

fetcher = DataFetcher()
data = fetcher.fetch('BTC', days=60)

validator = DataValidator()
result = validator.validate_price_dataframe(data)
print(result)
```

---

## Performance Issues

### Issue: High memory usage

**Symptoms**:
- System becomes slow
- Out of memory errors
- Swap usage increases

**Causes**:
- Too much data loaded
- Memory leaks
- Inefficient operations

**Solutions**:

1. Limit data points:
```yaml
analysis:
  max_data_points: 500
```

2. Clear cache periodically:
```python
from cryptvault.data.cache import DataCache

cache = DataCache()
cache.clear()
```

3. Process in batches:
```python
tickers = ['BTC', 'ETH', 'ADA', 'SOL']
for ticker in tickers:
    result = analyzer.analyze_ticker(ticker)
    # Process result
    del result  # Free memory
```

### Issue: Slow indicator calculations

**Symptoms**:
- Indicator calculation takes > 5 seconds
- CPU usage spikes

**Causes**:
- Large datasets
- Inefficient calculations
- Missing NumPy

**Solutions**:

1. Verify NumPy installed:
```bash
pip install numpy
python -c "import numpy; print(numpy.__version__)"
```

2. Reduce calculation complexity:
```python
# Use shorter periods
rsi = calculate_rsi(prices, period=7)  # Instead of 14
```

3. Profile performance:
```python
import time

start = time.time()
result = analyzer.analyze_ticker('BTC')
print(f"Analysis took {time.time() - start:.2f}s")
```

---

## Configuration Issues

### Issue: Configuration not loading

**Symptoms**:
```
ConfigurationError: Failed to load configuration
```

**Causes**:
- Missing config files
- Invalid YAML syntax
- Wrong file path

**Solutions**:

1. Verify config files exist:
```bash
ls -la config/
cat config/settings.yaml
```

2. Validate YAML syntax:
```bash
python -c "import yaml; yaml.safe_load(open('config/settings.yaml'))"
```

3. Use default configuration:
```python
from cryptvault.config.manager import ConfigManager

# Load default config
config = ConfigManager()
```

### Issue: Environment variables not working

**Symptoms**:
- Settings not applied
- Using wrong environment

**Causes**:
- Variables not exported
- Wrong variable names
- Shell issues

**Solutions**:

1. Verify environment variables:
```bash
# Linux/macOS
echo $CRYPTVAULT_ENV
env | grep CRYPTVAULT

# Windows
echo %CRYPTVAULT_ENV%
set | findstr CRYPTVAULT
```

2. Export variables correctly:
```bash
# Linux/macOS
export CRYPTVAULT_ENV=production

# Windows
set CRYPTVAULT_ENV=production
```

3. Use .env file:
```bash
# Create .env file
cat > .env << EOF
CRYPTVAULT_ENV=production
CRYPTVAULT_LOG_LEVEL=INFO
EOF
```

---

## Display Issues

### Issue: Colors not showing in terminal

**Symptoms**:
- Output is plain text
- No color codes visible

**Causes**:
- Terminal doesn't support colors
- Colors disabled in config
- Windows console issues

**Solutions**:

1. Enable colors:
```yaml
# In config/settings.yaml
display:
  enable_colors: true
```

2. Use color-capable terminal:
- Windows: Use Windows Terminal or PowerShell
- macOS: Use Terminal.app or iTerm2
- Linux: Most terminals support colors

3. Force color output:
```bash
export FORCE_COLOR=1
cryptvault analyze BTC
```

### Issue: Chart not displaying correctly

**Symptoms**:
- Chart is garbled
- Alignment issues
- Missing characters

**Causes**:
- Terminal size too small
- Unicode not supported
- Font issues

**Solutions**:

1. Increase terminal size:
```bash
# Resize terminal to at least 120x40
```

2. Adjust chart dimensions:
```yaml
display:
  chart_width: 80  # Reduce if terminal is small
  chart_height: 20
```

3. Disable Unicode:
```yaml
display:
  use_unicode: false
```

### Issue: Output too verbose

**Symptoms**:
- Too much information displayed
- Hard to read results

**Causes**:
- Debug logging enabled
- Verbose output mode

**Solutions**:

1. Reduce log level:
```bash
export CRYPTVAULT_LOG_LEVEL=WARNING
```

2. Use quiet mode:
```bash
cryptvault analyze BTC --quiet
```

3. Output to file:
```bash
cryptvault analyze BTC > results.txt
```

---

## ML Prediction Issues

### Issue: ML predictions not generated

**Symptoms**:
```
ml_predictions: null
```

**Causes**:
- ML disabled
- Insufficient training data
- Model loading failed

**Solutions**:

1. Enable ML:
```yaml
ml:
  enabled: true
```

2. Provide more data:
```bash
cryptvault analyze BTC --days 90  # More data for training
```

3. Check ML dependencies:
```bash
pip install scikit-learn tensorflow
```

### Issue: Low prediction confidence

**Symptoms**:
```
ensemble_confidence: 0.35
```

**Causes**:
- Insufficient training data
- High market volatility
- Model not trained

**Solutions**:

1. Increase training data:
```bash
cryptvault analyze BTC --days 180
```

2. This is normal for:
- Highly volatile markets
- Sideways price action
- Insufficient historical data

3. Interpret with caution:
- Confidence < 0.4: Low confidence
- Confidence 0.4-0.6: Medium confidence
- Confidence > 0.6: High confidence

---

## Debugging Tips

### Enable Debug Logging

```bash
# Set environment variable
export CRYPTVAULT_LOG_LEVEL=DEBUG

# Run analysis
cryptvault analyze BTC --days 60

# Check logs
tail -f logs/cryptvault.log
```

### Use Python Debugger

```python
import pdb
from cryptvault.core.analyzer import PatternAnalyzer

analyzer = PatternAnalyzer()
pdb.set_trace()  # Breakpoint
result = analyzer.analyze_ticker('BTC')
```

### Check Component Status

```python
from cryptvault.core.analyzer import PatternAnalyzer

analyzer = PatternAnalyzer()

# Check data sources
print(analyzer.data_fetcher.get_available_sources())

# Check ML status
if analyzer.ml_predictor:
    print(analyzer.ml_predictor.get_model_performance())
```

### Validate Input Data

```python
from cryptvault.data.validators import DataValidator
from cryptvault.data.fetchers import DataFetcher

# Fetch data
fetcher = DataFetcher()
data = fetcher.fetch('BTC', days=60)

# Validate
validator = DataValidator()
result = validator.validate_price_dataframe(data)

print(f"Valid: {result['is_valid']}")
print(f"Errors: {result['errors']}")
print(f"Statistics: {result['statistics']}")
```

### Profile Performance

```python
import cProfile
import pstats
from cryptvault.core.analyzer import PatternAnalyzer

analyzer = PatternAnalyzer()

# Profile analysis
profiler = cProfile.Profile()
profiler.enable()

result = analyzer.analyze_ticker('BTC', days=60)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 slowest functions
```

---

## FAQ

### Q: Why is my analysis different from other tools?

**A**: Different tools use different algorithms, data sources, and parameters. CryptVault's results may vary due to:
- Pattern detection sensitivity settings
- Data source differences
- Indicator calculation methods
- ML model predictions

### Q: Can I use CryptVault for real-time trading?

**A**: CryptVault is designed for educational and research purposes. It is NOT recommended for real-time trading without:
- Thorough backtesting
- Risk management
- Professional financial advice
- Understanding of limitations

### Q: How accurate are the ML predictions?

**A**: ML predictions are probabilistic and should be used as one of many factors in analysis. Accuracy varies based on:
- Market conditions
- Available training data
- Prediction horizon
- Asset volatility

Typical accuracy ranges from 55-70% for short-term predictions.

### Q: Why do I get different results each time?

**A**: Results may vary due to:
- New data points added
- Market conditions changed
- ML model retraining
- Random initialization in some algorithms

For consistent results, use the same data range and parameters.

### Q: Can I analyze stocks and crypto together?

**A**: Yes, CryptVault supports both:
```bash
cryptvault analyze AAPL --days 60  # Stock
cryptvault analyze BTC --days 60   # Crypto
```

### Q: How do I report a bug?

**A**: Report bugs on GitHub Issues with:
1. Clear description
2. Steps to reproduce
3. Expected vs actual behavior
4. Environment details
5. Relevant logs

### Q: Is there a GUI version?

**A**: Currently, CryptVault is CLI-only. A web interface is planned for future releases.

### Q: Can I contribute new patterns?

**A**: Yes! See CONTRIBUTING.md for guidelines on:
- Adding new pattern detectors
- Writing tests
- Submitting pull requests

---

## Getting Help

### Documentation

- **README**: Quick start and overview
- **API Reference**: `docs/API_REFERENCE.md`
- **Architecture**: `docs/ARCHITECTURE.md`
- **Deployment**: `docs/DEPLOYMENT.md`

### Support Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and community support
- **Email**: support@cryptvault.io
- **Documentation**: https://cryptvault.readthedocs.io

### Before Asking for Help

1. Check this troubleshooting guide
2. Search existing GitHub issues
3. Review documentation
4. Enable debug logging
5. Collect relevant information:
   - CryptVault version
   - Python version
   - Operating system
   - Error messages
   - Log files
   - Steps to reproduce

### Providing Information

When asking for help, include:

```
**Environment**:
- OS: Windows 10 / macOS 12 / Ubuntu 20.04
- Python: 3.9.7
- CryptVault: 4.0.0

**Issue**:
Clear description of the problem

**Steps to Reproduce**:
1. Run command: cryptvault analyze BTC --days 60
2. See error: ...

**Expected Behavior**:
What should happen

**Actual Behavior**:
What actually happens

**Logs**:
```
Paste relevant logs here
```

**Additional Context**:
Any other relevant information
```

---

## Common Error Messages

### DataFetchError

```
DataFetchError: Failed to fetch data for BTC from all sources
```
**Solution**: Check network, verify ticker, wait for rate limit reset

### ValidationError

```
ValidationError: Insufficient data: 15 points (minimum 30 required)
```
**Solution**: Increase days or change interval

### AnalysisError

```
AnalysisError: Pattern detection failed
```
**Solution**: Check logs, validate data, reduce complexity

### ConfigurationError

```
ConfigurationError: Invalid configuration value
```
**Solution**: Validate YAML syntax, check config values

### MLPredictionError

```
MLPredictionError: Failed to generate predictions
```
**Solution**: Provide more data, check ML dependencies

---

## Still Having Issues?

If you've tried the solutions in this guide and still have issues:

1. **Enable debug logging** and collect logs
2. **Search GitHub issues** for similar problems
3. **Create a new issue** with detailed information
4. **Join the community** for help from other users

We're here to help! Don't hesitate to reach out.
