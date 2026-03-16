"""
Alternative Data Sources for Enhanced Predictions

Fetches sentiment, on-chain metrics, and other alternative data.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Optional

import numpy as np
import pandas as pd
import requests

logger = logging.getLogger(__name__)


class AlternativeDataFetcher:
    """Fetch alternative data sources for crypto analysis."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "CryptVault/5.1.0"})

    def fetch_fear_greed_index(self, days: int = 30) -> Optional[pd.DataFrame]:
        """
        Fetch Crypto Fear & Greed Index.
        
        Free API, no key required.
        Range: 0-100 (0=Extreme Fear, 100=Extreme Greed)
        """
        try:
            url = f"https://api.alternative.me/fng/?limit={days}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if "data" not in data:
                logger.warning("No fear & greed data available")
                return None
            
            records = []
            for item in data["data"]:
                records.append({
                    "timestamp": datetime.fromtimestamp(int(item["timestamp"])),
                    "fear_greed_value": int(item["value"]),
                })
            
            df = pd.DataFrame(records)
            df.set_index("timestamp", inplace=True)
            df.sort_index(inplace=True)
            
            # Add derived features
            df["fear_greed_ma7"] = df["fear_greed_value"].rolling(7).mean()
            df["fear_greed_ma30"] = df["fear_greed_value"].rolling(30).mean()
            df["fear_greed_change"] = df["fear_greed_value"].diff()
            
            logger.info(f"Fetched {len(df)} days of Fear & Greed Index")
            return df
            
        except Exception as e:
            logger.error(f"Failed to fetch Fear & Greed Index: {e}")
            return None

    def fetch_google_trends_proxy(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        Fetch search interest proxy using CoinGecko trending data.
        
        Free API, no key required.
        """
        try:
            # Map symbols to CoinGecko IDs
            symbol_map = {
                "BTC": "bitcoin",
                "ETH": "ethereum",
                "SOL": "solana",
                "BNB": "binancecoin"
            }
            
            base_symbol = symbol.replace("-USD", "")
            coin_id = symbol_map.get(base_symbol, base_symbol.lower())
            
            # Get trending score (0-100)
            url = "https://api.coingecko.com/api/v3/search/trending"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Check if coin is in trending
            trending_score = 0
            if "coins" in data:
                for idx, item in enumerate(data["coins"]):
                    if item["item"]["id"] == coin_id:
                        trending_score = 100 - (idx * 10)  # Higher rank = higher score
                        break
            
            # Create simple dataframe
            df = pd.DataFrame({
                "timestamp": [datetime.now()],
                "trending_score": [trending_score],
                "is_trending": [trending_score > 0]
            })
            df.set_index("timestamp", inplace=True)
            
            logger.info(f"Trending score for {symbol}: {trending_score}")
            return df
            
        except Exception as e:
            logger.error(f"Failed to fetch trending data: {e}")
            return None

    def fetch_on_chain_metrics(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        Fetch basic on-chain metrics using CoinGecko.
        
        Free API, no key required.
        Includes: market cap, volume, circulating supply, etc.
        """
        try:
            symbol_map = {
                "BTC": "bitcoin",
                "ETH": "ethereum",
                "SOL": "solana",
                "BNB": "binancecoin"
            }
            
            base_symbol = symbol.replace("-USD", "")
            coin_id = symbol_map.get(base_symbol, base_symbol.lower())
            
            url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
            params = {
                "localization": "false",
                "tickers": "false",
                "community_data": "true",
                "developer_data": "false"
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract relevant metrics
            market_data = data.get("market_data", {})
            community_data = data.get("community_data", {})
            
            metrics = {
                "timestamp": datetime.now(),
                "market_cap_rank": data.get("market_cap_rank", 0),
                "market_cap_usd": market_data.get("market_cap", {}).get("usd", 0),
                "total_volume_usd": market_data.get("total_volume", {}).get("usd", 0),
                "circulating_supply": market_data.get("circulating_supply", 0),
                "total_supply": market_data.get("total_supply", 0),
                "max_supply": market_data.get("max_supply", 0),
                "price_change_24h": market_data.get("price_change_percentage_24h", 0),
                "price_change_7d": market_data.get("price_change_percentage_7d", 0),
                "price_change_30d": market_data.get("price_change_percentage_30d", 0),
                "market_cap_change_24h": market_data.get("market_cap_change_percentage_24h", 0),
                "twitter_followers": community_data.get("twitter_followers", 0),
                "reddit_subscribers": community_data.get("reddit_subscribers", 0),
                "reddit_active_48h": community_data.get("reddit_accounts_active_48h", 0),
            }
            
            df = pd.DataFrame([metrics])
            df.set_index("timestamp", inplace=True)
            
            logger.info(f"Fetched on-chain metrics for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Failed to fetch on-chain metrics: {e}")
            return None

    def fetch_exchange_metrics(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        Fetch exchange-related metrics.
        
        Includes volume, liquidity, and exchange data.
        """
        try:
            symbol_map = {
                "BTC": "bitcoin",
                "ETH": "ethereum",
                "SOL": "solana",
                "BNB": "binancecoin"
            }
            
            base_symbol = symbol.replace("-USD", "")
            coin_id = symbol_map.get(base_symbol, base_symbol.lower())
            
            # Get ticker data from multiple exchanges
            url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/tickers"
            params = {"depth": "true"}
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            tickers = data.get("tickers", [])
            
            if not tickers:
                return None
            
            # Aggregate metrics
            total_volume_24h = sum(t.get("converted_volume", {}).get("usd", 0) for t in tickers)
            avg_spread = np.mean([t.get("bid_ask_spread_percentage", 0) for t in tickers if t.get("bid_ask_spread_percentage")])
            num_exchanges = len(set(t.get("market", {}).get("identifier", "") for t in tickers))
            
            # Calculate liquidity score (higher volume, lower spread = better)
            liquidity_score = (total_volume_24h / 1e9) / (avg_spread + 0.01) if avg_spread else 0
            
            metrics = {
                "timestamp": datetime.now(),
                "total_volume_24h_usd": total_volume_24h,
                "avg_bid_ask_spread": avg_spread,
                "num_exchanges": num_exchanges,
                "liquidity_score": liquidity_score,
            }
            
            df = pd.DataFrame([metrics])
            df.set_index("timestamp", inplace=True)
            
            logger.info(f"Fetched exchange metrics for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Failed to fetch exchange metrics: {e}")
            return None

    def fetch_all_alternative_data(self, symbol: str, days: int = 30) -> Dict[str, pd.DataFrame]:
        """
        Fetch all available alternative data sources.
        
        Args:
            symbol: Cryptocurrency symbol (e.g., 'BTC-USD')
            days: Number of days of historical data
            
        Returns:
            Dictionary of dataframes with alternative data
        """
        data = {}
        
        # Fear & Greed Index (market sentiment)
        fg_data = self.fetch_fear_greed_index(days)
        if fg_data is not None:
            data["fear_greed"] = fg_data
        
        # Trending/Search interest
        trending_data = self.fetch_google_trends_proxy(symbol)
        if trending_data is not None:
            data["trending"] = trending_data
        
        # On-chain metrics
        onchain_data = self.fetch_on_chain_metrics(symbol)
        if onchain_data is not None:
            data["onchain"] = onchain_data
        
        # Exchange metrics
        exchange_data = self.fetch_exchange_metrics(symbol)
        if exchange_data is not None:
            data["exchange"] = exchange_data
        
        logger.info(f"Fetched {len(data)} alternative data sources for {symbol}")
        return data


def merge_alternative_data(
    price_df: pd.DataFrame,
    alt_data: Dict[str, pd.DataFrame]
) -> pd.DataFrame:
    """
    Merge alternative data with price data.
    
    Args:
        price_df: DataFrame with price data (indexed by timestamp)
        alt_data: Dictionary of alternative data DataFrames
        
    Returns:
        Merged DataFrame with all features
    """
    merged = price_df.copy()
    
    for source_name, source_df in alt_data.items():
        if source_df is None or source_df.empty:
            continue
        
        # Forward fill to match price data frequency
        source_df = source_df.reindex(merged.index, method="ffill")
        
        # Add prefix to avoid column name conflicts
        source_df = source_df.add_prefix(f"{source_name}_")
        
        # Merge
        merged = pd.concat([merged, source_df], axis=1)
    
    logger.info(f"Merged data shape: {merged.shape}")
    return merged
