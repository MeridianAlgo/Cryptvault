# CCXT Environment Variable Configuration

## Overview
The Cryptvault application now supports conditional use of CCXT (cryptocurrency exchange data) based on an environment variable.

## Configuration

### Default Behavior (YFinance Only)
By default, the application only uses YFinance for data fetching. This avoids:
- Geographic restrictions from Binance and other exchanges
- API rate limits
- Network connectivity issues

```bash
# Default - only YFinance
python cryptvault_cli.py BTC 60 1d
```

### Enabling CCXT
To enable CCXT data sources (including fallback to cryptocurrency exchanges), set the environment variable:

```bash
# Windows PowerShell
$env:CRYPTVAULT_ENABLE_CCXT = "1"
python cryptvault_cli.py BTC 60 1d

# Windows CMD
set CRYPTVAULT_ENABLE_CCXT=1
python cryptvault_cli.py BTC 60 1d

# Linux/Mac
export CRYPTVAULT_ENABLE_CCXT=1
python cryptvault_cli.py BTC 60 1d
```

### Source Priority
When CCXT is enabled:
1. **Primary**: YFinance (always tried first)
2. **Fallback**: CCXT exchanges (Binance, etc.)

When CCXT is disabled:
1. **Only**: YFinance

## Implementation Details

### Changes Made
- Modified `cryptvault/data/fetchers.py` to check for `CRYPTVAULT_ENABLE_CCXT` environment variable
- Fixed PriceDataFrame constructor parameter mismatch (`interval` vs `timeframe`)
- Updated imports to use correct PriceDataFrame class

### Error Handling
- If YFinance fails and CCXT is disabled: Application shows error
- If YFinance fails and CCXT is enabled: Application tries CCXT as fallback
- Geographic restrictions are automatically handled when CCXT is disabled

## Usage Examples

### Basic Usage (YFinance Only)
```bash
python cryptvault_cli.py BTC 60 1d
# Output: sources_tried=['yfinance']
```

### With CCXT Enabled
```bash
set CRYPTVAULT_ENABLE_CCXT=1
python cryptvault_cli.py BTC 60 1d
# Output: sources_tried=['yfinance', 'ccxt'] (if YFinance fails)
```

## Troubleshooting

### Geographic Restrictions
If you encounter errors like:
```
Service unavailable from a restricted location according to 'b. Eligibility'
```

Solution: Use the default configuration (YFinance only) without setting the environment variable.

### Data Source Issues
- **YFinance errors**: Check internet connection and symbol validity
- **CCXT errors**: Verify environment variable is set and check exchange availability

## Security Notes
- No API keys required for basic usage
- Environment variable controls data source behavior
- YFinance provides reliable data for most major cryptocurrencies and stocks
