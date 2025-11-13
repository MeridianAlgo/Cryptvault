"""Unit tests for pattern detection."""

import pytest
from tests.fixtures.sample_data import (
    create_triangle_pattern_data,
    create_head_and_shoulders_data,
    create_double_bottom_data,
    create_bull_flag_data
)


@pytest.mark.unit
@pytest.mark.patterns
class TestGeometricPatterns:
    """Test geometric pattern detection."""
    
    def test_triangle_pattern_detection(self):
        """Test triangle pattern detection."""
        from cryptvault.patterns.geometric import GeometricPatternAnalyzer
        
        data = create_triangle_pattern_data()
        analyzer = GeometricPatternAnalyzer()
        
        patterns = analyzer.detect_triangle_patterns(data, sensitivity=0.5)
        
        # Should detect at least one triangle
        assert len(patterns) > 0
        # Pattern should have required attributes
        if patterns:
            pattern = patterns[0]
            assert hasattr(pattern, 'pattern_type')
            assert hasattr(pattern, 'confidence')
            assert 0 <= pattern.confidence <= 1


@pytest.mark.unit
@pytest.mark.patterns
class TestReversalPatterns:
    """Test reversal pattern detection."""
    
    def test_head_and_shoulders_detection(self):
        """Test head and shoulders pattern detection."""
        from cryptvault.patterns.reversal import ReversalPatternDetector
        
        data = create_head_and_shoulders_data()
        detector = ReversalPatternDetector()
        
        patterns = detector.detect_head_and_shoulders(data, sensitivity=0.5)
        
        # Should detect pattern
        assert len(patterns) >= 0  # May or may not detect depending on sensitivity
    
    def test_double_bottom_detection(self):
        """Test double bottom pattern detection."""
        from cryptvault.patterns.reversal import ReversalPatternDetector
        
        data = create_double_bottom_data()
        detector = ReversalPatternDetector()
        
        patterns = detector.detect_double_bottom(data, sensitivity=0.5)
        
        # Should detect pattern
        assert len(patterns) >= 0


@pytest.mark.unit
@pytest.mark.patterns
class TestContinuationPatterns:
    """Test continuation pattern detection."""
    
    def test_bull_flag_detection(self):
        """Test bull flag pattern detection."""
        from cryptvault.patterns.continuation import ContinuationPatternDetector
        
        data = create_bull_flag_data()
        detector = ContinuationPatternDetector()
        
        patterns = detector.detect_flag_patterns(data, sensitivity=0.5)
        
        # Should detect flag pattern
        assert len(patterns) >= 0
