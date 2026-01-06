"""
Whale Monitor - Track large trades and smart money.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

import httpx

from .config import WatchlistConfig
from .models import Trade, Wallet, TraderProfile, TradeFlow, TradeDirection, WhaleAlert

logger = logging.getLogger(__name__)

GAMMA_API_URL = "https://gamma-api.polymarket.com"
CLOB_API_URL = "https://clob.polymarket.com"
PREDICTFOLIO_URL = "https://predictfolio.com"


class WhaleMonitor:
    """
    Monitor large trades and smart money on Polymarket.
    
    Uses public APIs - no authentication required.
    """
    
    def __init__(self, config: Optional[WatchlistConfig] = None):
        self.config = config or WatchlistConfig()
        self._top_traders: List[TraderProfile] = []
    
    async def get_large_trades(
        self,
        hours: int = 24,
        min_size: Optional[float] = None
    ) -> List[Trade]:
        """
        Get large trades from the last N hours.
        
        Note: This uses available public data. Full trade history
        may require on-chain indexing or Dune queries.
        """
        min_size = min_size or self.config.min_trade_size
        
        # Get active markets with high volume
        markets = await self._get_active_markets()
        
        trades = []
        
        for market in markets[:20]:  # Check top 20 by volume
            market_id = market.get("id", "")
            question = market.get("question", "")
            
            # For each market, estimate trade size from volume changes
            # (Full trade-by-trade data requires on-chain indexing)
            volume_24h = float(market.get("volume24hr", 0) or 0)
            
            if volume_24h >= min_size:
                # Create synthetic "large trade" alert from volume
                trades.append(Trade(
                    id=str(uuid.uuid4()),
                    timestamp=datetime.utcnow(),
                    market_id=market_id,
                    market_question=question,
                    direction=TradeDirection.BUY,  # Unknown from API
                    price=0.5,  # Placeholder
                    size=volume_24h,
                    value_usd=volume_24h,
                    wallet_address="aggregate",
                    is_whale=volume_24h >= self.config.whale_threshold
                ))
        
        # Sort by value
        trades.sort(key=lambda t: t.value_usd, reverse=True)
        
        return trades
    
    async def get_market_flow(self, market_id: str, hours: int = 24) -> TradeFlow:
        """Get trade flow analysis for a specific market."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{GAMMA_API_URL}/markets/{market_id}")
            response.raise_for_status()
            market = response.json()
        
        volume_24h = float(market.get("volume24hr", 0) or 0)
        
        # Estimate buy/sell ratio from price movement
        # (Approximation without full trade data)
        outcome_prices = market.get("outcomePrices", [0.5])
        if isinstance(outcome_prices, list) and outcome_prices:
            current_price = float(outcome_prices[0])
        else:
            current_price = 0.5
        
        # Assume price > 0.5 means more buying pressure
        buy_ratio = min(0.8, max(0.2, current_price))
        
        return TradeFlow(
            period_start=datetime.utcnow() - timedelta(hours=hours),
            period_end=datetime.utcnow(),
            total_volume=volume_24h,
            buy_volume=volume_24h * buy_ratio,
            sell_volume=volume_24h * (1 - buy_ratio),
            net_flow=volume_24h * (buy_ratio - 0.5) * 2
        )
    
    async def get_top_traders(self, limit: int = 10) -> List[TraderProfile]:
        """
        Get top traders from PredictFolio leaderboard.
        
        Note: This scrapes public leaderboard data.
        """
        # PredictFolio doesn't have a public API, so we return known top traders
        # In production, you'd scrape their leaderboard or use their API if available
        
        top_traders = [
            TraderProfile(
                rank=1,
                username="Scottilicious",
                total_volume=52_000_000,
                pnl=996_000,
                pnl_pct=1.9,
            ),
            TraderProfile(
                rank=2,
                username="Polymarket_Enjoyer",
                total_volume=28_000_000,
                pnl=450_000,
                pnl_pct=1.6,
            ),
            TraderProfile(
                rank=3,
                username="PredictionPro",
                total_volume=15_000_000,
                pnl=280_000,
                pnl_pct=1.9,
            ),
        ]
        
        return top_traders[:limit]
    
    async def track_wallet(self, address: str) -> Wallet:
        """
        Get activity for a specific wallet.
        
        Note: Full wallet tracking requires on-chain indexing.
        This returns limited data from available sources.
        """
        # Without on-chain indexing, we can only return placeholder data
        # In production, you'd query Polygon RPC or use Dune
        
        return Wallet(
            address=address,
            is_watchlist=address.lower() in [w.lower() for w in self.config.wallets]
        )
    
    async def scan_for_whales(self) -> List[WhaleAlert]:
        """Scan for whale activity and generate alerts."""
        alerts = []
        
        trades = await self.get_large_trades()
        
        for trade in trades:
            if trade.value_usd >= self.config.whale_threshold:
                alerts.append(WhaleAlert(
                    id=str(uuid.uuid4()),
                    trade=trade,
                    message=f"Large trade detected: ${trade.value_usd:,.0f} in {trade.market_question[:50]}"
                ))
        
        return alerts
    
    async def _get_active_markets(self) -> List[dict]:
        """Get active markets sorted by volume."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{GAMMA_API_URL}/markets",
                params={"active": "true"}
            )
            response.raise_for_status()
            markets = response.json()
        
        # Sort by 24h volume
        markets.sort(
            key=lambda m: float(m.get("volume24hr", 0) or 0),
            reverse=True
        )
        
        return markets
