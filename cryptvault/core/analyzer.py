"""
Core Pattern Analyzer

This module contains the main orchestrator for cryptocurrency chart pattern analysis.
It coordinates data fetching, pattern detection, ML predictions, and technical analysis
with comprehensive error handling and graceful degradation.

The analyzer is designed to continue operation even when individual components fail,
providing partial results and detailed error information.

Example:
    >>> from cryptvault.core.analyzer import PatternAnalyzer
    >>> analyzer = PatternAnalyzer()
    >>> result = analyzer.analyze_ticker('BTC', days=60)
    >>> if result['success']:
    ...     print(f"Found {result['patterns_found']} patterns")
"""

from typing import List, Dict, Optional, Any, Tuple
import time
import logging
from datetime import datetime
from dataclasses import dataclass, field

from ..data.models.models import PriceDataFrame
from ..data.models.parsers import CSVParser, JSONParser
from ..data.models.package_fetcher import PackageDataFetcher
from ..data.models.validator import DataValidator
from ..patterns.geometric import GeometricPatternAnalyzer
from ..patterns.reversal import ReversalPatternDetector
from ..patterns.advanced import AdvancedPatternAnalyzer
from ..patterns.divergence import DivergenceAnalyzer
from ..patterns.candlestick import CandlestickPatternAnalyzer
from ..patterns.types import DetectedPattern, PatternCategory
from ..visualization.terminal_chart import TerminalChart
from ..analysis.technical import TechnicalIndicators
from ..config.manager import ConfigManager
from ..ml.predictor import MLPredictor
from ..exceptions import (
    CryptVaultError,
    DataFetchError,
    ValidationError,
    AnalysisError,
    PatternDetectionError,
    MLPredictionError,
    IndicatorCalculationError,
    InsufficientDataError,
    InvalidTickerError
)


