# Changelog

All notable changes to CryptVault will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.1.0-Public] - 2025-10-18

### Added
- Complete data module implementation with models, parsers, validators, and fetchers
- Support for both cryptocurrency and stock analysis
- Enhanced ML prediction system with ensemble models
- Comprehensive pattern detection (50+ patterns)
- Desktop charting capabilities with matplotlib
- Portfolio analysis and multi-asset comparison
- Interactive CLI mode
- Prediction accuracy tracking and reporting
- Cache system for ML predictions
- Comprehensive test suite

### Changed
- Updated Python version requirement from 3.7+ to 3.8+
- Upgraded CI/CD pipeline to use actions/upload-artifact@v4 and actions/download-artifact@v4
- Removed emoji characters from all Python files for better terminal compatibility
- Reorganized documentation structure with proper linking
- Updated README with comprehensive documentation links
- Improved error messages and user feedback
- Enhanced logging system

### Fixed
- Fixed CI/CD pipeline Python 3.7 compatibility issues (Ubuntu 24.04 doesn't support Python 3.7)
- Fixed deprecated artifact upload/download actions (v3 -> v4)
- Fixed missing data module causing import errors
- Fixed pattern detection sensitivity issues
- Fixed ML prediction confidence calculations
- Resolved chart alignment and rendering issues

### Removed
- Duplicate README and desktop charts files
- Redundant emoji characters from codebase
- Python 3.7 support (now requires Python 3.8+)

### Security
- Added bandit security scanning to CI/CD pipeline
- Implemented proper input validation
- Added data quality checks

## [2.0.0] - 2025-09-15

### Added
- Enhanced ML forecasting system with 8+ models
- Unified chart rendering system
- Dual asset support (crypto and stocks)
- Advanced ensemble predictor
- Pattern confidence scoring

### Changed
- Improved ML confidence range (55-73% dynamic)
- Enhanced chart visualization
- Better pattern detection algorithms

### Fixed
- ML training warnings eliminated
- Chart fragmentation issues resolved
- Feature dimension consistency

## [1.0.0] - 2025-01-01

### Added
- Initial release
- Basic pattern detection
- Terminal-based charting
- CSV and JSON data parsing
- Technical indicators (RSI, MACD, Moving Averages)
- Basic ML predictions

---

## Version History Summary

- **3.1.0-Public** (2025-10-18): Production-ready public release with complete data module, CI/CD fixes, and emoji removal
- **2.0.0** (2025-09-15): Enhanced ML system and dual asset support
- **1.0.0** (2025-01-01): Initial release with basic features


---

## Related Documentation

### Project Information
- [Project Status](PROJECT_STATUS.md) - Current development status
- [Release Notes](RELEASE_NOTES_3.1.0.md) - Latest release
- [Changelog - Stock Support](CHANGELOG_STOCK_SUPPORT.md) - Stock feature updates

### Getting Started
- [Main README](../README.md) - Project overview
- [Quick Guide](../QUICK_GUIDE.md) - Fast reference

### Development
- [Developer Guide](DEVELOPER_GUIDE.md) - Development documentation
- [Contributing](../CONTRIBUTING.md) - Contribution guidelines

### Reference
- [Documentation Index](INDEX.md) - Complete documentation index

---

[📚 Documentation Index](INDEX.md) | [🏠 Main README](../README.md) | [📊 Project Status](PROJECT_STATUS.md)
