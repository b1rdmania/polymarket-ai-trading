"""
Configuration for volatility alerts.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class AlertConfig(BaseModel):
    """Configuration for the alert monitor."""
    
    # Price movement thresholds
    price_threshold_pct: float = Field(
        default=10.0,
        description="Alert when price moves more than this % in the check window"
    )
    
    # Volume thresholds
    volume_spike_multiplier: float = Field(
        default=3.0,
        description="Alert when volume is N times the average"
    )
    
    # Spread thresholds
    spread_threshold_pct: float = Field(
        default=5.0,
        description="Alert when bid-ask spread exceeds this %"
    )
    
    # Timing
    check_interval_sec: int = Field(
        default=60,
        description="How often to check for alerts (seconds)"
    )
    price_window_min: int = Field(
        default=60,
        description="Window for measuring price changes (minutes)"
    )
    
    # Market filtering
    markets: List[str] = Field(
        default_factory=list,
        description="Specific market keywords/slugs to watch (empty = trending)"
    )
    categories: List[str] = Field(
        default_factory=lambda: ["Politics", "Crypto"],
        description="Categories to monitor if no specific markets"
    )
    min_volume_24h: float = Field(
        default=10000.0,
        description="Minimum 24h volume to consider a market"
    )
    max_markets: int = Field(
        default=50,
        description="Maximum markets to monitor at once"
    )
    
    # Alert types to enable
    enable_price_alerts: bool = True
    enable_volume_alerts: bool = True
    enable_spread_alerts: bool = True
    enable_closing_alerts: bool = True
    
    # Closing soon threshold
    closing_hours_threshold: int = Field(
        default=24,
        description="Alert for markets closing within N hours"
    )
    
    # Deduplication
    alert_cooldown_min: int = Field(
        default=30,
        description="Minimum minutes between repeat alerts for same market"
    )


class WebhookConfig(BaseModel):
    """Configuration for webhook output."""
    
    url: str
    method: str = "POST"
    headers: dict = Field(default_factory=dict)
    include_market_data: bool = True


class TelegramConfig(BaseModel):
    """Configuration for Telegram output."""
    
    bot_token: str
    chat_id: str
    parse_mode: str = "HTML"


class DiscordConfig(BaseModel):
    """Configuration for Discord webhook output."""
    
    webhook_url: str
    username: str = "Volatility Bot"
    avatar_url: Optional[str] = None
