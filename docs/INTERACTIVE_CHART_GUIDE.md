# Interactive Chart Guide

## Using the Interactive Matplotlib Window

When you run `generate_chart.py` without the `--save` option, an interactive matplotlib window opens with a toolbar at the bottom.

## Toolbar Buttons

The toolbar at the bottom of the window provides these interactive features:

### 🏠 Home
- **Icon**: House icon
- **Function**: Reset view to original zoom/pan
- **Shortcut**: Press `h` or `r` key

### ⬅️ Back
- **Icon**: Left arrow
- **Function**: Go back to previous view
- **Shortcut**: Press `c` key (back) or `v` key (forward)

### ➡️ Forward
- **Icon**: Right arrow
- **Function**: Go forward to next view (after going back)

### ↔️ Pan/Zoom
- **Icon**: Cross arrows
- **Function**: Click to enable pan mode
- **Usage**: 
  - Left-click and drag to pan
  - Right-click and drag to zoom
- **Shortcut**: Press `p` key

### 🔍 Zoom to Rectangle
- **Icon**: Magnifying glass
- **Function**: Click to enable zoom mode
- **Usage**: Click and drag to select area to zoom into
- **Shortcut**: Press `o` key

### ⚙️ Configure Subplots
- **Icon**: Sliders
- **Function**: Adjust spacing and margins
- **Usage**: Opens dialog to fine-tune layout

### 💾 Save
- **Icon**: Floppy disk
- **Function**: Save current view to file
- **Usage**: Opens save dialog

## Keyboard Shortcuts

### Navigation
- `h` or `r` - Home (reset view)
- `c` - Back to previous view
- `v` - Forward to next view
- `p` - Pan/Zoom mode
- `o` - Zoom to rectangle mode

### View Controls
- `f` - Toggle fullscreen
- `g` - Toggle grid
- `l` - Toggle x-axis scale (linear/log)
- `L` - Toggle y-axis scale (linear/log)
- `k` - Toggle x-axis scale (linear/log)
- `K` - Toggle y-axis scale (linear/log)

### Window
- `q` - Close window
- `Ctrl+W` - Close window (Windows/Linux)
- `Cmd+W` - Close window (macOS)

## Mouse Controls

### Without Tool Selected
- **Scroll wheel**: Zoom in/out at cursor position
- **Right-click + drag**: Pan the view

### With Pan Tool Active (press `p`)
- **Left-click + drag**: Pan the view
- **Right-click + drag**: Zoom (drag right to zoom in, left to zoom out)

### With Zoom Tool Active (press `o`)
- **Click + drag**: Draw rectangle to zoom into
- **Right-click**: Zoom out

## Usage Examples

### Example 1: Zoom into a Pattern
```bash
python generate_chart.py BTC --days 60
```
1. Window opens with full chart
2. Click the zoom tool (🔍) or press `o`
3. Click and drag over the pattern you want to examine
4. Release to zoom in
5. Press `h` to return to full view

### Example 2: Pan Around the Chart
```bash
python generate_chart.py AAPL --days 90
```
1. Window opens with full chart
2. Click the pan tool (↔️) or press `p`
3. Click and drag to move around
4. Scroll wheel to zoom in/out
5. Press `h` to reset

### Example 3: Save a Specific View
```bash
python generate_chart.py TSLA --days 60
```
1. Zoom/pan to the view you want
2. Click the save button (💾)
3. Choose location and filename
4. Click Save

### Example 4: Compare Multiple Timeframes
```bash
# Open multiple windows
python generate_chart.py BTC --days 30
python generate_chart.py BTC --days 60
python generate_chart.py BTC --days 90
```
Each opens in a separate window for side-by-side comparison.

## Tips for Best Experience

### Performance
- Larger datasets (more days) may be slower to pan/zoom
- Close unused windows to free memory
- Use `--save` option for batch processing

### Viewing Patterns
1. **Zoom in on patterns**: Use zoom tool to examine pattern details
2. **Compare timeframes**: Open multiple windows with different day ranges
3. **Save interesting views**: Use save button to capture specific patterns
4. **Reset often**: Press `h` to return to full view

### Troubleshooting

**Issue**: Window is not interactive / no toolbar
- **Solution**: Make sure you're using TkAgg backend (already configured)
- **Check**: Run `python -c "import matplotlib; print(matplotlib.get_backend())"`
- **Should show**: `TkAgg`

**Issue**: Window opens but is blank
- **Solution**: Wait a few seconds for rendering
- **Try**: Close and reopen

**Issue**: Can't zoom or pan
- **Solution**: Click the tool button first (zoom or pan)
- **Try**: Press `p` for pan or `o` for zoom

