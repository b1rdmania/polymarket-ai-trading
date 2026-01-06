"""
Data models for trade execution.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Literal
import uuid


class TradeMode(str, Enum):
    """Trading mode."""
    PAPER = "paper"
    LIVE = "live"


class TradeStatus(str, Enum):
    """Trade execution status."""
    PENDING = "pending"
    SUBMITTED = "submitted"
    FILLED = "filled"
    PARTIAL = "partial"
    CANCELLED = "cancelled"
    FAILED = "failed"


class PositionStatus(str, Enum):
    """Position status."""
    OPEN = "open"
    CLOSED = "closed"
    LIQUIDATED = "liquidated"


@dataclass
class TradingConfig:
    """Trading system configuration."""
    mode: TradeMode = TradeMode.PAPER
    
    # Risk limits
    max_position_usd: float = 500
    max_total_exposure_usd: float = 2000
    max_positions: int = 10
    max_drawdown_pct: float = 25.0
    
    # Position sizing
    kelly_fraction: float = 0.25  # Fractional Kelly (conservative)
    min_position_usd: float = 50
    
    # Execution
    max_slippage_pct: float = 2.0
    max_spread_pct: float = 5.0
    check_interval_seconds: int = 300  # 5 minutes
    
    # Dry run mode (log only, don't execute)
    dry_run: bool = True


@dataclass
class Trade:
    """Represents a trade execution."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Market info
    market_id: str = ""
    market_question: str = ""
    token_id: str = ""
    
    # Trade details
    side: Literal["BUY", "SELL"] = "BUY"
    size: float = 0.0  # Number of shares
    price: float = 0.0  # Price per share
    value_usd: float = 0.0  # Total value
    
    # Execution
    status: TradeStatus = TradeStatus.PENDING
    filled_size: float = 0.0
    average_price: float = 0.0
    
    # Metadata
    signal_id: Optional[str] = None
    signal_type: Optional[str] = None
    signal_strength: Optional[str] = None
    
    # Error tracking
    error: Optional[str] = None
    retry_count: int = 0
    
    # Execution quality tracking (lesson from @the_smart_ape)
    metadata: dict = field(default_factory=dict)  # Stores slippage, latency, etc.


@dataclass
class Position:
    """Represents an open position."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trade_id: str = ""
    
    # Market info
    market_id: str = ""
    market_question: str = ""
    token_id: str = ""
    
    # Position details
    side: Literal["BUY", "SELL"] = "BUY"
    size: float = 0.0
    entry_price: float = 0.0
    current_price: float = 0.0
    
    # P&L
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    
    # Status
    status: PositionStatus = PositionStatus.OPEN
    opened_at: datetime = field(default_factory=datetime.utcnow)
    closed_at: Optional[datetime] = None
    
    # Risk management
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None


@dataclass
class ExecutionResult:
    """Result of a trade execution attempt."""
    success: bool
    trade: Trade
    message: str
    error: Optional[str] = None


@dataclass
class RiskCheckResult:
    """Result of risk checks."""
    passed: bool
    reason: str
    can_proceed: bool
    max_size_allowed: float = 0.0

