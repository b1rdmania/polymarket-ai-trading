"""
Risk Manager

Enforces position limits, exposure rules, and safety checks.
"""

import logging
from typing import Optional, List
from datetime import datetime

from .models import TradingConfig, Position, RiskCheckResult, Trade

logger = logging.getLogger(__name__)


class RiskManager:
    """
    Enforces trading risk limits.
    
    Hard limits (will reject trades):
    - Max position size
    - Max total exposure
    - Max number of positions
    - Max drawdown from peak
    - Max spread threshold
    
    Soft limits (will alert but allow):
    - Daily loss warnings
    - Unusual volatility
    """
    
    def __init__(self, config: TradingConfig):
        self.config = config
        self.peak_equity = 0.0
        self.current_equity = 0.0
        self.daily_pnl = 0.0
        self.daily_start = datetime.utcnow().date()
    
    def check_trade(
        self,
        size_usd: float,
        positions: List[Position],
        current_spread_pct: float,
    ) -> RiskCheckResult:
        """
        Check if a trade is allowed under current risk limits.
        
        Args:
            size_usd: Proposed trade size in USD
            positions: Current open positions
            current_spread_pct: Current bid-ask spread percentage
        
        Returns:
            RiskCheckResult indicating if trade can proceed
        """
        
        # Check position size limit
        if size_usd > self.config.max_position_usd:
            return RiskCheckResult(
                passed=False,
                reason=f"Position size ${size_usd:.2f} exceeds max ${self.config.max_position_usd}",
                can_proceed=False,
                max_size_allowed=self.config.max_position_usd
            )
        
        # Check minimum position size
        if size_usd < self.config.min_position_usd:
            return RiskCheckResult(
                passed=False,
                reason=f"Position size ${size_usd:.2f} below minimum ${self.config.min_position_usd}",
                can_proceed=False,
                max_size_allowed=0
            )
        
        # Check total exposure
        total_exposure = sum(pos.size * pos.entry_price for pos in positions if pos.status.value == "open")
        new_exposure = total_exposure + size_usd
        
        if new_exposure > self.config.max_total_exposure_usd:
            available = self.config.max_total_exposure_usd - total_exposure
            return RiskCheckResult(
                passed=False,
                reason=f"Total exposure ${new_exposure:.2f} exceeds max ${self.config.max_total_exposure_usd}",
                can_proceed=False,
                max_size_allowed=max(0, available)
            )
        
        # Check number of positions
        open_positions = len([p for p in positions if p.status.value == "open"])
        if open_positions >= self.config.max_positions:
            return RiskCheckResult(
                passed=False,
                reason=f"Already at max {self.config.max_positions} open positions",
                can_proceed=False,
                max_size_allowed=0
            )
        
        # Check spread
        if current_spread_pct > self.config.max_spread_pct:
            return RiskCheckResult(
                passed=False,
                reason=f"Spread {current_spread_pct:.2f}% exceeds max {self.config.max_spread_pct}%",
                can_proceed=False,
                max_size_allowed=0
            )
        
        # Check drawdown
        if self.peak_equity > 0:
            drawdown_pct = ((self.peak_equity - self.current_equity) / self.peak_equity) * 100
            if drawdown_pct > self.config.max_drawdown_pct:
                logger.critical(f"Max drawdown exceeded: {drawdown_pct:.2f}% > {self.config.max_drawdown_pct}%")
                return RiskCheckResult(
                    passed=False,
                    reason=f"Drawdown {drawdown_pct:.2f}% exceeds max {self.config.max_drawdown_pct}%",
                    can_proceed=False,
                    max_size_allowed=0
                )
        
        # All checks passed
        return RiskCheckResult(
            passed=True,
            reason="All risk checks passed",
            can_proceed=True,
            max_size_allowed=size_usd
        )
    
    def update_equity(self, equity: float):
        """Update current equity and track peak for drawdown calculation."""
        self.current_equity = equity
        if equity > self.peak_equity:
            self.peak_equity = equity
    
    def update_daily_pnl(self, pnl: float):
        """Update daily P&L and reset if new day."""
        today = datetime.utcnow().date()
        if today != self.daily_start:
            self.daily_start = today
            self.daily_pnl = 0.0
        
        self.daily_pnl += pnl
        
        # Soft alert for daily losses
        if self.daily_pnl < -200:
            logger.warning(f"Daily loss alert: ${self.daily_pnl:.2f}")
    
    def should_emergency_stop(self) -> bool:
        """Check if emergency stop should be triggered."""
        if self.peak_equity > 0:
            drawdown_pct = ((self.peak_equity - self.current_equity) / self.peak_equity) * 100
            if drawdown_pct > self.config.max_drawdown_pct:
                logger.critical("EMERGENCY STOP: Max drawdown exceeded")
                return True
        
        return False


