"""
Execution Engine

Trade execution infrastructure for systematic Polymarket trading.
"""

from .models import (
    TradingConfig,
    Trade,
    Position,
    ExecutionResult,
    RiskCheckResult,
)
from .executor import PolymarketExecutor
from .risk_manager import RiskManager
from .position_sizer import PositionSizer
from .orchestrator import TradeOrchestrator

__version__ = "0.1.0"

__all__ = [
    "TradingConfig",
    "Trade",
    "Position",
    "ExecutionResult",
    "RiskCheckResult",
    "PolymarketExecutor",
    "RiskManager",
    "PositionSizer",
    "TradeOrchestrator",
]


