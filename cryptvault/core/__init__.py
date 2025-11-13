"""
Core Business Logic Module

This module contains the core business logic for CryptVault, including
the main analysis orchestrator and portfolio management.

Components:
    - analyzer: Main analysis orchestrator with comprehensive error handling
    - portfolio: Portfolio analysis and management

Example:
    >>> from cryptvault.core.analyzer import PatternAnalyzer, AnalysisResult
    >>> analyzer = PatternAnalyzer()
    >>> result = analyzer.analyze_ticker('BTC', days=60)
    >>> if result.success:
    ...     print(f"Found {len(result.patterns)} patterns")
"""

from .analyzer import PatternAnalyzer, AnalysisResult, ResultValidator

__all__ = ['PatternAnalyzer', 'AnalysisResult', 'ResultValidator']
