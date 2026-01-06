"""
Mean Reversion Signals

Trading signals based on behavioral finance research.
"""

from .config import SignalConfig
from .generator import SignalGenerator
from .models import Signal, SignalType, SignalDirection

__version__ = "0.1.0"
__all__ = [
    "SignalConfig",
    "SignalGenerator",
    "Signal",
    "SignalType",
    "SignalDirection",
]
