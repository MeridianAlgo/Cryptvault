# CryptVault Desktop Application

## Overview

CryptVault ships with a native desktop GUI built on Tkinter and Matplotlib. It provides candlestick charting, pattern detection overlays, and ML price predictions in a dark-themed trading terminal layout.

## Launching

```bash
python launch_desktop.py
```

Or via the CLI:

```bash
python cryptvault_cli.py --desktop
```

## Layout

```
┌────────────────────────────────────────────────────────────────┐
│ CryptVault v6.0   Symbol: [BTC-USD]  [Analyze]  1D 5D 1M ...  │  <- Topbar
├──────────┬─────────────────────────────────┬───────────────────┤
│ NAVIGATE │                                 │  ML Prediction    │
│          │      Candlestick Chart          │  ─────────────    │
│ Chart    │      Bollinger Bands            │  Detected         │
│ Analysis │      Pattern overlays           │  Patterns         │
│          │      Volume                     │  (scrollable)     │
│ ─────── │      RSI                        │                   │
│ LAST     │                                 │                   │
│ ANALYSIS │                                 │                   │
└──────────┴─────────────────────────────────┴───────────────────┘
│ Status bar                                                      │
└────────────────────────────────────────────────────────────────┘
```

## Topbar Controls

| Control | Description |
|---------|-------------|
| Symbol entry | Type any ticker (BTC-USD, ETH-USD, AAPL) and press Enter or Analyze |
| Quick-pick buttons | BTC, ETH, SOL, BNB, XRP one-click analysis |
| Timeframe buttons | 1D, 5D, 1M, 3M, 6M, 1Y, 2Y |
| Analyze button | Fetches data, detects patterns, runs ML prediction |

## Chart Panel

The chart panel renders a professional candlestick chart with three sub-plots:

1. **Price chart** (top 60%) — candlesticks, Bollinger Bands, pattern overlays
2. **Volume** (middle 20%) — color-coded volume bars (green = up, red = down)
3. **RSI** (bottom 20%) — 14-period RSI with overbought (70) and oversold (30) zones

### Toolbar Toggles

- **BB** — Bollinger Bands (20-period, 2 standard deviations)
- **Volume** — volume subplot
- **RSI** — RSI subplot
- **Patterns** — pattern overlays on price chart
- **Reset Zoom** — restores full date range

### Scroll to Zoom

Scroll the mouse wheel over the chart to zoom in/out horizontally.

## Pattern Overlays

Patterns are drawn directly on the candlestick chart:

| Pattern Type | Visual |
|-------------|--------|
| Candlestick patterns | Triangle marker (^ bullish, v bearish) at pattern bar |
| Double Top / Bottom | Lines connecting the two peaks/troughs + dashed neckline |
| Head & Shoulders | Lines connecting LS → Head → RS + dashed neckline |
| Triple Top / Bottom | Lines connecting all three peaks/troughs |
| Triangles (Sym/Asc/Desc) | Upper and lower trendlines over the pattern window |
| Rising / Falling Wedge | Upper and lower trendlines over the pattern window |
| All patterns with target | Dotted horizontal target price line |

Green = bullish pattern. Red = bearish pattern.

## Analysis Panel

The right panel displays two cards:

### ML Prediction Card

- **Predicted Price** — next-bar price estimate
- **Direction** — UP / DOWN / NEUTRAL with arrow indicator
- **Confidence gauge** — 0–100% horizontal bar
- **Metadata** — MAPE, horizon, model name

The system tries `ProductionPredictor` (full ensemble) first, falling back to a momentum-based estimate if the full predictor is unavailable.

### Detected Patterns Card

Scrollable list of all patterns found in the current dataset. Each row shows:
- BULL / BEAR badge
- Pattern name and description
- Category (CANDLESTICK / REVERSAL / CONTINUATION / etc.)
- Strength percentage

Summary line shows total pattern count and bullish/bearish breakdown.

## Sidebar Stats

After each analysis, the sidebar updates with:
- Symbol
- Last price
- Period change %
- Total patterns detected
- Overall signal (Bullish / Bearish / Neutral)

## Architecture

```
cryptvault/desktop/
    app.py              entry point — creates and runs MainWindow
    main_window.py      main window, topbar, sidebar, analysis thread
    theme.py            dark color palette, fonts, ttk style definitions
    panels/
        chart_panel.py      Matplotlib candlestick chart + pattern drawing
        analysis_panel.py   ML prediction card + pattern list panel
```

## Data Flow

1. User enters symbol and clicks Analyze
2. `MainWindow._run_analysis()` launches a background thread
3. Thread fetches OHLCV data via `yfinance`
4. `ComprehensivePatternDetector.detect_all()` runs all pattern detectors
5. `ProductionPredictor.predict()` runs the ML ensemble
6. Results are queued back to the main thread via `root.after()`
7. `ChartPanel.update_chart()` and `AnalysisPanel.update()` redraw the UI

## Supported Symbols

Any symbol supported by Yahoo Finance:
- Crypto: `BTC-USD`, `ETH-USD`, `SOL-USD`, `BNB-USD`, `XRP-USD`
- Stocks: `AAPL`, `TSLA`, `GOOGL`, `MSFT`
- Indices: `^GSPC`, `^DJI`
