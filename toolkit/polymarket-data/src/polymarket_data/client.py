"""
Polymarket API Client

Read-only client for fetching data from Polymarket's public APIs.
No authentication required.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

import httpx

from .models import Market, Orderbook, OrderbookLevel, PriceHistory, PricePoint
from .rate_limiter import EndpointCategory, get_rate_limiter

logger = logging.getLogger(__name__)


# API endpoints
GAMMA_API_URL = "https://gamma-api.polymarket.com"
CLOB_API_URL = "https://clob.polymarket.com"


class PolymarketClient:
    """
    Read-only Polymarket API client.
    
    Fetches market data, orderbooks, and prices without requiring authentication.
    Rate limiting is built-in.
    
    Example:
        ```python
        client = PolymarketClient()
        
        # Search markets
        markets = await client.search("trump")
        
        # Get trending markets
        trending = await client.get_trending(timeframe="24h", limit=10)
        ```
    """
    
    def __init__(self, timeout: float = 30.0):
        """
        Initialize the client.
        
        Args:
            timeout: Request timeout in seconds (default 30)
        """
        self.timeout = timeout
        self._rate_limiter = get_rate_limiter()
    
    async def _request(
        self,
        url: str,
        category: EndpointCategory,
        params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Make a rate-limited API request."""
        await self._rate_limiter.acquire(category)
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
    
    # ========== Market Discovery ==========
    
    async def search(
        self,
        query: str,
        limit: int = 20,
        active_only: bool = True
    ) -> List[Market]:
        """
        Search markets by keyword.
        
        Args:
            query: Search query (market title, keywords)
            limit: Maximum results to return
            active_only: Only return active markets
        
        Returns:
            List of matching markets
        """
        params = {"query": query}
        if active_only:
            params["active"] = "true"
        
        data = await self._request(
            f"{GAMMA_API_URL}/markets",
            EndpointCategory.GAMMA_API,
            params
        )
        
        markets = [Market.model_validate(m) for m in data[:limit]]
        logger.info(f"Found {len(markets)} markets for query: {query}")
        return markets
    
    async def get_trending(
        self,
        timeframe: str = "24h",
        limit: int = 10
    ) -> List[Market]:
        """
        Get markets with highest trading volume.
        
        Args:
            timeframe: Volume period - '24h', '7d', or '30d'
            limit: Number of markets to return
        
        Returns:
            Markets sorted by volume (descending)
        """
        volume_key_map = {
            "24h": "volume24hr",
            "7d": "volume7d", 
            "30d": "volume30d"
        }
        volume_key = volume_key_map.get(timeframe, "volume24hr")
        
        data = await self._request(
            f"{GAMMA_API_URL}/markets",
            EndpointCategory.GAMMA_API,
            {"active": "true"}
        )
        
        # Sort by volume
        sorted_data = sorted(
            data,
            key=lambda m: float(m.get(volume_key, 0) or 0),
            reverse=True
        )
        
        markets = [Market.model_validate(m) for m in sorted_data[:limit]]
        logger.info(f"Found {len(markets)} trending markets ({timeframe})")
        return markets
    
    async def get_by_category(
        self,
        category: str,
        limit: int = 20,
        active_only: bool = True
    ) -> List[Market]:
        """
        Get markets by category/tag.
        
        Args:
            category: Category name (e.g., 'Politics', 'Sports', 'Crypto')
            limit: Maximum results
            active_only: Only active markets
        
        Returns:
            Markets in the category
        """
        params = {"tag": category}
        if active_only:
            params["active"] = "true"
        
        data = await self._request(
            f"{GAMMA_API_URL}/markets",
            EndpointCategory.GAMMA_API,
            params
        )
        
        markets = [Market.model_validate(m) for m in data[:limit]]
        logger.info(f"Found {len(markets)} markets in category: {category}")
        return markets
    
    async def get_closing_soon(
        self,
        hours: int = 24,
        limit: int = 20
    ) -> List[Market]:
        """
        Get markets closing within specified hours.
        
        Args:
            hours: Hours until close
            limit: Maximum results
        
        Returns:
            Markets closing soon, sorted by end date
        """
        cutoff = datetime.utcnow() + timedelta(hours=hours)
        
        data = await self._request(
            f"{GAMMA_API_URL}/markets",
            EndpointCategory.GAMMA_API,
            {"active": "true"}
        )
        
        closing_soon = []
        for m in data:
            end_date = m.get("endDate")
            if end_date:
                try:
                    if isinstance(end_date, str):
                        end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
                    else:
                        end_dt = datetime.fromtimestamp(int(end_date))
                    
                    if end_dt <= cutoff:
                        closing_soon.append(m)
                except Exception:
                    continue
        
        # Sort by end date (soonest first)
        closing_soon.sort(key=lambda m: m.get("endDate", ""))
        
        markets = [Market.model_validate(m) for m in closing_soon[:limit]]
        logger.info(f"Found {len(markets)} markets closing within {hours}h")
        return markets
    
    async def get_market(self, slug_or_id: str) -> Optional[Market]:
        """
        Get a single market by slug or ID.
        
        Args:
            slug_or_id: Market slug or ID
        
        Returns:
            Market if found, None otherwise
        """
        try:
            data = await self._request(
                f"{GAMMA_API_URL}/markets/{slug_or_id}",
                EndpointCategory.GAMMA_API
            )
            return Market.model_validate(data)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise
    
    # ========== Orderbook & Prices ==========
    
    async def get_orderbook(self, token_id: str) -> Orderbook:
        """
        Get current orderbook for a token.
        
        Args:
            token_id: The CLOB token ID
        
        Returns:
            Orderbook with bids and asks
        """
        data = await self._request(
            f"{CLOB_API_URL}/book",
            EndpointCategory.CLOB_API,
            {"token_id": token_id}
        )
        
        bids = [
            OrderbookLevel(price=float(b["price"]), size=float(b["size"]))
            for b in data.get("bids", [])
        ]
        asks = [
            OrderbookLevel(price=float(a["price"]), size=float(a["size"]))
            for a in data.get("asks", [])
        ]
        
        return Orderbook(token_id=token_id, bids=bids, asks=asks)
    
    async def get_price_history(
        self,
        token_id: str,
        interval: str = "1h",
        fidelity: int = 60
    ) -> PriceHistory:
        """
        Get historical price data for a token.
        
        Note: Only works for ACTIVE markets. Closed markets return empty history.
        
        Args:
            token_id: The CLOB token ID
            interval: Time interval (e.g., '1h', '1d')
            fidelity: Data points granularity
        
        Returns:
            Price history with timestamps
        """
        data = await self._request(
            f"{CLOB_API_URL}/prices-history",
            EndpointCategory.PRICE_HISTORY,
            {"market": token_id, "interval": interval, "fidelity": fidelity}
        )
        
        history = data.get("history", [])
        points = []
        for h in history:
            try:
                points.append(PricePoint(
                    t=datetime.fromtimestamp(h["t"]),
                    p=float(h["p"])
                ))
            except Exception:
                continue
        
        return PriceHistory(token_id=token_id, history=points)
    
    async def get_spread(self, token_id: str) -> Dict[str, Optional[float]]:
        """
        Get current bid-ask spread for a token.
        
        Args:
            token_id: The CLOB token ID
        
        Returns:
            Dict with bid, ask, spread, and mid_price
        """
        orderbook = await self.get_orderbook(token_id)
        return {
            "bid": orderbook.best_bid,
            "ask": orderbook.best_ask,
            "spread": orderbook.spread,
            "mid_price": orderbook.mid_price
        }
    
    # ========== Volatility Detection ==========
    
    async def detect_movers(
        self,
        threshold_pct: float = 10.0,
        timeframe: str = "24h",
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Find markets with large price movements.
        
        Args:
            threshold_pct: Minimum price change percentage
            timeframe: Time period to check
            limit: Maximum results
        
        Returns:
            Markets with price changes above threshold
        """
        trending = await self.get_trending(timeframe=timeframe, limit=100)
        
        movers = []
        for market in trending:
            if not market.token_ids:
                continue
            
            try:
                history = await self.get_price_history(market.token_ids[0])
                change = history.price_change_24h
                
                if change is not None and abs(change * 100) >= threshold_pct:
                    movers.append({
                        "market": market,
                        "price_change_pct": change * 100,
                        "direction": "up" if change > 0 else "down"
                    })
            except Exception as e:
                logger.warning(f"Failed to get history for {market.id}: {e}")
                continue
        
        # Sort by absolute change
        movers.sort(key=lambda x: abs(x["price_change_pct"]), reverse=True)
        
        logger.info(f"Found {len(movers[:limit])} markets moving >{threshold_pct}%")
        return movers[:limit]
