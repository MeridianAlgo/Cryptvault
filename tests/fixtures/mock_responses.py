"""
Mock API responses for testing.

Provides mock responses for external API calls to avoid network dependencies.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List


def get_mock_yfinance_response(symbol: str = 'BTC-USD', days: int = 30) -> Dict[str, Any]:
    """
    Get mock yfinance API response.
    
    Args:
        symbol: Ticker symbol
        days: Number of days of data
        
    Returns:
        Mock response dictionary
    """
    base_time = datetime(2024, 1, 1)
    data = []
    
    for i in range(days):
        data.append({
            'Date': (base_time + timedelta(days=i)).strftime('%Y-%m-%d'),
            'Open': 50000.0 + (i * 100),
            'High': 51000.0 + (i * 100),
            'Low': 49000.0 + (i * 100),
            'Close': 50500.0 + (i * 100),
            'Volume': 1000000.0
        })
    
    return {
        'symbol': symbol,
        'data': data,
        'currency': 'USD'
    }


def get_mock_ccxt_response(symbol: str = 'BTC/USD', days: int = 30) -> List[List]:
    """
    Get mock CCXT API response.
    
    Args:
        symbol: Trading pair
        days: Number of days of data
        
    Returns:
        Mock OHLCV data in CCXT format
    """
    base_time = datetime(2024, 1, 1)
    data = []
    
    for i in range(days):
        timestamp = int((base_time + timedelta(days=i)).timestamp() * 1000)
        data.append([
            timestamp,
            50000.0 + (i * 100),  # Open
            51000.0 + (i * 100),  # High
            49000.0 + (i * 100),  # Low
            50500.0 + (i * 100),  # Close
            1000000.0             # Volume
        ])
    
    return data


def get_mock_cryptocompare_response(symbol: str = 'BTC', days: int = 30) -> Dict[str, Any]:
    """
    Get mock CryptoCompare API response.
    
    Args:
        symbol: Cryptocurrency symbol
        days: Number of days of data
        
    Returns:
        Mock response dictionary
    """
    base_time = datetime(2024, 1, 1)
    data = []
    
    for i in range(days):
        timestamp = int((base_time + timedelta(days=i)).timestamp())
        data.append({
            'time': timestamp,
            'open': 50000.0 + (i * 100),
            'high': 51000.0 + (i * 100),
            'low': 49000.0 + (i * 100),
            'close': 50500.0 + (i * 100),
            'volumefrom': 1000000.0,
            'volumeto': 50000000000.0
        })
    
    return {
        'Response': 'Success',
        'Data': data,
        'HasWarning': False
    }


def get_mock_error_response(error_type: str = 'rate_limit') -> Dict[str, Any]:
    """
    Get mock error response.
    
    Args:
        error_type: Type of error ('rate_limit', 'not_found', 'server_error')
        
    Returns:
        Mock error response
    """
    error_responses = {
        'rate_limit': {
            'error': 'Rate limit exceeded',
            'code': 429,
            'message': 'Too many requests. Please try again later.'
        },
        'not_found': {
            'error': 'Symbol not found',
            'code': 404,
            'message': 'The requested symbol was not found.'
        },
        'server_error': {
            'error': 'Internal server error',
            'code': 500,
            'message': 'An internal error occurred. Please try again.'
        },
        'invalid_request': {
            'error': 'Invalid request',
            'code': 400,
            'message': 'The request parameters are invalid.'
        }
    }
    
    return error_responses.get(error_type, error_responses['server_error'])


def get_mock_ticker_info(symbol: str = 'BTC') -> Dict[str, Any]:
    """
    Get mock ticker information.
    
    Args:
        symbol: Ticker symbol
        
    Returns:
        Mock ticker info dictionary
    """
    ticker_info = {
        'BTC': {
            'symbol': 'BTC',
            'name': 'Bitcoin',
            'type': 'crypto',
            'exchange': 'Binance',
            'currency': 'USD',
            'market_cap': 1000000000000.0,
            'description': 'Bitcoin is a decentralized digital currency'
        },
        'ETH': {
            'symbol': 'ETH',
            'name': 'Ethereum',
            'type': 'crypto',
            'exchange': 'Binance',
            'currency': 'USD',
            'market_cap': 500000000000.0,
            'description': 'Ethereum is a decentralized platform'
        },
        'AAPL': {
            'symbol': 'AAPL',
            'name': 'Apple Inc.',
            'type': 'stock',
            'exchange': 'NASDAQ',
            'currency': 'USD',
            'market_cap': 3000000000000.0,
            'description': 'Apple Inc. designs and manufactures consumer electronics'
        }
    }
    
    return ticker_info.get(symbol, ticker_info['BTC'])
