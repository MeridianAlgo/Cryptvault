# Pattern Detection Reference

CryptVault detects 50+ patterns across 7 categories using `ComprehensivePatternDetector`.

## Categories

### 1. Single Candlestick

| Pattern | Bullish | Description |
|---------|---------|-------------|
| Doji | Neutral | Equal open/close — market indecision |
| Gravestone Doji | Bearish | Long upper wick at resistance |
| Dragonfly Doji | Bullish | Long lower wick at support |
| Hammer | Bullish | Long lower wick after downtrend |
| Hanging Man | Bearish | Long lower wick after uptrend |
| Inverted Hammer | Bullish | Long upper wick after downtrend |
| Shooting Star | Bearish | Long upper wick after uptrend |
| Bullish Marubozu | Bullish | Full body candle, no wicks — strong buying |
| Bearish Marubozu | Bearish | Full body candle, no wicks — strong selling |
| Spinning Top | Neutral | Small body, long wicks — indecision |

### 2. Two-Candle

| Pattern | Bullish | Description |
|---------|---------|-------------|
| Bullish Engulfing | Bullish | Bullish candle engulfs prior bearish candle |
| Bearish Engulfing | Bearish | Bearish candle engulfs prior bullish candle |
| Bullish Harami | Bullish | Small bullish inside prior bearish |
| Bearish Harami | Bearish | Small bearish inside prior bullish |
| Piercing Line | Bullish | Closes above midpoint of prior bearish candle |
| Dark Cloud Cover | Bearish | Closes below midpoint of prior bullish candle |
| Tweezer Top | Bearish | Two candles with equal highs — resistance |
| Tweezer Bottom | Bullish | Two candles with equal lows — support |

### 3. Three-Candle

| Pattern | Bullish | Description |
|---------|---------|-------------|
| Morning Star | Bullish | Bear → small body → bull: strong reversal |
| Evening Star | Bearish | Bull → small body → bear: strong reversal |
| Three White Soldiers | Bullish | Three consecutive strong bullish candles |
| Three Black Crows | Bearish | Three consecutive strong bearish candles |
| Abandoned Baby Bottom | Bullish | Gap + doji + gap: strong bullish reversal |
| Abandoned Baby Top | Bearish | Gap + doji + gap: strong bearish reversal |

### 4. Chart Patterns (Reversal)

| Pattern | Bullish | Description |
|---------|---------|-------------|
| Double Top | Bearish | Two equal peaks — neckline break triggers short |
| Double Bottom | Bullish | Two equal troughs — neckline break triggers long |
| Triple Top | Bearish | Three equal peaks — strong resistance |
| Triple Bottom | Bullish | Three equal troughs — strong support |
| Head & Shoulders | Bearish | LS-Head-RS formation with neckline |
| Inverse Head & Shoulders | Bullish | Inverted LS-Head-RS with neckline |
| Rising Wedge | Bearish | Both trendlines rising but narrowing |
| Falling Wedge | Bullish | Both trendlines falling but narrowing |

### 5. Chart Patterns (Continuation)

| Pattern | Bullish | Description |
|---------|---------|-------------|
| Symmetrical Triangle | Neutral | Converging trendlines — breakout imminent |
| Ascending Triangle | Bullish | Flat resistance, rising support |
| Descending Triangle | Bearish | Falling resistance, flat support |
| Bull Flag | Bullish | Strong up-move followed by pullback consolidation |
| Bear Flag | Bearish | Strong down-move followed by bounce consolidation |
| Bull Pennant | Bullish | Strong up-move with tight symmetric consolidation |
| Bear Pennant | Bearish | Strong down-move with tight symmetric consolidation |
| Cup & Handle | Bullish | U-shaped base with small handle pullback |

### 6. Harmonic Patterns

Detected via Fibonacci ratio validation. Uses 8% tolerance.

| Pattern | Notes |
|---------|-------|
| Gartley | XB=0.618, BD=1.272-1.618 |
| Butterfly | XB=0.786, BD=1.618-2.618 |
| Bat | XB=0.382-0.500, BD=1.618-2.618 |
| Crab | XB=0.382-0.618, BD=2.240-3.618 |
| Shark | XB=0.446-0.618, BD=0.886-1.130 |
| Cypher | XB=0.382-0.618, BD=0.786 |

### 7. Divergence

| Pattern | Bullish | Description |
|---------|---------|-------------|
| RSI Bullish Divergence | Bullish | Price lower lows, RSI higher lows |
| RSI Bearish Divergence | Bearish | Price higher highs, RSI lower highs |
| MACD Bullish Divergence | Bullish | Price lower lows, MACD higher lows |
| MACD Bearish Divergence | Bearish | Price higher highs, MACD lower highs |

## Pattern Output Format

Each detected pattern is returned as a dict:

```python
{
    "name": "Double Top",
    "category": "reversal",
    "bullish": False,
    "direction": "bearish",
    "strength": 0.80,        # 0.0 - 1.0
    "index": 42,             # bar index where pattern completes
    "description": "Two equal peaks – bearish reversal signal",
    "target": 45230.0,       # price target (None if not applicable)
    "stop_loss": 52800.0,    # stop loss level (None if not applicable)
    "extra": {               # key point indices for chart drawing
        "p1": 25,
        "p2": 42,
        "neck": 48100.0,
    }
}
```

## Usage

```python
from cryptvault.patterns.comprehensive import ComprehensivePatternDetector
import yfinance as yf

df = yf.Ticker("BTC-USD").history(period="90d", interval="1d")
df.columns = [c.lower() for c in df.columns]

detector = ComprehensivePatternDetector()
patterns = detector.detect_all(df)

for p in patterns:
    direction = "BULL" if p["bullish"] else "BEAR"
    print(f"[{direction}] {p['name']} @ bar {p['index']}  strength={p['strength']:.0%}")
```

## Configuration

The detector uses these defaults:

| Parameter | Value | Description |
|-----------|-------|-------------|
| Lookback order | 5 | Minimum bars between pivot extrema |
| Doji ratio | 5% | Max body/range ratio for doji classification |
| Hammer lower wick | 2x body | Minimum lower wick for hammer |
| ATR period | 14 | ATR smoothing period |
| RSI period | 14 | RSI smoothing period |
| Harmonic tolerance | 8% | Fibonacci ratio matching tolerance |
| Max results | 50 | Maximum patterns returned by `detect_all` |
