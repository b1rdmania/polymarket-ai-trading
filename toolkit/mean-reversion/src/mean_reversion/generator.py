"""
Signal Generator - Core mean reversion logic.

Based on Berg & Rietz (2018) and behavioral finance research:
- Overconfidence bias at intermediate horizons (1-3 weeks)
- Longshots tend to be underpriced at these horizons
- Favorites tend to be overpriced
- Bias disappears near resolution
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Optional

import httpx

from .config import SignalConfig
from .models import Signal, SignalType, SignalDirection, SignalStrength, SignalSummary

logger = logging.getLogger(__name__)

GAMMA_API_URL = "https://gamma-api.polymarket.com"
CLOB_API_URL = "https://clob.polymarket.com"


class SignalGenerator:
    """
    Generates mean reversion signals from Polymarket data.
    
    Based on behavioral finance research showing:
    - Overconfidence bias at 1-3 week horizons
    - Longshots underpriced, favorites overpriced
    - Price spikes from emotional reaction tend to revert
    """
    
    def __init__(self, config: Optional[SignalConfig] = None):
        self.config = config or SignalConfig()
    
    async def scan(self, limit: int = 50) -> List[Signal]:
        """
        Scan markets for mean reversion signals.
        
        Returns signals sorted by strength.
        """
        signals = []
        
        # Get active markets
        markets = await self._get_markets(limit * 2)  # Fetch more, filter down
        
        for market in markets:
            try:
                signal = await self._analyze_market(market)
                if signal:
                    signals.append(signal)
            except Exception as e:
                logger.debug(f"Failed to analyze market: {e}")
                continue
        
        # Sort by absolute mispricing
        signals.sort(key=lambda s: abs(s.mispricing_pct), reverse=True)
        
        return signals[:limit]
    
    async def analyze(self, market_id: str) -> Optional[Signal]:
        """Analyze a specific market for signals."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{GAMMA_API_URL}/markets/{market_id}")
                response.raise_for_status()
                market = response.json()
                return await self._analyze_market(market)
        except Exception as e:
            logger.error(f"Failed to analyze market {market_id}: {e}")
            return None
    
    async def get_summary(self) -> SignalSummary:
        """Get summary of current signals."""
        signals = await self.scan(limit=100)
        
        summary = SignalSummary(
            total_signals=len(signals),
            buy_signals=sum(1 for s in signals if s.direction == SignalDirection.BUY),
            sell_signals=sum(1 for s in signals if s.direction == SignalDirection.SELL),
            strong_signals=sum(1 for s in signals if s.strength in [SignalStrength.STRONG, SignalStrength.VERY_STRONG]),
            total_position_size=sum(s.position_size for s in signals),
            top_signals=signals[:5]
        )
        
        return summary
    
    async def _get_markets(self, limit: int) -> List[dict]:
        """Fetch markets from API."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{GAMMA_API_URL}/markets",
                params={"active": "true"}
            )
            response.raise_for_status()
            markets = response.json()
            
            # Filter by volume
            markets = [
                m for m in markets
                if float(m.get("volume24hr", 0) or 0) >= self.config.min_volume_24h
            ]
            
            # Sort by volume
            markets.sort(
                key=lambda m: float(m.get("volume24hr", 0) or 0),
                reverse=True
            )
            
            return markets[:limit]
    
    async def _analyze_market(self, market: dict) -> Optional[Signal]:
        """Analyze a single market for mean reversion opportunity."""
        market_id = market.get("id", "")
        question = market.get("question", "Unknown")
        
        # Check horizon
        horizon_days = self._get_horizon_days(market)
        if horizon_days is None:
            return None
        
        # Check if in optimal horizon range
        min_days, max_days = self.config.horizon_days
        if not (min_days <= horizon_days <= max_days):
            # Only generate signals in the overconfidence zone
            return None
        
        # Get current price
        token_ids = market.get("clobTokenIds", [])
        if not token_ids:
            return None
        
        price_data = await self._get_price_data(token_ids[0])
        if not price_data:
            return None
        
        current_price = price_data["mid"]
        spread_pct = price_data["spread_pct"]
        
        # Check spread
        if spread_pct > self.config.max_spread_pct:
            return None
        
        # Determine signal type
        signal = self._evaluate_mispricing(
            market=market,
            current_price=current_price,
            horizon_days=horizon_days,
            token_id=token_ids[0]
        )
        
        return signal
    
    def _get_horizon_days(self, market: dict) -> Optional[int]:
        """Calculate days until market resolution."""
        end_date = market.get("endDate")
        if not end_date:
            return None
        
        try:
            if isinstance(end_date, str):
                end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
            else:
                end_dt = datetime.fromtimestamp(int(end_date))
            
            now = datetime.utcnow()
            delta = end_dt.replace(tzinfo=None) - now
            return max(0, delta.days)
        except Exception:
            return None
    
    async def _get_price_data(self, token_id: str) -> Optional[dict]:
        """Get current price data from orderbook."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{CLOB_API_URL}/book",
                    params={"token_id": token_id}
                )
                response.raise_for_status()
                data = response.json()
                
                bids = data.get("bids", [])
                asks = data.get("asks", [])
                
                if not bids or not asks:
                    return None
                
                best_bid = float(bids[0]["price"])
                best_ask = float(asks[0]["price"])
                mid = (best_bid + best_ask) / 2
                spread_pct = ((best_ask - best_bid) / mid) * 100 if mid > 0 else 100
                
                return {
                    "bid": best_bid,
                    "ask": best_ask,
                    "mid": mid,
                    "spread_pct": spread_pct
                }
        except Exception as e:
            logger.debug(f"Failed to get price data: {e}")
            return None
    
    def _evaluate_mispricing(
        self,
        market: dict,
        current_price: float,
        horizon_days: int,
        token_id: str
    ) -> Optional[Signal]:
        """
        Evaluate if market is mispriced based on behavioral biases.
        
        At intermediate horizons (1-3 weeks):
        - Longshots (<30%) tend to be underpriced → BUY signal
        - Favorites (>70%) tend to be overpriced → SELL signal
        """
        
        # Determine if longshot or favorite
        is_longshot = current_price < self.config.longshot_threshold
        is_favorite = current_price > self.config.favorite_threshold
        
        if not is_longshot and not is_favorite:
            # Mid-range prices don't show systematic bias
            return None
        
        # Estimate fair value based on bias research
        # Berg & Rietz show ~5-10% mispricing at extremes
        if is_longshot:
            # Longshots are underpriced - fair value is higher
            bias_adjustment = 0.05 + (0.05 * (1 - current_price / self.config.longshot_threshold))
            fair_value = current_price + bias_adjustment
            direction = SignalDirection.BUY
            signal_type = SignalType.BUY_LONGSHOT
        else:
            # Favorites are overpriced - fair value is lower
            bias_adjustment = 0.05 + (0.05 * (current_price - self.config.favorite_threshold) / (1 - self.config.favorite_threshold))
            fair_value = current_price - bias_adjustment
            direction = SignalDirection.SELL
            signal_type = SignalType.SELL_FAVORITE
        
        mispricing_pct = ((fair_value - current_price) / current_price) * 100
        
        # Check if mispricing exceeds threshold
        if abs(mispricing_pct) < self.config.min_mispricing_pct:
            return None
        
        # Calculate edge and position size
        edge = abs(fair_value - current_price)
        
        # Kelly criterion: f* = edge / odds
        # For binary markets: f* = (p*b - q) / b where b = odds, p = prob of winning
        # Simplified: edge / variance
        variance = current_price * (1 - current_price)
        kelly_size = (edge / variance) * self.config.max_position_usd if variance > 0 else 0
        
        # Apply fractional Kelly and confidence discount
        position_size = kelly_size * self.config.kelly_fraction * self.config.confidence_discount
        
        # Clamp to limits
        position_size = max(self.config.min_position_usd, min(self.config.max_position_usd, position_size))
        
        # Determine strength
        if abs(mispricing_pct) >= 15:
            strength = SignalStrength.VERY_STRONG
        elif abs(mispricing_pct) >= 10:
            strength = SignalStrength.STRONG
        elif abs(mispricing_pct) >= 5:
            strength = SignalStrength.MODERATE
        else:
            strength = SignalStrength.WEAK
        
        return Signal(
            id=str(uuid.uuid4()),
            type=signal_type,
            direction=direction,
            strength=strength,
            market_id=market.get("id", ""),
            market_question=market.get("question", "Unknown"),
            market_slug=market.get("slug", ""),
            token_id=token_id,
            current_price=current_price,
            fair_value_estimate=fair_value,
            mispricing_pct=mispricing_pct,
            edge_estimate=edge,
            kelly_size=kelly_size,
            position_size=position_size,
            horizon_days=horizon_days,
            rationale=f"{'Longshot underpriced' if is_longshot else 'Favorite overpriced'} at {horizon_days}d horizon (overconfidence zone)"
        )
