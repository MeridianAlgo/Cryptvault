# Matplotlib Toolbar Guide

## Understanding the Interactive Window

When you run `python generate_chart.py BTC --days 60`, a window opens with your chart. At the **bottom** of this window, there is a toolbar with several buttons.

## Toolbar Location

The toolbar is located at the **BOTTOM** of the window, below the chart. It looks like a gray bar with small icon buttons.

## Toolbar Buttons (Left to Right)

### 1. Home Button
- **Icon**: Small house
- **Function**: Reset view to original
- **How to use**: Click once to reset zoom/pan

### 2. Back Button  
- **Icon**: Left arrow
- **Function**: Go to previous view
- **How to use**: Click to undo zoom/pan

### 3. Forward Button
- **Icon**: Right arrow
- **Function**: Go to next view (after going back)
- **How to use**: Click to redo zoom/pan

### 4. Pan/Zoom Button
- **Icon**: Four arrows pointing outward
- **Function**: Enable pan mode
- **How to use**: 
  1. Click the button (it will appear pressed/highlighted)
  2. Left-click and drag on chart to move around
  3. Right-click and drag to zoom
  4. Click button again to disable

### 5. Zoom to Rectangle Button
- **Icon**: Magnifying glass
- **Function**: Zoom into a specific area
- **How to use**:
  1. Click the button (it will appear pressed/highlighted)
  2. Click and drag on chart to draw a rectangle
  3. Release to zoom into that area
  4. Click button again to disable

### 6. Configure Subplots Button
- **Icon**: Sliders/adjustments
- **Function**: Adjust spacing and margins
- **How to use**: Click to open configuration dialog

### 7. Save Button
- **Icon**: Floppy disk
- **Function**: Save current view to file
- **How to use**: Click to open save dialog

## How to Use Interactive Features

### To Zoom In
**Method 1: Zoom Tool**
1. Click the zoom button (magnifying glass)
2. Click and drag to select area
3. Release to zoom

**Method 2: Mouse Wheel**
1. Hover mouse over chart
2. Scroll up to zoom in
3. Scroll down to zoom out

### To Pan (Move Around)
**Method 1: Pan Tool**
1. Click the pan button (four arrows)
2. Click and drag to move
3. Release when done

**Method 2: Right-Click Drag**
1. Right-click and hold on chart
2. Drag to move
3. Release when done

### To Reset View
1. Click the home button (house icon)
2. View returns to original

## Troubleshooting

### "I don't see a toolbar"
- Check the very bottom of the window
- The toolbar is a thin gray bar below the chart
- Try maximizing the window

### "The buttons don't do anything"
- Make sure you click the button first to activate it
- The button should appear pressed/highlighted when active
- Try clicking directly on the icon

### "I can't zoom or pan"
- Click the zoom or pan button first
- The button must be active (highlighted)
- Then click and drag on the chart itself

### "The window is blank"
- Wait a few seconds for the chart to render
- Check if the window is behind other windows
- Try closing and reopening

### "Still not working"
Try this test:
```bash
python test_matplotlib_interactive.py
```

This opens a simple plot. If this doesn't work either, there may be a matplotlib installation issue.

## Alternative: Save to File

If interactive mode doesn't work, you can save charts to files:

```bash
python generate_chart.py BTC --days 60 --save btc.png
```

Then open the PNG file in any image viewer.

## Visual Guide

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│                                                         │
│                    CHART AREA                           │
│                                                         │
│                                                         │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│ [🏠] [◀] [▶] [✥] [🔍] [⚙] [💾]  ← TOOLBAR (BOTTOM)    │
└─────────────────────────────────────────────────────────┘
```

## Expected Behavior

When working correctly:
1. Window opens with chart displayed
2. Toolbar visible at bottom
3. Clicking zoom button highlights it
4. Dragging on chart creates zoom rectangle
5. Releasing zooms into that area
6. Home button resets view

## System Requirements

- Python 3.8+
- matplotlib installed
- tkinter installed (usually comes with Python)
- Display/GUI environment (not headless)

## Additional Help

If you continue to have issues:
1. Check matplotlib version: `python -c "import matplotlib; print(matplotlib.__version__)"`
2. Check backend: `python -c "import matplotlib; print(matplotlib.get_backend())"`
3. Should show "tkagg" or similar GUI backend
4. Try reinstalling matplotlib: `pip install --upgrade matplotlib`

---

For more help, see:
- [Interactive Features Summary](INTERACTIVE_FEATURES_SUMMARY.md)
- [Interactive Chart Guide](INTERACTIVE_CHART_GUIDE.md)
- [Stock Support Guide](STOCK_SUPPORT_AND_CHARTS.md)


---

## Related Documentation

### Chart Guides
- [Interactive Chart Guide](INTERACTIVE_CHART_GUIDE.md) - Complete interactive guide
- [Interactive Features Summary](INTERACTIVE_FEATURES_SUMMARY.md) - Quick reference
- [Stock Support & Charts](STOCK_SUPPORT_AND_CHARTS.md) - Stock analysis guide
- [Chart Generation Results](CHART_GENERATION_RESULTS.md) - Example outputs

### Getting Started
- [Main README](../README.md) - Project overview
- [Quick Guide](../QUICK_GUIDE.md) - Fast reference
- [Setup Complete](../SETUP_COMPLETE.md) - Setup summary

### Core Features
- [CLI vs Core](CLI_VS_CORE.md) - Understanding entry points
- [Developer Guide](DEVELOPER_GUIDE.md) - Development documentation
- [Platform Support](PLATFORM_SUPPORT.md) - OS compatibility

### Reference
- [Documentation Index](INDEX.md) - Complete documentation index
- [Contributing](../CONTRIBUTING.md) - Contribution guidelines

---

[📚 Documentation Index](INDEX.md) | [🏠 Main README](../README.md) | [🎮 Interactive Guide](INTERACTIVE_CHART_GUIDE.md)
