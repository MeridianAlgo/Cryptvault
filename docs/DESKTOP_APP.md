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
│ CryptVault [BTC-USD] [Analyze] BTC ETH …  Forecast  1m 5m 15m 1H 1M … │
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

![CryptVault desktop terminal](assets/desktop.png)

Pattern geometry is computed in Python and handed to the chart as primitives in
`[timestamp, price]` space, so every diagram stays locked to the candles through
any pan or zoom. Pivots are **snapped to the real swing high/low** within ±2
bars, so lines touch the wicks instead of floating at the close.

Every primitive is tagged with a group — the pattern instance it belongs to,
keyed `name@bar` so two detections of the same pattern stay distinct. The three
strongest are drawn on load; clicking a pattern in the sidebar isolates it.
Drawing all of them at once is unreadable, which is the whole reason for the
grouping.

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

## Timeframes

Each label is the **bar interval**; the window attached to it keeps the bar
count workable and stays inside Yahoo's intraday history caps (1m to 7 days,
5m and 15m to 60, 1h to 730).

| Label | Window | Interval | Approx. bars (crypto) |
|---|---|---|---|
| `1m` | 1 day | 1 minute | 1,440 |
| `5m` | 5 days | 5 minutes | 1,440 |
| `15m` | 10 days | 15 minutes | 960 |
| `1H` | 30 days | 1 hour | 720 |
| `1M` | 30 days | 1 day | 30 |
| `3M` | 90 days | 1 day | 90 |
| `6M` | 180 days | 1 day | 180 |
| `1Y` | 365 days | 1 day | 365 |
| `2Y` | 730 days | 1 week | 104 |

Patterns are detected across the whole window, but the chart opens on the most
recent 400 bars — at 1,400 bars every diagram would be a few pixels wide. Zoom
out to see the rest.

## Forecast (beta)

The trend estimate is drawn past the last bar as its own overlay, toggled from
the top bar:

- a **dashed path** from the last close to the predicted price
- a **volatility envelope** around it, widening with the square root of the
  horizon and with the model's own lack of confidence
- a dotted **divider** at the last real bar, so projection is never mistaken for
  history

The envelope is a volatility cone, **not a calibrated prediction interval**, and
the underlying estimate is momentum-based rather than the trained ensemble. That
is why it ships as beta. Horizon is reported as a bar count, e.g. `30 x 15m`.

## Architecture

```
cryptvault/desktop/
    app.py        entry point — starts the server, opens the window
    server.py     stdlib http.server: page, vendored JS, /api/analyze
    api.py        fetch → patterns → forecast → trading-vue payload
    shapes.py     pattern pivots → drawing primitives, plus the forecast cone
    index.html    the UI + the custom `CVShapes` trading-vue overlay
```

### Routes

| Route | Returns |
|---|---|
| `GET /` | the single-page UI |
| `GET /vendor/<file>` | Vue 2 and trading-vue-js, downloaded once to `~/.cryptvault/vendor` |
| `GET /api/meta` | version and available timeframes |
| `GET /api/analyze?symbol=&tf=` | the full analysis payload |

The payload carries `forecast_end` so the chart can widen its range to include
the projection instead of rendering it off-screen.

### Payload

```jsonc
{
  "chart":    { "type": "Candles", "data": [[t, o, h, l, c, v], ...] },
  "onchart":  [ { "type": "Channel",  "name": "Bollinger 20/2" },
                { "type": "CVShapes", "name": "Patterns",        "settings": { ... } },
                { "type": "CVShapes", "name": "Forecast (beta)", "settings": { ... } } ],
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
| `text` | boxed label — collision-avoided and clamped inside the grid |
| `mark` | directional triangle |

Each primitive also carries `g`, its group key (`""` = always-on swing
structure). The overlay draws `settings.only` when set, otherwise
`settings.defaults`.

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
