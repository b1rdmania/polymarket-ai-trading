"""
Whale Tracker

Monitor large trades and smart money on Polymarket.
"""

from .config import WatchlistConfig
from .monitor import WhaleMonitor
from .models import Trade, Wallet, TraderProfile

__version__ = "0.1.0"
__all__ = [
    "WatchlistConfig",
    "WhaleMonitor",
    "Trade",
    "Wallet",
    "TraderProfile",
]
