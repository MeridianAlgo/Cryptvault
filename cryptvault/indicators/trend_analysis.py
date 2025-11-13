"""Trend analysis utilities."""

from typing import List, Optional
from dataclasses import dataclass


@dataclass
class PeakTrough:
    """Represents a peak or trough in price data."""
    index: int
    value: float
    type: str  # 'peak' or 'trough'


class TrendAnalysis:
    """Analyze price trends and find peaks/troughs."""

    def __init__(self):
        pass

    def find_peaks_and_troughs(self, data: List[float], min_distance: int = 5) -> List[PeakTrough]:
        """
        Find peaks and troughs in price data.

        Args:
            data: List of price values
            min_distance: Minimum distance between peaks/troughs

        Returns:
            List of PeakTrough objects
        """
        if len(data) < 3:
            return []

        peaks_troughs = []

        for i in range(min_distance, len(data) - min_distance):
            # Check if it's a peak
            is_peak = True
            is_trough = True

            for j in range(1, min_distance + 1):
                if data[i] <= data[i - j] or data[i] <= data[i + j]:
                    is_peak = False
                if data[i] >= data[i - j] or data[i] >= data[i + j]:
                    is_trough = False

            if is_peak:
                peaks_troughs.append(PeakTrough(index=i, value=data[i], type='peak'))
            elif is_trough:
                peaks_troughs.append(PeakTrough(index=i, value=data[i], type='trough'))

        return peaks_troughs
