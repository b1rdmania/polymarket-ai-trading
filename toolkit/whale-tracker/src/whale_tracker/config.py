"""
Configuration for whale tracking.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class WatchlistConfig(BaseModel):
    """Configuration for whale monitoring."""
    
    # Trade size thresholds
    min_trade_size: float = Field(
        default=1000.0,
        description="Minimum trade size in USD to consider 'large'"
    )
    whale_threshold: float = Field(
        default=10000.0,
        description="Trade size to consider 'whale' activity"
    )
    
    # Wallet watchlist
    wallets: List[str] = Field(
        default_factory=list,
        description="Specific wallet addresses to monitor"
    )
    
    # Top trader tracking
    track_top_traders: bool = Field(
        default=True,
        description="Track activity of PredictFolio top traders"
    )
    top_trader_count: int = Field(
        default=20,
        description="Number of top traders to track"
    )
    
    # Time windows
    lookback_hours: int = Field(
        default=24,
        description="Hours to look back for trade history"
    )
    
    # Alerts
    alert_on_whale: bool = True
    alert_on_watchlist: bool = True
    
    # PredictFolio
    predictfolio_enabled: bool = Field(
        default=True,
        description="Use PredictFolio for top trader data"
    )
    
    # Dune (optional)
    dune_api_key: Optional[str] = Field(
        default=None,
        description="Dune Analytics API key for historical queries"
    )
