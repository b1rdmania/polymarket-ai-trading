"""
Polymarket Data Fetcher

Read-only library for fetching Polymarket data without authentication.
"""

from .client import PolymarketClient
from .models import Market, Orderbook, PriceHistory

__version__ = "0.1.0"
__all__ = ["PolymarketClient", "Market", "Orderbook", "PriceHistory"]
