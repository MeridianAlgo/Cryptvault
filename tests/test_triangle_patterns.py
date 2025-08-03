"""Tests for triangle pattern detection."""

import pytest
from datetime import datetime, timedelta
from crypto_chart_analyzer.patterns.geometric import GeometricPatternAnalyzer
from crypto_chart_analyzer.patterns.types import PatternType
from crypto_chart_analyzer.data.models import PricePoint, PriceDataFrame


class TestTrianglePatterns:
    """Test cases for triangle pattern detection."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = GeometricPatternAnalyzer()
    
    def create_ascending_triangle_data(self) -> PriceDataFrame:
        """Create sample data with ascending triangle pattern."""
        base_time = datetime(2023, 1, 1, 12, 0, 0)
        
        # Ascending triangle: horizontal resistance around 110, rising support
        prices = [
            100, 105, 102, 108, 104, 110, 106, 109, 107, 110,
            108, 109, 109, 110, 109.5, 110, 110, 109.8, 110.2, 111  # Breakout
        ]
        
        data = []
        for i, price in enumerate(prices):
            timestamp = base_time + timedelta(hours=i)
            
            # Create realistic OHLC with the pattern
            if i < 15:  # Before breakout
                high = min(price + 1, 110.5)  # Resistance around 110
                low = price - 1
            else:  # Breakout
                high = price + 2
                low = price - 0.5
            
            point = PricePoint(
                timestamp=timestamp,
                open=price,
                high=high,
                low=low,
                close=price + 0.5,
                volume=1000 - (i * 20)  # Decreasing volume
            )
            data.append(point)
        
        return PriceDataFrame(data=data, symbol="BTC", timeframe="1h")
    
    def create_descending_triangle_data(self) -> PriceDataFrame:
        """Create sample data with descending triangle pattern."""
        base_time = datetime(2023, 1, 1, 12, 0, 0)
        
        # Descending triangle: horizontal support around 90, falling resistance
        prices = [
            110, 105, 108, 102, 106, 100, 104, 98, 102, 96,
            100, 94, 98, 92, 96, 91, 94, 90.5, 92, 89  # Breakdown
        ]
        
        data = []
        for i, price in enumerate(prices):
            timestamp = base_time + timedelta(hours=i)
            
            # Create realistic OHLC with the pattern
            if i < 17:  # Before breakdown
                high = price + 1
                low = max(price - 1, 89.5)  # Support around 90
            else:  # Breakdown
                high = price + 0.5
                low = price - 2
            
            point = PricePoint(
                timestamp=timestamp,
                open=price,
                high=high,
                low=low,
                close=price - 0.5,
                volume=800 - (i * 15)  # Decreasing volume
            )
            data.append(point)
        
        return PriceDataFrame(data=data, symbol="BTC", timeframe="1h")
    
    def create_symmetrical_triangle_data(self) -> PriceDataFrame:
        """Create sample data with symmetrical triangle pattern."""
        base_time = datetime(2023, 1, 1, 12, 0, 0)
        
        # Symmetrical triangle: converging trend lines
        prices = [
            100, 108, 102, 106, 104, 105, 104.5, 104.8, 104.2, 104.6,
            104.3, 104.5, 104.4, 104.45, 104.35, 104.4, 104.38, 104.42, 104.39, 105  # Breakout
        ]
        
        data = []
        for i, price in enumerate(prices):
            timestamp = base_time + timedelta(hours=i)
            
            # Create converging high/low ranges
            range_factor = max(0.2, 1 - (i * 0.04))  # Decreasing range
            
            point = PricePoint(
                timestamp=timestamp,
                open=price,
                high=price + range_factor,
                low=price - range_factor,
                close=price + 0.1,
                volume=1200 - (i * 30)  # Decreasing volume
            )
            data.append(point)
        
        return PriceDataFrame(data=data, symbol="BTC", timeframe="1h")
    
    def test_detect_ascending_triangle(self):
        """Test detection of ascending triangle pattern."""
        data = self.create_ascending_triangle_data()
        patterns = self.analyzer.detect_triangle_patterns(data, sensitivity=0.5)
        
        # Should detect at least one pattern
        assert len(patterns) > 0
        
        # Check for ascending triangle
        ascending_triangles = [p for p in patterns if p.pattern_type == PatternType.ASCENDING_TRIANGLE]
        assert len(ascending_triangles) > 0
        
        # Verify pattern properties
        pattern = ascending_triangles[0]
        assert pattern.confidence > 0.3
        assert pattern.start_index < pattern.end_index
        assert 'upper_resistance' in pattern.key_levels
        assert 'lower_support' in pattern.key_levels
        assert pattern.volume_profile.volume_trend in ['decreasing', 'stable']
    
    def test_detect_descending_triangle(self):
        """Test detection of descending triangle pattern."""
        data = self.create_descending_triangle_data()
        patterns = self.analyzer.detect_triangle_patterns(data, sensitivity=0.5)
        
        # Should detect at least one pattern
        assert len(patterns) > 0
        
        # Check for descending triangle
        descending_triangles = [p for p in patterns if p.pattern_type == PatternType.DESCENDING_TRIANGLE]
        assert len(descending_triangles) > 0
        
        # Verify pattern properties
        pattern = descending_triangles[0]
        assert pattern.confidence > 0.3
        assert pattern.key_levels['upper_slope'] < 0  # Falling resistance
        assert abs(pattern.key_levels['lower_slope']) < 0.1  # Horizontal support
    
    def test_detect_symmetrical_triangle(self):
        """Test detection of symmetrical triangle pattern."""
        data = self.create_symmetrical_triangle_data()
        patterns = self.analyzer.detect_triangle_patterns(data, sensitivity=0.5)
        
        # Should detect at least one pattern
        assert len(patterns) > 0
        
        # Check for symmetrical triangle
        symmetrical_triangles = [p for p in patterns if p.pattern_type == PatternType.SYMMETRICAL_TRIANGLE]
        assert len(symmetrical_triangles) > 0
        
        # Verify pattern properties
        pattern = symmetrical_triangles[0]
        assert pattern.confidence > 0.3
        assert pattern.key_levels['upper_slope'] < 0  # Falling resistance
        assert pattern.key_levels['lower_slope'] > 0  # Rising support
    
    def test_triangle_classification(self):
        """Test triangle type classification logic."""
        # Test ascending triangle classification
        ascending_type = self.analyzer._classify_triangle_type(0.0001, 0.5)  # Horizontal, rising
        assert ascending_type == PatternType.ASCENDING_TRIANGLE
        
        # Test descending triangle classification
        descending_type = self.analyzer._classify_triangle_type(-0.5, 0.0001)  # Falling, horizontal
        assert descending_type == PatternType.DESCENDING_TRIANGLE
        
        # Test symmetrical triangle classification
        symmetrical_type = self.analyzer._classify_triangle_type(-0.3, 0.3)  # Converging
        assert symmetrical_type == PatternType.SYMMETRICAL_TRIANGLE
        
        # Test invalid classification
        invalid_type = self.analyzer._classify_triangle_type(0.5, 0.5)  # Both rising
        assert invalid_type is None
    
    def test_convergence_calculation(self):
        """Test trend line convergence calculation."""
        # Test normal convergence
        convergence = self.analyzer._calculate_convergence_point(-0.5, 110, 0.3, 90)
        assert isinstance(convergence, float)
        assert convergence > 0
        
        # Test parallel lines (no convergence)
        parallel_convergence = self.analyzer._calculate_convergence_point(0.5, 100, 0.5, 90)
        assert parallel_convergence == float('inf')
    
    def test_convergence_validation(self):
        """Test convergence point validation."""
        # Valid convergence
        assert self.analyzer._validate_triangle_convergence(50, 10, 40) is True
        
        # Invalid convergence (too far)
        assert self.analyzer._validate_triangle_convergence(200, 10, 40) is False
        
        # Invalid convergence (parallel lines)
        assert self.analyzer._validate_triangle_convergence(float('inf'), 10, 40) is False
    
    def test_trendline_fit_calculation(self):
        """Test trend line fit quality calculation."""
        # Perfect fit data
        perfect_values = [100, 101, 102, 103, 104]
        perfect_fit = self.analyzer._calculate_trendline_fit(perfect_values, 1.0, 100, 0, 'resistance')
        assert perfect_fit > 0.8
        
        # Poor fit data
        noisy_values = [100, 105, 95, 110, 90]
        poor_fit = self.analyzer._calculate_trendline_fit(noisy_values, 1.0, 100, 0, 'resistance')
        assert poor_fit < perfect_fit
    
    def test_trendline_touches_count(self):
        """Test trend line touches counting."""
        # Data that touches trend line multiple times
        values = [100, 101, 102, 103, 104]  # Perfect linear progression
        touches = self.analyzer._count_trendline_touches(values, 1.0, 100, 0, tolerance=0.02)
        assert touches == 5  # All points should touch
        
        # Data with fewer touches
        sparse_values = [100, 105, 102, 108, 104]  # Only some points touch
        sparse_touches = self.analyzer._count_trendline_touches(sparse_values, 1.0, 100, 0, tolerance=0.02)
        assert sparse_touches < touches
    
    def test_volume_pattern_analysis(self):
        """Test triangle volume pattern analysis."""
        # Decreasing volume (ideal for triangles)
        decreasing_volume = [1000, 900, 800, 700, 600]
        decreasing_score = self.analyzer._analyze_triangle_volume_pattern(decreasing_volume)
        assert decreasing_score > 0.5
        
        # Increasing volume (less ideal)
        increasing_volume = [600, 700, 800, 900, 1000]
        increasing_score = self.analyzer._analyze_triangle_volume_pattern(increasing_volume)
        assert increasing_score < decreasing_score
    
    def test_pattern_length_scoring(self):
        """Test pattern length appropriateness scoring."""
        # Ideal length
        ideal_score = self.analyzer._score_pattern_length(25)
        assert ideal_score == 1.0
        
        # Too short
        short_score = self.analyzer._score_pattern_length(5)
        assert short_score < 1.0
        
        # Too long
        long_score = self.analyzer._score_pattern_length(100)
        assert long_score < 1.0
    
    def test_sensitivity_adjustment(self):
        """Test sensitivity parameter effects."""
        data = self.create_ascending_triangle_data()
        
        # High sensitivity should find more patterns
        high_sens_patterns = self.analyzer.detect_triangle_patterns(data, sensitivity=0.9)
        
        # Low sensitivity should find fewer patterns
        low_sens_patterns = self.analyzer.detect_triangle_patterns(data, sensitivity=0.1)
        
        # High sensitivity should generally find more or equal patterns
        assert len(high_sens_patterns) >= len(low_sens_patterns)
    
    def test_insufficient_data(self):
        """Test behavior with insufficient data."""
        # Create very short data
        short_data = self.create_ascending_triangle_data()
        short_dataframe = PriceDataFrame(data=short_data.data[:5], symbol="BTC")
        
        patterns = self.analyzer.detect_triangle_patterns(short_dataframe)
        
        # Should return empty list for insufficient data
        assert len(patterns) == 0
    
    def test_overlapping_pattern_filtering(self):
        """Test filtering of overlapping patterns."""
        # Create mock overlapping patterns
        from crypto_chart_analyzer.patterns.types import DetectedPattern, PatternCategory, VolumeProfile
        
        pattern1 = DetectedPattern(
            pattern_type=PatternType.ASCENDING_TRIANGLE,
            category=PatternCategory.BULLISH_CONTINUATION,
            confidence=0.8,
            start_time=datetime.now(),
            end_time=datetime.now(),
            start_index=0,
            end_index=20,
            key_levels={},
            volume_profile=VolumeProfile(0, "stable", False),
            description="Test pattern 1"
        )
        
        pattern2 = DetectedPattern(
            pattern_type=PatternType.ASCENDING_TRIANGLE,
            category=PatternCategory.BULLISH_CONTINUATION,
            confidence=0.6,
            start_time=datetime.now(),
            end_time=datetime.now(),
            start_index=10,
            end_index=30,  # Overlaps with pattern1
            key_levels={},
            volume_profile=VolumeProfile(0, "stable", False),
            description="Test pattern 2"
        )
        
        pattern3 = DetectedPattern(
            pattern_type=PatternType.ASCENDING_TRIANGLE,
            category=PatternCategory.BULLISH_CONTINUATION,
            confidence=0.7,
            start_time=datetime.now(),
            end_time=datetime.now(),
            start_index=40,
            end_index=60,  # No overlap
            key_levels={},
            volume_profile=VolumeProfile(0, "stable", False),
            description="Test pattern 3"
        )
        
        patterns = [pattern1, pattern2, pattern3]
        filtered = self.analyzer._filter_overlapping_patterns(patterns)
        
        # Should keep pattern1 (highest confidence) and pattern3 (no overlap)
        assert len(filtered) == 2
        assert pattern1 in filtered
        assert pattern3 in filtered
        assert pattern2 not in filtered
    
    def test_volume_profile_calculation(self):
        """Test volume profile calculation."""
        data = self.create_ascending_triangle_data()
        
        volume_profile = self.analyzer._calculate_volume_profile(data, 0, 10)
        
        assert volume_profile.avg_volume > 0
        assert volume_profile.volume_trend in ['increasing', 'decreasing', 'stable']
        assert isinstance(volume_profile.volume_confirmation, bool)
    
    def test_pattern_description_generation(self):
        """Test pattern description generation."""
        description = self.analyzer._generate_triangle_description(
            PatternType.ASCENDING_TRIANGLE, 0.75, 20
        )
        
        assert "Ascending Triangle" in description
        assert "bullish continuation" in description
        assert "high" in description  # High confidence
        assert "20 periods" in description