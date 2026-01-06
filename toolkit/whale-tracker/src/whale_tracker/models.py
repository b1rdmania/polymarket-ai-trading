"""
Models for whale tracking.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class TradeDirection(str, Enum):
    """Trade direction."""
    BUY = "buy"
    SELL = "sell"


class Trade(BaseModel):
    """A single trade on Polymarket."""
    
    id: str = Field(..., description="Trade ID")
    timestamp: datetime
    
    # Market
    market_id: str
    market_question: str = ""
    token_id: str = ""
    
    # Trade details
    direction: TradeDirection
    price: float
    size: float  # In contracts
    value_usd: float  # USD value
    
    # Wallet
    wallet_address: str
    
    # Context
    is_whale: bool = False
    is_watchlist: bool = False
    
    def __str__(self) -> str:
        arrow = "↑" if self.direction == TradeDirection.BUY else "↓"
        return f"{arrow} ${self.value_usd:,.0f} @ {self.price:.2f}"


class Wallet(BaseModel):
    """A wallet profile."""
    
    address: str
    
    # Stats
    total_volume: float = 0.0
    total_trades: int = 0
    pnl: float = 0.0
    win_rate: float = 0.0
    
    # Activity
    last_trade: Optional[datetime] = None
    active_positions: int = 0
    
    # Recent trades
    recent_trades: List[Trade] = Field(default_factory=list)
    
    # Tags
    is_whale: bool = False
    is_top_trader: bool = False
    is_watchlist: bool = False


class TraderProfile(BaseModel):
    """Top trader profile from PredictFolio."""
    
    rank: int
    username: str = ""
    wallet_address: str = ""
    
    # Performance
    total_volume: float = 0.0
    pnl: float = 0.0
    pnl_pct: float = 0.0
    win_rate: float = 0.0
    
    # Activity
    total_trades: int = 0
    active_markets: int = 0
    
    # Recent
    recent_trades: List[Trade] = Field(default_factory=list)
    
    def __str__(self) -> str:
        return f"#{self.rank} {self.username or self.wallet_address[:10]} - ${self.pnl:+,.0f}"


class TradeFlow(BaseModel):
    """Aggregate trade flow analysis."""
    
    period_start: datetime
    period_end: datetime
    
    # Volume
    total_volume: float = 0.0
    buy_volume: float = 0.0
    sell_volume: float = 0.0
    net_flow: float = 0.0  # Positive = net buying
    
    # Counts
    total_trades: int = 0
    whale_trades: int = 0
    
    # Top
    largest_trade: Optional[Trade] = None
    most_active_wallet: Optional[str] = None
    
    @property
    def buy_ratio(self) -> float:
        """Ratio of buy volume to total."""
        if self.total_volume == 0:
            return 0.5
        return self.buy_volume / self.total_volume


class WhaleAlert(BaseModel):
    """Alert for whale activity."""
    
    id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    trade: Trade
    alert_type: str = "whale_trade"
    
    message: str = ""
    
    def __str__(self) -> str:
        return f"🐋 WHALE: {self.trade}"
