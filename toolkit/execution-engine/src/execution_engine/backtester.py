"""
Historical Backtester

Tests trading signals on historical Polymarket data.

Limitations:
- Polymarket's historical API is incomplete for many markets
- We'll try multiple data sources
- Results are estimates (real trading has slippage, fees, etc.)
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import httpx
from pathlib import Path
import json

import sys
import os
toolkit_path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(toolkit_path))

from mean_reversion import SignalGenerator, SignalConfig
from mean_reversion.models import Signal, SignalDirection
from execution_engine.models import TradingConfig, Trade, TradeStatus
from execution_engine.position_sizer import PositionSizer
from execution_engine.risk_manager import RiskManager

logger = logging.getLogger(__name__)


class HistoricalBacktester:
    """
    Backtest trading signals on historical data.
    
    Data sources (in order of preference):
    1. Adjacent API (requires paid key)
    2. Polymarket CLOB historical (often empty)
    3. Recorded data (if you've been recording)
    4. Manual market data
    """
    
    def __init__(self, config: TradingConfig):
        self.config = config
        self.signal_generator = SignalGenerator(SignalConfig())
        self.position_sizer = PositionSizer(config)
        self.risk_manager = RiskManager(config)
        
        self.trades: List[Trade] = []
        self.capital = config.max_total_exposure_usd
        self.initial_capital = self.capital
        
    async def backtest_market(self, market_slug: str) -> Dict:
        """
        Backtest a single market.
        
        Args:
            market_slug: Market slug (e.g., "trump-popular-vote-2024")
        
        Returns:
            Backtest results dictionary
        """
        logger.info(f"Backtesting market: {market_slug}")
        
        # Try to get historical data
        historical_data = await self._fetch_historical_data(market_slug)
        
        if not historical_data:
            logger.warning(f"No historical data available for {market_slug}")
            return {"error": "No data available"}
        
        logger.info(f"Found {len(historical_data)} data points")
        
        # Simulate trading on historical data
        results = await self._simulate_trading(market_slug, historical_data)
        
        return results
    
    async def backtest_multiple_markets(
        self,
        market_slugs: List[str]
    ) -> Dict:
        """Backtest across multiple markets."""
        logger.info(f"Backtesting {len(market_slugs)} markets")
        
        all_results = []
        
        for slug in market_slugs:
            try:
                result = await self.backtest_market(slug)
                if "error" not in result:
                    all_results.append(result)
            except Exception as e:
                logger.error(f"Failed to backtest {slug}: {e}")
        
        # Aggregate results
        return self._aggregate_results(all_results)
    
    async def _fetch_historical_data(
        self,
        market_slug: str
    ) -> Optional[List[Dict]]:
        """
        Try to fetch historical data from available sources.
        """
        
        # Source 1: Try Polymarket CLOB API
        data = await self._try_polymarket_historical(market_slug)
        if data:
            return data
        
        # Source 2: Try Adjacent API (if key available)
        adjacent_key = os.getenv("ADJACENT_API_KEY")
        if adjacent_key:
            data = await self._try_adjacent_api(market_slug, adjacent_key)
            if data:
                return data
        
        # Source 3: Check recorded data
        data = self._try_recorded_data(market_slug)
        if data:
            return data
        
        logger.warning(f"No data source available for {market_slug}")
        return None
    
    async def _try_polymarket_historical(
        self,
        market_slug: str
    ) -> Optional[List[Dict]]:
        """Try Polymarket's CLOB historical endpoint."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # First get market info
                response = await client.get(
                    f"https://gamma-api.polymarket.com/markets/{market_slug}"
                )
                if response.status_code != 200:
                    return None
                
                market = response.json()
                token_ids = market.get("clobTokenIds", [])
                
                if not token_ids:
                    return None
                
                # Try to get historical prices
                response = await client.get(
                    "https://clob.polymarket.com/prices-history",
                    params={
                        "market": token_ids[0],
                        "interval": "1h",
                        "fidelity": 100
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    history = data.get("history", [])
                    
                    if history:
                        logger.info(f"Found {len(history)} data points from Polymarket")
                        return history
                
        except Exception as e:
            logger.debug(f"Polymarket historical fetch failed: {e}")
        
        return None
    
    async def _try_adjacent_api(
        self,
        market_slug: str,
        api_key: str
    ) -> Optional[List[Dict]]:
        """Try Adjacent API (paid service with better data)."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"https://api.adjacent.finance/v1/polymarket/market/{market_slug}/ohlcv",
                    headers={"Authorization": f"Bearer {api_key}"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Found data from Adjacent API")
                    return data
                
        except Exception as e:
            logger.debug(f"Adjacent API fetch failed: {e}")
        
        return None
    
    def _try_recorded_data(self, market_slug: str) -> Optional[List[Dict]]:
        """Check if we have recorded data for this market."""
        recordings_dir = Path("data/recordings")
        
        if not recordings_dir.exists():
            return None
        
        # Search through recorded files
        for file in recordings_dir.glob("snapshots_*.jsonl.gz"):
            # Would parse and filter for this market
            # Simplified for now
            pass
        
        return None
    
    async def _simulate_trading(
        self,
        market_slug: str,
        historical_data: List[Dict]
    ) -> Dict:
        """
        Simulate trading on historical data.
        
        For each data point:
        1. Check if signal would have triggered
        2. Calculate position size
        3. Simulate entry
        4. Track until exit condition
        5. Calculate P&L
        """
        
        trades = []
        positions = []
        
        for i, data_point in enumerate(historical_data):
            timestamp = datetime.fromtimestamp(data_point.get("t", 0))
            price = data_point.get("p", 0)
            
            # Check if we'd have a signal at this point
            # (Simplified - in reality we'd need more context)
            
            # For demonstration, let's check if price is at extreme
            if price < 0.30:  # Longshot
                # Would we have bought?
                signal_strength = "STRONG" if price < 0.25 else "MODERATE"
                
                # Simulate entry
                entry_trade = {
                    "timestamp": timestamp,
                    "entry_price": price,
                    "side": "BUY",
                    "market": market_slug,
                }
                
                # Look ahead to find exit
                exit_price = self._find_exit(historical_data[i:], price)
                
                if exit_price:
                    pnl = (exit_price - price) * 100  # 100 shares
                    entry_trade["exit_price"] = exit_price
                    entry_trade["pnl"] = pnl
                    
                    trades.append(entry_trade)
        
        # Calculate metrics
        total_pnl = sum(t.get("pnl", 0) for t in trades)
        winning_trades = [t for t in trades if t.get("pnl", 0) > 0]
        
        return {
            "market": market_slug,
            "total_trades": len(trades),
            "winning_trades": len(winning_trades),
            "win_rate": len(winning_trades) / len(trades) * 100 if trades else 0,
            "total_pnl": total_pnl,
            "trades": trades
        }
    
    def _find_exit(
        self,
        future_data: List[Dict],
        entry_price: float
    ) -> Optional[float]:
        """Find exit price (mean reversion target or stop loss)."""
        # Look for price moving back up
        for data_point in future_data[:100]:  # Look ahead ~100 periods
            price = data_point.get("p", 0)
            
            # Take profit at 10% gain
            if price >= entry_price * 1.10:
                return price
            
            # Stop loss at 20% loss
            if price <= entry_price * 0.80:
                return price
        
        # If no exit found, return last price
        if future_data:
            return future_data[-1].get("p", entry_price)
        
        return entry_price
    
    def _aggregate_results(self, results: List[Dict]) -> Dict:
        """Aggregate results across multiple markets."""
        total_trades = sum(r["total_trades"] for r in results)
        winning_trades = sum(r["winning_trades"] for r in results)
        total_pnl = sum(r["total_pnl"] for r in results)
        
        return {
            "markets_tested": len(results),
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "win_rate": winning_trades / total_trades * 100 if total_trades > 0 else 0,
            "total_pnl": total_pnl,
            "roi_pct": (total_pnl / self.initial_capital) * 100,
            "individual_results": results
        }
    
    def print_results(self, results: Dict):
        """Print backtest results."""
        print("\n" + "="*60)
        print("BACKTEST RESULTS")
        print("="*60)
        
        if "error" in results:
            print(f"Error: {results['error']}")
            return
        
        print(f"\nMarkets Tested: {results.get('markets_tested', 1)}")
        print(f"Total Trades: {results['total_trades']}")
        print(f"Winning Trades: {results['winning_trades']}")
        print(f"Win Rate: {results['win_rate']:.1f}%")
        print(f"Total P&L: ${results['total_pnl']:.2f}")
        print(f"ROI: {results.get('roi_pct', 0):.1f}%")
        
        print("\n" + "="*60 + "\n")


async def main():
    """Run backtest from command line."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Backtest on historical markets")
    parser.add_argument(
        '--market',
        required=True,
        help='Market slug to test (e.g., "trump-popular-vote-2024")'
    )
    parser.add_argument(
        '--config',
        default='config/trading.yaml',
        help='Trading config file'
    )
    
    args = parser.parse_args()
    
    # Create config
    config = TradingConfig()
    
    # Create backtester
    backtester = HistoricalBacktester(config)
    
    # Run backtest
    results = await backtester.backtest_market(args.market)
    
    # Print results
    backtester.print_results(results)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())


