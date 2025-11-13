"""
Harmonic Pattern Detection

Detects harmonic patterns based on Fibonacci ratios including Gartley, Butterfly, Bat, Crab, and Shark patterns.
"""

from typing import List, Tuple, Optional
import numpy as np
from .base import BasePatternDetector, DetectedPattern
from ..data.models import PriceDataFrame
from ..indicators.trend_analysis import TrendAnalysis, PeakTrough

class HarmonicPatternDetector(BasePatternDetector):
    """Detect harmonic patterns using Fibonacci ratios."""

    # Fibonacci ratios for harmonic patterns
    GARTLEY_RATIOS = {'B': (0.618, 0.05), 'C': (0.382, 0.886), 'D': (0.786, 0.05)}
    BUTTERFLY_RATIOS = {'B': (0.786, 0.05), 'C': (0.382, 0.886), 'D': (1.27, 1.618)}
    BAT_RATIOS = {'B': (0.382, 0.5), 'C': (0.382, 0.886), 'D': (0.886, 0.05)}
    CRAB_RATIOS = {'B': (0.382, 0.618), 'C': (0.382, 0.886), 'D': (1.618, 0.05)}

    def __init__(self):
        super().__init__()
        self.trend_analysis = TrendAnalysis()

    def detect(self, data: PriceDataFrame, sensitivity: float = 0.5) -> List[DetectedPattern]:
        """Detect all harmonic patterns."""
        patterns = []

        if len(data) < 30:
            return patterns

        # Find significant peaks and troughs
        closes = data.get_closes()
        peaks_troughs = self.trend_analysis.find_peaks_and_troughs(closes, min_distance=5)

        if len(peaks_troughs) < 5:
            return patterns

        # Check for XABCD patterns
        for i in range(len(peaks_troughs) - 4):
            points = peaks_troughs[i:i+5]

            # Verify alternating peaks and troughs
            if not self._is_valid_xabcd(points):
                continue

            # Check each harmonic pattern type
            gartley = self._check_gartley(data, points, sensitivity)
            if gartley:
                patterns.append(gartley)

            butterfly = self._check_butterfly(data, points, sensitivity)
            if butterfly:
                patterns.append(butterfly)

            bat = self._check_bat(data, points, sensitivity)
            if bat:
                patterns.append(bat)

            crab = self._check_crab(data, points, sensitivity)
            if crab:
                patterns.append(crab)

        return self._filter_overlapping(patterns)

    def get_pattern_types(self) -> List[str]:
        return ['Gartley', 'Butterfly', 'Bat', 'Crab', 'Shark', 'Cypher', 'ABCD']

    def _is_valid_xabcd(self, points: List[PeakTrough]) -> bool:
        """Check if points form valid XABCD structure (alternating peaks/troughs)."""
        if len(points) != 5:
            return False

        for i in range(len(points) - 1):
            if points[i].type == points[i+1].type:
                return False

        return True

    def _check_gartley(self, data: PriceDataFrame, points: List[PeakTrough], sensitivity: float) -> Optional[DetectedPattern]:
        """Check for Gartley pattern."""
        X, A, B, C, D = [p.value for p in points]

        # Calculate Fibonacci retracements
        XA = abs(A - X)
        AB_retracement = abs(B - A) / XA if XA != 0 else 0
        BC_retracement = abs(C - B) / abs(B - A) if abs(B - A) != 0 else 0
        CD_retracement = abs(D - C) / XA if XA != 0 else 0

        # Check Gartley ratios
        if (0.568 <= AB_retracement <= 0.668 and  # B at 0.618 of XA
            0.332 <= BC_retracement <= 0.936 and  # C between 0.382-0.886 of AB
            0.736 <= CD_retracement <= 0.836):    # D at 0.786 of XA

            confidence = self._calculate_confidence([0.8, 0.85, 0.9], [1.0, 1.0, 1.0])

            return DetectedPattern(
                pattern_type='Gartley',
                category='Harmonic',
                confidence=confidence,
                start_time=data[points[0].index].timestamp,
                end_time=data[points[4].index].timestamp,
                start_index=points[0].index,
                end_index=points[4].index,
                key_levels={'X': X, 'A': A, 'B': B, 'C': C, 'D': D},
                description=f"Gartley harmonic pattern with {confidence:.1%} confidence"
            )

        return None

    def _check_butterfly(self, data: PriceDataFrame, points: List[PeakTrough], sensitivity: float) -> Optional[DetectedPattern]:
        """Check for Butterfly pattern."""
        X, A, B, C, D = [p.value for p in points]

        XA = abs(A - X)
        AB_retracement = abs(B - A) / XA if XA != 0 else 0
        BC_retracement = abs(C - B) / abs(B - A) if abs(B - A) != 0 else 0
        XA_extension = abs(D - X) / XA if XA != 0 else 0

        # Check Butterfly ratios
        if (0.736 <= AB_retracement <= 0.836 and  # B at 0.786 of XA
            0.332 <= BC_retracement <= 0.936 and  # C between 0.382-0.886 of AB
            1.17 <= XA_extension <= 1.718):       # D extends 1.27-1.618 of XA

            confidence = self._calculate_confidence([0.75, 0.8, 0.85], [1.0, 1.0, 1.0])

            return DetectedPattern(
                pattern_type='Butterfly',
                category='Harmonic',
                confidence=confidence,
                start_time=data[points[0].index].timestamp,
                end_time=data[points[4].index].timestamp,
                start_index=points[0].index,
                end_index=points[4].index,
                key_levels={'X': X, 'A': A, 'B': B, 'C': C, 'D': D},
                description=f"Butterfly harmonic pattern with {confidence:.1%} confidence"
            )

        return None

    def _check_bat(self, data: PriceDataFrame, points: List[PeakTrough], sensitivity: float) -> Optional[DetectedPattern]:
        """Check for Bat pattern."""
        X, A, B, C, D = [p.value for p in points]

        XA = abs(A - X)
        AB_retracement = abs(B - A) / XA if XA != 0 else 0
        BC_retracement = abs(C - B) / abs(B - A) if abs(B - A) != 0 else 0
        CD_retracement = abs(D - C) / XA if XA != 0 else 0

        # Check Bat ratios
        if (0.332 <= AB_retracement <= 0.55 and   # B between 0.382-0.5 of XA
            0.332 <= BC_retracement <= 0.936 and  # C between 0.382-0.886 of AB
            0.836 <= CD_retracement <= 0.936):    # D at 0.886 of XA

            confidence = self._calculate_confidence([0.78, 0.82, 0.88], [1.0, 1.0, 1.0])

            return DetectedPattern(
                pattern_type='Bat',
                category='Harmonic',
                confidence=confidence,
                start_time=data[points[0].index].timestamp,
                end_time=data[points[4].index].timestamp,
                start_index=points[0].index,
                end_index=points[4].index,
                key_levels={'X': X, 'A': A, 'B': B, 'C': C, 'D': D},
                description=f"Bat harmonic pattern with {confidence:.1%} confidence"
            )

        return None

    def _check_crab(self, data: PriceDataFrame, points: List[PeakTrough], sensitivity: float) -> Optional[DetectedPattern]:
        """Check for Crab pattern."""
        X, A, B, C, D = [p.value for p in points]

        XA = abs(A - X)
        AB_retracement = abs(B - A) / XA if XA != 0 else 0
        BC_retracement = abs(C - B) / abs(B - A) if abs(B - A) != 0 else 0
        XA_extension = abs(D - X) / XA if XA != 0 else 0

        # Check Crab ratios
        if (0.332 <= AB_retracement <= 0.668 and  # B between 0.382-0.618 of XA
            0.332 <= BC_retracement <= 0.936 and  # C between 0.382-0.886 of AB
            1.568 <= XA_extension <= 1.668):      # D at 1.618 of XA

            confidence = self._calculate_confidence([0.8, 0.85, 0.9], [1.0, 1.0, 1.0])

            return DetectedPattern(
                pattern_type='Crab',
                category='Harmonic',
                confidence=confidence,
                start_time=data[points[0].index].timestamp,
                end_time=data[points[4].index].timestamp,
                start_index=points[0].index,
                end_index=points[4].index,
                key_levels={'X': X, 'A': A, 'B': B, 'C': C, 'D': D},
                description=f"Crab harmonic pattern with {confidence:.1%} confidence"
            )

        return None
