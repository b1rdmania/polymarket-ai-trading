"""
Alert Monitor - Main monitoring loop.

Watches Polymarket for volatility and generates alerts.
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set

import httpx

from .config import AlertConfig
from .models import Alert, AlertType, AlertSeverity
from .handlers import AlertHandler, ConsoleHandler

logger = logging.getLogger(__name__)

# API endpoints
GAMMA_API_URL = "https://gamma-api.polymarket.com"
CLOB_API_URL = "https://clob.polymarket.com"


class AlertMonitor:
    """
    Monitors Polymarket for volatility and generates alerts.
    
    Example:
        ```python
        config = AlertConfig(price_threshold_pct=10.0)
        monitor = AlertMonitor(config)
        monitor.add_handler(ConsoleHandler())
        await monitor.start()
        ```
    """
    
    def __init__(self, config: Optional[AlertConfig] = None):
        self.config = config or AlertConfig()
        self.handlers: List[AlertHandler] = []
        self._running = False
        
        # Price tracking
        self._price_history: Dict[str, List[tuple]] = {}  # market_id -> [(timestamp, price)]
        
        # Deduplication
        self._recent_alerts: Dict[str, datetime] = {}  # market_id+type -> last alert time
        
        # Watchlist
        self._watchlist: Set[str] = set()
    
    def add_handler(self, handler: AlertHandler) -> None:
        """Add an alert handler."""
        self.handlers.append(handler)
    
    async def start(self) -> None:
        """Start the monitoring loop."""
        if not self.handlers:
            self.handlers.append(ConsoleHandler())
            logger.info("No handlers configured, using console output")
        
        self._running = True
        logger.info(f"Starting volatility monitor (check every {self.config.check_interval_sec}s)")
        
        while self._running:
            try:
                await self._check_cycle()
            except Exception as e:
                logger.error(f"Error in check cycle: {e}")
            
            await asyncio.sleep(self.config.check_interval_sec)
    
    def stop(self) -> None:
        """Stop the monitoring loop."""
        self._running = False
        logger.info("Stopping volatility monitor")
    
    async def _check_cycle(self) -> None:
        """Run one check cycle."""
        # Get markets to monitor
        markets = await self._get_markets_to_monitor()
        logger.debug(f"Monitoring {len(markets)} markets")
        
        alerts = []
        
        for market in markets:
            market_id = market.get("id", "")
            
            # Get current price
            token_ids = market.get("clobTokenIds", [])
            if not token_ids:
                continue
            
            try:
                current_price = await self._get_current_price(token_ids[0])
            except Exception:
                continue
            
            # Update price history
            now = datetime.utcnow()
            if market_id not in self._price_history:
                self._price_history[market_id] = []
            
            self._price_history[market_id].append((now, current_price))
            
            # Trim old prices
            cutoff = now - timedelta(minutes=self.config.price_window_min)
            self._price_history[market_id] = [
                (t, p) for t, p in self._price_history[market_id]
                if t > cutoff
            ]
            
            # Check for price alerts
            if self.config.enable_price_alerts:
                price_alert = self._check_price_movement(market, current_price)
                if price_alert and self._should_alert(price_alert):
                    alerts.append(price_alert)
            
            # Check for spread alerts
            if self.config.enable_spread_alerts:
                spread_alert = await self._check_spread(market, token_ids[0])
                if spread_alert and self._should_alert(spread_alert):
                    alerts.append(spread_alert)
            
            # Check for closing soon
            if self.config.enable_closing_alerts:
                closing_alert = self._check_closing_soon(market)
                if closing_alert and self._should_alert(closing_alert):
                    alerts.append(closing_alert)
        
        # Dispatch alerts
        for alert in alerts:
            await self._dispatch_alert(alert)
    
    async def _get_markets_to_monitor(self) -> List[dict]:
        """Get list of markets to monitor."""
        markets = []
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # If specific markets configured, search for them
            if self.config.markets:
                for query in self.config.markets:
                    try:
                        response = await client.get(
                            f"{GAMMA_API_URL}/markets",
                            params={"query": query, "active": "true"}
                        )
                        response.raise_for_status()
                        markets.extend(response.json()[:10])
                    except Exception as e:
                        logger.warning(f"Failed to search for '{query}': {e}")
            
            # Otherwise, get trending
            else:
                try:
                    response = await client.get(
                        f"{GAMMA_API_URL}/markets",
                        params={"active": "true"}
                    )
                    response.raise_for_status()
                    all_markets = response.json()
                    
                    # Sort by 24h volume
                    all_markets.sort(
                        key=lambda m: float(m.get("volume24hr", 0) or 0),
                        reverse=True
                    )
                    
                    # Filter by minimum volume
                    markets = [
                        m for m in all_markets
                        if float(m.get("volume24hr", 0) or 0) >= self.config.min_volume_24h
                    ][:self.config.max_markets]
                    
                except Exception as e:
                    logger.error(f"Failed to fetch markets: {e}")
        
        return markets
    
    async def _get_current_price(self, token_id: str) -> float:
        """Get current mid price for a token."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{CLOB_API_URL}/book",
                params={"token_id": token_id}
            )
            response.raise_for_status()
            data = response.json()
            
            bids = data.get("bids", [])
            asks = data.get("asks", [])
            
            best_bid = float(bids[0]["price"]) if bids else 0
            best_ask = float(asks[0]["price"]) if asks else 1
            
            return (best_bid + best_ask) / 2
    
    def _check_price_movement(self, market: dict, current_price: float) -> Optional[Alert]:
        """Check for significant price movement."""
        market_id = market.get("id", "")
        history = self._price_history.get(market_id, [])
        
        if len(history) < 2:
            return None
        
        # Get oldest price in window
        oldest_price = history[0][1]
        
        if oldest_price == 0:
            return None
        
        change_pct = ((current_price - oldest_price) / oldest_price) * 100
        
        if abs(change_pct) < self.config.price_threshold_pct:
            return None
        
        # Determine alert type and severity
        if change_pct > 0:
            alert_type = AlertType.PRICE_SPIKE
            direction = "up"
        else:
            alert_type = AlertType.PRICE_DROP
            direction = "down"
        
        if abs(change_pct) >= 20:
            severity = AlertSeverity.CRITICAL
        elif abs(change_pct) >= 15:
            severity = AlertSeverity.HIGH
        else:
            severity = AlertSeverity.MEDIUM
        
        return Alert(
            id=str(uuid.uuid4()),
            type=alert_type,
            severity=severity,
            market_id=market_id,
            market_question=market.get("question", "Unknown"),
            market_slug=market.get("slug", ""),
            message=f"Price moved {change_pct:+.1f}% ({direction}) in last {self.config.price_window_min}min",
            current_price=current_price,
            previous_price=oldest_price,
            price_change_pct=change_pct,
            suggested_action="Consider mean reversion if emotional overreaction" if abs(change_pct) >= 10 else None
        )
    
    async def _check_spread(self, market: dict, token_id: str) -> Optional[Alert]:
        """Check for wide spreads."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{CLOB_API_URL}/book",
                    params={"token_id": token_id}
                )
                response.raise_for_status()
                data = response.json()
                
                bids = data.get("bids", [])
                asks = data.get("asks", [])
                
                if not bids or not asks:
                    return None
                
                best_bid = float(bids[0]["price"])
                best_ask = float(asks[0]["price"])
                
                if best_bid == 0:
                    return None
                
                spread_pct = ((best_ask - best_bid) / best_bid) * 100
                
                if spread_pct < self.config.spread_threshold_pct:
                    return None
                
                return Alert(
                    id=str(uuid.uuid4()),
                    type=AlertType.SPREAD_WIDE,
                    severity=AlertSeverity.MEDIUM,
                    market_id=market.get("id", ""),
                    market_question=market.get("question", "Unknown"),
                    market_slug=market.get("slug", ""),
                    message=f"Wide spread detected: {spread_pct:.1f}% (liquidity thin)",
                    bid=best_bid,
                    ask=best_ask,
                    spread_pct=spread_pct
                )
        
        except Exception as e:
            logger.debug(f"Failed to check spread: {e}")
            return None
    
    def _check_closing_soon(self, market: dict) -> Optional[Alert]:
        """Check if market is closing soon."""
        end_date = market.get("endDate")
        if not end_date:
            return None
        
        try:
            if isinstance(end_date, str):
                end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
            else:
                end_dt = datetime.fromtimestamp(int(end_date))
            
            now = datetime.utcnow()
            hours_remaining = (end_dt.replace(tzinfo=None) - now).total_seconds() / 3600
            
            if hours_remaining > self.config.closing_hours_threshold or hours_remaining < 0:
                return None
            
            return Alert(
                id=str(uuid.uuid4()),
                type=AlertType.CLOSING_SOON,
                severity=AlertSeverity.LOW,
                market_id=market.get("id", ""),
                market_question=market.get("question", "Unknown"),
                market_slug=market.get("slug", ""),
                message=f"Market closing in {hours_remaining:.1f} hours (near-resolution efficiency)",
                metadata={"hours_remaining": hours_remaining}
            )
        
        except Exception:
            return None
    
    def _should_alert(self, alert: Alert) -> bool:
        """Check if we should send this alert (deduplication)."""
        key = f"{alert.market_id}:{alert.type.value}"
        
        last_alert = self._recent_alerts.get(key)
        if last_alert:
            elapsed = (datetime.utcnow() - last_alert).total_seconds() / 60
            if elapsed < self.config.alert_cooldown_min:
                return False
        
        self._recent_alerts[key] = datetime.utcnow()
        return True
    
    async def _dispatch_alert(self, alert: Alert) -> None:
        """Send alert to all handlers."""
        for handler in self.handlers:
            try:
                await handler.handle(alert)
            except Exception as e:
                logger.error(f"Handler {handler.__class__.__name__} failed: {e}")