@dataclass
class AnalysisResult:
    """
    Structured analysis result with comprehensive information.

    Attributes:
        success: Whether analysis completed successfully
        symbol: Ticker symbol analyzed
        patterns: List of detected patterns
        pattern_summary: Summary statistics of patterns
        technical_indicators: Technical indicator values
        ml_predictions: ML prediction results (optional)
        ticker_info: Ticker metadata
        chart: Chart visualization output
        recommendations: Trading recommendations
        analysis_time: Time taken for analysis in seconds
        analysis_timestamp: When analysis was performed
        configuration_used: Configuration settings used
        errors: List of non-fatal errors encountered
        warnings: List of warnings
        data_summary: Summary of input data
    """
    success: bool
    symbol: str
    patterns: List[Dict[str, Any]] = field(default_factory=list)
    pattern_summary: Dict[str, Any] = field(default_factory=dict)
    technical_indicators: Dict[str, Any] = field(default_factory=dict)
    ml_predictions: Optional[Dict[str, Any]] = None
    ticker_info: Dict[str, Any] = field(default_factory=dict)
    chart: Optional[str] = None
    recommendations: List[str] = field(default_factory=list)
    analysis_time: float = 0.0
    analysis_timestamp: Optional[datetime] = None
    configuration_used: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    data_summary: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary format."""
        return {
            'success': self.success,
            'symbol': self.symbol,
            'patterns_found': len(self.patterns),
            'patterns': self.patterns,
            'pattern_summary': self.pattern_summary,
            'technical_indicators': self.technical_indicators,
            'ml_predictions': self.ml_predictions,
            'ticker_info': self.ticker_info,
            'chart': self.chart,
            'recommendations': self.recommendations,
            'analysis_time_seconds': self.analysis_time,
            'analysis_timestamp': self.analysis_timestamp,
            'configuration_used': self.configuration_used,
            'errors': self.errors,
            'warnings': self.warnings,
            'data_summary': self.data_summary
        }


class PatternAnalyzer:
    """
    Main orchestrator for cryptocurrency chart pattern analysis.

    This class coordinates all analysis components including data fetching,
    pattern detection, ML predictions, and technical indicators. It implements
    comprehensive error handling and graceful degradation to provide partial
    results even when individual components fail.

    Attributes:
        config: Configuration manager
        logger: Logger instance

    Example:
        >>> analyzer = PatternAnalyzer()
        >>> result = analyzer.analyze_ticker('BTC', days=60)
        >>> print(f"Analysis completed in {result.analysis_time:.2f}s")
    """

    def __init__(self, config_manager: Optional[ConfigManager] = None) -> None:
        """
        Initialize the pattern analyzer with all components.

        Args:
            config_manager: Optional configuration manager. If not provided,
                          default configuration will be used.
        """
        # Configuration management
        self.config: ConfigManager = config_manager or ConfigManager()

        # Setup logging
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.logger.info("Initializing PatternAnalyzer")

        # Initialize components with error handling
        self._initialize_components()

    def _initialize_components(self) -> None:
        """Initialize all analysis components with error handling."""
        # Data handling components
        try:
            self.csv_parser = CSVParser()
            self.json_parser = JSONParser()
            self.data_fetcher = PackageDataFetcher()
            self.validator = DataValidator()
            self.logger.debug("Data handling components initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize data components: {e}")
            raise AnalysisError(
                "Failed to initialize data handling components",
                details={'error': str(e)},
                original_error=e
            )

        # Pattern detection components
        try:
            self.geometric_analyzer = GeometricPatternAnalyzer()
            self.reversal_analyzer = ReversalPatternDetector()
            self.advanced_analyzer = AdvancedPatternAnalyzer()
            self.divergence_analyzer = DivergenceAnalyzer()
            self.candlestick_analyzer = CandlestickPatternAnalyzer()
            self.logger.debug("Pattern detection components initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize pattern detectors: {e}")
            raise AnalysisError(
                "Failed to initialize pattern detection components",
                details={'error': str(e)},
                original_error=e
            )

        # Technical indicators
        try:
            self.technical_indicators = TechnicalIndicators()
            self.logger.debug("Technical indicators initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize technical indicators: {e}")
            raise AnalysisError(
                "Failed to initialize technical indicators",
                details={'error': str(e)},
                original_error=e
            )

        # ML Predictor (optional - failure is non-fatal)
        try:
            self.ml_predictor = MLPredictor()
            self.logger.debug("ML predictor initialized")
        except Exception as e:
            self.logger.warning(f"ML predictor initialization failed: {e}")
            self.ml_predictor = None

        # Visualization
        try:
            self.chart_renderer = TerminalChart(
                width=self.config.display.chart_width,
                height=self.config.display.chart_height,
                enable_colors=self.config.display.enable_colors
            )
            self.logger.debug("Chart renderer initialized")
        except Exception as e:
            self.logger.warning(f"Chart renderer initialization failed: {e}")
            self.chart_renderer = None

    def analyze_ticker(
        self,
        ticker: str,
        days: int = 60,
        interval: str = '1d',
        sensitivity: Optional[float] = None
    ) -> AnalysisResult:
        """
        Analyze cryptocurrency by ticker symbol with real-time data fetching.

        This method fetches historical data for the specified ticker and performs
        comprehensive analysis including pattern detection, technical indicators,
        and ML predictions. It implements graceful degradation to provide partial
        results even if some components fail.

        Args:
            ticker: Cryptocurrency ticker symbol (e.g., 'BTC', 'ETH', 'AAPL')
            days: Number of days of historical data to fetch (default: 60)
            interval: Data interval - '1m', '5m', '1h', '4h', '1d', '1wk' (default: '1d')
            sensitivity: Pattern detection sensitivity 0.0-1.0 (default: from config)

        Returns:
            AnalysisResult containing patterns, indicators, and recommendations

        Raises:
            InvalidTickerError: If ticker symbol is invalid or unsupported
            DataFetchError: If data cannot be fetched
            InsufficientDataError: If insufficient data for analysis

        Example:
            >>> analyzer = PatternAnalyzer()
            >>> result = analyzer.analyze_ticker('BTC', days=60, interval='1d')
            >>> if result.success:
            ...     print(f"Found {len(result.patterns)} patterns")
        """
        start_time = time.time()
        self.logger.info(f"Starting analysis for {ticker} ({days} days, {interval} interval)")

        # Create result object
        result = AnalysisResult(
            success=False,
            symbol=ticker.upper(),
            analysis_timestamp=datetime.now()
        )

        try:
            # Step 1: Validate and fetch data
            data_frame, fetch_errors = self._fetch_and_validate_data(ticker, days, interval)
            result.errors.extend(fetch_errors)

            if data_frame is None:
                result.analysis_time = time.time() - start_time
                return result

            # Step 2: Perform comprehensive analysis
            self._perform_comprehensive_analysis(data_frame, sensitivity, result)

            # Step 3: Mark as successful
            result.success = True
            result.analysis_time = time.time() - start_time

            self.logger.info(
                f"Analysis completed successfully in {result.analysis_time:.2f}s. "
                f"Found {len(result.patterns)} patterns"
            )

        except Exception as e:
            # Catch-all for unexpected errors
            self.logger.error(f"Unexpected error during analysis: {e}", exc_info=True)
            result.errors.append(f"Unexpected error: {str(e)}")
            result.analysis_time = time.time() - start_time

        return result


    def analyze_from_csv(
        self,
        csv_data: str,
        sensitivity: Optional[float] = None
    ) -> AnalysisResult:
        """
        Analyze patterns from CSV data.

        Args:
            csv_data: CSV formatted price data with columns:
                     timestamp, open, high, low, close, volume
            sensitivity: Pattern detection sensitivity 0.0-1.0 (default: from config)

        Returns:
            AnalysisResult containing analysis results

        Example:
            >>> csv_data = "timestamp,open,high,low,close,volume\\n..."
            >>> result = analyzer.analyze_from_csv(csv_data)
        """
        start_time = time.time()
        self.logger.info("Starting analysis from CSV data")

        result = AnalysisResult(
            success=False,
            symbol="CSV_DATA",
            analysis_timestamp=datetime.now()
        )

        try:
            # Parse CSV data
            data_frame = self.csv_parser.parse(csv_data)
            result.symbol = data_frame.symbol or "CSV_DATA"

            # Validate data
            validation_result = self.validator.validate_price_dataframe(data_frame)
            if not validation_result['is_valid']:
                result.errors.append("Data validation failed")
                result.errors.extend(validation_result['errors'])
                result.warnings.extend(validation_result.get('suggestions', []))
                result.analysis_time = time.time() - start_time
                return result

            result.data_summary = validation_result['statistics']

            # Perform analysis
            self._perform_comprehensive_analysis(data_frame, sensitivity, result)
            result.success = True

        except Exception as e:
            self.logger.error(f"CSV analysis failed: {e}", exc_info=True)
            result.errors.append(f"CSV parsing error: {str(e)}")
            result.warnings.append(f"Expected format: {self.csv_parser.get_sample_format()}")

        result.analysis_time = time.time() - start_time
        return result

    def analyze_from_json(
        self,
        json_data: str,
        sensitivity: Optional[float] = None
    ) -> AnalysisResult:
        """
        Analyze patterns from JSON data.

        Args:
            json_data: JSON formatted price data
            sensitivity: Pattern detection sensitivity 0.0-1.0 (default: from config)

        Returns:
            AnalysisResult containing analysis results

        Example:
            >>> json_data = '{"data": [{"timestamp": "...", "close": 50000}]}'
            >>> result = analyzer.analyze_from_json(json_data)
        """
        start_time = time.time()
        self.logger.info("Starting analysis from JSON data")

        result = AnalysisResult(
            success=False,
            symbol="JSON_DATA",
            analysis_timestamp=datetime.now()
        )

        try:
            # Parse JSON data
            data_frame = self.json_parser.parse(json_data)
            result.symbol = data_frame.symbol or "JSON_DATA"

            # Validate data
            validation_result = self.validator.validate_price_dataframe(data_frame)
            if not validation_result['is_valid']:
                result.errors.append("Data validation failed")
                result.errors.extend(validation_result['errors'])
                result.warnings.extend(validation_result.get('suggestions', []))
                result.analysis_time = time.time() - start_time
                return result

            result.data_summary = validation_result['statistics']

            # Perform analysis
            self._perform_comprehensive_analysis(data_frame, sensitivity, result)
            result.success = True

        except Exception as e:
            self.logger.error(f"JSON analysis failed: {e}", exc_info=True)
            result.errors.append(f"JSON parsing error: {str(e)}")
            result.warnings.append(f"Expected format: {self.json_parser.get_sample_format()}")

        result.analysis_time = time.time() - start_time
        return result

    def analyze_dataframe(
        self,
        data_frame: PriceDataFrame,
        sensitivity: Optional[float] = None
    ) -> AnalysisResult:
        """
        Analyze patterns from PriceDataFrame.

        Args:
            data_frame: Price data frame to analyze
            sensitivity: Pattern detection sensitivity 0.0-1.0 (default: from config)

        Returns:
            AnalysisResult containing analysis results

        Example:
            >>> data_frame = PriceDataFrame(...)
            >>> result = analyzer.analyze_dataframe(data_frame)
        """
        start_time = time.time()
        self.logger.info(f"Starting analysis from PriceDataFrame ({len(data_frame)} points)")

        result = AnalysisResult(
            success=False,
            symbol=data_frame.symbol or "DATAFRAME",
            analysis_timestamp=datetime.now()
        )

        try:
            # Validate data
            validation_result = self.validator.validate_price_dataframe(data_frame)
            if not validation_result['is_valid']:
                result.errors.append("Data validation failed")
                result.errors.extend(validation_result['errors'])
                result.warnings.extend(validation_result.get('suggestions', []))
                result.analysis_time = time.time() - start_time
                return result

            result.data_summary = validation_result['statistics']

            # Perform analysis
            self._perform_comprehensive_analysis(data_frame, sensitivity, result)
            result.success = True

        except Exception as e:
            self.logger.error(f"DataFrame analysis failed: {e}", exc_info=True)
            result.errors.append(f"Analysis error: {str(e)}")

        result.analysis_time = time.time() - start_time
        return result

    def _fetch_and_validate_data(
        self,
        ticker: str,
        days: int,
        interval: str
    ) -> Tuple[Optional[PriceDataFrame], List[str]]:
        """
        Fetch and validate data with comprehensive error handling.

        Args:
            ticker: Ticker symbol
            days: Number of days of data
            interval: Data interval

        Returns:
            Tuple of (data_frame, errors_list)
        """
        errors = []

        try:
            # Validate ticker
            if not self.data_fetcher.validate_ticker(ticker):
                error_msg = f"Ticker '{ticker}' is not supported or not found"
                self.logger.error(error_msg)
                errors.append(error_msg)
                errors.append(f"Try one of: {', '.join(self.data_fetcher.get_supported_tickers()[:10])}")
                return None, errors

            # Fetch historical data
            self.logger.debug(f"Fetching {days} days of {interval} data for {ticker}")
            data_frame = self.data_fetcher.fetch_historical_data(ticker, days, interval)

            if not data_frame:
                error_msg = f"Failed to fetch data for {ticker}"
                self.logger.error(error_msg)
                errors.append(error_msg)
                errors.append("Check internet connection and try again")
                return None, errors

            # Validate data
            validation_result = self.validator.validate_price_dataframe(data_frame)
            if not validation_result['is_valid']:
                self.logger.error("Data validation failed")
                errors.append("Data validation failed")
                errors.extend(validation_result['errors'])
                return None, errors

            # Check data size constraints
            if len(data_frame) < self.config.analysis.min_data_points:
                error_msg = (
                    f"Insufficient data points. Need at least "
                    f"{self.config.analysis.min_data_points}, got {len(data_frame)}"
                )
                self.logger.error(error_msg)
                errors.append(error_msg)
                return None, errors

            # Truncate if too much data
            if len(data_frame) > self.config.analysis.max_data_points:
                self.logger.warning(
                    f"Data truncated from {len(data_frame)} to "
                    f"{self.config.analysis.max_data_points} points"
                )
                data_frame = PriceDataFrame(
                    data=data_frame.data[-self.config.analysis.max_data_points:],
                    symbol=data_frame.symbol,
                    timeframe=data_frame.timeframe
                )

            self.logger.info(f"Successfully fetched and validated {len(data_frame)} data points")
            return data_frame, errors

        except Exception as e:
            self.logger.error(f"Data fetch/validation error: {e}", exc_info=True)
            errors.append(f"Data fetch error: {str(e)}")
            return None, errors

    def _perform_comprehensive_analysis(
        self,
        data_frame: PriceDataFrame,
        sensitivity: Optional[float],
        result: AnalysisResult
    ) -> None:
        """
        Perform comprehensive analysis with graceful degradation.

        This method orchestrates all analysis components. If any component fails,
        it logs the error and continues with other components, ensuring partial
        results are still returned.

        Args:
            data_frame: Price data to analyze
            sensitivity: Pattern detection sensitivity
            result: AnalysisResult object to populate
        """
        # Use configured sensitivity if not provided
        if sensitivity is None:
            sensitivity = self.config.sensitivity.geometric_patterns

        self.logger.info(f"Performing analysis with sensitivity: {sensitivity}")

        # Store configuration used
        result.configuration_used = {
            'sensitivity_level': self.config.sensitivity.level.value,
            'patterns_enabled': len(self.config.patterns.get_enabled_patterns()),
            'colors_enabled': self.config.display.enable_colors,
            'min_confidence': self.config.sensitivity.get_min_confidence('geometric')
        }

        # Store data summary
        result.data_summary = {
            'total_points': len(data_frame),
            'symbol': data_frame.symbol,
            'timeframe': data_frame.timeframe,
            'start_time': data_frame.data[0].timestamp if data_frame.data else None,
            'end_time': data_frame.data[-1].timestamp if data_frame.data else None
        }

        # Component 1: Pattern Detection (with graceful degradation)
        patterns = self._detect_patterns_with_error_handling(data_frame, sensitivity, result)

        # Component 2: Technical Indicators (with graceful degradation)
        self._calculate_indicators_with_error_handling(data_frame, result)

        # Component 3: ML Predictions (optional, with graceful degradation)
        self._generate_ml_predictions_with_error_handling(data_frame, patterns, result)

        # Component 4: Chart Generation (optional, with graceful degradation)
        self._generate_chart_with_error_handling(data_frame, patterns, result)

        # Component 5: Generate Recommendations
        self._generate_recommendations(result)

        # Component 6: Add ticker info if available
        self._add_ticker_info(data_frame, result)

    def _detect_patterns_with_error_handling(
        self,
        data_frame: PriceDataFrame,
        sensitivity: float,
        result: AnalysisResult
    ) -> List[DetectedPattern]:
        """
        Detect patterns with comprehensive error handling.

        Each pattern detector is wrapped in try-except to ensure one failing
        detector doesn't prevent others from running.

        Args:
            data_frame: Price data
            sensitivity: Detection sensitivity
            result: Result object to update

        Returns:
            List of detected patterns
        """
        all_patterns = []

        try:
            self.logger.debug("Starting pattern detection")

            # Geometric patterns
            if self.config.patterns.enabled_geometric:
                patterns, errors = self._detect_geometric_patterns(data_frame, sensitivity)
                all_patterns.extend(patterns)
                result.errors.extend(errors)

            # Reversal patterns
            if self.config.patterns.enabled_reversal:
                patterns, errors = self._detect_reversal_patterns(data_frame, sensitivity)
                all_patterns.extend(patterns)
                result.errors.extend(errors)

            # Advanced patterns
            patterns, errors = self._detect_advanced_patterns(data_frame, sensitivity)
            all_patterns.extend(patterns)
            result.errors.extend(errors)

            # Harmonic patterns
            if self.config.patterns.enabled_harmonic:
                patterns, errors = self._detect_harmonic_patterns(data_frame, sensitivity)
                all_patterns.extend(patterns)
                result.errors.extend(errors)

            # Candlestick patterns
            if self.config.patterns.enabled_candlestick:
                patterns, errors = self._detect_candlestick_patterns(data_frame, sensitivity)
                all_patterns.extend(patterns)
                result.errors.extend(errors)

            # Divergence patterns
            if self.config.patterns.enabled_divergence:
                patterns, errors = self._detect_divergence_patterns(data_frame, sensitivity)
                all_patterns.extend(patterns)
                result.errors.extend(errors)

            # Sort by confidence
            all_patterns.sort(key=lambda p: p.confidence, reverse=True)

            # Filter patterns based on configuration
            filtered_patterns = self._filter_patterns(all_patterns)

            # Format patterns for output
            result.patterns = self._format_patterns_for_output(filtered_patterns)
            result.pattern_summary = self._create_pattern_summary(filtered_patterns)

            self.logger.info(f"Pattern detection completed. Found {len(filtered_patterns)} patterns")

            return filtered_patterns

        except Exception as e:
            self.logger.error(f"Pattern detection failed: {e}", exc_info=True)
            result.errors.append(f"Pattern detection error: {str(e)}")
            result.warnings.append("Pattern detection partially failed, results may be incomplete")
            return []


    def _detect_geometric_patterns(
        self,
        data_frame: PriceDataFrame,
        sensitivity: float
    ) -> Tuple[List[DetectedPattern], List[str]]:
        """Detect geometric patterns with error handling."""
        patterns = []
        errors = []

        try:
            geometric_sensitivity = self.config.sensitivity.get_pattern_sensitivity('geometric')

            # Triangles
            if any(self.config.patterns.is_pattern_enabled(p) for p in
                   ['ascending_triangle', 'descending_triangle', 'symmetrical_triangle']):
                try:
                    triangles = self.geometric_analyzer.detect_triangle_patterns(
                        data_frame, geometric_sensitivity
                    )
                    patterns.extend(triangles)
                except Exception as e:
                    self.logger.warning(f"Triangle detection failed: {e}")
                    errors.append(f"Triangle detection failed: {str(e)}")

            # Flags
            if any(self.config.patterns.is_pattern_enabled(p) for p in ['bull_flag', 'bear_flag']):
                try:
                    flags = self.geometric_analyzer.detect_flag_patterns(
                        data_frame, geometric_sensitivity
                    )
                    patterns.extend(flags)
                except Exception as e:
                    self.logger.warning(f"Flag detection failed: {e}")
                    errors.append(f"Flag detection failed: {str(e)}")

            # Cup and Handle
            if self.config.patterns.is_pattern_enabled('cup_and_handle'):
                try:
                    cups = self.geometric_analyzer.detect_cup_and_handle(
                        data_frame, geometric_sensitivity
                    )
                    patterns.extend(cups)
                except Exception as e:
                    self.logger.warning(f"Cup and handle detection failed: {e}")
                    errors.append(f"Cup and handle detection failed: {str(e)}")

            # Wedges
            if any(self.config.patterns.is_pattern_enabled(p) for p in
                   ['rising_wedge', 'falling_wedge']):
                try:
                    wedges = self.geometric_analyzer.detect_wedge_patterns(
                        data_frame, geometric_sensitivity
                    )
                    patterns.extend(wedges)
                except Exception as e:
                    self.logger.warning(f"Wedge detection failed: {e}")
                    errors.append(f"Wedge detection failed: {str(e)}")

            # Rectangles
            if any(self.config.patterns.is_pattern_enabled(p) for p in ['rectangle', 'channel']):
                try:
                    rectangles = self.geometric_analyzer.detect_rectangle_patterns(
                        data_frame, geometric_sensitivity
                    )
                    patterns.extend(rectangles)
                except Exception as e:
                    self.logger.warning(f"Rectangle detection failed: {e}")
                    errors.append(f"Rectangle detection failed: {str(e)}")

        except Exception as e:
            self.logger.error(f"Geometric pattern detection failed: {e}")
            errors.append(f"Geometric pattern detection failed: {str(e)}")

        return patterns, errors

    def _detect_reversal_patterns(
        self,
        data_frame: PriceDataFrame,
        sensitivity: float
    ) -> Tuple[List[DetectedPattern], List[str]]:
        """Detect reversal patterns with error handling."""
        patterns = []
        errors = []

        try:
            reversal_sensitivity = self.config.sensitivity.get_pattern_sensitivity('reversal')

            # Double/Triple patterns
            if any(self.config.patterns.is_pattern_enabled(p) for p in
                   ['double_top', 'double_bottom', 'triple_top', 'triple_bottom']):
                try:
                    double_triple = self.reversal_analyzer.detect_double_triple_patterns(
                        data_frame, reversal_sensitivity
                    )
                    patterns.extend(double_triple)
                except Exception as e:
                    self.logger.warning(f"Double/triple pattern detection failed: {e}")
                    errors.append(f"Double/triple pattern detection failed: {str(e)}")

            # Head and Shoulders
            if self.config.patterns.is_pattern_enabled('head_shoulders'):
                try:
                    head_shoulders = self.reversal_analyzer.detect_head_and_shoulders_patterns(
                        data_frame, reversal_sensitivity
                    )
                    patterns.extend(head_shoulders)
                except Exception as e:
                    self.logger.warning(f"Head and shoulders detection failed: {e}")
                    errors.append(f"Head and shoulders detection failed: {str(e)}")

        except Exception as e:
            self.logger.error(f"Reversal pattern detection failed: {e}")
            errors.append(f"Reversal pattern detection failed: {str(e)}")

        return patterns, errors

    def _detect_advanced_patterns(
        self,
        data_frame: PriceDataFrame,
        sensitivity: float
    ) -> Tuple[List[DetectedPattern], List[str]]:
        """Detect advanced patterns with error handling."""
        patterns = []
        errors = []

        try:
            # Diamond patterns
            if self.config.patterns.is_pattern_enabled('diamond'):
                try:
                    diamonds = self.advanced_analyzer.detect_diamond_patterns(
                        data_frame, sensitivity
                    )
                    patterns.extend(diamonds)
                except Exception as e:
                    self.logger.warning(f"Diamond detection failed: {e}")
                    errors.append(f"Diamond detection failed: {str(e)}")

            # Expanding triangles
            if self.config.patterns.is_pattern_enabled('expanding_triangle'):
                try:
                    expanding = self.advanced_analyzer.detect_expanding_triangle_patterns(
                        data_frame, sensitivity
                    )
                    patterns.extend(expanding)
                except Exception as e:
                    self.logger.warning(f"Expanding triangle detection failed: {e}")
                    errors.append(f"Expanding triangle detection failed: {str(e)}")

        except Exception as e:
            self.logger.error(f"Advanced pattern detection failed: {e}")
            errors.append(f"Advanced pattern detection failed: {str(e)}")

        return patterns, errors

    def _detect_harmonic_patterns(
        self,
        data_frame: PriceDataFrame,
        sensitivity: float
    ) -> Tuple[List[DetectedPattern], List[str]]:
        """Detect harmonic patterns with error handling."""
        patterns = []
        errors = []

        try:
            harmonic_sensitivity = self.config.sensitivity.get_pattern_sensitivity('harmonic')

            if any(self.config.patterns.is_pattern_enabled(p) for p in
                   ['gartley', 'butterfly', 'bat', 'crab', 'abcd', 'cypher']):
                try:
                    harmonics = self.advanced_analyzer.detect_harmonic_patterns(
                        data_frame, harmonic_sensitivity
                    )
                    patterns.extend(harmonics)
                except Exception as e:
                    self.logger.warning(f"Harmonic pattern detection failed: {e}")
                    errors.append(f"Harmonic pattern detection failed: {str(e)}")

        except Exception as e:
            self.logger.error(f"Harmonic pattern detection failed: {e}")
            errors.append(f"Harmonic pattern detection failed: {str(e)}")

        return patterns, errors

    def _detect_candlestick_patterns(
        self,
        data_frame: PriceDataFrame,
        sensitivity: float
    ) -> Tuple[List[DetectedPattern], List[str]]:
        """Detect candlestick patterns with error handling."""
        patterns = []
        errors = []

        try:
            candlestick_sensitivity = self.config.sensitivity.get_pattern_sensitivity('candlestick')

            # Single candlestick patterns
            try:
                single_candles = self.candlestick_analyzer.detect_single_candlestick_patterns(
                    data_frame, candlestick_sensitivity
                )
                patterns.extend(single_candles)
            except Exception as e:
                self.logger.warning(f"Single candlestick detection failed: {e}")
                errors.append(f"Single candlestick detection failed: {str(e)}")

            # Multi-candlestick patterns
            try:
                multi_candles = self.candlestick_analyzer.detect_multi_candlestick_patterns(
                    data_frame, candlestick_sensitivity
                )
                patterns.extend(multi_candles)
            except Exception as e:
                self.logger.warning(f"Multi-candlestick detection failed: {e}")
                errors.append(f"Multi-candlestick detection failed: {str(e)}")

        except Exception as e:
            self.logger.error(f"Candlestick pattern detection failed: {e}")
            errors.append(f"Candlestick pattern detection failed: {str(e)}")

        return patterns, errors

    def _detect_divergence_patterns(
        self,
        data_frame: PriceDataFrame,
        sensitivity: float
    ) -> Tuple[List[DetectedPattern], List[str]]:
        """Detect divergence patterns with error handling."""
        patterns = []
        errors = []

        try:
            divergence_sensitivity = self.config.sensitivity.get_pattern_sensitivity('divergence')

            if any(self.config.patterns.is_pattern_enabled(p) for p in
                   ['bullish_divergence', 'bearish_divergence', 'hidden_divergence']):
                try:
                    divergences = self.divergence_analyzer.detect_price_indicator_divergence(
                        data_frame, divergence_sensitivity
                    )
                    patterns.extend(divergences)
                except Exception as e:
                    self.logger.warning(f"Divergence detection failed: {e}")
                    errors.append(f"Divergence detection failed: {str(e)}")

        except Exception as e:
            self.logger.error(f"Divergence pattern detection failed: {e}")
            errors.append(f"Divergence pattern detection failed: {str(e)}")

        return patterns, errors

    def _calculate_indicators_with_error_handling(
        self,
        data_frame: PriceDataFrame,
        result: AnalysisResult
    ) -> None:
        """Calculate technical indicators with error handling."""
        try:
            self.logger.debug("Calculating technical indicators")
            indicators = {}

            # RSI
            try:
                rsi = self.technical_indicators.calculate_rsi(data_frame)
                current_rsi = next((val for val in reversed(rsi) if val is not None), None)
                indicators['rsi'] = {
                    'current': current_rsi,
                    'overbought': current_rsi and current_rsi > 70,
                    'oversold': current_rsi and current_rsi < 30
                }
            except Exception as e:
                self.logger.warning(f"RSI calculation failed: {e}")
                result.warnings.append("RSI calculation failed")

            # MACD
            try:
                macd = self.technical_indicators.calculate_macd(data_frame)
                current_macd = next((val for val in reversed(macd['macd']) if val is not None), None)
                current_signal = next((val for val in reversed(macd['signal']) if val is not None), None)

                indicators['macd'] = {
                    'current_macd': current_macd,
                    'current_signal': current_signal,
                    'bullish_crossover': current_macd and current_signal and current_macd > current_signal
                }
            except Exception as e:
                self.logger.warning(f"MACD calculation failed: {e}")
                result.warnings.append("MACD calculation failed")

            result.technical_indicators = indicators
            self.logger.debug("Technical indicators calculated successfully")

        except Exception as e:
            self.logger.error(f"Technical indicator calculation failed: {e}", exc_info=True)
            result.errors.append(f"Technical indicator calculation failed: {str(e)}")
            result.warnings.append("Technical indicators unavailable")

    def _generate_ml_predictions_with_error_handling(
        self,
        data_frame: PriceDataFrame,
        patterns: List[DetectedPattern],
        result: AnalysisResult
    ) -> None:
        """Generate ML predictions with error handling."""
        if not self.ml_predictor:
            self.logger.debug("ML predictor not available, skipping predictions")
            result.warnings.append("ML predictions unavailable (predictor not initialized)")
            return

        try:
            self.logger.debug("Generating ML predictions")
            ml_predictions = self.ml_predictor.predict(data_frame, patterns)
            result.ml_predictions = self._format_ml_predictions(ml_predictions)
            self.logger.info("ML predictions generated successfully")

        except Exception as e:
            self.logger.warning(f"ML prediction failed: {e}")
            result.warnings.append("ML predictions unavailable due to error")
            result.ml_predictions = None

    def _generate_chart_with_error_handling(
        self,
        data_frame: PriceDataFrame,
        patterns: List[DetectedPattern],
        result: AnalysisResult
    ) -> None:
        """Generate chart visualization with error handling."""
        if not self.chart_renderer:
            self.logger.debug("Chart renderer not available, skipping chart generation")
            result.warnings.append("Chart visualization unavailable (renderer not initialized)")
            return

        try:
            self.logger.debug("Generating chart visualization")
            result.chart = self.chart_renderer.render_chart(data_frame, patterns)
            self.logger.debug("Chart generated successfully")

        except Exception as e:
            self.logger.warning(f"Chart generation failed: {e}")
            result.warnings.append("Chart visualization unavailable due to error")
            result.chart = None


    def _filter_patterns(self, patterns: List[DetectedPattern]) -> List[DetectedPattern]:
        """
        Filter patterns based on configuration settings.

        Args:
            patterns: List of detected patterns

        Returns:
            Filtered list of patterns
        """
        filtered_patterns = []
        patterns_by_type = {}

        for pattern in patterns:
            pattern_type = pattern.pattern_type.value

            # Check if pattern type is enabled
            if not self.config.patterns.is_pattern_enabled(pattern_type):
                continue

            # Check minimum confidence threshold
            category_key = self._get_category_key(pattern.category)
            min_confidence = self.config.sensitivity.get_min_confidence(category_key)

            if pattern.confidence < min_confidence:
                continue

            # Check pattern duration constraints
            duration_candles = pattern.end_index - pattern.start_index + 1
            if (duration_candles < self.config.sensitivity.min_pattern_duration or
                duration_candles > self.config.sensitivity.max_pattern_duration):
                continue

            # Check volume confirmation if required
            if (self.config.sensitivity.require_volume_confirmation and
                not pattern.volume_profile.volume_confirmation):
                continue

            # Group by type for limiting
            if pattern_type not in patterns_by_type:
                patterns_by_type[pattern_type] = []
            patterns_by_type[pattern_type].append(pattern)

        # Apply per-type limits
        for pattern_type, type_patterns in patterns_by_type.items():
            type_patterns.sort(key=lambda p: p.confidence, reverse=True)
            limited_patterns = type_patterns[:self.config.patterns.max_patterns_per_type]
            filtered_patterns.extend(limited_patterns)

        # Sort all patterns by confidence
        filtered_patterns.sort(key=lambda p: p.confidence, reverse=True)

        # Apply total limit
        if len(filtered_patterns) > self.config.patterns.max_total_patterns:
            filtered_patterns = filtered_patterns[:self.config.patterns.max_total_patterns]

        # Filter overlapping patterns if enabled
        if self.config.patterns.filter_overlapping:
            filtered_patterns = self._remove_overlapping_patterns(filtered_patterns)

        return filtered_patterns

    def _get_category_key(self, category: PatternCategory) -> str:
        """Get category key for configuration lookup."""
        category_map = {
            'Bullish Continuation': 'geometric',
            'Bearish Continuation': 'geometric',
            'Bullish Reversal': 'reversal',
            'Bearish Reversal': 'reversal',
            'Bilateral/Neutral': 'geometric',
            'Harmonic Pattern': 'harmonic',
            'Candlestick Pattern': 'candlestick',
            'Divergence Pattern': 'divergence'
        }
        return category_map.get(category.value, 'geometric')

    def _remove_overlapping_patterns(
        self,
        patterns: List[DetectedPattern]
    ) -> List[DetectedPattern]:
        """Remove overlapping patterns, keeping higher confidence ones."""
        if not patterns:
            return patterns

        non_overlapping = []

        for pattern in patterns:
            is_overlapping = False

            for existing in non_overlapping:
                # Calculate overlap
                overlap_start = max(pattern.start_index, existing.start_index)
                overlap_end = min(pattern.end_index, existing.end_index)

                if overlap_start <= overlap_end:
                    # Calculate overlap percentage
                    pattern_length = pattern.end_index - pattern.start_index + 1
                    overlap_length = overlap_end - overlap_start + 1
                    overlap_ratio = overlap_length / pattern_length

                    if overlap_ratio >= self.config.patterns.overlap_threshold:
                        is_overlapping = True
                        break

            if not is_overlapping:
                non_overlapping.append(pattern)

        return non_overlapping

    def _format_patterns_for_output(
        self,
        patterns: List[DetectedPattern]
    ) -> List[Dict[str, Any]]:
        """Format patterns for output display."""
        formatted_patterns = []

        for pattern in patterns:
            formatted_patterns.append({
                'type': pattern.pattern_type.value.replace('_', ' ').title(),
                'category': pattern.category.value,
                'confidence': f"{pattern.confidence:.1%}",
                'confidence_raw': pattern.confidence,
                'start_time': pattern.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                'end_time': pattern.end_time.strftime("%Y-%m-%d %H:%M:%S"),
                'duration_hours': pattern.get_duration_days() * 24,
                'is_bullish': pattern.is_bullish(),
                'is_bearish': pattern.is_bearish(),
                'is_reversal': pattern.is_reversal(),
                'description': pattern.description,
                'key_levels': pattern.key_levels,
                'volume_confirmation': pattern.volume_profile.volume_confirmation
            })

        return formatted_patterns

    def _create_pattern_summary(
        self,
        patterns: List[DetectedPattern]
    ) -> Dict[str, Any]:
        """Create summary statistics of detected patterns."""
        if not patterns:
            return {'total': 0}

        # Count by category
        category_counts = {}
        for pattern in patterns:
            category = pattern.category.value
            category_counts[category] = category_counts.get(category, 0) + 1

        # Count by sentiment
        bullish_count = sum(1 for p in patterns if p.is_bullish())
        bearish_count = sum(1 for p in patterns if p.is_bearish())
        neutral_count = len(patterns) - bullish_count - bearish_count

        # Average confidence
        avg_confidence = sum(p.confidence for p in patterns) / len(patterns)

        return {
            'total': len(patterns),
            'by_category': category_counts,
            'sentiment': {
                'bullish': bullish_count,
                'bearish': bearish_count,
                'neutral': neutral_count
            },
            'average_confidence': f"{avg_confidence:.1%}",
            'highest_confidence': f"{max(p.confidence for p in patterns):.1%}",
            'most_common_category': max(category_counts.items(), key=lambda x: x[1])[0] if category_counts else None
        }

    def _generate_recommendations(self, result: AnalysisResult) -> None:
        """Generate trading recommendations based on analysis."""
        recommendations = []
        patterns = result.patterns
        indicators = result.technical_indicators

        if not patterns:
            recommendations.append("No significant patterns detected. Consider waiting for clearer signals.")
            result.recommendations = recommendations
            return

        # Pattern-based recommendations
        bullish_patterns = [p for p in patterns if p.get('is_bullish', False)]
        bearish_patterns = [p for p in patterns if p.get('is_bearish', False)]

        if len(bullish_patterns) > len(bearish_patterns):
            recommendations.append("📈 Bullish bias: More bullish patterns detected than bearish")
            if bullish_patterns and bullish_patterns[0]['confidence_raw'] > 0.7:
                recommendations.append(
                    f"🔥 Strong bullish signal: {bullish_patterns[0]['type']} "
                    f"with {bullish_patterns[0]['confidence']} confidence"
                )
        elif len(bearish_patterns) > len(bullish_patterns):
            recommendations.append("📉 Bearish bias: More bearish patterns detected than bullish")
            if bearish_patterns and bearish_patterns[0]['confidence_raw'] > 0.7:
                recommendations.append(
                    f"⚠️ Strong bearish signal: {bearish_patterns[0]['type']} "
                    f"with {bearish_patterns[0]['confidence']} confidence"
                )
        else:
            recommendations.append("⚖️ Mixed signals: Equal bullish and bearish patterns detected")

        # Indicator-based recommendations
        if 'rsi' in indicators and indicators['rsi'].get('current'):
            rsi_val = indicators['rsi']['current']
            if indicators['rsi'].get('overbought'):
                recommendations.append(f"⚠️ RSI overbought at {rsi_val:.1f} - potential pullback ahead")
            elif indicators['rsi'].get('oversold'):
                recommendations.append(f"💡 RSI oversold at {rsi_val:.1f} - potential bounce opportunity")

        # Volume confirmation
        volume_confirmed = sum(1 for p in patterns if p.get('volume_confirmation', False))
        if volume_confirmed > len(patterns) * 0.6:
            recommendations.append("✅ Good volume confirmation on most patterns")
        elif volume_confirmed < len(patterns) * 0.3:
            recommendations.append("⚠️ Weak volume confirmation - patterns may be less reliable")

        # Risk management
        recommendations.append("💡 Always use proper risk management and position sizing")
        recommendations.append("📊 Consider multiple timeframes for confirmation")

        result.recommendations = recommendations

    def _add_ticker_info(self, data_frame: PriceDataFrame, result: AnalysisResult) -> None:
        """Add ticker information to result."""
        try:
            ticker_info = {
                'symbol': data_frame.symbol or result.symbol,
                'data_points': len(data_frame),
                'data_interval': data_frame.timeframe,
                'last_update': data_frame.data[-1].timestamp.strftime("%Y-%m-%d %H:%M:%S") if data_frame.data else None
            }

            # Add price change information
            if len(data_frame) > 1:
                first_price = data_frame.data[0].close
                last_price = data_frame.data[-1].close
                price_change = (last_price - first_price) / first_price

                ticker_info['price_change'] = {
                    'absolute': last_price - first_price,
                    'percentage': price_change,
                    'first_price': first_price,
                    'last_price': last_price
                }

            # Try to get current price
            try:
                current_price = self.data_fetcher.get_current_price(data_frame.symbol)
                if current_price:
                    ticker_info['current_price'] = current_price
            except Exception:
                pass

            result.ticker_info = ticker_info

        except Exception as e:
            self.logger.warning(f"Failed to add ticker info: {e}")

    def _format_ml_predictions(self, ml_predictions: Any) -> Dict[str, Any]:
        """Format ML predictions for output."""
        try:
            # Handle both dict and object formats
            if isinstance(ml_predictions, dict):
                # Already in dict format, return as-is
                return ml_predictions
            
            # Object format - convert to dict
            result = {}
            
            # Price forecast
            price_forecast = getattr(ml_predictions, 'price_forecast', None)
            if price_forecast:
                if isinstance(price_forecast, dict):
                    result['price_forecast'] = price_forecast
                else:
                    result['price_forecast'] = {
                        'daily_prices': getattr(price_forecast, 'daily_prices', []),
                        'expected_return': f"{getattr(price_forecast, 'expected_return', 0):.2%}",
                        'prediction_dates': [
                            d.strftime("%Y-%m-%d") if hasattr(d, 'strftime') else str(d)
                            for d in getattr(price_forecast, 'prediction_dates', [])
                        ],
                        'confidence_intervals': getattr(price_forecast, 'confidence_intervals', {}),
                        'probability_up': getattr(price_forecast, 'probability_up', 0.5)
                    }
            
            # Trend forecast
            trend_forecast = getattr(ml_predictions, 'trend_forecast', None)
            if trend_forecast:
                if isinstance(trend_forecast, dict):
                    result['trend_forecast'] = trend_forecast
                else:
                    result['trend_forecast'] = {
                        'trend_7d': getattr(trend_forecast, 'trend_7d', 'Unknown'),
                        'trend_30d': getattr(trend_forecast, 'trend_30d', 'Unknown'),
                        'trend_strength': f"{getattr(trend_forecast, 'trend_strength', 0):.1%}",
                        'reversal_probability': f"{getattr(trend_forecast, 'reversal_probability', 0):.1%}"
                    }
            
            # Market regime
            market_regime = getattr(ml_predictions, 'market_regime', None)
            if market_regime:
                if isinstance(market_regime, dict):
                    result['market_regime'] = market_regime
                else:
                    regime_prob = getattr(market_regime, 'regime_probability', {})
                    if not isinstance(regime_prob, dict):
                        regime_prob = {}
                    result['market_regime'] = {
                        'current_regime': getattr(market_regime, 'current_regime', 'Unknown'),
                        'regime_probability': {k: f"{v:.1%}" for k, v in regime_prob.items()},
                        'regime_persistence': f"{getattr(market_regime, 'regime_persistence', 0):.1f} days"
                    }
            
            result['model_performance'] = getattr(ml_predictions, 'model_performance', {})
            result['feature_importance'] = getattr(ml_predictions, 'feature_importance', {})
            
            pred_timestamp = getattr(ml_predictions, 'prediction_timestamp', None)
            if pred_timestamp:
                if hasattr(pred_timestamp, 'strftime'):
                    result['prediction_timestamp'] = pred_timestamp.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    result['prediction_timestamp'] = str(pred_timestamp)
            
            return result
        except Exception as e:
            self.logger.error(f"Failed to format ML predictions: {e}")
            return {'error': 'Failed to format ML predictions'}

    # Utility methods for backward compatibility and convenience

    def get_supported_tickers(self) -> List[str]:
        """Get list of commonly supported ticker symbols."""
        try:
            return self.data_fetcher.get_supported_tickers()
        except Exception as e:
            self.logger.error(f"Failed to get supported tickers: {e}")
            return []

    def search_tickers(self, query: str, limit: int = 10) -> List[Dict[str, str]]:
        """
        Search for cryptocurrency tickers matching a query.

        Args:
            query: Search query (coin name or symbol)
            limit: Maximum number of results

        Returns:
            List of matching tickers with symbol, name, and id
        """
        try:
            return self.data_fetcher.search_tickers(query, limit)
        except Exception as e:
            self.logger.error(f"Ticker search failed: {e}")
            return []

    def get_current_price(self, ticker: str) -> Optional[float]:
        """Get current price for a cryptocurrency."""
        try:
            return self.data_fetcher.get_current_price(ticker)
        except Exception as e:
            self.logger.error(f"Failed to get current price for {ticker}: {e}")
            return None



class ResultValidator:
    """
    Validator for analysis results.

    This class validates and sanitizes analysis results before returning them
    to ensure data integrity and security.

    Example:
        >>> validator = ResultValidator()
        >>> is_valid, errors = validator.validate_result(result)
        >>> if not is_valid:
        ...     print(f"Validation errors: {errors}")
    """

    def __init__(self) -> None:
        """Initialize result validator."""
        self.logger = logging.getLogger(__name__)

    def validate_result(self, result: AnalysisResult) -> Tuple[bool, List[str]]:
        """
        Validate analysis result for completeness and correctness.

        Args:
            result: AnalysisResult to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Validate required fields
        if not self._validate_required_fields(result, errors):
            return False, errors

        # Validate data types
        if not self._validate_data_types(result, errors):
            return False, errors

        # Validate data ranges
        if not self._validate_data_ranges(result, errors):
            return False, errors

        # Sanitize result
        self._sanitize_result(result)

        return len(errors) == 0, errors

    def _validate_required_fields(
        self,
        result: AnalysisResult,
        errors: List[str]
    ) -> bool:
        """Validate that required fields are present."""
        required_fields = ['success', 'symbol', 'analysis_timestamp']

        for field in required_fields:
            if not hasattr(result, field) or getattr(result, field) is None:
                errors.append(f"Missing required field: {field}")

        # If success is True, additional fields are required
        if result.success:
            success_required = ['patterns', 'pattern_summary', 'data_summary']
            for field in success_required:
                if not hasattr(result, field) or getattr(result, field) is None:
                    errors.append(f"Missing required field for successful analysis: {field}")

        return len(errors) == 0

    def _validate_data_types(
        self,
        result: AnalysisResult,
        errors: List[str]
    ) -> bool:
        """Validate data types of result fields."""
        # Validate boolean fields
        if not isinstance(result.success, bool):
            errors.append(f"Field 'success' must be boolean, got {type(result.success)}")

        # Validate string fields
        if not isinstance(result.symbol, str):
            errors.append(f"Field 'symbol' must be string, got {type(result.symbol)}")

        # Validate list fields
        if not isinstance(result.patterns, list):
            errors.append(f"Field 'patterns' must be list, got {type(result.patterns)}")

        if not isinstance(result.errors, list):
            errors.append(f"Field 'errors' must be list, got {type(result.errors)}")

        if not isinstance(result.warnings, list):
            errors.append(f"Field 'warnings' must be list, got {type(result.warnings)}")

        if not isinstance(result.recommendations, list):
            errors.append(f"Field 'recommendations' must be list, got {type(result.recommendations)}")

        # Validate dict fields
        if not isinstance(result.pattern_summary, dict):
            errors.append(f"Field 'pattern_summary' must be dict, got {type(result.pattern_summary)}")

        if not isinstance(result.technical_indicators, dict):
            errors.append(f"Field 'technical_indicators' must be dict, got {type(result.technical_indicators)}")

        if not isinstance(result.ticker_info, dict):
            errors.append(f"Field 'ticker_info' must be dict, got {type(result.ticker_info)}")

        if not isinstance(result.configuration_used, dict):
            errors.append(f"Field 'configuration_used' must be dict, got {type(result.configuration_used)}")

        if not isinstance(result.data_summary, dict):
            errors.append(f"Field 'data_summary' must be dict, got {type(result.data_summary)}")

        # Validate numeric fields
        if not isinstance(result.analysis_time, (int, float)):
            errors.append(f"Field 'analysis_time' must be numeric, got {type(result.analysis_time)}")

        # Validate datetime field
        if result.analysis_timestamp and not isinstance(result.analysis_timestamp, datetime):
            errors.append(f"Field 'analysis_timestamp' must be datetime, got {type(result.analysis_timestamp)}")

        return len(errors) == 0

    def _validate_data_ranges(
        self,
        result: AnalysisResult,
        errors: List[str]
    ) -> bool:
        """Validate data ranges and values."""
        # Validate analysis_time is non-negative
        if result.analysis_time < 0:
            errors.append(f"Field 'analysis_time' must be non-negative, got {result.analysis_time}")

        # Validate analysis_time is reasonable (< 1 hour)
        if result.analysis_time > 3600:
            errors.append(f"Field 'analysis_time' is unreasonably large: {result.analysis_time}s")

        # Validate symbol is not empty
        if not result.symbol or len(result.symbol.strip()) == 0:
            errors.append("Field 'symbol' cannot be empty")

        # Validate symbol length
        if len(result.symbol) > 20:
            errors.append(f"Field 'symbol' is too long: {len(result.symbol)} characters")

        # Validate patterns
        for i, pattern in enumerate(result.patterns):
            if not isinstance(pattern, dict):
                errors.append(f"Pattern {i} must be a dictionary")
                continue

            # Validate pattern has required fields
            required_pattern_fields = ['type', 'confidence', 'category']
            for field in required_pattern_fields:
                if field not in pattern:
                    errors.append(f"Pattern {i} missing required field: {field}")

            # Validate confidence_raw is in valid range
            if 'confidence_raw' in pattern:
                conf = pattern['confidence_raw']
                if not isinstance(conf, (int, float)) or conf < 0 or conf > 1:
                    errors.append(f"Pattern {i} confidence_raw must be between 0 and 1, got {conf}")

        # Validate pattern_summary
        if result.pattern_summary and 'total' in result.pattern_summary:
            total = result.pattern_summary['total']
            if not isinstance(total, int) or total < 0:
                errors.append(f"pattern_summary.total must be non-negative integer, got {total}")

            # Validate total matches patterns length
            if total != len(result.patterns):
                errors.append(
                    f"pattern_summary.total ({total}) does not match patterns length ({len(result.patterns)})"
                )

        return len(errors) == 0

    def _sanitize_result(self, result: AnalysisResult) -> None:
        """
        Sanitize result data to prevent security issues.

        This includes:
        - Removing potentially sensitive information
        - Truncating overly long strings
        - Normalizing data formats
        """
        # Sanitize symbol (remove special characters, limit length)
        result.symbol = self._sanitize_string(result.symbol, max_length=20)

        # Sanitize error messages (truncate if too long)
        result.errors = [self._sanitize_string(err, max_length=500) for err in result.errors]

        # Sanitize warnings
        result.warnings = [self._sanitize_string(warn, max_length=500) for warn in result.warnings]

        # Sanitize recommendations
        result.recommendations = [self._sanitize_string(rec, max_length=500) for rec in result.recommendations]

        # Sanitize chart output (limit size)
        if result.chart and len(result.chart) > 100000:  # 100KB limit
            self.logger.warning("Chart output truncated due to size")
            result.chart = result.chart[:100000] + "\n... [truncated]"

        # Sanitize pattern descriptions
        for pattern in result.patterns:
            if 'description' in pattern:
                pattern['description'] = self._sanitize_string(pattern['description'], max_length=1000)

    def _sanitize_string(self, value: str, max_length: int = 500) -> str:
        """
        Sanitize a string value.

        Args:
            value: String to sanitize
            max_length: Maximum allowed length

        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            value = str(value)

        # Remove null bytes
        value = value.replace('\x00', '')

        # Truncate if too long
        if len(value) > max_length:
            value = value[:max_length] + "..."

        return value

    def validate_and_sanitize(self, result: AnalysisResult) -> AnalysisResult:
        """
        Validate and sanitize result, returning the sanitized version.

        Args:
            result: AnalysisResult to validate and sanitize

        Returns:
            Sanitized AnalysisResult

        Raises:
            ValidationError: If validation fails
        """
        is_valid, errors = self.validate_result(result)

        if not is_valid:
            error_msg = "Result validation failed: " + "; ".join(errors)
            self.logger.error(error_msg)
            raise ValidationError(
                error_msg,
                details={'validation_errors': errors}
            )

        return result


# Add validation to PatternAnalyzer
def _add_result_validation_to_analyzer():
    """Add result validation to PatternAnalyzer class."""
    original_analyze_ticker = PatternAnalyzer.analyze_ticker
    original_analyze_from_csv = PatternAnalyzer.analyze_from_csv
    original_analyze_from_json = PatternAnalyzer.analyze_from_json
    original_analyze_dataframe = PatternAnalyzer.analyze_dataframe

    validator = ResultValidator()

    def validated_analyze_ticker(self, *args, **kwargs):
        result = original_analyze_ticker(self, *args, **kwargs)
        try:
            return validator.validate_and_sanitize(result)
        except ValidationError as e:
            self.logger.error(f"Result validation failed: {e}")
            result.errors.append(f"Result validation failed: {str(e)}")
            return result

    def validated_analyze_from_csv(self, *args, **kwargs):
        result = original_analyze_from_csv(self, *args, **kwargs)
        try:
            return validator.validate_and_sanitize(result)
        except ValidationError as e:
            self.logger.error(f"Result validation failed: {e}")
            result.errors.append(f"Result validation failed: {str(e)}")
            return result

    def validated_analyze_from_json(self, *args, **kwargs):
        result = original_analyze_from_json(self, *args, **kwargs)
        try:
            return validator.validate_and_sanitize(result)
        except ValidationError as e:
            self.logger.error(f"Result validation failed: {e}")
            result.errors.append(f"Result validation failed: {str(e)}")
            return result

    def validated_analyze_dataframe(self, *args, **kwargs):
        result = original_analyze_dataframe(self, *args, **kwargs)
        try:
            return validator.validate_and_sanitize(result)
        except ValidationError as e:
            self.logger.error(f"Result validation failed: {e}")
            result.errors.append(f"Result validation failed: {str(e)}")
            return result

    PatternAnalyzer.analyze_ticker = validated_analyze_ticker
    PatternAnalyzer.analyze_from_csv = validated_analyze_from_csv
    PatternAnalyzer.analyze_from_json = validated_analyze_from_json
    PatternAnalyzer.analyze_dataframe = validated_analyze_dataframe


# Apply validation wrapper
_add_result_validation_to_analyzer()
