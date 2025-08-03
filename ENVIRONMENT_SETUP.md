# 🔧 CryptVault Environment Setup Guide

## 📁 Where to Create .env File

Create your `.env` file in the **root directory** of CryptVault (same folder as `cryptvault_cli.py`):

```
ChartLS/
├── cryptvault/           # Main package
├── cryptvault_cli.py     # CLI script
├── .env                  # ← CREATE HERE
├── .env.example          # Template file
├── requirements.txt
└── README.md
```

## 🚀 Quick Setup

### 1. **Copy the Example File**
```bash
# Copy the example to create your .env file
cp .env.example .env

# Or on Windows
copy .env.example .env
```

### 2. **Basic Setup (No API Keys Needed)**
CryptVault works perfectly **without any API keys** using free tiers:

```env
# .env file - Basic setup
LOG_LEVEL=WARNING
DEFAULT_DAYS=30
DEFAULT_INTERVAL=1d
```

### 3. **Advanced Setup (With API Keys)**
For higher rate limits and more data sources:

```env
# .env file - Advanced setup
COINGECKO_API_KEY=your_key_here
BINANCE_API_KEY=your_key_here
LOG_LEVEL=INFO
DEFAULT_DAYS=30
```

## 🔑 Getting API Keys (Optional)

### CoinGecko Pro API
- **URL**: https://www.coingecko.com/en/api/pricing
- **Free Tier**: 10,000 calls/month
- **Pro Tier**: 50,000+ calls/month
- **Benefits**: Higher rate limits, more data

### Binance API
- **URL**: https://www.binance.com/en/my/settings/api-management
- **Free**: Yes (with limits)
- **Benefits**: Direct exchange data, real-time prices

### Coinbase Pro API
- **URL**: https://pro.coinbase.com/profile/api
- **Free**: Yes (with limits)
- **Benefits**: Professional exchange data

## 📝 Environment Variables Reference

### **API Configuration**
```env
# API Keys (all optional)
COINGECKO_API_KEY=your_key
BINANCE_API_KEY=your_key
BINANCE_SECRET_KEY=your_secret
COINBASE_API_KEY=your_key
COINBASE_SECRET=your_secret
COINBASE_PASSPHRASE=your_passphrase

# API Settings
API_TIMEOUT=10
MAX_RETRIES=3
RATE_LIMIT_DELAY=1.0
```

### **Analysis Settings**
```env
# Default parameters
DEFAULT_DAYS=30
DEFAULT_INTERVAL=1d
DEFAULT_SENSITIVITY=0.5

# Pattern detection
MIN_PATTERN_CONFIDENCE=0.6
MAX_PATTERNS_PER_TYPE=5
ENABLE_VOLUME_CONFIRMATION=true
```

### **ML Model Settings**
```env
# PyTorch settings
ENABLE_PYTORCH=true
ENABLE_ENSEMBLE=true
LSTM_SEQUENCE_LENGTH=60
HIDDEN_UNITS=128
```

### **Display Settings**
```env
# Chart rendering
CHART_WIDTH=80
CHART_HEIGHT=20
ENABLE_COLORS=true

# Logging
LOG_LEVEL=WARNING  # DEBUG, INFO, WARNING, ERROR
ENABLE_FILE_LOGGING=true
```

### **Performance Settings**
```env
# Caching
ENABLE_CACHING=true
CACHE_DURATION_MINUTES=5

# Storage
SAVE_ANALYSIS_RESULTS=false
RESULTS_DIRECTORY=./results
```

## 🔒 Security Best Practices

### 1. **Keep .env Private**
```bash
# Add to .gitignore
echo ".env" >> .gitignore
```

### 2. **Use Read-Only API Keys**
- Only enable "Read" permissions
- Never enable "Trade" or "Withdraw" permissions
- Use IP restrictions when possible

### 3. **Rotate Keys Regularly**
- Change API keys every 3-6 months
- Monitor API usage for unusual activity

## 🧪 Testing Your Setup

### 1. **Test Without API Keys**
```bash
# Should work with free tiers
python cryptvault_cli.py --demo
```

### 2. **Test With API Keys**
```bash
# Should show improved rate limits
python cryptvault_cli.py --status
python cryptvault_cli.py BTC 30 1d
```

### 3. **Check API Status**
```bash
# Monitor API health
python cryptvault_cli.py --status
```

## 🚨 Troubleshooting

### **Common Issues**

#### `.env file not found`
- Ensure `.env` is in the root directory
- Check file name (no `.txt` extension)
- Verify file permissions

#### `API key invalid`
- Double-check key format
- Ensure no extra spaces
- Verify key is active on provider's website

#### `Rate limits still hit`
- API keys may take time to activate
- Check your plan limits
- Monitor usage on provider's dashboard

### **Debug Mode**
```env
# Enable detailed logging
LOG_LEVEL=DEBUG
ENABLE_FILE_LOGGING=true
```

Then check `cryptvault.log` for detailed information.

## 📊 Example .env Files

### **Minimal Setup**
```env
# Just the basics
LOG_LEVEL=WARNING
DEFAULT_DAYS=30
```

### **Power User Setup**
```env
# Full configuration
COINGECKO_API_KEY=cg_1234567890abcdef
BINANCE_API_KEY=1234567890abcdef
LOG_LEVEL=INFO
DEFAULT_DAYS=30
DEFAULT_INTERVAL=4h
MIN_PATTERN_CONFIDENCE=0.7
ENABLE_PYTORCH=true
CHART_WIDTH=100
ENABLE_COLORS=true
```

### **Development Setup**
```env
# For developers
LOG_LEVEL=DEBUG
ENABLE_FILE_LOGGING=true
SAVE_ANALYSIS_RESULTS=true
RESULTS_DIRECTORY=./dev_results
ENABLE_CACHING=false
```

## ✅ Verification

After setting up your `.env` file:

1. **Test basic functionality**:
   ```bash
   python cryptvault_cli.py --demo
   ```

2. **Check API status**:
   ```bash
   python cryptvault_cli.py --status
   ```

3. **Run full analysis**:
   ```bash
   python cryptvault_cli.py BTC 30 1d
   ```

If everything works, you're all set! 🎉

## 💡 Pro Tips

- **Start without API keys** - CryptVault works great with free tiers
- **Add keys gradually** - Test one API at a time
- **Monitor usage** - Check provider dashboards regularly
- **Use environment-specific files** - `.env.dev`, `.env.prod`, etc.
- **Document your setup** - Keep notes on which keys are for what

---

**CryptVault Environment Setup Complete!** 🚀