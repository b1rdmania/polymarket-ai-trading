"""
Alert handlers for different output channels.
"""

import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Optional

import httpx

from .models import Alert

logger = logging.getLogger(__name__)


class AlertHandler(ABC):
    """Base class for alert handlers."""
    
    @abstractmethod
    async def handle(self, alert: Alert) -> bool:
        """
        Handle an alert.
        
        Returns True if handled successfully.
        """
        pass


class ConsoleHandler(AlertHandler):
    """Print alerts to console with colors."""
    
    def __init__(self, use_colors: bool = True):
        self.use_colors = use_colors
    
    async def handle(self, alert: Alert) -> bool:
        # Color codes
        colors = {
            "reset": "\033[0m",
            "green": "\033[92m",
            "red": "\033[91m",
            "yellow": "\033[93m",
            "cyan": "\033[96m",
            "bold": "\033[1m",
        }
        
        if not self.use_colors:
            colors = {k: "" for k in colors}
        
        # Choose color based on alert type
        if "spike" in alert.type.value or alert.price_change_pct and alert.price_change_pct > 0:
            color = colors["green"]
        elif "drop" in alert.type.value or alert.price_change_pct and alert.price_change_pct < 0:
            color = colors["red"]
        else:
            color = colors["yellow"]
        
        timestamp = alert.timestamp.strftime("%H:%M:%S")
        
        print(f"{colors['cyan']}[{timestamp}]{colors['reset']} "
              f"{colors['bold']}{color}{alert.type.value.upper()}{colors['reset']}: "
              f"{alert.message}")
        
        if alert.price_change_pct:
            print(f"         Change: {color}{alert.price_change_pct:+.1f}%{colors['reset']}")
        
        print()
        return True


class FileHandler(AlertHandler):
    """Write alerts to a JSON Lines file."""
    
    def __init__(self, filepath: str = "alerts.jsonl"):
        self.filepath = Path(filepath)
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
    
    async def handle(self, alert: Alert) -> bool:
        try:
            with open(self.filepath, "a") as f:
                f.write(alert.model_dump_json() + "\n")
            return True
        except Exception as e:
            logger.error(f"Failed to write alert to file: {e}")
            return False


class WebhookHandler(AlertHandler):
    """POST alerts to a webhook URL."""
    
    def __init__(
        self,
        url: str,
        headers: Optional[dict] = None,
        timeout: float = 10.0
    ):
        self.url = url
        self.headers = headers or {"Content-Type": "application/json"}
        self.timeout = timeout
    
    async def handle(self, alert: Alert) -> bool:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.url,
                    json=alert.model_dump(mode="json"),
                    headers=self.headers
                )
                response.raise_for_status()
                logger.debug(f"Webhook sent: {response.status_code}")
                return True
        except Exception as e:
            logger.error(f"Webhook failed: {e}")
            return False


class DiscordHandler(AlertHandler):
    """Send alerts to Discord webhook."""
    
    def __init__(
        self,
        webhook_url: str,
        username: str = "Volatility Bot",
        avatar_url: Optional[str] = None
    ):
        self.webhook_url = webhook_url
        self.username = username
        self.avatar_url = avatar_url
    
    async def handle(self, alert: Alert) -> bool:
        payload = {
            "username": self.username,
            "embeds": [alert.to_discord_embed()]
        }
        
        if self.avatar_url:
            payload["avatar_url"] = self.avatar_url
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self.webhook_url,
                    json=payload
                )
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Discord webhook failed: {e}")
            return False


class TelegramHandler(AlertHandler):
    """Send alerts to Telegram."""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    async def handle(self, alert: Alert) -> bool:
        payload = {
            "chat_id": self.chat_id,
            "text": alert.to_telegram_html(),
            "parse_mode": "HTML"
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(self.api_url, json=payload)
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Telegram send failed: {e}")
            return False


class MultiHandler(AlertHandler):
    """Send to multiple handlers."""
    
    def __init__(self, *handlers: AlertHandler):
        self.handlers = list(handlers)
    
    def add(self, handler: AlertHandler):
        self.handlers.append(handler)
    
    async def handle(self, alert: Alert) -> bool:
        results = []
        for handler in self.handlers:
            try:
                result = await handler.handle(alert)
                results.append(result)
            except Exception as e:
                logger.error(f"Handler {handler.__class__.__name__} failed: {e}")
                results.append(False)
        
        return any(results)  # Success if any handler succeeded
