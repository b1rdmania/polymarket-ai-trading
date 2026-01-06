"""
Pydantic models for Polymarket data structures.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class Market(BaseModel):
    """Polymarket market data."""
    
    id: str = Field(..., description="Market ID")
    question: str = Field(..., description="Market question")
    slug: str = Field(default="", description="URL slug")
    
    # Pricing
    outcome_prices: Optional[List[float]] = Field(default=None, alias="outcomePrices")
    best_bid: Optional[float] = Field(default=None, alias="bestBid")
    best_ask: Optional[float] = Field(default=None, alias="bestAsk")
    spread: Optional[float] = Field(default=None)
    
    # Volume
    volume_24h: float = Field(default=0, alias="volume24hr")
    volume_7d: float = Field(default=0, alias="volume7d")
    volume_30d: float = Field(default=0, alias="volume30d")
    volume_total: float = Field(default=0, alias="volume")
    
    # Liquidity
    liquidity: float = Field(default=0)
    
    # Status
    active: bool = Field(default=True)
    closed: bool = Field(default=False)
    resolved: bool = Field(default=False)
    
    # Timing
    end_date: Optional[datetime] = Field(default=None, alias="endDate")
    created_at: Optional[datetime] = Field(default=None, alias="createdAt")
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    category: Optional[str] = Field(default=None)
    
    # Token IDs for trading
    token_ids: Optional[List[str]] = Field(default=None, alias="clobTokenIds")
    
    class Config:
        populate_by_name = True


class OrderbookLevel(BaseModel):
    """Single level in orderbook."""
    
    price: float
    size: float


class Orderbook(BaseModel):
    """Orderbook for a market."""
    
    token_id: str
    bids: List[OrderbookLevel] = Field(default_factory=list)
    asks: List[OrderbookLevel] = Field(default_factory=list)
    
    @property
    def best_bid(self) -> Optional[float]:
        """Best bid price."""
        return self.bids[0].price if self.bids else None
    
    @property
    def best_ask(self) -> Optional[float]:
        """Best ask price."""
        return self.asks[0].price if self.asks else None
    
    @property
    def spread(self) -> Optional[float]:
        """Bid-ask spread."""
        if self.best_bid and self.best_ask:
            return self.best_ask - self.best_bid
        return None
    
    @property
    def mid_price(self) -> Optional[float]:
        """Mid price."""
        if self.best_bid and self.best_ask:
            return (self.best_bid + self.best_ask) / 2
        return None


class PricePoint(BaseModel):
    """Single price point in history."""
    
    timestamp: datetime = Field(..., alias="t")
    price: float = Field(..., alias="p")


class PriceHistory(BaseModel):
    """Historical price data for a market."""
    
    token_id: str
    history: List[PricePoint] = Field(default_factory=list)
    
    @property
    def latest_price(self) -> Optional[float]:
        """Most recent price."""
        return self.history[-1].price if self.history else None
    
    @property
    def price_change_24h(self) -> Optional[float]:
        """24-hour price change."""
        if len(self.history) < 2:
            return None
        # Find price from ~24h ago
        now = self.history[-1].timestamp
        for point in reversed(self.history):
            delta = now - point.timestamp
            if delta.total_seconds() >= 86400:  # 24 hours
                return self.history[-1].price - point.price
        return None


class TrendingMarket(BaseModel):
    """Market with trending metrics."""
    
    market: Market
    volume_rank: int
    volume_change_pct: Optional[float] = None
    price_change_24h: Optional[float] = None
