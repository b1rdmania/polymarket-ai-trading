#!/usr/bin/env python3
"""
Mean Reversion Trader with AI Gate

Scans Polymarket for extreme prices, uses AI to filter bad trades.
"""

import asyncio
import argparse
import logging
import sqlite3
import httpx
import yaml
import json
import os
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
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')


class MeanReversionTrader:
    """
    Mean reversion trader with configurable thresholds and Kelly sizing.
    - Fetches ALL markets from Polymarket (500+)
    - Finds extreme prices based on config thresholds
    - Uses Kelly criterion for position sizing
    - AI gate filters out bad trades
    """
    
    def __init__(self, model_name: str, config_path: str):
        self.model_name = model_name
        self.config = self._load_config(config_path)
        
        # Database path
        db_name = self.config.get('data', {}).get('db_path', f'data/trades_{model_name}.db')
        self.db_path = BASE_DIR / db_name
        
        # Risk parameters from config
        risk = self.config.get('risk', {})
        self.bankroll = 1000.0
        self.kelly_fraction = risk.get('kelly_fraction', 0.25)
        self.max_position_usd = risk.get('max_position_usd', 500)
        self.max_positions = risk.get('max_positions', 10)
        self.max_total_exposure = risk.get('max_total_exposure_usd', 2000)
        
        # Signal thresholds from config
        signals = self.config.get('signals', {}).get('mean_reversion', {})
        self.favorite_threshold = signals.get('favorite_threshold', 0.70)  # YES > 70% = favorite
        self.longshot_threshold = signals.get('longshot_threshold', 0.30)  # YES < 30% = longshot
        self.min_mispricing_pct = signals.get('min_mispricing_pct', 5.0)   # Min edge required
        
        # Execution parameters
        execution = self.config.get('execution', {})
        self.check_interval = execution.get('check_interval_seconds', 300)
        
        # Fixed parameters
        self.min_volume = 10000           # $10k minimum volume
        self.take_profit_pct = 50.0       # Sell at +50%
        self.stop_loss_pct = -50.0        # Sell at -50%
        
        # Track positions in memory (keyed by trade_id)
        self.positions: Dict[str, Dict] = {}
        
        self._init_db()
        self._load_positions()
        
        logger.info(f"Trader initialized: {len(self.positions)} positions, ${self.bankroll:.0f} bankroll")
        logger.info(f"Thresholds: favorite>{self.favorite_threshold:.0%}, longshot<{self.longshot_threshold:.0%}, min_edge>{self.min_mispricing_pct}%")
        logger.info(f"Risk: kelly={self.kelly_fraction}, max_pos=${self.max_position_usd}, max_total=${self.max_total_exposure}")
    
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
        Uses configurable thresholds and calculates edge.
        Returns signal dict or None.
        """
        # Check volume
        volume = float(market.get('volume', 0) or 0)
        if volume < self.min_volume:
            return None
        
        # Get YES price
        yes_price = self.get_price(market, 'YES')
        if yes_price is None or yes_price <= 0 or yes_price >= 1:
            return None
        
        # Calculate fair value (assume 50% for mean reversion)
        fair_value = 0.50
        
        # Check for longshot (YES < longshot_threshold)
        # Strategy: buy YES, expecting reversion up toward fair value
        if yes_price < self.longshot_threshold:
            edge_pct = ((fair_value - yes_price) / yes_price) * 100
            if edge_pct >= self.min_mispricing_pct:
                return {
                    'side': 'YES',
                    'price': yes_price,
                    'edge': edge_pct,
                    'reason': f'Longshot YES at {yes_price*100:.0f}% (edge: {edge_pct:.0f}%)'
                }
        
        # Check for heavy favorite (YES > favorite_threshold)
        # Strategy: buy NO, expecting reversion down toward fair value
        elif yes_price > self.favorite_threshold:
            no_price = 1 - yes_price
            edge_pct = ((fair_value - no_price) / no_price) * 100
            if edge_pct >= self.min_mispricing_pct:
                return {
                    'side': 'NO',
                    'price': no_price,
                    'edge': edge_pct,
                    'reason': f'Favorite at {yes_price*100:.0f}%, NO at {no_price*100:.0f}% (edge: {edge_pct:.0f}%)'
                }
        
        return None
    
    def calculate_kelly_size(self, edge_pct: float, price: float, ai_confidence: float = 0.5) -> float:
        """
        Calculate position size using Kelly criterion.
        
        Kelly formula: f* = (bp - q) / b
        Where: b = odds (payout ratio), p = win probability, q = 1-p
        
        We use fractional Kelly (kelly_fraction) to reduce variance.
        """
        if price <= 0 or price >= 1:
            return 0
        
        # Implied odds from price
        b = (1 - price) / price  # e.g., price=0.20 -> b=4 (4:1 odds)
        
        # Estimate win probability from edge and AI confidence
        # Higher edge + higher AI confidence = higher estimated win prob
        base_win_prob = 0.50 + (edge_pct / 200)  # Edge gives base probability
        p = base_win_prob * (0.7 + 0.3 * ai_confidence)  # AI confidence adjusts
        p = max(0.1, min(0.9, p))  # Clamp between 10-90%
        q = 1 - p
        
        # Kelly formula
        kelly = (b * p - q) / b
        
        if kelly <= 0:
            return 0
        
        # Apply fractional Kelly and constraints
        position_size = self.bankroll * kelly * self.kelly_fraction
        position_size = min(position_size, self.max_position_usd)
        position_size = max(position_size, 10)  # Minimum $10 bet
        
        return round(position_size, 2)
    
    async def ai_evaluate(self, market: Dict, signal: Dict) -> Optional[Dict]:
        """
        Ask AI if this trade makes sense. Returns enhanced signal or None to reject.
        """
        if not OPENAI_API_KEY:
            return signal  # No API key, skip AI gate
        
        question = market.get('question', 'Unknown')
        description = market.get('description', '')[:500]
        end_date = market.get('endDate', 'Unknown')
        
        prompt = f"""You're evaluating a prediction market trade. Be brief.

