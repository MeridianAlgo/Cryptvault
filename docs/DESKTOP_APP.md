# CryptVault Desktop Application

## Overview

The CryptVault desktop terminal renders its charts with
[**trading-vue-js**](https://github.com/tvjsx/trading-vue-js) — a hackable,
canvas-based charting engine built for traders. Python does the analysis;
trading-vue does the drawing.

The app is a single-page UI served by a small local HTTP server. It opens in a
native window when `pywebview` is installed, and in your default browser
otherwise. The server binds to `127.0.0.1` only.

## Launching

```bash
python launch_desktop.py
```

Or via the CLI:

```bash
python cryptvault_cli.py --desktop
```

Optional native window:

```bash
pip install pywebview
```

## Layout

```
┌───────────────────────────────────────────────────────────────────────┐
│ CryptVault  [BTC-USD] [Analyze]  BTC ETH SOL …    1D 5D 1M 3M 6M 1Y   │
├──────────────────────────────────────────────┬────────────────────────┤
│                                              │  Overview              │
│   Candles + Bollinger channel                │   price / change       │
│   Pattern diagrams (CVShapes overlay)        │   range / bars         │
│   Volume                                     │   signal               │
│                                              │  Forecast              │
│   ───────────────────────────────────────    │   direction / target   │
│   RSI 14                                     │  Patterns              │
│                                              │   ranked list          │
└──────────────────────────────────────────────┴────────────────────────┘
```

Pan, zoom, crosshair, log/linear scaling and the price/RSI splitter all come
from trading-vue-js.

## Pattern Diagrams

Pattern geometry is computed in Python and handed to the chart as primitives in
`[timestamp, price]` space, so every diagram stays locked to the candles through
any pan or zoom. Pivots are **snapped to the real swing high/low** within ±2
bars, so lines touch the wicks instead of floating at the close.

| Pattern | Drawn as |
|---|---|
| Double Top / Bottom | M/W polyline peak → valley → peak, plus the neckline extended right |
| Triple Top / Bottom | Zigzag through all three extremes with the connecting swings |
| Head & Shoulders (+ inverse) | LS → armpit → Head → armpit → RS, with a **sloped** neckline through both armpits, labelled LS/RS |
| Triangles, Wedges | Both fitted trendlines with a shaded body between them |
| Bull / Bear Flag, Pennants | Pole line plus the consolidation channel |
| Cup & Handle | Parabola fitted through rim → bottom → rim, dotted handle, rim line |
| Harmonics (Gartley, Bat, Crab…) | XABCD zigzag with labelled pivots and both shaded legs |
| RSI / MACD Divergence | Dotted line between the two diverging price pivots |
| Candlestick patterns | Triangle marker pointing at the bar |
| Any pattern with a target | Dotted horizontal target line |
| Always on | Swing pivot dots plus fitted support/resistance trendlines |

Green = bullish, red = bearish.

## Architecture

```
cryptvault/desktop/
    app.py        entry point — starts the server, opens the window
    server.py     stdlib http.server: page, vendored JS, /api/analyze
    api.py        fetch → patterns → forecast → trading-vue payload
    shapes.py     pattern pivots → drawing primitives (the diagram engine)
    index.html    the UI + the custom `CVShapes` trading-vue overlay
```

### Routes

| Route | Returns |
|---|---|
| `GET /` | the single-page UI |
| `GET /vendor/<file>` | Vue 2 and trading-vue-js, downloaded once to `~/.cryptvault/vendor` |
| `GET /api/meta` | version and available timeframes |
| `GET /api/analyze?symbol=&tf=` | the full analysis payload |

### Payload

```jsonc
{
  "chart":    { "type": "Candles", "data": [[t, o, h, l, c, v], ...] },
  "onchart":  [ { "type": "Channel",  "name": "Bollinger 20/2" },
                { "type": "CVShapes", "settings": { "shapes": [ ... ] } } ],
  "offchart": [ { "type": "Range", "name": "RSI 14" } ],
  "patterns": [ ... ], "prediction": { ... }, "stats": { ... }
}
```

### The `CVShapes` overlay

One custom trading-vue overlay renders four primitives, so adding a new pattern
diagram is a Python change only — no JavaScript:

| Kind | Shape |
|---|---|
| `poly` | polyline, optionally dashed and/or filled |
| `dot` | pivot marker |
| `text` | boxed label |
| `mark` | directional triangle |

## Vendored assets

Vue 2.6.14 and trading-vue-js 1.0.2 are pinned and cached in
`~/.cryptvault/vendor` on first launch. After that the UI runs offline — only
the market-data fetch needs the network.

## Data Flow

1. The page requests `/api/analyze?symbol=…&tf=…`
2. `api.fetch()` pulls OHLCV via `yfinance`
3. `ComprehensivePatternDetector.detect_all()` runs every detector
4. `shapes.build()` turns pattern pivots into drawing primitives
5. The payload is returned as JSON and bound to the `trading-vue` component
6. `CVShapes.draw()` maps `[timestamp, price]` to screen space and paints

## Supported Symbols

Any symbol supported by Yahoo Finance:
- Crypto: `BTC-USD`, `ETH-USD`, `SOL-USD`, `BNB-USD`, `XRP-USD`
- Stocks: `AAPL`, `TSLA`, `GOOGL`, `MSFT`
- Indices: `^GSPC`, `^DJI`
