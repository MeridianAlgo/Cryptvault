"""Portfolio analysis and correlation system for multiple cryptocurrencies."""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass

from ..data.models import PriceDataFrame
from ..data.package_fetcher import PackageDataFetcher
from ..analyzer import PatternAnalyzer


@dataclass
class PortfolioAsset:
    """Portfolio asset with allocation."""
    symbol: str
    allocation: float  # Percentage (0.0 to 1.0)
    current_price: Optional[float] = None
    price_change_24h: Optional[float] = None


@dataclass
class CorrelationMatrix:
    """Correlation matrix between assets."""
    symbols: List[str]
    matrix: np.ndarray
    timeframe: str
    calculated_at: datetime


@dataclass
class PortfolioMetrics:
    """Portfolio performance metrics."""
    total_value: float
    daily_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    correlation_score: float
    diversification_ratio: float


class PortfolioAnalyzer:
    """Analyze cryptocurrency portfolios and correlations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_fetcher = PackageDataFetcher()
        self.pattern_analyzer = PatternAnalyzer()
    
    def analyze_portfolio(self, assets: List[PortfolioAsset], 
                         days: int = 30) -> Dict[str, Any]:
        """Analyze portfolio performance and correlations."""
        try:
            self.logger.info(f"Analyzing portfolio with {len(assets)} assets")
            
            # Fetch data for all assets
            asset_data = {}
            for asset in assets:
                data = self.data_fetcher.fetch_historical_data(asset.symbol, days, '1d')
                if data:
                    asset_data[asset.symbol] = data
                    asset.current_price = data.data[-1].close
                    
                    # Calculate 24h change
                    if len(data.data) >= 2:
                        prev_price = data.data[-2].close
                        asset.price_change_24h = (asset.current_price - prev_price) / prev_price
            
            if len(asset_data) < 2:
                return {'success': False, 'error': 'Need at least 2 assets with data'}
            
            # Calculate correlations
            correlation_matrix = self._calculate_correlations(asset_data)
            
            # Calculate portfolio metrics
            portfolio_metrics = self._calculate_portfolio_metrics(assets, asset_data)
            
            # Analyze individual assets
            asset_analysis = {}
            for asset in assets:
                if asset.symbol in asset_data:
                    analysis = self.pattern_analyzer.analyze_dataframe(asset_data[asset.symbol])
                    asset_analysis[asset.symbol] = {
                        'patterns_found': analysis.get('patterns_found', 0),
                        'top_pattern': analysis['patterns'][0] if analysis.get('patterns') else None,
                        'ml_predictions': analysis.get('ml_predictions')
                    }
            
            # Generate portfolio recommendations
            recommendations = self._generate_portfolio_recommendations(
                assets, correlation_matrix, portfolio_metrics, asset_analysis
            )
            
            return {
                'success': True,
                'portfolio_metrics': portfolio_metrics,
                'correlation_matrix': correlation_matrix,
                'asset_analysis': asset_analysis,
                'recommendations': recommendations,
                'analysis_timestamp': datetime.now()
            }
        
        except Exception as e:
            self.logger.error(f"Portfolio analysis failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _calculate_correlations(self, asset_data: Dict[str, PriceDataFrame]) -> CorrelationMatrix:
        """Calculate correlation matrix between assets."""
        symbols = list(asset_data.keys())
        
        # Get price series for each asset
        price_series = {}
        min_length = float('inf')
        
        for symbol, data in asset_data.items():
            prices = [point.close for point in data.data]
            price_series[symbol] = prices
            min_length = min(min_length, len(prices))
        
        # Align all series to same length
        for symbol in symbols:
            price_series[symbol] = price_series[symbol][-min_length:]
        
        # Calculate returns
        returns_matrix = []
        for symbol in symbols:
            prices = price_series[symbol]
            returns = [(prices[i] - prices[i-1]) / prices[i-1] 
                      for i in range(1, len(prices))]
            returns_matrix.append(returns)
        
        # Calculate correlation matrix
        returns_array = np.array(returns_matrix)
        correlation_matrix = np.corrcoef(returns_array)
        
        return CorrelationMatrix(
            symbols=symbols,
            matrix=correlation_matrix,
            timeframe='30d',
            calculated_at=datetime.now()
        )
    
    def _calculate_portfolio_metrics(self, assets: List[PortfolioAsset], 
                                   asset_data: Dict[str, PriceDataFrame]) -> PortfolioMetrics:
        """Calculate portfolio performance metrics."""
        # Calculate weighted returns
        portfolio_returns = []
        total_allocation = sum(asset.allocation for asset in assets)
        
        # Get aligned price data
        min_length = min(len(asset_data[asset.symbol].data) 
                        for asset in assets if asset.symbol in asset_data)
        
        for i in range(1, min_length):
            daily_return = 0.0
            
            for asset in assets:
                if asset.symbol in asset_data:
                    data = asset_data[asset.symbol].data
                    prev_price = data[-(min_length-i+1)].close
                    curr_price = data[-(min_length-i)].close
                    
                    asset_return = (curr_price - prev_price) / prev_price
                    weight = asset.allocation / total_allocation
                    daily_return += asset_return * weight
            
            portfolio_returns.append(daily_return)
        
        # Calculate metrics
        if not portfolio_returns:
            return PortfolioMetrics(0, 0, 0, 0, 0, 0, 0)
        
        daily_return = np.mean(portfolio_returns)
        volatility = np.std(portfolio_returns)
        
        # Sharpe ratio (assuming 0% risk-free rate)
        sharpe_ratio = daily_return / volatility if volatility > 0 else 0
        
        # Max drawdown
        cumulative_returns = np.cumprod([1 + r for r in portfolio_returns])
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdowns = (cumulative_returns - running_max) / running_max
        max_drawdown = np.min(drawdowns)
        
        # Portfolio value (assuming $10,000 base)
        total_value = 10000 * cumulative_returns[-1]
        
        # Correlation score (average correlation)
        correlation_score = 0.5  # Placeholder
        diversification_ratio = 0.7  # Placeholder
        
        return PortfolioMetrics(
            total_value=total_value,
            daily_return=daily_return,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            correlation_score=correlation_score,
            diversification_ratio=diversification_ratio
        )
    
    def _generate_portfolio_recommendations(self, assets: List[PortfolioAsset],
                                          correlation_matrix: CorrelationMatrix,
                                          metrics: PortfolioMetrics,
                                          asset_analysis: Dict) -> List[str]:
        """Generate portfolio optimization recommendations."""
        recommendations = []
        
        # Correlation analysis
        high_correlations = []
        for i, symbol1 in enumerate(correlation_matrix.symbols):
            for j, symbol2 in enumerate(correlation_matrix.symbols):
                if i < j:  # Avoid duplicates
                    corr = correlation_matrix.matrix[i][j]
                    if corr > 0.8:
                        high_correlations.append((symbol1, symbol2, corr))
        
        if high_correlations:
            recommendations.append(
                f"High correlation detected: Consider reducing exposure to highly correlated assets"
            )
        
        # Allocation analysis
        max_allocation = max(asset.allocation for asset in assets)
        if max_allocation > 0.5:
            recommendations.append(
                "Consider reducing concentration risk - largest position exceeds 50%"
            )
        
        # Performance analysis
        if metrics.sharpe_ratio < 0.5:
            recommendations.append(
                "Low risk-adjusted returns - consider rebalancing or asset selection review"
            )
        
        if metrics.max_drawdown < -0.2:
            recommendations.append(
                "High drawdown risk detected - consider adding defensive assets"
            )
        
        # Pattern-based recommendations
        bullish_assets = []
        bearish_assets = []
        
        for symbol, analysis in asset_analysis.items():
            if analysis.get('top_pattern'):
                pattern = analysis['top_pattern']
                if pattern.get('is_bullish'):
                    bullish_assets.append(symbol)
                elif pattern.get('is_bearish'):
                    bearish_assets.append(symbol)
        
        if bullish_assets:
            recommendations.append(
                f"Bullish patterns detected in: {', '.join(bullish_assets)} - consider increasing allocation"
            )
        
        if bearish_assets:
            recommendations.append(
                f"Bearish patterns detected in: {', '.join(bearish_assets)} - consider reducing allocation"
            )
        
        return recommendations
    
    def suggest_rebalancing(self, current_assets: List[PortfolioAsset],
                          target_volatility: float = 0.15) -> Dict[str, float]:
        """Suggest portfolio rebalancing based on risk targets."""
        # Simplified rebalancing suggestion
        total_allocation = sum(asset.allocation for asset in current_assets)
        equal_weight = 1.0 / len(current_assets)
        
        suggestions = {}
        for asset in current_assets:
            # Move towards equal weight with some adjustment
            current_weight = asset.allocation / total_allocation
            suggested_weight = (current_weight + equal_weight) / 2
            suggestions[asset.symbol] = suggested_weight
        
        return suggestions
    
    def calculate_portfolio_var(self, assets: List[PortfolioAsset], 
                               confidence: float = 0.95) -> float:
        """Calculate portfolio Value at Risk."""
        # Simplified VaR calculation
        portfolio_volatility = 0.15  # Placeholder
        z_score = 1.96 if confidence == 0.95 else 2.33  # 95% or 99%
        
        return portfolio_volatility * z_score