Market: {question}
Description: {description}
End Date: {end_date}
Current Price: {signal['side']} at {signal['price']*100:.0f}%
Strategy: Mean reversion - betting price will move toward 50%

Is this a reasonable trade? Consider:
1. Is the market still active/relevant (not already resolved or stale)?
2. Does the extreme price suggest genuine mispricing vs correct pricing of unlikely outcome?
3. Any obvious red flags?

Respond with JSON only:
{{"approve": true/false, "confidence": 0.0-1.0, "reason": "brief reason"}}"""

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.3,
                        "max_tokens": 150
                    }
                )
                resp.raise_for_status()
                
                content = resp.json()['choices'][0]['message']['content']
                # Parse JSON from response
                content = content.strip()
                if content.startswith('```'):
                    content = content.split('\n', 1)[1].rsplit('```', 1)[0]
                
                result = json.loads(content)
                
                if result.get('approve', False):
                    signal['ai_confidence'] = result.get('confidence', 0.5)
                    signal['ai_reason'] = result.get('reason', '')
                    signal['reason'] += f" | AI: {signal['ai_reason']}"
                    logger.info(f"AI approved: {question[:40]}... ({signal['ai_confidence']:.0%})")
                    return signal
                else:
                    logger.info(f"AI rejected: {question[:40]}... - {result.get('reason', 'no reason')}")
                    return None
                    
        except Exception as e:
            logger.warning(f"AI evaluation failed: {e}, proceeding without")
            return signal  # Fail open - if AI fails, still allow trade
    
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
        """Open a new trade using Kelly-sized position."""
        market_id = market.get('id', 'unknown')
        
        # Check if we already have this market
        for pos in self.positions.values():
            if pos['market_id'] == market_id:
                return False
        
        # Check max positions
        if len(self.positions) >= self.max_positions:
            return False
        
        # Calculate position size using Kelly criterion
        edge = signal.get('edge', 10)
        ai_confidence = signal.get('ai_confidence', 0.5)
        position_size = self.calculate_kelly_size(edge, signal['price'], ai_confidence)
        
        # Check total exposure
        current_exposure = sum(p['size_usd'] for p in self.positions.values())
        if current_exposure + position_size > self.max_total_exposure:
            return False
        
        # Check bankroll
        if position_size > self.bankroll:
            return False
        
        entry_price = signal['price']
        shares = position_size / entry_price
        
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
            position_size,
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
            'size_usd': position_size,
            'shares': shares
        }
        
        self.bankroll -= position_size
        
        logger.info(f"OPEN: {signal['side']} ${position_size:.0f} @ {entry_price*100:.1f}% (edge:{edge:.0f}%) - {market.get('question', '')[:50]}")
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
        
        # 2. Look for new entries (with AI gate)
        opened = 0
        candidates = []
        for market in markets:
            signal = self.find_signal(market)
            if signal:
                candidates.append((market, signal))
        
        logger.info(f"Found {len(candidates)} candidates, running AI evaluation...")
        
        for market, signal in candidates:
            # Check if we can still open positions
            if len(self.positions) >= self.max_positions:
                break
            
            # AI gate
            approved_signal = await self.ai_evaluate(market, signal)
            if approved_signal and self.open_trade(market, approved_signal):
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
    
    logger.info(f"=== POLYMARKET MEAN REVERSION TRADER ({args.model}) ===")
    trader = MeanReversionTrader(args.model, args.config)
    await trader.run()


if __name__ == "__main__":
    asyncio.run(main())
