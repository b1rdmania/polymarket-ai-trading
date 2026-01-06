"""
Position Sizer

Implements Kelly Criterion for optimal position sizing.
"""

import logging
import math
from typing import Optional

from .models import TradingConfig

logger = logging.getLogger(__name__)


class PositionSizer:
    """
    Calculate optimal position sizes using Kelly Criterion.
    
    Kelly formula for binary outcomes:
    f* = (p * b - q) / b
    
    Where:
    - f* = fraction of bankroll to bet
    - p = probability of winning
    - q = probability of losing (1 - p)
    - b = odds received (profit/loss ratio)
    
    We use fractional Kelly for safety (typically 25% of full Kelly).
    """
    
    def __init__(self, config: TradingConfig):
        self.config = config
    
    def calculate_size(
        self,
        edge: float,
        current_price: float,
        fair_value: float,
        bankroll: float,
    ) -> float:
        """
        Calculate optimal position size using Kelly Criterion.
        
        Args:
            edge: Estimated edge (fair_value - current_price for longs)
            current_price: Current market price
            fair_value: Estimated fair value
            bankroll: Available capital
        
        Returns:
            Position size in USD
        """
        
        # For prediction markets, variance is price * (1 - price)
        variance = current_price * (1 - current_price)
        
        if variance <= 0:
            logger.warning("Invalid variance, using min position size")
            return self.config.min_position_usd
        
        # Kelly fraction = edge / variance
        kelly_full = abs(edge) / variance
        
        # Apply fractional Kelly
        kelly_fraction = kelly_full * self.config.kelly_fraction
        
        # Calculate position size
        position_size = kelly_fraction * bankroll
        
        # Apply limits
        position_size = max(self.config.min_position_usd, position_size)
        position_size = min(self.config.max_position_usd, position_size)
        
        logger.info(
            f"Position sizing: edge={edge:.4f}, variance={variance:.4f}, "
            f"kelly_full={kelly_full:.4f}, fraction={kelly_fraction:.4f}, "
            f"size=${position_size:.2f}"
        )
        
        return position_size
    
    def calculate_from_signal(
        self,
        current_price: float,
        fair_value: float,
        mispricing_pct: float,
        bankroll: float,
    ) -> float:
        """
        Calculate position size from signal parameters.
        
        Args:
            current_price: Current market price (0-1)
            fair_value: Estimated fair value (0-1)
            mispricing_pct: Mispricing percentage
            bankroll: Available capital
        
        Returns:
            Position size in USD
        """
        edge = abs(fair_value - current_price)
        return self.calculate_size(edge, current_price, fair_value, bankroll)
    
    def shares_for_usd(self, usd_amount: float, price: float) -> int:
        """
        Calculate number of shares to buy for a USD amount.
        
        Args:
            usd_amount: Amount in USD to spend
            price: Price per share
        
        Returns:
            Number of shares (integer)
        """
        if price <= 0:
            return 0
        
        shares = math.floor(usd_amount / price)
        return max(0, shares)


