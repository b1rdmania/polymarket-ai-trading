"""
Alert models and types.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class AlertType(str, Enum):
    """Types of volatility alerts."""
    
    PRICE_SPIKE = "price_spike"       # Large price movement
    PRICE_DROP = "price_drop"         # Large price drop
    VOLUME_SURGE = "volume_surge"     # Unusual volume
    SPREAD_WIDE = "spread_wide"       # Spread widening (liquidity thin)
    CLOSING_SOON = "closing_soon"     # Market nearing resolution


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    
    LOW = "low"           # Informational
    MEDIUM = "medium"     # Worth noting
    HIGH = "high"         # Significant move
    CRITICAL = "critical" # Major event


class Alert(BaseModel):
    """A volatility alert."""
    
    # Identity
    id: str = Field(..., description="Unique alert ID")
    type: AlertType
    severity: AlertSeverity = AlertSeverity.MEDIUM
    
    # Timing
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Market info
    market_id: str
    market_question: str
    market_slug: str = ""
    
    # Alert specifics
    message: str
    
    # Price data
    current_price: Optional[float] = None
    previous_price: Optional[float] = None
    price_change_pct: Optional[float] = None
    
    # Volume data
    current_volume: Optional[float] = None
    average_volume: Optional[float] = None
    volume_multiplier: Optional[float] = None
    
    # Spread data
    bid: Optional[float] = None
    ask: Optional[float] = None
    spread_pct: Optional[float] = None
    
    # Actions
    suggested_action: Optional[str] = None
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def to_slack_block(self) -> Dict[str, Any]:
        """Format as Slack block."""
        emoji = {
            AlertType.PRICE_SPIKE: "📈",
            AlertType.PRICE_DROP: "📉",
            AlertType.VOLUME_SURGE: "🔥",
            AlertType.SPREAD_WIDE: "⚠️",
            AlertType.CLOSING_SOON: "⏰",
        }.get(self.type, "🔔")
        
        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{emoji} *{self.type.value.upper()}*\n{self.message}"
            }
        }
    
    def to_discord_embed(self) -> Dict[str, Any]:
        """Format as Discord embed."""
        color = {
            AlertSeverity.LOW: 0x808080,
            AlertSeverity.MEDIUM: 0xFFFF00,
            AlertSeverity.HIGH: 0xFF8C00,
            AlertSeverity.CRITICAL: 0xFF0000,
        }.get(self.severity, 0x808080)
        
        return {
            "title": f"{self.type.value.upper()}",
            "description": self.message,
            "color": color,
            "fields": [
                {"name": "Market", "value": self.market_question[:100], "inline": False},
                {"name": "Change", "value": f"{self.price_change_pct:+.1f}%" if self.price_change_pct else "N/A", "inline": True},
            ],
            "timestamp": self.timestamp.isoformat()
        }
    
    def to_telegram_html(self) -> str:
        """Format as Telegram HTML message."""
        emoji = {
            AlertType.PRICE_SPIKE: "📈",
            AlertType.PRICE_DROP: "📉",
            AlertType.VOLUME_SURGE: "🔥",
            AlertType.SPREAD_WIDE: "⚠️",
            AlertType.CLOSING_SOON: "⏰",
        }.get(self.type, "🔔")
        
        return f"""
{emoji} <b>{self.type.value.upper()}</b>

{self.message}

<b>Market:</b> {self.market_question[:80]}
<b>Change:</b> {self.price_change_pct:+.1f}% 
<b>Time:</b> {self.timestamp.strftime('%H:%M UTC')}
""".strip()
    
    def __str__(self) -> str:
        return f"[{self.type.value}] {self.message}"
