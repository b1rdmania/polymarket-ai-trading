"""
Signal Aggregator

Combines signals from multiple sources (mean reversion, volatility, whale tracker).
Deduplicates and prioritizes by strength.
"""

import logging
import sys
import os
from typing import List
from collections import defaultdict

# Add toolkit packages to path
toolkit_path = os.path.join(os.path.dirname(__file__), "../..")
sys.path.insert(0, toolkit_path)

logger = logging.getLogger(__name__)


class SignalAggregator:
    """
    Collect and aggregate signals from all sources.
    
    Sources:
    - Mean reversion generator
    - Volatility alerts
    - Whale tracker (when implemented)
    
    Features:
    - Deduplicates signals for the same market
    - Prioritizes by signal strength
    - Combines corroborating signals
    """
    
    def __init__(self):
        self.signal_generators = []
        self._init_generators()
    
    def _init_generators(self):
        """Initialize all signal generators."""
        try:
            from mean_reversion import SignalGenerator, SignalConfig
            self.mean_reversion_gen = SignalGenerator(SignalConfig())
            logger.info("Mean reversion generator initialized")
        except ImportError as e:
            logger.warning(f"Could not import mean reversion generator: {e}")
            self.mean_reversion_gen = None
        
        try:
            from volatility_alerts import AlertMonitor, AlertConfig
            self.volatility_monitor = AlertMonitor(AlertConfig())
            logger.info("Volatility monitor initialized")
        except ImportError as e:
            logger.warning(f"Could not import volatility monitor: {e}")
            self.volatility_monitor = None
        
        # Whale tracker not yet fully implemented
        self.whale_tracker = None
    
    async def get_all_signals(self, limit: int = 50):
        """
        Get signals from all sources.
        
        Args:
            limit: Maximum number of signals to return
        
        Returns:
            List of Signal objects, sorted by strength and mispricing
        """
        all_signals = []
        
        # Mean reversion signals
        if self.mean_reversion_gen:
            try:
                mr_signals = await self.mean_reversion_gen.scan(limit=limit)
                all_signals.extend(mr_signals)
                logger.info(f"Mean reversion: {len(mr_signals)} signals")
            except Exception as e:
                logger.error(f"Mean reversion scan failed: {e}")
        
        # Volatility signals
        if self.volatility_monitor:
            try:
                vol_alerts = await self.volatility_monitor.scan_volatile_markets()
                # Convert alerts to signals (would need implementation)
                # For now, skip
                logger.info(f"Volatility: {len(vol_alerts)} alerts")
            except Exception as e:
                logger.error(f"Volatility scan failed: {e}")
        
        # Whale signals
        if self.whale_tracker:
            try:
                whale_alerts = await self.whale_tracker.scan_for_whales()
                logger.info(f"Whale tracking: {len(whale_alerts)} alerts")
            except Exception as e:
                logger.error(f"Whale scan failed: {e}")
        
        # Deduplicate and prioritize
        unique_signals = self._deduplicate_signals(all_signals)
        
        # Sort by absolute mispricing
        sorted_signals = sorted(
            unique_signals,
            key=lambda s: abs(s.mispricing_pct),
            reverse=True
        )
        
        logger.info(f"Total unique signals: {len(sorted_signals)}")
        
        return sorted_signals[:limit]
    
    def _deduplicate_signals(self, signals: List):
        """
        Remove duplicate signals for the same market.
        
        If multiple signals exist for same market:
        - Keep the one with highest mispricing
        - Or combine if they agree on direction
        """
        if not signals:
            return []
        
        # Group by market_id
        by_market = defaultdict(list)
        for signal in signals:
            by_market[signal.market_id].append(signal)
        
        # Keep best signal per market
        deduplicated = []
        for market_id, market_signals in by_market.items():
            if len(market_signals) == 1:
                deduplicated.append(market_signals[0])
            else:
                # Multiple signals - pick strongest
                best_signal = max(
                    market_signals,
                    key=lambda s: abs(s.mispricing_pct)
                )
                
                # Check if signals agree on direction
                directions = [s.direction for s in market_signals]
                if len(set(directions)) == 1:
                    # All agree - increase confidence
                    best_signal.metadata['corroborating_signals'] = len(market_signals)
                    logger.info(
                        f"Multiple signals agree on {market_id}: "
                        f"{len(market_signals)} sources"
                    )
                
                deduplicated.append(best_signal)
        
        return deduplicated
    
    async def get_top_opportunities(self, min_strength: str = "MODERATE", limit: int = 10):
        """
        Get only the highest conviction signals.
        
        Args:
            min_strength: Minimum signal strength (WEAK, MODERATE, STRONG, VERY_STRONG)
            limit: Maximum signals to return
        
        Returns:
            Filtered list of top signals
        """
        from mean_reversion.models import SignalStrength
        
        all_signals = await self.get_all_signals(limit=limit * 2)
        
        # Map strength names to enum
        strength_map = {
            "WEAK": SignalStrength.WEAK,
            "MODERATE": SignalStrength.MODERATE,
            "STRONG": SignalStrength.STRONG,
            "VERY_STRONG": SignalStrength.VERY_STRONG,
        }
        
        min_strength_enum = strength_map.get(min_strength, SignalStrength.MODERATE)
        strength_order = [
            SignalStrength.WEAK,
            SignalStrength.MODERATE,
            SignalStrength.STRONG,
            SignalStrength.VERY_STRONG,
        ]
        min_index = strength_order.index(min_strength_enum)
        
        # Filter by strength
        filtered = [
            s for s in all_signals
            if strength_order.index(s.strength) >= min_index
        ]
        
        logger.info(
            f"Filtered to {len(filtered)} signals with strength >= {min_strength}"
        )
        
        return filtered[:limit]


