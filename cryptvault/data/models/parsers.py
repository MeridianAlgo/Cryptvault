"""Data parsers for CSV and JSON formats."""

import json
import csv
from io import StringIO
from datetime import datetime
from typing import Dict, Any
from . import PricePoint, PriceDataFrame


class CSVParser:
    """Parse CSV formatted price data."""

    def parse(self, csv_data: str) -> PriceDataFrame:
        """Parse CSV data into PriceDataFrame."""
        reader = csv.DictReader(StringIO(csv_data))
        data_points = []

        for row in reader:
            point = PricePoint(
                timestamp=datetime.fromisoformat(row['timestamp']),
                open=float(row['open']),
                high=float(row['high']),
                low=float(row['low']),
                close=float(row['close']),
                volume=float(row['volume'])
            )
            data_points.append(point)

        return PriceDataFrame(data_points)

    def get_sample_format(self) -> str:
        """Get sample CSV format."""
        return "timestamp,open,high,low,close,volume"


class JSONParser:
    """Parse JSON formatted price data."""

    def parse(self, json_data: str) -> PriceDataFrame:
        """Parse JSON data into PriceDataFrame."""
        data = json.loads(json_data)
        data_points = []

        for item in data:
            point = PricePoint(
                timestamp=datetime.fromisoformat(item['timestamp']),
                open=float(item['open']),
                high=float(item['high']),
                low=float(item['low']),
                close=float(item['close']),
                volume=float(item['volume'])
            )
            data_points.append(point)

        return PriceDataFrame(data_points)

    def get_sample_format(self) -> str:
        """Get sample JSON format."""
        return '[{"timestamp":"2024-01-01T00:00:00","open":100,"high":105,"low":95,"close":102,"volume":1000}]'