**Issue**: Window freezes
- **Solution**: Close window and try with fewer days
- **Try**: Use `--save` option instead

## Advanced Features

### Multiple Charts
Open multiple charts simultaneously:
```bash
# Open in separate terminals/command prompts
python generate_chart.py BTC --days 60
python generate_chart.py ETH --days 60
python generate_chart.py AAPL --days 90
```

### Custom Backend (if TkAgg doesn't work)
```python
# Add to top of generate_chart.py
import matplotlib
matplotlib.use('Qt5Agg')  # or 'WXAgg', 'GTK3Agg'
```

### Programmatic Control
```python
from generate_chart import generate_chart

# Display chart
generate_chart('BTC', days=60, interval='1d', save_path=None)

# Save chart
generate_chart('AAPL', days=90, interval='1d', save_path='apple.png')
```

## Comparison: Display vs Save

### Display Mode (Default)
```bash
python generate_chart.py BTC --days 60
```
**Pros**:
- Interactive zoom/pan
- Examine patterns closely
- Save specific views
- Real-time exploration

**Cons**:
- Blocks terminal until closed
- One chart at a time per terminal
- Requires manual closing

### Save Mode
```bash
python generate_chart.py BTC --days 60 --save btc.png
```
**Pros**:
- Batch processing
- Automated workflows
- No manual interaction needed
- Multiple charts quickly

**Cons**:
- No interactivity
- Fixed view
- Can't zoom after saving

## Best Practices

### For Analysis
1. **Start with display mode** to explore patterns
2. **Zoom into interesting areas** using the zoom tool
3. **Save specific views** using the save button
4. **Compare multiple timeframes** in separate windows

### For Reports
1. **Use display mode** to find best view
2. **Zoom/pan to optimal view**
3. **Save using toolbar** or use `--save` option
4. **Include in presentations/reports**

### For Automation
1. **Use `--save` option** for batch processing
2. **Script multiple symbols** in a loop
3. **Generate reports automatically**
4. **No manual interaction needed**

## Examples Gallery

### Quick Analysis
```bash
# Quick look at Bitcoin
python generate_chart.py BTC

# Examine Apple stock
python generate_chart.py AAPL --days 90

# Check S&P 500
python generate_chart.py SPY --days 180
```

### Detailed Examination
```bash
# Open chart
python generate_chart.py TSLA --days 60

# Then in the window:
# 1. Press 'o' for zoom mode
# 2. Drag over pattern area
# 3. Examine pattern details
# 4. Press 'h' to reset
# 5. Try different areas
```

### Batch Save
```bash
# Save multiple charts
python generate_chart.py BTC --days 60 --save btc.png
python generate_chart.py ETH --days 60 --save eth.png
python generate_chart.py AAPL --days 90 --save aapl.png
python generate_chart.py TSLA --days 90 --save tsla.png
```

## Documentation Links

- [Main README](README.md)
- [Stock Support Guide](docs/STOCK_SUPPORT_AND_CHARTS.md)
- [Quick Reference](STOCK_AND_CHART_FEATURES.md)
- [Chart Generation Results](CHART_GENERATION_RESULTS.md)

---

**Made with ❤️ by the MeridianAlgo Algorithmic Research Team (Quantum Meridian)**


---

## Related Documentation

### Chart Guides
- [Stock Support & Charts](STOCK_SUPPORT_AND_CHARTS.md) - Stock analysis guide
- [Matplotlib Toolbar Guide](MATPLOTLIB_TOOLBAR_GUIDE.md) - Detailed toolbar usage
- [Interactive Features Summary](INTERACTIVE_FEATURES_SUMMARY.md) - Quick reference
- [Chart Generation Results](CHART_GENERATION_RESULTS.md) - Example outputs

### Getting Started
- [Main README](../README.md) - Project overview
- [Quick Guide](../QUICK_GUIDE.md) - Fast reference
- [Setup Guide](setup/SETUP_GUIDE.md) - Installation instructions

### Core Features
- [CLI vs Core](CLI_VS_CORE.md) - Understanding entry points
- [Developer Guide](DEVELOPER_GUIDE.md) - Development documentation
- [Platform Support](PLATFORM_SUPPORT.md) - OS compatibility

### Reference
- [Documentation Index](INDEX.md) - Complete documentation index
- [Changelog](CHANGELOG.md) - Version history
- [Contributing](../CONTRIBUTING.md) - Contribution guidelines

---

[📚 Documentation Index](INDEX.md) | [🏠 Main README](../README.md) | [🎨 Stock & Charts Guide](STOCK_SUPPORT_AND_CHARTS.md)
