"""Main pattern analyzer orchestrator with configuration support."""

from typing import List, Dict, Optional, Any
import time
import logging
from datetime import datetime

from .data.models import PriceDataFrame
from .data.parsers import CSVParser, JSONParser
from .data.package_fetcher import PackageDataFetcher
from .data.validator import DataValidator
from .patterns.geometric import GeometricPatternAnalyzer
from .patterns.reversal import ReversalPatternAnalyzer
from .patterns.advanced import AdvancedPatternAnalyzer
from .patterns.divergence import DivergenceAnalyzer
from .patterns.candlestick import CandlestickPatternAnalyzer
from .patterns.types import DetectedPattern, PatternCategory
from .visualization.terminal_chart import TerminalChart
from .indicators.technical import TechnicalIndicators
from .config.manager import ConfigManager
from .storage.result_storage import AnalysisResultStorage
from .ml.prediction.predictor import MLPredictor


class PatternAnalyzer:
    """Main orchestrator for cryptocurrency chart pattern analysis with configuration support."""
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """Initialize the pattern analyzer with all components."""
        # Configuration management
        self.config = config_manager or ConfigManager()
        
        # Result storage
        self.storage = AnalysisResultStorage() if self.config.analysis.save_results else None
        
        # ML Predictor
        self.ml_predictor = MLPredictor()
        
        # Data handling
        self.csv_parser = CSVParser()
        self.json_parser = JSONParser()
        self.data_fetcher = PackageDataFetcher()
        self.validator = DataValidator()
        
        # Pattern detection
        self.geometric_analyzer = GeometricPatternAnalyzer()
        self.reversal_analyzer = ReversalPatternAnalyzer()
        self.advanced_analyzer = AdvancedPatternAnalyzer()
        self.divergence_analyzer = DivergenceAnalyzer()
        self.candlestick_analyzer = CandlestickPatternAnalyzer()
        
        # Technical indicators
        self.technical_indicators = TechnicalIndicators()
        
        # Visualization
        self.chart_renderer = TerminalChart(
            width=self.config.display.chart_width,
            height=self.config.display.chart_height,
            enable_colors=self.config.display.enable_colors
        )
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
    def analyze_from_csv(self, csv_data: str, sensitivity: Optional[float] = None) -> Dict[str, Any]:
        """
        Analyze patterns from CSV data.
        
        Args:
            csv_data: CSV formatted price data
            sensitivity: Pattern detection sensitivity (0.0 to 1.0)
            
        Returns:
            Analysis results dictionary
        """
        try:
            # Parse data
            data_frame = self.csv_parser.parse(csv_data)
            return self._perform_analysis(data_frame, sensitivity)
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'suggestions': [
                    "Check CSV format - ensure required columns: timestamp,open,high,low,close,volume",
                    "Verify data quality - no missing values or invalid prices",
                    "Use the sample format: " + self.csv_parser.get_sample_format()
                ]
            }
    
    def analyze_from_json(self, json_data: str, sensitivity: Optional[float] = None) -> Dict[str, Any]:
        """
        Analyze patterns from JSON data.
        
        Args:
            json_data: JSON formatted price data
            sensitivity: Pattern detection sensitivity (0.0 to 1.0)
            
        Returns:
            Analysis results dictionary
        """
        try:
            # Parse data
            data_frame = self.json_parser.parse(json_data)
            return self._perform_analysis(data_frame, sensitivity)
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'suggestions': [
                    "Check JSON format - ensure required fields: timestamp,open,high,low,close,volume",
                    "Verify JSON structure is valid",
                    "Use the sample format: " + self.json_parser.get_sample_format()
                ]
            }
    
    def analyze_dataframe(self, data_frame: PriceDataFrame, 
                         sensitivity: Optional[float] = None) -> Dict[str, Any]:
        """
        Analyze patterns from PriceDataFrame.
        
        Args:
            data_frame: Price data frame
            sensitivity: Pattern detection sensitivity (0.0 to 1.0)
            
        Returns:
            Analysis results dictionary
        """
        return self._perform_analysis(data_frame, sensitivity)
    
    def _perform_analysis(self, data_frame: PriceDataFrame, 
                         sensitivity: Optional[float] = None) -> Dict[str, Any]:
        """Perform comprehensive pattern analysis with configuration support."""
        start_time = time.time()
        
        # Use configured sensitivity if not provided
        if sensitivity is None:
            sensitivity = self.config.sensitivity.geometric_patterns
        
        self.logger.info(f"Starting analysis with sensitivity: {sensitivity}")
        
        # Validate data
        validation_result = self.validator.validate_price_dataframe(data_frame)
        
        if not validation_result['is_valid']:
            self.logger.error("Data validation failed")
            return {
                'success': False,
                'error': 'Data validation failed',
                'validation_errors': validation_result['errors'],
                'suggestions': validation_result['suggestions']
            }
        
        # Check data size constraints
        if len(data_frame) < self.config.analysis.min_data_points:
            return {
                'success': False,
                'error': f'Insufficient data points. Need at least {self.config.analysis.min_data_points}, got {len(data_frame)}',
                'suggestions': ['Provide more historical data for better pattern detection']
            }
        
        if len(data_frame) > self.config.analysis.max_data_points:
            self.logger.warning(f"Data truncated from {len(data_frame)} to {self.config.analysis.max_data_points} points")
            data_frame = PriceDataFrame(
                data=data_frame.data[-self.config.analysis.max_data_points:],
                symbol=data_frame.symbol,
                timeframe=data_frame.timeframe
            )
        
        # Detect patterns based on configuration
        patterns = self._detect_all_patterns(data_frame, sensitivity)
        
        # Filter patterns based on configuration
        filtered_patterns = self._filter_patterns(patterns)
        
        # Calculate technical indicators
        indicators = self._calculate_indicators(data_frame)
        
        # Generate chart
        chart_output = self.chart_renderer.render_chart(data_frame, filtered_patterns)
        
        # Generate ML predictions (no caching for fresh predictions each time)
        ml_predictions = None
        try:
            ml_predictions = self.ml_predictor.predict(data_frame, filtered_patterns)
            self.logger.info("ML predictions generated successfully")
        except Exception as e:
            self.logger.warning(f"ML prediction failed: {e}")
            ml_predictions = None
        
        # Calculate analysis time
        analysis_time = time.time() - start_time
        
        # Calculate analysis time
        analysis_time = time.time() - start_time
        
        self.logger.info(f"Analysis completed in {analysis_time:.2f} seconds. Found {len(filtered_patterns)} patterns.")
        
        # Compile results
        results = {
            'success': True,
            'analysis_timestamp': datetime.now(),
            'analysis_time_seconds': analysis_time,
            'data_summary': validation_result['statistics'],
            'patterns_found': len(filtered_patterns),
            'patterns': self._format_patterns_for_output(filtered_patterns),
            'pattern_summary': self._create_pattern_summary(filtered_patterns),
            'technical_indicators': indicators,
            'chart': chart_output,
            'recommendations': self._generate_recommendations(filtered_patterns, indicators),
            'configuration_used': {
                'sensitivity_level': self.config.sensitivity.level.value,
                'patterns_enabled': len(self.config.patterns.get_enabled_patterns()),
                'colors_enabled': self.config.display.enable_colors
            },
            'ml_predictions': self._format_ml_predictions(ml_predictions) if ml_predictions else None
        }
        
        # Skip result storage for faster analysis
        # Results are not saved to disk for performance
        
        return results
    
    def _detect_all_patterns(self, data_frame: PriceDataFrame, 
                           sensitivity: float) -> List[DetectedPattern]:
        """Detect all available patterns based on configuration."""
        all_patterns = []
        
        try:
            # Geometric patterns (if enabled)
            if self.config.patterns.enabled_geometric:
                geometric_sensitivity = self.config.sensitivity.get_pattern_sensitivity('geometric')
                
                if self.config.patterns.is_pattern_enabled('ascending_triangle') or \
                   self.config.patterns.is_pattern_enabled('descending_triangle') or \
                   self.config.patterns.is_pattern_enabled('symmetrical_triangle'):
                    triangles = self.geometric_analyzer.detect_triangle_patterns(data_frame, geometric_sensitivity)
                    all_patterns.extend(triangles)
                
                if self.config.patterns.is_pattern_enabled('bull_flag') or \
                   self.config.patterns.is_pattern_enabled('bear_flag'):
                    flags = self.geometric_analyzer.detect_flag_patterns(data_frame, geometric_sensitivity)
                    all_patterns.extend(flags)
                
                if self.config.patterns.is_pattern_enabled('cup_and_handle'):
                    cups = self.geometric_analyzer.detect_cup_and_handle(data_frame, geometric_sensitivity)
                    all_patterns.extend(cups)
                
                if self.config.patterns.is_pattern_enabled('rising_wedge') or \
                   self.config.patterns.is_pattern_enabled('falling_wedge'):
                    wedges = self.geometric_analyzer.detect_wedge_patterns(data_frame, geometric_sensitivity)
                    all_patterns.extend(wedges)
                
                if self.config.patterns.is_pattern_enabled('rectangle') or \
                   self.config.patterns.is_pattern_enabled('channel'):
                    rectangles = self.geometric_analyzer.detect_rectangle_patterns(data_frame, geometric_sensitivity)
                    all_patterns.extend(rectangles)
            
            # Reversal patterns (if enabled)
            if self.config.patterns.enabled_reversal:
                reversal_sensitivity = self.config.sensitivity.get_pattern_sensitivity('reversal')
                
                if self.config.patterns.is_pattern_enabled('double_top') or \
                   self.config.patterns.is_pattern_enabled('double_bottom') or \
                   self.config.patterns.is_pattern_enabled('triple_top') or \
                   self.config.patterns.is_pattern_enabled('triple_bottom'):
                    double_triple = self.reversal_analyzer.detect_double_triple_patterns(data_frame, reversal_sensitivity)
                    all_patterns.extend(double_triple)
                
                if self.config.patterns.is_pattern_enabled('head_shoulders'):
                    head_shoulders = self.reversal_analyzer.detect_head_and_shoulders_patterns(data_frame, reversal_sensitivity)
                    all_patterns.extend(head_shoulders)
            
            # Advanced patterns (if enabled)
            if self.config.patterns.is_pattern_enabled('diamond'):
                diamonds = self.advanced_analyzer.detect_diamond_patterns(data_frame, sensitivity)
                all_patterns.extend(diamonds)
            
            if self.config.patterns.is_pattern_enabled('expanding_triangle'):
                expanding = self.advanced_analyzer.detect_expanding_triangle_patterns(data_frame, sensitivity)
                all_patterns.extend(expanding)
            
            # Harmonic patterns (if enabled)
            if self.config.patterns.enabled_harmonic:
                harmonic_sensitivity = self.config.sensitivity.get_pattern_sensitivity('harmonic')
                
                if any(self.config.patterns.is_pattern_enabled(pattern) for pattern in 
                      ['gartley', 'butterfly', 'bat', 'crab', 'abcd', 'cypher']):
                    harmonics = self.advanced_analyzer.detect_harmonic_patterns(data_frame, harmonic_sensitivity)
                    all_patterns.extend(harmonics)
            
            # Candlestick patterns (if enabled)
            if self.config.patterns.enabled_candlestick:
                candlestick_sensitivity = self.config.sensitivity.get_pattern_sensitivity('candlestick')
                
                # Single candlestick patterns
                single_candles = self.candlestick_analyzer.detect_single_candlestick_patterns(data_frame, candlestick_sensitivity)
                all_patterns.extend(single_candles)
                
                # Multi-candlestick patterns
                multi_candles = self.candlestick_analyzer.detect_multi_candlestick_patterns(data_frame, candlestick_sensitivity)
                all_patterns.extend(multi_candles)
            
            # Divergence patterns (if enabled)
            if self.config.patterns.enabled_divergence:
                divergence_sensitivity = self.config.sensitivity.get_pattern_sensitivity('divergence')
                
                if self.config.patterns.is_pattern_enabled('bullish_divergence') or \
                   self.config.patterns.is_pattern_enabled('bearish_divergence') or \
                   self.config.patterns.is_pattern_enabled('hidden_divergence'):
                    divergences = self.divergence_analyzer.detect_price_indicator_divergence(data_frame, divergence_sensitivity)
                    all_patterns.extend(divergences)
            
        except Exception as e:
            self.logger.warning(f"Pattern detection error: {e}")
        
        # Sort by confidence
        all_patterns.sort(key=lambda p: p.confidence, reverse=True)
        
        return all_patterns
    
    def _filter_patterns(self, patterns: List[DetectedPattern]) -> List[DetectedPattern]:
        """Filter patterns based on configuration settings."""
        filtered_patterns = []
        
        # Group patterns by type for limiting
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
            # Sort by confidence and take top N
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
    
    def _get_category_key(self, category) -> str:
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
    
    def _remove_overlapping_patterns(self, patterns: List[DetectedPattern]) -> List[DetectedPattern]:
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
    
    def _calculate_indicators(self, data_frame: PriceDataFrame) -> Dict[str, Any]:
        """Calculate technical indicators."""
        indicators = {}
        
        try:
            # RSI
            rsi = self.technical_indicators.calculate_rsi(data_frame)
            current_rsi = next((val for val in reversed(rsi) if val is not None), None)
            indicators['rsi'] = {
                'current': current_rsi,
                'overbought': current_rsi and current_rsi > 70,
                'oversold': current_rsi and current_rsi < 30
            }
            
            # MACD
            macd = self.technical_indicators.calculate_macd(data_frame)
            current_macd = next((val for val in reversed(macd['macd']) if val is not None), None)
            current_signal = next((val for val in reversed(macd['signal']) if val is not None), None)
            
            indicators['macd'] = {
                'current_macd': current_macd,
                'current_signal': current_signal,
                'bullish_crossover': current_macd and current_signal and current_macd > current_signal
            }
            
        except Exception as e:
            indicators['error'] = f"Indicator calculation error: {e}"
        
        return indicators
    
    def _format_patterns_for_output(self, patterns: List[DetectedPattern]) -> List[Dict[str, Any]]:
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
    
    def _create_pattern_summary(self, patterns: List[DetectedPattern]) -> Dict[str, Any]:
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
    
    def _generate_recommendations(self, patterns: List[DetectedPattern], 
                                indicators: Dict[str, Any]) -> List[str]:
        """Generate trading recommendations based on analysis."""
        recommendations = []
        
        if not patterns:
            recommendations.append("No significant patterns detected. Consider waiting for clearer signals.")
            return recommendations
        
        # Pattern-based recommendations
        bullish_patterns = [p for p in patterns if p.is_bullish()]
        bearish_patterns = [p for p in patterns if p.is_bearish()]
        
        if len(bullish_patterns) > len(bearish_patterns):
            recommendations.append("📈 Bullish bias: More bullish patterns detected than bearish")
            if bullish_patterns[0].confidence > 0.7:
                recommendations.append(f"🔥 Strong bullish signal: {bullish_patterns[0].pattern_type.value.replace('_', ' ').title()} with {bullish_patterns[0].confidence:.1%} confidence")
        
        elif len(bearish_patterns) > len(bullish_patterns):
            recommendations.append("📉 Bearish bias: More bearish patterns detected than bullish")
            if bearish_patterns[0].confidence > 0.7:
                recommendations.append(f"⚠️ Strong bearish signal: {bearish_patterns[0].pattern_type.value.replace('_', ' ').title()} with {bearish_patterns[0].confidence:.1%} confidence")
        
        else:
            recommendations.append("⚖️ Mixed signals: Equal bullish and bearish patterns detected")
        
        # Indicator-based recommendations
        if 'rsi' in indicators and indicators['rsi']['current']:
            rsi_val = indicators['rsi']['current']
            if indicators['rsi']['overbought']:
                recommendations.append(f"⚠️ RSI overbought at {rsi_val:.1f} - potential pullback ahead")
            elif indicators['rsi']['oversold']:
                recommendations.append(f"💡 RSI oversold at {rsi_val:.1f} - potential bounce opportunity")
        
        # Volume confirmation
        volume_confirmed = sum(1 for p in patterns if p.volume_profile.volume_confirmation)
        if volume_confirmed > len(patterns) * 0.6:
            recommendations.append("✅ Good volume confirmation on most patterns")
        elif volume_confirmed < len(patterns) * 0.3:
            recommendations.append("⚠️ Weak volume confirmation - patterns may be less reliable")
        
        # Risk management
        recommendations.append("💡 Always use proper risk management and position sizing")
        recommendations.append("📊 Consider multiple timeframes for confirmation")
        
        return recommendations
    
    def get_pattern_details(self, pattern_index: int, patterns: List[DetectedPattern]) -> str:
        """Get detailed information about a specific pattern."""
        if pattern_index < 0 or pattern_index >= len(patterns):
            return "Invalid pattern index"
        
        pattern = patterns[pattern_index]
        
        details = [
            f"Pattern: {pattern.pattern_type.value.replace('_', ' ').title()}",
            f"Category: {pattern.category.value}",
            f"Confidence: {pattern.confidence:.1%}",
            f"Duration: {pattern.get_duration_days():.1f} days",
            f"Start: {pattern.start_time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"End: {pattern.end_time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "Description:",
            pattern.description,
            "",
            "Key Levels:"
        ]
        
        for key, value in pattern.key_levels.items():
            if isinstance(value, (int, float)):
                details.append(f"  {key.replace('_', ' ').title()}: {value:.4f}")
            else:
                details.append(f"  {key.replace('_', ' ').title()}: {value}")
        
        details.extend([
            "",
            "Volume Profile:",
            f"  Average Volume: {pattern.volume_profile.avg_volume:,.0f}",
            f"  Volume Trend: {pattern.volume_profile.volume_trend}",
            f"  Volume Confirmation: {'Yes' if pattern.volume_profile.volume_confirmation else 'No'}"
        ])
        
        return "\n".join(details)
    
    def set_sensitivity(self, sensitivity: float):
        """Set pattern detection sensitivity."""
        self.sensitivity = max(0.0, min(1.0, sensitivity))
    
    def set_min_confidence(self, min_confidence: float):
        """Set minimum confidence threshold for pattern reporting."""
        self.min_confidence = max(0.0, min(1.0, min_confidence))
    
    def set_chart_dimensions(self, width: int, height: int):
        """Set chart rendering dimensions."""
        self.chart_renderer.set_dimensions(width, height)
    
    def enable_colors(self, enabled: bool):
        """Enable or disable color output."""
        self.chart_renderer.enable_colors(enabled)
    
    # Configuration management methods
    def update_sensitivity_settings(self, **kwargs):
        """Update sensitivity settings."""
        self.config.update_sensitivity(**kwargs)
        self.logger.info("Sensitivity settings updated")
    
    def update_display_settings(self, **kwargs):
        """Update display settings."""
        self.config.update_display(**kwargs)
        
        # Update chart renderer with new settings
        self.chart_renderer = TerminalChart(
            width=self.config.display.chart_width,
            height=self.config.display.chart_height,
            enable_colors=self.config.display.enable_colors
        )
        self.logger.info("Display settings updated")
    
    def update_pattern_settings(self, **kwargs):
        """Update pattern settings."""
        self.config.update_patterns(**kwargs)
        self.logger.info("Pattern settings updated")
    
    def set_sensitivity_preset(self, level: str):
        """Set sensitivity to a predefined level."""
        from .config.settings import SensitivityLevel
        
        try:
            sensitivity_level = SensitivityLevel(level.lower())
            self.config.set_sensitivity_preset(sensitivity_level)
            self.logger.info(f"Sensitivity preset set to: {level}")
        except ValueError:
            self.logger.error(f"Invalid sensitivity level: {level}")
            raise ValueError(f"Invalid sensitivity level. Choose from: {[l.value for l in SensitivityLevel]}")
    
    def enable_pattern_type(self, pattern_name: str, enabled: bool = True):
        """Enable or disable a specific pattern type."""
        self.config.enable_pattern(pattern_name, enabled)
        action = "enabled" if enabled else "disabled"
        self.logger.info(f"Pattern '{pattern_name}' {action}")
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get summary of current configuration."""
        return self.config.get_config_summary()
    
    def validate_configuration(self) -> Dict[str, list]:
        """Validate current configuration."""
        return self.config.validate_config()
    
    def export_configuration(self, file_path: str) -> bool:
        """Export configuration to file."""
        success = self.config.export_config(file_path)
        if success:
            self.logger.info(f"Configuration exported to: {file_path}")
        else:
            self.logger.error(f"Failed to export configuration to: {file_path}")
        return success
    
    def import_configuration(self, file_path: str) -> bool:
        """Import configuration from file."""
        success = self.config.import_config(file_path)
        if success:
            # Update chart renderer with new settings
            self.chart_renderer = TerminalChart(
                width=self.config.display.chart_width,
                height=self.config.display.chart_height,
                enable_colors=self.config.display.enable_colors
            )
            self.logger.info(f"Configuration imported from: {file_path}")
        else:
            self.logger.error(f"Failed to import configuration from: {file_path}")
        return success
    
    def reset_configuration(self):
        """Reset configuration to defaults."""
        self.config.reset_to_defaults()
        
        # Update chart renderer with default settings
        self.chart_renderer = TerminalChart(
            width=self.config.display.chart_width,
            height=self.config.display.chart_height,
            enable_colors=self.config.display.enable_colors
        )
        self.logger.info("Configuration reset to defaults")
    
    def create_user_preset(self, name: str, description: str = "") -> bool:
        """Create a user-defined preset from current settings."""
        success = self.config.create_user_preset(name, description)
        if success:
            self.logger.info(f"User preset '{name}' created")
        else:
            self.logger.error(f"Failed to create user preset '{name}'")
        return success
    
    def load_user_preset(self, name: str) -> bool:
        """Load a user-defined preset."""
        success = self.config.load_user_preset(name)
        if success:
            # Update chart renderer with preset settings
            self.chart_renderer = TerminalChart(
                width=self.config.display.chart_width,
                height=self.config.display.chart_height,
                enable_colors=self.config.display.enable_colors
            )
            self.logger.info(f"User preset '{name}' loaded")
        else:
            self.logger.error(f"Failed to load user preset '{name}'")
        return success
    
    def list_user_presets(self) -> Dict[str, str]:
        """List available user presets."""
        return self.config.list_user_presets()
    
    def get_pattern_configuration(self, pattern_name: str) -> Dict[str, Any]:
        """Get configuration for a specific pattern."""
        return self.config.get_pattern_config(pattern_name)
    
    def _format_ml_predictions(self, ml_result) -> Dict[str, Any]:
        """Format ML predictions for output."""
        try:
            return {
                'price_forecast': {
                    'next_7_days': ml_result.price_forecast.daily_prices,
                    'confidence_intervals': ml_result.price_forecast.confidence_intervals,
                    'probability_up': ml_result.price_forecast.probability_up,
                    'expected_return_7d': ml_result.price_forecast.expected_return,
                    'volatility_forecast': ml_result.price_forecast.risk_metrics.get('volatility', 0.03),
                    'prediction_dates': [d.strftime('%Y-%m-%d') for d in ml_result.price_forecast.prediction_dates]
                },
                'trend_forecast': {
                    'trend_7d': ml_result.trend_forecast.trend_7d,
                    'trend_30d': ml_result.trend_forecast.trend_30d,
                    'trend_strength': ml_result.trend_forecast.trend_strength,
                    'probabilities': ml_result.trend_forecast.trend_probability,
                    'reversal_probability': ml_result.trend_forecast.reversal_probability
                },
                'market_regime': {
                    'current': ml_result.market_regime.current_regime,
                    'confidence': max(ml_result.market_regime.regime_probability.values()),
                    'expected_duration': f"{ml_result.market_regime.regime_persistence:.0f} days",
                    'regime_probabilities': ml_result.market_regime.regime_probability
                },
                'model_performance': ml_result.model_performance,
                'feature_importance': ml_result.feature_importance,
                'prediction_timestamp': ml_result.prediction_timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            self.logger.error(f"Failed to format ML predictions: {e}")
            return {
                'error': 'ML prediction formatting failed',
                'fallback': True
            }
    
    # Analysis result management methods
    def load_saved_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a previously saved analysis result.
        
        Args:
            analysis_id: ID of the analysis to load
            
        Returns:
            Analysis result dictionary or None if not found
        """
        if not self.storage:
            self.logger.error("Storage not initialized. Enable save_results in configuration.")
            return None
        
        try:
            result = self.storage.load_analysis_result(analysis_id)
            if not result:
                self.logger.error(f"Analysis result not found: {analysis_id}")
                return None
            
            # Convert back to analysis format
            analysis_data = {
                'success': True,
                'analysis_timestamp': result.timestamp,
                'analysis_time_seconds': result.analysis_time_seconds,
                'data_summary': {
                    'total_points': result.data_points,
                    'start_time': result.data_start,
                    'end_time': result.data_end,
                    'symbol': result.symbol,
                    'timeframe': result.timeframe
                },
                'patterns_found': result.patterns_found,
                'patterns': result.patterns,
                'pattern_summary': result.pattern_summary,
                'technical_indicators': result.technical_indicators,
                'recommendations': result.recommendations,
                'configuration_used': {
                    'sensitivity_level': result.sensitivity_level,
                    'patterns_enabled': result.patterns_enabled,
                    'colors_enabled': result.colors_enabled
                },
                'loaded_from_storage': True,
                'original_analysis_id': result.analysis_id
            }
            
            self.logger.info(f"Analysis result loaded: {analysis_id}")
            return analysis_data
            
        except Exception as e:
            self.logger.error(f"Failed to load analysis result {analysis_id}: {e}")
            return None
    
    def list_saved_analyses(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        List saved analysis results.
        
        Args:
            limit: Maximum number of results to return
            
        Returns:
            List of analysis summaries
        """
        if not self.storage:
            self.logger.error("Storage not initialized. Enable save_results in configuration.")
            return []
        
        try:
            return self.storage.list_saved_results(limit)
        except Exception as e:
            self.logger.error(f"Failed to list saved analyses: {e}")
            return []
    
    def delete_saved_analysis(self, analysis_id: str) -> bool:
        """
        Delete a saved analysis result.
        
        Args:
            analysis_id: ID of the analysis to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.storage:
            self.logger.error("Storage not initialized. Enable save_results in configuration.")
            return False
        
        try:
            success = self.storage.delete_analysis_result(analysis_id)
            if success:
                self.logger.info(f"Analysis result deleted: {analysis_id}")
            return success
        except Exception as e:
            self.logger.error(f"Failed to delete analysis result {analysis_id}: {e}")
            return False
    
    def export_analysis_result(self, analysis_id: str, output_path: str) -> bool:
        """
        Export analysis result to JSON file.
        
        Args:
            analysis_id: ID of the analysis to export
            output_path: Output file path
            
        Returns:
            True if successful, False otherwise
        """
        if not self.storage:
            self.logger.error("Storage not initialized. Enable save_results in configuration.")
            return False
        
        try:
            success = self.storage.export_to_json(analysis_id, output_path)
            if success:
                self.logger.info(f"Analysis result exported to: {output_path}")
            return success
        except Exception as e:
            self.logger.error(f"Failed to export analysis result: {e}")
            return False
    
    def import_analysis_result(self, input_path: str) -> Optional[str]:
        """
        Import analysis result from JSON file.
        
        Args:
            input_path: Input file path
            
        Returns:
            New analysis ID if successful, None otherwise
        """
        if not self.storage:
            self.logger.error("Storage not initialized. Enable save_results in configuration.")
            return None
        
        try:
            analysis_id = self.storage.import_from_json(input_path)
            if analysis_id:
                self.logger.info(f"Analysis result imported with ID: {analysis_id}")
            return analysis_id
        except Exception as e:
            self.logger.error(f"Failed to import analysis result: {e}")
            return None
    
    def display_saved_analysis(self, analysis_id: str, include_chart: bool = True) -> str:
        """
        Display a saved analysis result in formatted text.
        
        Args:
            analysis_id: ID of the analysis to display
            include_chart: Whether to regenerate and include chart
            
        Returns:
            Formatted analysis display string
        """
        analysis_data = self.load_saved_analysis(analysis_id)
        if not analysis_data:
            return f"Analysis result not found: {analysis_id}"
        
        # Format the display
        lines = []
        lines.append("=" * 80)
        lines.append(f"SAVED ANALYSIS RESULT: {analysis_id}")
        lines.append("=" * 80)
        lines.append("")
        
        # Basic info
        data_summary = analysis_data['data_summary']
        lines.append(f"Symbol: {data_summary['symbol']}")
        lines.append(f"Timeframe: {data_summary['timeframe']}")
        lines.append(f"Analysis Date: {analysis_data['analysis_timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Analysis Time: {analysis_data['analysis_time_seconds']:.2f} seconds")
        lines.append(f"Data Points: {data_summary['total_points']}")
        lines.append(f"Data Period: {data_summary['start_time'].strftime('%Y-%m-%d')} to {data_summary['end_time'].strftime('%Y-%m-%d')}")
        lines.append("")
        
        # Configuration used
        config_used = analysis_data['configuration_used']
        lines.append("Configuration Used:")
        lines.append(f"  Sensitivity Level: {config_used['sensitivity_level']}")
        lines.append(f"  Patterns Enabled: {config_used['patterns_enabled']}")
        lines.append(f"  Colors Enabled: {config_used['colors_enabled']}")
        lines.append("")
        
        # Pattern summary
        pattern_summary = analysis_data['pattern_summary']
        lines.append(f"Patterns Found: {analysis_data['patterns_found']}")
        if pattern_summary.get('by_category'):
            lines.append("By Category:")
            for category, count in pattern_summary['by_category'].items():
                lines.append(f"  {category}: {count}")
        
        if pattern_summary.get('sentiment'):
            sentiment = pattern_summary['sentiment']
            lines.append(f"Sentiment: {sentiment['bullish']} Bullish, {sentiment['bearish']} Bearish, {sentiment['neutral']} Neutral")
        
        lines.append(f"Average Confidence: {pattern_summary.get('average_confidence', 'N/A')}")
        lines.append("")
        
        # Top patterns
        patterns = analysis_data['patterns']
        if patterns:
            lines.append("Top Patterns:")
            for i, pattern in enumerate(patterns[:5]):
                lines.append(f"  {i+1}. {pattern['type']} - {pattern['confidence']} confidence")
                lines.append(f"     {pattern['description']}")
        lines.append("")
        
        # Technical indicators
        indicators = analysis_data['technical_indicators']
        if indicators and 'error' not in indicators:
            lines.append("Technical Indicators:")
            if 'rsi' in indicators and indicators['rsi']['current']:
                rsi_info = indicators['rsi']
                status = "Overbought" if rsi_info['overbought'] else "Oversold" if rsi_info['oversold'] else "Normal"
                lines.append(f"  RSI: {rsi_info['current']:.1f} ({status})")
            
            if 'macd' in indicators:
                macd_info = indicators['macd']
                if macd_info['current_macd'] and macd_info['current_signal']:
                    crossover = "Bullish" if macd_info['bullish_crossover'] else "Bearish"
                    lines.append(f"  MACD: {macd_info['current_macd']:.4f} / Signal: {macd_info['current_signal']:.4f} ({crossover})")
        lines.append("")
        
        # Recommendations
        recommendations = analysis_data['recommendations']
        if recommendations:
            lines.append("Recommendations:")
            for rec in recommendations:
                lines.append(f"  • {rec}")
        lines.append("")
        
        # Chart (if requested and we have the original data)
        if include_chart:
            lines.append("Note: Chart regeneration requires original price data")
            lines.append("Use the original analysis for chart display")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def get_storage_statistics(self) -> Dict[str, Any]:
        """Get storage statistics."""
        if not self.storage:
            return {'error': 'Storage not initialized'}
        
        try:
            return self.storage.get_storage_stats()
        except Exception as e:
            self.logger.error(f"Failed to get storage statistics: {e}")
            return {'error': str(e)}
    
    def cleanup_old_analyses(self, days_to_keep: int = 30) -> int:
        """
        Clean up old analysis results.
        
        Args:
            days_to_keep: Number of days to keep results
            
        Returns:
            Number of results deleted
        """
        if not self.storage:
            self.logger.error("Storage not initialized. Enable save_results in configuration.")
            return 0
        
        try:
            deleted_count = self.storage.cleanup_old_results(days_to_keep)
            self.logger.info(f"Cleaned up {deleted_count} old analysis results")
            return deleted_count
        except Exception as e:
            self.logger.error(f"Failed to cleanup old analyses: {e}")
            return 0    

    def analyze_ticker(self, ticker: str, days: int = 30, 
                      interval: str = '4h', sensitivity: Optional[float] = None) -> Dict[str, Any]:
        """
        Analyze cryptocurrency by ticker symbol with real-time data fetching.
        
        Args:
            ticker: Cryptocurrency ticker (e.g., 'BTC', 'ETH')
            days: Number of days of historical data to fetch
            interval: Data interval ('1h', '4h', '1d')
            sensitivity: Pattern detection sensitivity (0.0 to 1.0)
            
        Returns:
            Analysis results dictionary
        """
        try:
            self.logger.info(f"Analyzing {ticker} with {days} days of {interval} data")
            
            # Validate ticker
            if not self.data_fetcher.validate_ticker(ticker):
                return {
                    'success': False,
                    'error': f'Ticker "{ticker}" not supported or not found',
                    'suggestions': [
                        f'Try one of these supported tickers: {", ".join(self.data_fetcher.get_supported_tickers()[:10])}',
                        'Use search_tickers() to find available cryptocurrencies',
                        'Check ticker symbol spelling'
                    ]
                }
            
            # Fetch historical data
            data_frame = self.data_fetcher.fetch_historical_data(ticker, days, interval)
            
            if not data_frame:
                return {
                    'success': False,
                    'error': f'Failed to fetch data for {ticker}',
                    'suggestions': [
                        'Check internet connection',
                        'Try a different ticker symbol',
                        'Reduce the number of days requested',
                        'Try again later (API rate limits may apply)'
                    ]
                }
            
            # Get current price for additional context
            current_price = self.data_fetcher.get_current_price(ticker)
            
            # Perform analysis
            results = self._perform_analysis(data_frame, sensitivity)
            
            # Add ticker-specific information
            if results['success']:
                results['ticker_info'] = {
                    'symbol': ticker.upper(),
                    'current_price': current_price,
                    'data_points': len(data_frame),
                    'data_interval': interval,
                    'data_period_days': days,
                    'data_source': 'Real-time API',
                    'last_update': data_frame.data[-1].timestamp.strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Add price change information
                if len(data_frame) > 1:
                    first_price = data_frame.data[0].close
                    last_price = data_frame.data[-1].close
                    price_change = (last_price - first_price) / first_price
                    
                    results['ticker_info']['price_change'] = {
                        'absolute': last_price - first_price,
                        'percentage': price_change,
                        'period': f'{days} days'
                    }
            
            return results
            
        except Exception as e:
            self.logger.error(f"Ticker analysis failed for {ticker}: {e}")
            return {
                'success': False,
                'error': f'Analysis failed for {ticker}: {str(e)}',
                'suggestions': [
                    'Check ticker symbol validity',
                    'Verify internet connection',
                    'Try with different parameters (days, interval)',
                    'Check system logs for detailed error information'
                ]
            }
    
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
    
    def get_supported_tickers(self) -> List[str]:
        """Get list of commonly supported ticker symbols."""
        return self.data_fetcher.get_supported_tickers()
    
    def get_current_price(self, ticker: str) -> Optional[float]:
        """Get current price for a cryptocurrency."""
        try:
            return self.data_fetcher.get_current_price(ticker)
        except Exception as e:
            self.logger.error(f"Failed to get current price for {ticker}: {e}")
            return None
    
    def _format_ml_predictions(self, ml_predictions) -> Dict[str, Any]:
        """Format ML predictions for output."""
        if not ml_predictions:
            return None
        
        try:
            return {
                'price_forecast': {
                    'daily_prices': ml_predictions.price_forecast.daily_prices,
                    'expected_return': f"{ml_predictions.price_forecast.expected_return:.2%}",
                    'prediction_dates': [d.strftime("%Y-%m-%d") for d in ml_predictions.price_forecast.prediction_dates],
                    'confidence_intervals': ml_predictions.price_forecast.confidence_intervals,
                    'probability_up': ml_predictions.price_forecast.probability_up
                },
                'trend_forecast': {
                    'trend_7d': ml_predictions.trend_forecast.trend_7d,
                    'trend_30d': ml_predictions.trend_forecast.trend_30d,
                    'trend_strength': f"{ml_predictions.trend_forecast.trend_strength:.1%}",
                    'reversal_probability': f"{ml_predictions.trend_forecast.reversal_probability:.1%}"
                },
                'market_regime': {
                    'current_regime': ml_predictions.market_regime.current_regime,
                    'regime_probability': {k: f"{v:.1%}" for k, v in ml_predictions.market_regime.regime_probability.items()},
                    'regime_persistence': f"{ml_predictions.market_regime.regime_persistence:.1f} days"
                },
                'model_performance': ml_predictions.model_performance,
                'feature_importance': ml_predictions.feature_importance,
                'prediction_timestamp': ml_predictions.prediction_timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            self.logger.error(f"Failed to format ML predictions: {e}")
            return {'error': 'Failed to format ML predictions'}