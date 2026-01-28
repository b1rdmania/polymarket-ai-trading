#!/usr/bin/env python3
"""
Systematic Trading Agent - REAL IMPLEMENTATION

Connects to Polymarket, scans for mean reversion opportunities,
and executes paper trades based on model parameters.
"""

import asyncio
import argparse
import logging
import sqlite3
import httpx
import yaml
import json
import random
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API endpoints
GAMMA_API = "https://gamma-api.polymarket.com"

# Base directory
BASE_DIR = Path(__file__).parent.parent


class PaperTrader:
    """
    Real paper trading agent that:
    - Fetches live market data from Polymarket
    - Detects mean reversion signals
    - Executes simulated trades
    - Tracks P&L
    """
    
    def __init__(self, model_name: str, config_path: str):
        self.model_name = model_name
        self.config = self._load_config(config_path)
        self.db_path = BASE_DIR / self.config.get('data', {}).get('db_path', f'data/trades_{model_name}.db')
        self.bankroll = 1000.0  # Starting paper money
        self.positions: Dict[str, Dict] = {}  # Open positions
        
        # Model parameters from config
        signals_config = self.config.get('signals', {}).get('mean_reversion', {})
        self.favorite_threshold = signals_config.get('favorite_threshold', 0.75)
        self.longshot_threshold = signals_config.get('longshot_threshold', 0.25)
        self.min_mispricing_pct = signals_config.get('min_mispricing_pct', 5.0)
        
        risk_config = self.config.get('risk', {})
        self.kelly_fraction = risk_config.get('kelly_fraction', 0.25)
        self.max_position_usd = risk_config.get('max_position_usd', 500)
        self.max_positions = risk_config.get('max_positions', 8)
        
        exec_config = self.config.get('execution', {})
        self.check_interval = exec_config.get('check_interval_seconds', 300)
        
        # Initialize database
        self._init_db()
        
        logger.info(f"Initialized {model_name} trader")
        logger.info(f"  Favorite threshold: {self.favorite_threshold}")
        logger.info(f"  Longshot threshold: {self.longshot_threshold}")
        logger.info(f"  Min mispricing: {self.min_mispricing_pct}%")
        logger.info(f"  Kelly fraction: {self.kelly_fraction}")
        logger.info(f"  Max position: ${self.max_position_usd}")
        logger.info(f"  Check interval: {self.check_interval}s")
    
    def _load_config(self, config_path: str) -> dict:
        """Load YAML configuration."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Could not load config {config_path}: {e}")
            return {}
    
    def _init_db(self):
        """Initialize SQLite database for trade storage."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Trades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                model TEXT NOT NULL,
                market_id TEXT NOT NULL,
                market_question TEXT,
                side TEXT NOT NULL,
                entry_price REAL NOT NULL,
                size_usd REAL NOT NULL,
                shares REAL NOT NULL,
                status TEXT DEFAULT 'open',
                exit_price REAL,
                exit_timestamp TEXT,
                pnl REAL,
                signal_strength REAL,
                notes TEXT
            )
        ''')
        
        # Scans table (for logging activity)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                model TEXT NOT NULL,
                markets_scanned INTEGER,
                signals_found INTEGER,
                trades_executed INTEGER,
                notes TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")
    
    async def fetch_markets(self) -> List[Dict]:
        """Fetch active markets from Polymarket."""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{GAMMA_API}/markets",
                    params={
                        "limit": 200,
                        "active": "true",
                        "closed": "false"
                    }
                )
                response.raise_for_status()
                markets = response.json()
                
                if isinstance(markets, list):
                    # Filter for markets with meaningful volume
                    filtered = [
                        m for m in markets
                        if float(m.get('volume', 0) or 0) > 10000
                    ]
                    return filtered
                return []
        except Exception as e:
            logger.error(f"Failed to fetch markets: {e}")
            return []
    
    def analyze_market(self, market: Dict) -> Optional[Dict]:
        """
        Analyze a market for mean reversion signal.
        Returns signal dict if opportunity found, None otherwise.
        """
        try:
            # Parse prices
            prices_str = market.get('outcomePrices', '[]')
            if isinstance(prices_str, str):
                prices = json.loads(prices_str)
            else:
                prices = prices_str
            
            if not prices or len(prices) < 1:
                return None
            
            yes_price = float(prices[0])
            
            # Check for extreme prices (potential mean reversion)
            signal = None
            
            # Favorite overpriced (YES too high)
            if yes_price >= self.favorite_threshold:
                # Bet NO - price likely to revert down
                mispricing = (yes_price - 0.5) * 100  # How far from 50%
                if mispricing >= self.min_mispricing_pct:
                    signal = {
                        'side': 'NO',
                        'price': 1 - yes_price,
                        'yes_price': yes_price,
                        'mispricing_pct': mispricing,
                        'strength': mispricing / 50,  # 0-1 scale
                        'reason': f"Favorite overpriced at {yes_price*100:.0f}%"
                    }
            
            # Longshot underpriced (YES too low)
            elif yes_price <= self.longshot_threshold:
                # Bet YES - price likely to revert up
                mispricing = (0.5 - yes_price) * 100
                if mispricing >= self.min_mispricing_pct:
                    signal = {
                        'side': 'YES',
                        'price': yes_price,
                        'yes_price': yes_price,
                        'mispricing_pct': mispricing,
                        'strength': mispricing / 50,
                        'reason': f"Longshot underpriced at {yes_price*100:.0f}%"
                    }
            
            return signal
            
        except Exception as e:
            logger.debug(f"Error analyzing market: {e}")
            return None
    
    def calculate_position_size(self, signal: Dict) -> float:
        """Calculate position size using Kelly criterion."""
        # Simplified Kelly: fraction * edge * bankroll
        edge = signal['mispricing_pct'] / 100
        kelly_size = self.kelly_fraction * edge * self.bankroll
        
        # Cap at max position size
        size = min(kelly_size, self.max_position_usd)
        
        # Don't bet more than we have
        size = min(size, self.bankroll * 0.25)  # Max 25% of bankroll per trade
        
        return max(size, 10.0)  # Minimum $10 trade
    
    def execute_paper_trade(self, market: Dict, signal: Dict) -> bool:
        """Execute a paper trade and record it."""
        try:
            # Check if we already have a position in this market
            market_id = market.get('id', market.get('conditionId', 'unknown'))
            if market_id in self.positions:
                logger.info(f"Already have position in {market_id}")
                return False
            
            # Check max positions
            if len(self.positions) >= self.max_positions:
                logger.info(f"Max positions ({self.max_positions}) reached")
                return False
            
            # Calculate position size
            size_usd = self.calculate_position_size(signal)
            entry_price = signal['price']
            shares = size_usd / entry_price
            
            # Deduct from bankroll
            self.bankroll -= size_usd
            
            # Record trade
            trade_data = {
                'market_id': market_id,
                'market_question': market.get('question', 'Unknown'),
                'side': signal['side'],
                'entry_price': entry_price,
                'size_usd': size_usd,
                'shares': shares,
                'signal_strength': signal['strength'],
                'timestamp': datetime.now().isoformat()
            }
            
            # Save to database
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO trades (
                    timestamp, model, market_id, market_question, side,
                    entry_price, size_usd, shares, status, signal_strength, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'open', ?, ?)
            ''', (
                trade_data['timestamp'],
                self.model_name,
                trade_data['market_id'],
                trade_data['market_question'],
                trade_data['side'],
                trade_data['entry_price'],
                trade_data['size_usd'],
                trade_data['shares'],
                trade_data['signal_strength'],
                signal['reason']
            ))
            conn.commit()
            conn.close()
            
            # Track position
            self.positions[market_id] = trade_data
            
            logger.info(f"TRADE EXECUTED: {signal['side']} ${size_usd:.2f} on '{market.get('question', 'Unknown')[:50]}' @ {entry_price:.2f}")
            logger.info(f"  Reason: {signal['reason']}")
            logger.info(f"  Bankroll remaining: ${self.bankroll:.2f}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to execute trade: {e}")
            return False
    
    def log_scan(self, markets_scanned: int, signals_found: int, trades_executed: int):
        """Log scan activity to database."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO scans (timestamp, model, markets_scanned, signals_found, trades_executed)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                self.model_name,
                markets_scanned,
                signals_found,
                trades_executed
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.debug(f"Failed to log scan: {e}")
    
    async def run_scan_cycle(self) -> Dict:
        """Run one scan cycle."""
        logger.info(f"[{self.model_name}] Starting scan cycle...")
        
        # Fetch markets
        markets = await self.fetch_markets()
        logger.info(f"[{self.model_name}] Fetched {len(markets)} active markets")
        
        signals_found = 0
        trades_executed = 0
        
        # Analyze each market
        for market in markets:
            signal = self.analyze_market(market)
            
            if signal:
                signals_found += 1
                question = market.get('question', 'Unknown')[:40]
                logger.info(f"[{self.model_name}] SIGNAL: {signal['side']} on '{question}' ({signal['reason']})")
                
                # Try to execute trade
                if self.execute_paper_trade(market, signal):
                    trades_executed += 1
        
        # Log scan results
        self.log_scan(len(markets), signals_found, trades_executed)
        
        if signals_found == 0:
            logger.info(f"[{self.model_name}] No signals found - markets stable")
        else:
            logger.info(f"[{self.model_name}] Scan complete: {signals_found} signals, {trades_executed} trades")
        
        return {
            'markets_scanned': len(markets),
            'signals_found': signals_found,
            'trades_executed': trades_executed
        }
    
    async def run(self):
        """Main trading loop."""
        logger.info(f"[{self.model_name}] Trading loop started")
        logger.info(f"[{self.model_name}] Initial bankroll: ${self.bankroll:.2f}")
        
        cycle = 0
        while True:
            cycle += 1
            try:
                logger.info(f"[{self.model_name}] === Cycle {cycle} ===")
                await self.run_scan_cycle()
            except Exception as e:
                logger.error(f"[{self.model_name}] Error in cycle {cycle}: {e}")
            
            # Wait for next cycle
            logger.info(f"[{self.model_name}] Sleeping {self.check_interval}s until next scan...")
            await asyncio.sleep(self.check_interval)


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Polymarket Trading Agent')
    parser.add_argument('--mode', default='paper', choices=['paper', 'live'])
    parser.add_argument('--config', required=True)
    parser.add_argument('--model', required=True)
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info(f"POLYMARKET TRADING AGENT - {args.model.upper()}")
    logger.info("=" * 60)
    logger.info(f"Mode: {args.mode}")
    logger.info(f"Config: {args.config}")
    logger.info(f"Model: {args.model}")
    logger.info("=" * 60)
    
    # Create and run trader
    trader = PaperTrader(args.model, args.config)
    await trader.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Agent stopped by user")
    except Exception as e:
        logger.error(f"Agent crashed: {e}", exc_info=True)
        raise
