"""Analysis result storage and persistence."""

import json
import os
import pickle
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
import logging

from ..patterns.types import DetectedPattern, PatternType, PatternCategory


@dataclass
class AnalysisResult:
    """Data class for storing complete analysis results."""

    # Analysis metadata
    analysis_id: str
    timestamp: datetime
    analysis_time_seconds: float

    # Data information
    symbol: str
    timeframe: str
    data_points: int
    data_start: datetime
    data_end: datetime

    # Configuration used
    sensitivity_level: str
    patterns_enabled: int
    colors_enabled: bool

    # Analysis results
    patterns_found: int
    patterns: List[Dict[str, Any]]
    pattern_summary: Dict[str, Any]
    technical_indicators: Dict[str, Any]
    recommendations: List[str]

    # Additional metadata
    version: str = "1.0"
    created_by: str = "Crypto Chart Analyzer"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)

        # Convert datetime objects to strings
        data['timestamp'] = self.timestamp.isoformat()
        data['data_start'] = self.data_start.isoformat()
        data['data_end'] = self.data_end.isoformat()

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalysisResult':
        """Create from dictionary."""
        # Convert string timestamps back to datetime
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        data['data_start'] = datetime.fromisoformat(data['data_start'])
        data['data_end'] = datetime.fromisoformat(data['data_end'])

        return cls(**data)

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the analysis result."""
        return {
            'analysis_id': self.analysis_id,
            'timestamp': self.timestamp,
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'patterns_found': self.patterns_found,
            'analysis_time': f"{self.analysis_time_seconds:.2f}s",
            'data_period': f"{self.data_start.strftime('%Y-%m-%d')} to {self.data_end.strftime('%Y-%m-%d')}",
            'top_pattern': self.patterns[0]['type'] if self.patterns else 'None'
        }


class AnalysisResultStorage:
    """Handles saving and loading of analysis results."""

    def __init__(self, storage_dir: str = None):
        """Initialize result storage."""
        if storage_dir is None:
            # Default to user's home directory
            storage_dir = os.path.join(os.path.expanduser("~"), ".crypto_chart_analyzer", "results")

        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger(__name__)

        # Create subdirectories for different formats
        (self.storage_dir / "json").mkdir(exist_ok=True)
        (self.storage_dir / "pickle").mkdir(exist_ok=True)
        (self.storage_dir / "csv").mkdir(exist_ok=True)

    def save_analysis_result(self, analysis_data: Dict[str, Any],
                           symbol: str = "UNKNOWN",
                           timeframe: str = "UNKNOWN") -> str:
        """
        Save analysis result with timestamped filename.

        Args:
            analysis_data: Complete analysis result dictionary
            symbol: Trading symbol
            timeframe: Timeframe of the data

        Returns:
            Analysis ID (filename without extension)
        """
        try:
            # Generate analysis ID
            timestamp = datetime.now()
            analysis_id = f"{symbol}_{timeframe}_{timestamp.strftime('%Y%m%d_%H%M%S')}"

            # Extract data information
            data_summary = analysis_data.get('data_summary', {})

            # Create AnalysisResult object
            result = AnalysisResult(
                analysis_id=analysis_id,
                timestamp=timestamp,
                analysis_time_seconds=analysis_data.get('analysis_time_seconds', 0.0),
                symbol=symbol,
                timeframe=timeframe,
                data_points=data_summary.get('total_points', 0),
                data_start=data_summary.get('start_time', timestamp),
                data_end=data_summary.get('end_time', timestamp),
                sensitivity_level=analysis_data.get('configuration_used', {}).get('sensitivity_level', 'unknown'),
                patterns_enabled=analysis_data.get('configuration_used', {}).get('patterns_enabled', 0),
                colors_enabled=analysis_data.get('configuration_used', {}).get('colors_enabled', False),
                patterns_found=analysis_data.get('patterns_found', 0),
                patterns=analysis_data.get('patterns', []),
                pattern_summary=analysis_data.get('pattern_summary', {}),
                technical_indicators=analysis_data.get('technical_indicators', {}),
                recommendations=analysis_data.get('recommendations', [])
            )

            # Save in multiple formats
            self._save_json(result, analysis_id)
            self._save_pickle(result, analysis_id)
            self._save_csv_summary(result, analysis_id)

            self.logger.info(f"Analysis result saved with ID: {analysis_id}")
            return analysis_id

        except Exception as e:
            self.logger.error(f"Failed to save analysis result: {e}")
            raise

    def load_analysis_result(self, analysis_id: str, format: str = "json") -> Optional[AnalysisResult]:
        """
        Load analysis result by ID.

        Args:
            analysis_id: Analysis ID to load
            format: Format to load ("json" or "pickle")

        Returns:
            AnalysisResult object or None if not found
        """
        try:
            if format == "json":
                return self._load_json(analysis_id)
            elif format == "pickle":
                return self._load_pickle(analysis_id)
            else:
                raise ValueError(f"Unsupported format: {format}")

        except Exception as e:
            self.logger.error(f"Failed to load analysis result {analysis_id}: {e}")
            return None

    def list_saved_results(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        List saved analysis results.

        Args:
            limit: Maximum number of results to return

        Returns:
            List of result summaries
        """
        results = []

        try:
            json_dir = self.storage_dir / "json"

            # Get all JSON files
            json_files = list(json_dir.glob("*.json"))

            # Sort by modification time (newest first)
            json_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

            # Load summaries
            for json_file in json_files[:limit]:
                try:
                    analysis_id = json_file.stem
                    result = self._load_json(analysis_id)
                    if result:
                        summary = result.get_summary()
                        summary['file_size'] = json_file.stat().st_size
                        summary['file_path'] = str(json_file)
                        results.append(summary)
                except Exception as e:
                    self.logger.warning(f"Failed to load summary for {json_file}: {e}")
                    continue

            return results

        except Exception as e:
            self.logger.error(f"Failed to list saved results: {e}")
            return []

    def delete_analysis_result(self, analysis_id: str) -> bool:
        """
        Delete analysis result by ID.

        Args:
            analysis_id: Analysis ID to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            deleted_any = False

            # Delete JSON file
            json_file = self.storage_dir / "json" / f"{analysis_id}.json"
            if json_file.exists():
                json_file.unlink()
                deleted_any = True

            # Delete pickle file
            pickle_file = self.storage_dir / "pickle" / f"{analysis_id}.pkl"
            if pickle_file.exists():
                pickle_file.unlink()
                deleted_any = True

            # Delete CSV file
            csv_file = self.storage_dir / "csv" / f"{analysis_id}.csv"
            if csv_file.exists():
                csv_file.unlink()
                deleted_any = True

            if deleted_any:
                self.logger.info(f"Analysis result {analysis_id} deleted")
            else:
                self.logger.warning(f"Analysis result {analysis_id} not found")

            return deleted_any

        except Exception as e:
            self.logger.error(f"Failed to delete analysis result {analysis_id}: {e}")
            return False

    def export_to_json(self, analysis_id: str, output_path: str) -> bool:
        """
        Export analysis result to a specific JSON file.

        Args:
            analysis_id: Analysis ID to export
            output_path: Output file path

        Returns:
            True if successful, False otherwise
        """
        try:
            result = self.load_analysis_result(analysis_id, "json")
            if not result:
                return False

            with open(output_path, 'w') as f:
                json.dump(result.to_dict(), f, indent=2, default=str)

            self.logger.info(f"Analysis result exported to: {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to export analysis result: {e}")
            return False

    def import_from_json(self, input_path: str) -> Optional[str]:
        """
        Import analysis result from JSON file.

        Args:
            input_path: Input file path

        Returns:
            Analysis ID if successful, None otherwise
        """
        try:
            with open(input_path, 'r') as f:
                data = json.load(f)

            result = AnalysisResult.from_dict(data)

            # Generate new analysis ID to avoid conflicts
            timestamp = datetime.now()
            new_analysis_id = f"{result.symbol}_{result.timeframe}_{timestamp.strftime('%Y%m%d_%H%M%S')}_imported"
            result.analysis_id = new_analysis_id

            # Save imported result
            self._save_json(result, new_analysis_id)
            self._save_pickle(result, new_analysis_id)
            self._save_csv_summary(result, new_analysis_id)

            self.logger.info(f"Analysis result imported with ID: {new_analysis_id}")
            return new_analysis_id

        except Exception as e:
            self.logger.error(f"Failed to import analysis result: {e}")
            return None

    def cleanup_old_results(self, days_to_keep: int = 30) -> int:
        """
        Clean up old analysis results.

        Args:
            days_to_keep: Number of days to keep results

        Returns:
            Number of results deleted
        """
        try:
            cutoff_time = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
            deleted_count = 0

            for format_dir in ["json", "pickle", "csv"]:
                format_path = self.storage_dir / format_dir

                for file_path in format_path.glob("*"):
                    if file_path.stat().st_mtime < cutoff_time:
                        file_path.unlink()
                        deleted_count += 1

            self.logger.info(f"Cleaned up {deleted_count} old analysis results")
            return deleted_count

        except Exception as e:
            self.logger.error(f"Failed to cleanup old results: {e}")
            return 0

    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        try:
            stats = {
                'storage_dir': str(self.storage_dir),
                'total_results': 0,
                'total_size_mb': 0.0,
                'formats': {}
            }

            for format_dir in ["json", "pickle", "csv"]:
                format_path = self.storage_dir / format_dir
                files = list(format_path.glob("*"))

                format_stats = {
                    'count': len(files),
                    'size_mb': sum(f.stat().st_size for f in files) / (1024 * 1024)
                }

                stats['formats'][format_dir] = format_stats
                stats['total_results'] += format_stats['count']
                stats['total_size_mb'] += format_stats['size_mb']

            # Adjust total results (each result is saved in 3 formats)
            stats['total_results'] = stats['formats']['json']['count']

            return stats

        except Exception as e:
            self.logger.error(f"Failed to get storage stats: {e}")
            return {'error': str(e)}

    def _save_json(self, result: AnalysisResult, analysis_id: str):
        """Save result as JSON."""
        json_file = self.storage_dir / "json" / f"{analysis_id}.json"

        with open(json_file, 'w') as f:
            json.dump(result.to_dict(), f, indent=2, default=str)

    def _save_pickle(self, result: AnalysisResult, analysis_id: str):
        """Save result as pickle."""
        pickle_file = self.storage_dir / "pickle" / f"{analysis_id}.pkl"

        with open(pickle_file, 'wb') as f:
            pickle.dump(result, f)

    def _save_csv_summary(self, result: AnalysisResult, analysis_id: str):
        """Save result summary as CSV."""
        import csv

        csv_file = self.storage_dir / "csv" / f"{analysis_id}.csv"

        # Create CSV with pattern summary
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)

            # Write header
            writer.writerow(['Analysis ID', 'Timestamp', 'Symbol', 'Timeframe', 'Patterns Found', 'Analysis Time'])
            writer.writerow([
                result.analysis_id,
                result.timestamp.isoformat(),
                result.symbol,
                result.timeframe,
                result.patterns_found,
                f"{result.analysis_time_seconds:.2f}s"
            ])

            # Write patterns
            if result.patterns:
                writer.writerow([])  # Empty row
                writer.writerow(['Pattern Type', 'Category', 'Confidence', 'Start Time', 'End Time', 'Description'])

                for pattern in result.patterns:
                    writer.writerow([
                        pattern.get('type', ''),
                        pattern.get('category', ''),
                        pattern.get('confidence', ''),
                        pattern.get('start_time', ''),
                        pattern.get('end_time', ''),
                        pattern.get('description', '')
                    ])

    def _load_json(self, analysis_id: str) -> Optional[AnalysisResult]:
        """Load result from JSON."""
        json_file = self.storage_dir / "json" / f"{analysis_id}.json"

        if not json_file.exists():
            return None

        with open(json_file, 'r') as f:
            data = json.load(f)

        return AnalysisResult.from_dict(data)

    def _load_pickle(self, analysis_id: str) -> Optional[AnalysisResult]:
        """Load result from pickle."""
        pickle_file = self.storage_dir / "pickle" / f"{analysis_id}.pkl"

        if not pickle_file.exists():
            return None

        with open(pickle_file, 'rb') as f:
            return pickle.load(f)
