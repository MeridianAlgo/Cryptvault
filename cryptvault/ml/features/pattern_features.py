"""Pattern-based feature extraction for ML models."""

import numpy as np
from typing import List, Dict, Any
import logging

from ...patterns.types import DetectedPattern, PatternCategory


class PatternFeatureExtractor:
    """Extract pattern-based features for ML models."""
    
    def __init__(self):
        """Initialize pattern feature extractor."""
        self.logger = logging.getLogger(__name__)
    
    def extract(self, patterns: List[DetectedPattern]) -> List[float]:
        """
        Extract pattern-based features.
        
        Args:
            patterns: List of detected patterns
            
        Returns:
            List of pattern features
        """
        try:
            features = []
            
            # Pattern presence features
            presence_features = self._extract_pattern_presence(patterns)
            features.extend(presence_features)
            
            # Pattern confidence features
            confidence_features = self._extract_confidence_features(patterns)
            features.extend(confidence_features)
            
            # Pattern category features
            category_features = self._extract_category_features(patterns)
            features.extend(category_features)
            
            # Pattern timing features
            timing_features = self._extract_timing_features(patterns)
            features.extend(timing_features)
            
            self.logger.debug(f"Extracted {len(features)} pattern features")
            return features
            
        except Exception as e:
            self.logger.error(f"Pattern feature extraction failed: {e}")
            return [0.0] * 15  # Return zeros as fallback
    
    def _extract_pattern_presence(self, patterns: List[DetectedPattern]) -> List[float]:
        """Extract binary features for pattern presence."""
        features = []
        
        # Key pattern types to track
        key_patterns = [
            'triangle', 'flag', 'wedge', 'rectangle', 'head_shoulders',
            'double_top', 'double_bottom', 'cup_handle'
        ]
        
        pattern_names = [p.pattern_type.value.lower() for p in patterns]
        
        for pattern_type in key_patterns:
            # Check if any pattern contains this type
            present = any(pattern_type in name for name in pattern_names)
            features.append(1.0 if present else 0.0)
        
        return features
    
    def _extract_confidence_features(self, patterns: List[DetectedPattern]) -> List[float]:
        """Extract confidence-based features."""
        features = []
        
        if patterns:
            confidences = [p.confidence for p in patterns]
            
            features.extend([
                max(confidences),  # Highest confidence
                np.mean(confidences),  # Average confidence
                len([c for c in confidences if c > 0.7])  # Count of high-confidence patterns
            ])
        else:
            features.extend([0.0, 0.0, 0.0])
        
        return features
    
    def _extract_category_features(self, patterns: List[DetectedPattern]) -> List[float]:
        """Extract pattern category features."""
        features = []
        
        # Count patterns by category
        category_counts = {
            PatternCategory.BULLISH_CONTINUATION: 0,
            PatternCategory.BEARISH_CONTINUATION: 0,
            PatternCategory.BULLISH_REVERSAL: 0,
            PatternCategory.BEARISH_REVERSAL: 0
        }
        
        for pattern in patterns:
            if pattern.category in category_counts:
                category_counts[pattern.category] += 1
        
        # Normalize by total patterns
        total_patterns = len(patterns) if patterns else 1
        
        features.extend([
            category_counts[PatternCategory.BULLISH_CONTINUATION] / total_patterns,
            category_counts[PatternCategory.BEARISH_CONTINUATION] / total_patterns,
            category_counts[PatternCategory.BULLISH_REVERSAL] / total_patterns,
            category_counts[PatternCategory.BEARISH_REVERSAL] / total_patterns
        ])
        
        return features
    
    def _extract_timing_features(self, patterns: List[DetectedPattern]) -> List[float]:
        """Extract timing-based pattern features."""
        features = []
        
        if patterns:
            # Most recent pattern age (in relative terms)
            most_recent = max(patterns, key=lambda p: p.end_time)
            pattern_age = (most_recent.end_time - most_recent.start_time).total_seconds() / 86400  # Days
            
            # Average pattern duration
            durations = [(p.end_time - p.start_time).total_seconds() / 86400 for p in patterns]
            avg_duration = np.mean(durations)
            
            features.extend([
                min(pattern_age, 30.0) / 30.0,  # Normalize to 0-1 (max 30 days)
                min(avg_duration, 14.0) / 14.0   # Normalize to 0-1 (max 14 days)
            ])
        else:
            features.extend([0.0, 0.0])
        
        return features
    
    def get_feature_names(self) -> List[str]:
        """Get names of all extracted features."""
        return [
            # Pattern presence
            'has_triangle', 'has_flag', 'has_wedge', 'has_rectangle', 
            'has_head_shoulders', 'has_double_top', 'has_double_bottom', 'has_cup_handle',
            # Confidence features
            'max_confidence', 'avg_confidence', 'high_confidence_count',
            # Category features
            'bullish_continuation_ratio', 'bearish_continuation_ratio',
            'bullish_reversal_ratio', 'bearish_reversal_ratio',
            # Timing features
            'pattern_age', 'avg_duration'
        ]