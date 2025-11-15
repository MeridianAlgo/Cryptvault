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
                    analysis_dict = analysis.to_dict() if hasattr(analysis, 'to_dict') else analysis
                    asset_analysis[asset.symbol] = {
                        'patterns_found': analysis_dict.get('patterns_found', 0),
                        'top_pattern': analysis_dict['patterns'][0] if analysis_dict.get('patterns') else None,
                        'ml_predictions': analysis_dict.get('ml_predictions')
                    }

            # Generate portfolio recommendations
            recommendations = self._generate_portfolio_recommendations(
                assets, correlation_matrix, portfolio_metrics, asset_analysis
            )

            # Calculate diversification score
            diversification_score = self._calculate_diversification_score(correlation_matrix)

            return {
                'success': True,
                'portfolio_metrics': portfolio_metrics,
                'correlation_matrix': correlation_matrix,
                'asset_analysis': asset_analysis,
                'recommendations': recommendations,
                'diversification_score': diversification_score,
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

        # Calculate current portfolio value
        portfolio_value = 0.0
        for asset in assets:
            if asset.symbol in asset_data and asset.current_price:
                # Calculate monetary value based on allocation percentage
                # Assuming the allocation represents percentage of total portfolio value
                asset_value = (asset.allocation / total_allocation) * 10000  # Base portfolio value of $10,000
                portfolio_value += asset_value

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
        if portfolio_returns:
            daily_return = portfolio_returns[-1] if portfolio_returns else 0.0
        else:
            daily_return = 0.0

        return PortfolioMetrics(
            total_value=portfolio_value,
            daily_return=daily_return,
            volatility=np.std(portfolio_returns) if portfolio_returns else 0.0,
            sharpe_ratio=self._calculate_sharpe_ratio(portfolio_returns) if portfolio_returns else 0.0,
            max_drawdown=self._calculate_max_drawdown(portfolio_returns) if portfolio_returns else 0.0,
            correlation_score=0.5,  # Placeholder
            diversification_ratio=0.7  # Placeholder
        )

    def _calculate_sharpe_ratio(self, portfolio_returns):
        # Sharpe ratio (assuming 0% risk-free rate)
        daily_return = np.mean(portfolio_returns)
        volatility = np.std(portfolio_returns)
        return daily_return / volatility if volatility > 0 else 0

    def _calculate_max_drawdown(self, portfolio_returns):
        # Max drawdown
        cumulative_returns = np.cumprod([1 + r for r in portfolio_returns])
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdowns = (cumulative_returns - running_max) / running_max
        return np.min(drawdowns)
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

    def _calculate_diversification_score(self, correlation_matrix: CorrelationMatrix) -> float:
        """Calculate diversification score based on asset correlations.
        
        Args:
            correlation_matrix: Matrix of correlations between assets
            
        Returns:
            Diversification score (0-100)
        """
        if not correlation_matrix or len(correlation_matrix.symbols) < 2:
            return 0.0
        
        # Get correlation matrix
        matrix = correlation_matrix.matrix
        
        # Calculate average off-diagonal correlation (excluding self-correlations)
        n = len(matrix)
        if n <= 1:
            return 0.0
            
        sum_correlations = 0.0
        count = 0
        
        for i in range(n):
            for j in range(n):
                if i != j:  # Skip diagonal elements (self-correlations)
                    sum_correlations += abs(matrix[i][j])
                    count += 1
        
        if count == 0:
            return 0.0
            
        avg_correlation = sum_correlations / count
        
        # Convert correlation to diversification score
        # Lower correlation = higher diversification
        # Score: 100 when avg correlation is 0, 0 when avg correlation is 1
        diversification_score = (1 - avg_correlation) * 100
        
        return max(0.0, min(100.0, diversification_score))

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

    def compare_assets(self, symbols: List[str], days: int = 30) -> Dict[str, Any]:
        """Compare multiple assets side by side.
        
        Args:
            symbols: List of asset symbols to compare
            days: Number of days of data to analyze
            
        Returns:
            Comparison results with metrics for each asset
        """
        try:
            self.logger.info(f"Comparing {len(symbols)} assets")
            
            # Fetch data for all symbols
            asset_data = {}
            for symbol in symbols:
                data = self.data_fetcher.fetch_historical_data(symbol, days, '1d')
                if data:
                    asset_data[symbol] = data
            
            if len(asset_data) < 2:
                return {'success': False, 'error': 'Need at least 2 assets with data'}
            
            # Analyze each asset
            asset_analysis = {}
            for symbol, data in asset_data.items():
                analysis = self.pattern_analyzer.analyze_dataframe(data)
                analysis_dict = analysis.to_dict() if hasattr(analysis, 'to_dict') else analysis
                
                # Calculate basic metrics
                prices = [point.close for point in data.data]
                if len(prices) >= 2:
                    current_price = prices[-1]
                    price_change = (prices[-1] - prices[-2]) / prices[-2] if len(prices) >= 2 else 0
                    volatility = np.std([(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]) if len(prices) > 1 else 0
                else:
                    current_price = 0
                    price_change = 0
                    volatility = 0
                
                asset_analysis[symbol] = {
                    'current_price': current_price,
                    'price_change_24h': price_change * 100,  # Convert to percentage
                    'volatility': volatility * 100,  # Convert to percentage
                    'patterns_found': analysis_dict.get('patterns_found', 0),
                    'top_pattern': analysis_dict['patterns'][0] if analysis_dict.get('patterns') else None,
                    'technical_indicators': analysis_dict.get('technical_indicators', {}),
                    'recommendations': analysis_dict.get('recommendations', [])
                }
            
            # Calculate correlations between assets
            correlation_matrix = self._calculate_correlations(asset_data)
            
            # Generate comparison insights
            insights = self._generate_comparison_insights(asset_analysis, correlation_matrix)
            
            return {
                'success': True,
                'asset_analysis': asset_analysis,
                'correlation_matrix': correlation_matrix,
                'insights': insights,
                'analysis_timestamp': datetime.now()
            }
            
        except Exception as e:
            self.logger.error(f"Asset comparison failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _generate_comparison_insights(self, asset_analysis: Dict, correlation_matrix: CorrelationMatrix) -> List[str]:
        """Generate insights from asset comparison."""
        insights = []
        
        # Find best performer
        best_performer = None
        best_change = -float('inf')
        for symbol, analysis in asset_analysis.items():
            change = analysis.get('price_change_24h', 0)
            if change > best_change:
                best_change = change
                best_performer = symbol
        
        if best_performer:
            insights.append(f"Best 24h performer: {best_performer} ({best_change:.2f}%)")
        
        # Find most volatile
        most_volatile = None
        highest_volatility = -1
        for symbol, analysis in asset_analysis.items():
            vol = analysis.get('volatility', 0)
            if vol > highest_volatility:
                highest_volatility = vol
                most_volatile = symbol
        
        if most_volatile:
            insights.append(f"Most volatile: {most_volatile} ({highest_volatility:.2f}%)")
        
        # Correlation insights
        if len(correlation_matrix.symbols) >= 2:
            matrix = correlation_matrix.matrix
            n = len(matrix)
            max_corr = 0
            min_corr = 1
            max_pair = None
            min_pair = None
            
            for i in range(n):
                for j in range(i+1, n):
                    corr = abs(matrix[i][j])
                    if corr > max_corr:
                        max_corr = corr
                        max_pair = (correlation_matrix.symbols[i], correlation_matrix.symbols[j])
                    if corr < min_corr:
                        min_corr = corr
                        min_pair = (correlation_matrix.symbols[i], correlation_matrix.symbols[j])
            
            if max_pair:
                insights.append(f"Highest correlation: {max_pair[0]}-{max_pair[1]} ({max_corr:.2f})")
            if min_pair:
                insights.append(f"Lowest correlation: {min_pair[0]}-{min_pair[1]} ({min_corr:.2f})")
        
        return insights
