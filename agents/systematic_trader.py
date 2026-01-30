#!/usr/bin/env python3
"""
Simple Mean Reversion Trader

Scans Polymarket for extreme prices, bets on reversion to mean.
KISS: No AI, no complex caching, just find mispriced markets and trade.
"""

import asyncio
import argparse
import logging
import sqlite3
import httpx
import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

GAMMA_API = "https://gamma-api.polymarket.com"
BASE_DIR = Path(__file__).parent.parent


class SimpleTrader:
    """
    Simple mean reversion trader.
    - Fetches ALL markets from Polymarket
    - Finds extreme prices (< 20% or > 80%)
    - Bets on reversion toward 50%
    - Takes profit at +50%, stops loss at -50%
    """
    
    def __init__(self, model_name: str, config_path: str):
        self.model_name = model_name
        self.config = self._load_config(config_path)
        
        # Database path
        db_name = self.config.get('data', {}).get('db_path', f'data/trades_{model_name}.db')
        self.db_path = BASE_DIR / db_name
        
        # Simple parameters
        self.bankroll = 1000.0
        self.min_volume = 10000           # $10k minimum volume
        self.extreme_threshold = 0.20     # Trade when YES < 20% or > 80%
        self.take_profit_pct = 50.0       # Sell at +50%
        self.stop_loss_pct = -50.0        # Sell at -50%
        self.max_positions = 15
        self.position_size = 50.0         # $50 per trade
        self.check_interval = 300         # 5 minutes
        
        # Track positions in memory (keyed by trade_id)
        self.positions: Dict[str, Dict] = {}
        
        self._init_db()
        self._load_positions()
        
        logger.info(f"Trader initialized: {len(self.positions)} open positions, ${self.bankroll:.0f} bankroll")
    
    def _load_config(self, path: str) -> dict:
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f) or {}
        except:
            return {}
    
    def _init_db(self):
        """Create trades table if not exists."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        conn.execute('''
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
                notes TEXT
            )
        ''')
        conn.commit()
        conn.close()
    
    def _load_positions(self):
        """Load open positions from database."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, market_id, market_question, side, entry_price, size_usd, shares
                FROM trades WHERE status = 'open' AND model = ?
            ''', (self.model_name,))
            
            for row in cursor.fetchall():
                self.positions[str(row[0])] = {
                    'trade_id': row[0],
                    'market_id': row[1],
                    'market_question': row[2],
                    'side': row[3],
                    'entry_price': row[4],
                    'size_usd': row[5],
                    'shares': row[6]
                }
            conn.close()
        except Exception as e:
            logger.error(f"Failed to load positions: {e}")
    
    async def fetch_all_markets(self) -> List[Dict]:
        """Fetch all active markets from Polymarket."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{GAMMA_API}/markets",
                    params={"limit": 500, "active": "true", "closed": "false"}
                )
                response.raise_for_status()
                return response.json() if isinstance(response.json(), list) else []
        except Exception as e:
            logger.error(f"Failed to fetch markets: {e}")
            return []
    
    def get_price(self, market: Dict, side: str) -> Optional[float]:
        """Get current price for YES or NO."""
        try:
            prices = market.get('outcomePrices', '[]')
            if isinstance(prices, str):
                prices = json.loads(prices)
            if len(prices) >= 2:
                return float(prices[0]) if side == 'YES' else float(prices[1])
        except:
            pass
        return None
    
    def find_signal(self, market: Dict) -> Optional[Dict]:
        """
        Check if market has an extreme price worth trading.
        Returns signal dict or None.
        """
        # Check volume
        volume = float(market.get('volume', 0) or 0)
        if volume < self.min_volume:
            return None
        
        # Get YES price
        yes_price = self.get_price(market, 'YES')
        if yes_price is None:
            return None
        
        # Check for extreme prices
        if yes_price <= self.extreme_threshold:
            # YES is very cheap - buy YES expecting reversion up
            return {
                'side': 'YES',
                'price': yes_price,
                'reason': f'YES underpriced at {yes_price*100:.0f}%'
            }
        elif yes_price >= (1 - self.extreme_threshold):
            # YES is very expensive - buy NO expecting reversion down
            return {
                'side': 'NO',
                'price': 1 - yes_price,
                'reason': f'NO underpriced at {(1-yes_price)*100:.0f}%'
            }
        
        return None
    
    def should_close(self, position: Dict, current_price: float) -> Optional[Dict]:
        """Check if position should be closed."""
        entry = position['entry_price']
        if entry <= 0:
            return None
        
        pnl_pct = ((current_price - entry) / entry) * 100
        
        if pnl_pct >= self.take_profit_pct:
            return {'reason': f'Take profit +{pnl_pct:.0f}%', 'price': current_price}
        elif pnl_pct <= self.stop_loss_pct:
            return {'reason': f'Stop loss {pnl_pct:.0f}%', 'price': current_price}
        
        return None
    
    def open_trade(self, market: Dict, signal: Dict) -> bool:
        """Open a new trade."""
        market_id = market.get('id', 'unknown')
        
        # Check if we already have this market
        for pos in self.positions.values():
            if pos['market_id'] == market_id:
                return False
        
        # Check max positions
        if len(self.positions) >= self.max_positions:
            return False
        
        # Check bankroll
        if self.position_size > self.bankroll:
            return False
        
        entry_price = signal['price']
        shares = self.position_size / entry_price
        
        # Save to database
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO trades (timestamp, model, market_id, market_question, side, entry_price, size_usd, shares, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'open', ?)
        ''', (
            datetime.now().isoformat(),
            self.model_name,
            market_id,
            market.get('question', 'Unknown'),
            signal['side'],
            entry_price,
            self.position_size,
            shares,
            signal['reason']
        ))
        trade_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Track in memory
        self.positions[str(trade_id)] = {
            'trade_id': trade_id,
            'market_id': market_id,
            'market_question': market.get('question', 'Unknown'),
            'side': signal['side'],
            'entry_price': entry_price,
            'size_usd': self.position_size,
            'shares': shares
        }
        
        self.bankroll -= self.position_size
        
        logger.info(f"OPEN: {signal['side']} ${self.position_size:.0f} @ {entry_price*100:.1f}% - {market.get('question', '')[:50]}")
        return True
    
    def close_trade(self, position: Dict, exit_price: float, reason: str):
        """Close a trade and record P&L."""
        pnl = (position['shares'] * exit_price) - position['size_usd']
        
        conn = sqlite3.connect(str(self.db_path))
        conn.execute('''
            UPDATE trades SET status = 'closed', exit_price = ?, exit_timestamp = ?, pnl = ?, notes = notes || ' | ' || ?
            WHERE id = ?
        ''', (exit_price, datetime.now().isoformat(), pnl, reason, position['trade_id']))
        conn.commit()
        conn.close()
        
        self.bankroll += position['shares'] * exit_price
        del self.positions[str(position['trade_id'])]
        
        logger.info(f"CLOSE: {position['side']} @ {exit_price*100:.1f}% - P&L: ${pnl:+.2f} - {reason}")
    
    async def run_cycle(self):
        """Run one scan cycle."""
        markets = await self.fetch_all_markets()
        logger.info(f"Fetched {len(markets)} markets, checking {len(self.positions)} positions")
        
        # Build market lookup
        market_lookup = {m.get('id'): m for m in markets if m.get('id')}
        market_by_question = {m.get('question', ''): m for m in markets}
        
        # 1. Check exits on existing positions
        closed = 0
        for pos in list(self.positions.values()):
            market = market_lookup.get(pos['market_id']) or market_by_question.get(pos['market_question'])
            if not market:
                continue
            
            current = self.get_price(market, pos['side'])
            if current is None:
                continue
            
            close_signal = self.should_close(pos, current)
            if close_signal:
                self.close_trade(pos, close_signal['price'], close_signal['reason'])
                closed += 1
        
        # 2. Look for new entries
        opened = 0
        for market in markets:
            signal = self.find_signal(market)
            if signal and self.open_trade(market, signal):
                opened += 1
        
        logger.info(f"Cycle done: {opened} opened, {closed} closed, {len(self.positions)} positions, ${self.bankroll:.0f} bankroll")
    
    async def run(self):
        """Main loop."""
        logger.info(f"Starting trader, scanning every {self.check_interval}s")
        
        while True:
            try:
                await self.run_cycle()
            except Exception as e:
                logger.error(f"Cycle error: {e}")
            
            await asyncio.sleep(self.check_interval)


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', default='paper')
    parser.add_argument('--config', required=True)
    parser.add_argument('--model', required=True)
    args = parser.parse_args()
    
    logger.info(f"=== POLYMARKET TRADER ({args.model}) ===")
    trader = SimpleTrader(args.model, args.config)
    await trader.run()


if __name__ == "__main__":
    asyncio.run(main())
