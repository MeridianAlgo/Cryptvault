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
┌────────────────────────────────────────────────────────────────────────┐
│ CryptVault [BTC] [Analyze]  64,034.50 +1.38%    LIVE Forecast  1m…1W   │
├────────┬──────────────────────────────────────┬────────────────────────┤
│ BTC    │                                      │  range / bias          │
│ ETH    │  Candles + Bollinger channel         │  forecast / forming    │
│ SOL    │  Pattern diagrams (CVShapes)         ├────────────────────────┤
│ …      │  Volume                              │  Patterns   [filter]   │
│        │  ──────────────────────────────────  │   Forming now          │
│ live   │  RSI 14                              │   Reversal             │
│ mids   │                                      │   Continuation …       │
└────────┴──────────────────────────────────────┴────────────────────────┘
```

The left rail carries live mid prices and switches market in one click. The
price readout lifts green or red for a moment on each tick — the whole motion
budget, spent on making liveness legible without anything moving.

Pan, zoom, crosshair, log/linear scaling and the price/RSI splitter all come
from trading-vue-js.

## Pattern Diagrams

![CryptVault desktop terminal](assets/desktop.png)

Pattern geometry is computed in Python and handed to the chart as primitives in
`[timestamp, price]` space, so every diagram stays locked to the candles through
any pan or zoom. Pivots are **snapped to the real swing high/low** within ±2
bars, so lines touch the wicks instead of floating at the close.

Every primitive is tagged with a group — the pattern instance it belongs to,
keyed `name@bar` so two detections of the same pattern stay distinct. A handful
are drawn on load — forming patterns first — and clicking one in the panel
isolates it **and scrolls the chart to it**. Drawing sixty at once is
unreadable, which is the whole reason for the grouping; `Draw all` does it
anyway when you want the full picture.

Nothing is listed that cannot be drawn. Patterns without a bespoke diagram fall
back to a bracket around the exact candles the signal is made of.

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
| Rectangle | The range box, both edges carried to the right edge |
| Rounding Top / Bottom | The fitted quadratic, sampled, with its rim line |
| Broadening Formation | Both diverging trendlines, unshaded |
| Diamond Top / Bottom | Four-corner ring through the widest swing |
| Three Drives | Numbered pushes through the true extremes, with the retracements |
| Island Reversal | The stranded cluster, with the gap bars either side marked |
| Candlestick patterns | A bracket around the `span` candles the signal is made of |
| Always on | Swing pivot dots plus fitted support/resistance trendlines |

Green = bullish, red = bearish. Amber is reserved for the application's own
voice — selection, focus, live state, a pending apex — so a green number on
screen always means the market moved, never that a control is active.

## Projections

Two different claims about the future, both dashed so neither can be mistaken
for price that already printed.

**Pattern targets.** Any pattern with a measured move draws its trigger level
carried past the last bar, a path from the current close to the target, and the
stop. The horizon is the pattern's own width — classic measured-move timing,
rather than an invented number.

**Forming patterns.** `_FormingDetector` finds structures that have *not*
completed and projects the missing pivots into future index space:

| Forming | Projected |
|---|---|
| Head & Shoulders | The right shoulder, at the left shoulder's level, symmetric about the head |
| Double Top / Bottom | The second peak, as many bars after the valley as the first was before it |
| Triple Top / Bottom | The third rejection at the shared level |
| Apex Breakout | Where and when the trendlines cross, with **both** legs measured by the pattern's height |

The payload keeps `have` (pivots that really happened) separate from `future`,
so confirmed geometry draws solid and the projection draws ghosted. An apex has
no direction yet, so both outcomes are drawn — one arrow would be a claim the
data does not support.

## Timeframes

Every label is a **bar interval**, never a date range — the previous set mixed
the two in one control strip, so two identical-looking buttons did completely
different things. Each carries a bar count that keeps diagrams legible. The
Yahoo fallback maps each onto a window inside Yahoo's intraday history caps
(1m to 7 days, 5m and 15m to 60, 1h to 730).

| Label | Bars | Span |
|---|---|---|
| `1m` | 720 | 12 hours |
| `5m` | 576 | 2 days |
| `15m` | 672 | 7 days |
| `1H` | 720 | 30 days |
| `4H` | 540 | 90 days |
| `1D` | 365 | 1 year |
| `1W` | 208 | 4 years |

Patterns are detected across the whole window, but the chart opens on the most
recent 260 bars — at 700 bars every diagram would be a few pixels wide. Zoom
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
    app.py          entry point — starts the server, opens the window
    server.py       stdlib http.server: page, vendored JS, the API
    hyperliquid.py  venue candles and live mids, standard library only
    api.py          fetch → patterns → projection → trading-vue payload
    shapes.py       pattern pivots → drawing primitives, targets, forecast cone
    index.html      the UI + the custom `CVShapes` trading-vue overlay
```

## Market data

Candles come from the [Hyperliquid](https://hyperliquid.xyz) public `/info`
endpoint — no key, no SDK, one `urllib` POST. It is the venue the price is
formed on, so the newest bar is the one still forming rather than a delayed
vendor copy, which is what makes live mode honest.

`coin_for()` maps whatever the user types (`btc`, `BTC-USD`, `BTCUSDT`) onto a
listed ticker, including the venue's `k`-prefixed thousand-denominated books
(`PEPE` → `kPEPE`). Anything unlisted falls back to Yahoo via `yfinance`, and
the payload's `source` field always says which one answered.

### Routes

| Route | Returns |
|---|---|
| `GET /` | the single-page UI |
| `GET /vendor/<file>` | Vue 2 and trading-vue-js, downloaded once to `~/.cryptvault/vendor` |
| `GET /api/meta` | version, timeframes, the market rail |
| `GET /api/analyze?symbol=&tf=` | the full analysis payload |
| `GET /api/tick?symbol=&tf=` | live mid and the bar still forming (~4s poll) |
| `GET /api/markets` | live mids for the watchlist |

`/api/tick` deliberately does no pattern work: it runs every few seconds, and a
full rescan on that cadence would burn CPU redrawing geometry that has not
meaningfully changed. Patterns are re-detected on a slower background cycle that
preserves whatever the user has selected.

The payload carries `forecast_end` and `draw_end` so the chart can widen its
range to include the projections instead of rendering them off-screen.

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
structure). The overlay draws `settings.only` when set, everything when
`settings.all` is on, and otherwise `settings.defaults`. A `poly` may carry `a`
to override its fill alpha — the forecast cone covers far more canvas than a
pattern and needs a fainter one.

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
