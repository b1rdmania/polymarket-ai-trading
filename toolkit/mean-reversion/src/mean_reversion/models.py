"""
Signal models for mean reversion.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class SignalType(str, Enum):
    """Types of mean reversion signals."""
    
    FADE_SPIKE = "fade_spike"           # Price spiked, expect reversion
    BUY_LONGSHOT = "buy_longshot"       # Underpriced low-probability contract
    SELL_FAVORITE = "sell_favorite"     # Overpriced high-probability contract
    CLOSING_EDGE = "closing_edge"       # Near-resolution mispricing


class SignalDirection(str, Enum):
    """Trade direction."""
    
    BUY = "buy"
    SELL = "sell"


class SignalStrength(str, Enum):
    """Signal strength/confidence."""
    
    WEAK = "weak"           # 1-5% edge
    MODERATE = "moderate"   # 5-10% edge
    STRONG = "strong"       # 10-15% edge
    VERY_STRONG = "very_strong"  # >15% edge


class Signal(BaseModel):
    """A mean reversion trading signal."""
    
    # Identity
    id: str = Field(..., description="Unique signal ID")
    type: SignalType
    direction: SignalDirection
    strength: SignalStrength = SignalStrength.MODERATE
    
    # Timing
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    
    # Market info
    market_id: str
    market_question: str
    market_slug: str = ""
    token_id: str = ""
    
    # Pricing
    current_price: float
    fair_value_estimate: float
    mispricing_pct: float  # Positive = underpriced, Negative = overpriced
    
    # Position sizing
    edge_estimate: float  # Expected edge as decimal
    kelly_size: float     # Full Kelly position size
    position_size: float  # Recommended position (after fractional Kelly)
    
    # Context
    horizon_days: Optional[int] = None  # Days until resolution
    recent_spike_pct: Optional[float] = None  # If this is a fade signal
    
    # Risk
    max_loss: Optional[float] = None
    breakeven_probability: Optional[float] = None
    
    # Execution parameters
    entry_price: Optional[float] = None  # Target entry price (defaults to current_price)
    stop_loss: Optional[float] = None    # Stop loss price
    take_profit: Optional[float] = None  # Take profit price
    max_slippage_pct: float = 2.0        # Maximum acceptable slippage
    
    # Metadata
    rationale: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def to_trade_instruction(self) -> str:
        """Generate human-readable trade instruction."""
        action = "BUY" if self.direction == SignalDirection.BUY else "SELL"
        return (
            f"{action} ${self.position_size:.0f} at {self.current_price:.2f}\n"
            f"Market: {self.market_question[:60]}\n"
            f"Edge: {self.edge_estimate*100:.1f}% | Mispricing: {self.mispricing_pct:+.1f}%"
        )
    
    def __str__(self) -> str:
        arrow = "↑" if self.direction == SignalDirection.BUY else "↓"
        return f"[{self.type.value}] {arrow} {self.market_question[:50]}... ({self.mispricing_pct:+.1f}%)"


class SignalSummary(BaseModel):
    """Summary of multiple signals."""
    
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    total_signals: int = 0
    buy_signals: int = 0
    sell_signals: int = 0
    
    strong_signals: int = 0
    total_position_size: float = 0.0
    
    top_signals: list[Signal] = Field(default_factory=list)
