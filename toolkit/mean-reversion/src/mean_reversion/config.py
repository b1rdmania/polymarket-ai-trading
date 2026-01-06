"""
Configuration for mean reversion signals.
"""

from typing import Tuple
from pydantic import BaseModel, Field


class SignalConfig(BaseModel):
    """Configuration for the signal generator."""
    
    # Mispricing thresholds
    min_mispricing_pct: float = Field(
        default=5.0,
        description="Minimum mispricing to generate a signal (%)"
    )
    
    # Horizon filtering (days until resolution)
    horizon_days: Tuple[int, int] = Field(
        default=(7, 21),
        description="Optimal horizon range (min, max days) - overconfidence zone"
    )
    
    # Price zones
    longshot_threshold: float = Field(
        default=0.30,
        description="Price below this = longshot (potential underpricing)"
    )
    favorite_threshold: float = Field(
        default=0.70,
        description="Price above this = favorite (potential overpricing)"
    )
    
    # Position sizing
    kelly_fraction: float = Field(
        default=0.25,
        description="Fraction of Kelly criterion to use (0.25 = quarter Kelly)"
    )
    max_position_usd: float = Field(
        default=500.0,
        description="Maximum position size in USD"
    )
    min_position_usd: float = Field(
        default=10.0,
        description="Minimum position size in USD"
    )
    
    # Market filtering
    min_volume_24h: float = Field(
        default=10000.0,
        description="Minimum 24h volume to consider"
    )
    min_liquidity: float = Field(
        default=5000.0,
        description="Minimum liquidity in market"
    )
    max_spread_pct: float = Field(
        default=5.0,
        description="Maximum bid-ask spread to trade"
    )
    
    # Signal decay
    spike_lookback_hours: int = Field(
        default=24,
        description="Hours to look back for price spikes"
    )
    spike_threshold_pct: float = Field(
        default=10.0,
        description="Price move % to consider a spike"
    )
    
    # Confidence adjustments
    confidence_discount: float = Field(
        default=0.8,
        description="Multiply edge by this for conservative sizing"
    )
