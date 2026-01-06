"""
Volatility Alerts

Real-time price movement detection for Polymarket.
"""

from .config import AlertConfig
from .monitor import AlertMonitor
from .models import Alert, AlertType
from .handlers import ConsoleHandler, WebhookHandler, FileHandler

__version__ = "0.1.0"
__all__ = [
    "AlertConfig",
    "AlertMonitor", 
    "Alert",
    "AlertType",
    "ConsoleHandler",
    "WebhookHandler",
    "FileHandler",
]
