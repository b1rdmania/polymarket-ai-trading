#!/usr/bin/env python3
"""
Systematic Trading Agent - COMPLETE IMPLEMENTATION

Connects to Polymarket, scans for mean reversion opportunities,
executes paper trades, and SELLS when price reverts or market resolves.

Smart filtering:
- Caches ruled-out markets (don't rescan every cycle)
- Filters stale/resolved markets by date
- Checks recent volume activity
"""

import asyncio
import argparse
import logging
import sqlite3
import httpx
import yaml
import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Set

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

# Current year for filtering stale markets
CURRENT_YEAR = datetime.now().year


class MarketCache:
    """
    Cache for markets we've analyzed and ruled out.
    Prevents re-scanning the same market every cycle.
    """
    
    def __init__(self, refresh_interval_minutes: int = 60):
        self.ruled_out: Dict[str, Dict] = {}  # market_id -> {reason, timestamp, last_price}
        self.refresh_interval = timedelta(minutes=refresh_interval_minutes)
    
    def is_ruled_out(self, market_id: str) -> bool:
        """Check if market was recently ruled out."""
        if market_id not in self.ruled_out:
            return False
        
        entry = self.ruled_out[market_id]
        age = datetime.now() - entry['timestamp']
        
        # Refresh cache after interval
        if age > self.refresh_interval:
            del self.ruled_out[market_id]
            return False
        
        return True
    
    def rule_out(self, market_id: str, reason: str, price: float = None):
        """Mark a market as ruled out."""
        self.ruled_out[market_id] = {
            'reason': reason,
            'timestamp': datetime.now(),
            'last_price': price
        }
    
    def clear_if_price_changed(self, market_id: str, current_price: float, threshold: float = 0.05):
        """Clear cache entry if price has moved significantly."""
        if market_id in self.ruled_out:
            last_price = self.ruled_out[market_id].get('last_price')
            if last_price and abs(current_price - last_price) > threshold:
                del self.ruled_out[market_id]
                return True
        return False
    
    def get_stats(self) -> Dict:
        """Get cache statistics."""
        return {
            'ruled_out_count': len(self.ruled_out),
            'reasons': {}
        }


class PaperTrader:
    """
    Complete paper trading agent that:
    - Fetches live market data from Polymarket
    - Detects mean reversion signals (BUY)
    - Monitors positions and SELLS when price reverts
    - Tracks P&L on closed positions
    """
    
    def __init__(self, model_name: str, config_path: str):
        self.model_name = model_name
        self.config = self._load_config(config_path)
        self.db_path = BASE_DIR / self.config.get('data', {}).get('db_path', f'data/trades_{model_name}.db')
        self.bankroll = 1000.0  # Starting paper money
        
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
        
        # Sell thresholds
        self.take_profit_pct = 50.0
        self.stop_loss_pct = -50.0
        self.reversion_threshold = 0.40
        
        # Market selection thresholds
        self.min_volume_24hr = 1000    # Minimum $1k 24hr volume (active market)
        self.min_volume_total = 50000  # Minimum $50k total volume (established market)
        
        # Smart caching - don't rescan ruled-out markets
        self.market_cache = MarketCache(refresh_interval_minutes=60)
        
        # Initialize database
        self._init_db()
        
        # Load open positions from database
        self._load_open_positions()
        
        logger.info(f"Initialized {model_name} trader")
        logger.info(f"  Thresholds: favorite>{self.favorite_threshold}, longshot<{self.longshot_threshold}")
        logger.info(f"  Min mispricing: {self.min_mispricing_pct}%")
        logger.info(f"  Volume filters: 24hr>${self.min_volume_24hr}, total>${self.min_volume_total}")
        logger.info(f"  Open positions: {len(self.positions)}")
    
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
        
        # Scans table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                model TEXT NOT NULL,
                markets_scanned INTEGER,
                signals_found INTEGER,
                trades_executed INTEGER,
                positions_closed INTEGER,
                notes TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_open_positions(self):
        """Load open positions from database."""
        self.positions: Dict[str, Dict] = {}
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, market_id, market_question, side, entry_price, size_usd, shares
                FROM trades WHERE status = 'open' AND model = ?
            ''', (self.model_name,))
            
            for row in cursor.fetchall():
                self.positions[row[1]] = {
                    'trade_id': row[0],
                    'market_id': row[1],
                    'market_question': row[2],
                    'side': row[3],
                    'entry_price': row[4],
                    'size_usd': row[5],
                    'shares': row[6]
                }
            
            conn.close()
            logger.info(f"Loaded {len(self.positions)} open positions from database")
        except Exception as e:
            logger.error(f"Failed to load positions: {e}")
    
    def is_stale_market(self, market: Dict) -> Optional[str]:
        """
        Check if market is stale and should be skipped.
        Returns rejection reason if stale, None if OK.
        """
        question = market.get('question', '').lower()
        description = market.get('description', '').lower()
        
        # Check for past years in the question (2020-2025 when we're in 2026)
        past_years = [str(y) for y in range(2020, CURRENT_YEAR)]
        for year in past_years:
            if year in question:
                # But allow if it's a historical comparison like "beat 2024 record"
                if f"beat {year}" not in question and f"than {year}" not in question:
                    return f"Contains past year {year}"
        
        # Check end date if available
        end_date_str = market.get('endDate') or market.get('end_date_iso')
        if end_date_str:
            try:
                # Parse various date formats
                for fmt in ['%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d']:
                    try:
                        end_date = datetime.strptime(end_date_str[:19], fmt[:len(end_date_str[:19])])
                        if end_date < datetime.now() - timedelta(days=7):
                            return f"End date passed: {end_date_str[:10]}"
                        break
                    except:
                        continue
            except:
                pass
        
        # Check if already resolved
        if market.get('resolved', False):
            return "Already resolved"
        
        # Check for obvious closed indicators
        if market.get('closed', False) and not market.get('active', True):
            return "Closed market"
        
        return None  # Market is OK
    
    def has_sufficient_activity(self, market: Dict) -> Optional[str]:
        """
        Check if market has sufficient trading activity.
        Returns rejection reason if not, None if OK.
        """
        volume_total = float(market.get('volume', 0) or 0)
        volume_24hr = float(market.get('volume24hr', 0) or 0)
        
        if volume_total < self.min_volume_total:
            return f"Low total volume: ${volume_total:,.0f}"
        
        if volume_24hr < self.min_volume_24hr:
            return f"Low 24hr volume: ${volume_24hr:,.0f}"
        
        # Check volume ratio - if 24hr is tiny fraction of total, market may be dead
        if volume_total > 100000 and volume_24hr < volume_total * 0.001:
            return f"Inactive: 24hr vol only {volume_24hr/volume_total*100:.2f}% of total"
        
        return None  # Market is active enough
    
    async def fetch_markets(self) -> List[Dict]:
        """Fetch active markets from Polymarket with smart filtering."""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{GAMMA_API}/markets",
                    params={
                        "limit": 200,
                        "active": "true"
                    }
                )
                response.raise_for_status()
                markets = response.json()
                
                if not isinstance(markets, list):
                    return []
                
                return markets
        except Exception as e:
            logger.error(f"Failed to fetch markets: {e}")
            return []
    
    def get_market_price(self, market: Dict, side: str) -> Optional[float]:
        """Get current price for a side (YES/NO) from market data."""
        try:
            prices_str = market.get('outcomePrices', '[]')
            if isinstance(prices_str, str):
                prices = json.loads(prices_str)
            else:
                prices = prices_str
            
            if not prices or len(prices) < 2:
                return None
            
            yes_price = float(prices[0])
            no_price = float(prices[1])
            
            return yes_price if side == 'YES' else no_price
        except:
            return None
    
    def should_sell(self, position: Dict, current_price: float, market: Dict) -> Optional[Dict]:
        """
        Determine if we should sell this position.
        Returns sell signal dict if yes, None if no.
        """
        entry_price = position['entry_price']
        side = position['side']
        
        # Check if market is closed/resolved
        if market.get('closed', False):
            # Market resolved - check if we won or lost
            # If closed, price should be 0 or 1
            if current_price >= 0.95:  # We won
                return {
                    'reason': 'Market resolved - WIN',
                    'exit_price': 1.0
                }
            elif current_price <= 0.05:  # We lost
                return {
                    'reason': 'Market resolved - LOSS',
                    'exit_price': 0.0
                }
        
        # Calculate unrealized P&L percentage
        if entry_price > 0:
            pnl_pct = ((current_price - entry_price) / entry_price) * 100
        else:
            pnl_pct = 0
        
        # Take profit - price went up significantly
        if pnl_pct >= self.take_profit_pct:
            return {
                'reason': f'Take profit at +{pnl_pct:.1f}%',
                'exit_price': current_price
            }
        
        # Stop loss - price went down significantly
        if pnl_pct <= self.stop_loss_pct:
            return {
                'reason': f'Stop loss at {pnl_pct:.1f}%',
                'exit_price': current_price
            }
        
        # Mean reversion complete - price returned toward fair value
        # If we bought a longshot (low price), sell when it reverts up
        # If we bought a favorite NO (high YES price), sell when YES drops
        if side == 'YES' and entry_price < 0.30 and current_price >= self.reversion_threshold:
            return {
                'reason': f'Mean reversion complete ({entry_price*100:.0f}% → {current_price*100:.0f}%)',
                'exit_price': current_price
            }
        elif side == 'NO' and entry_price < 0.30 and current_price >= self.reversion_threshold:
            return {
                'reason': f'Mean reversion complete ({entry_price*100:.0f}% → {current_price*100:.0f}%)',
                'exit_price': current_price
            }
        
        return None
    
    def close_position(self, position: Dict, exit_price: float, reason: str) -> float:
        """Close a position and calculate P&L."""
        try:
            shares = position['shares']
            entry_price = position['entry_price']
            size_usd = position['size_usd']
            
            # Calculate P&L
            # If we bought shares at entry_price, and sell at exit_price
            exit_value = shares * exit_price
            pnl = exit_value - size_usd
            
            # Update database
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE trades 
                SET status = 'closed', exit_price = ?, exit_timestamp = ?, pnl = ?, notes = notes || ' | ' || ?
                WHERE id = ?
            ''', (
                exit_price,
                datetime.now().isoformat(),
                pnl,
                reason,
                position['trade_id']
            ))
            conn.commit()
            conn.close()
            
            # Add back to bankroll
            self.bankroll += exit_value
            
            # Remove from positions
            if position['market_id'] in self.positions:
                del self.positions[position['market_id']]
            
            logger.info(f"POSITION CLOSED: {position['side']} '{position['market_question'][:40]}'")
            logger.info(f"  Entry: {entry_price:.4f} → Exit: {exit_price:.4f}")
            logger.info(f"  P&L: ${pnl:.2f} ({reason})")
            logger.info(f"  Bankroll: ${self.bankroll:.2f}")
            
            return pnl
            
        except Exception as e:
            logger.error(f"Failed to close position: {e}")
            return 0
    
    def analyze_market_for_entry(self, market: Dict) -> Optional[Dict]:
        """
        Analyze a market for entry signal.
        Note: Volume/stale checks already done in scan cycle.
        """
        try:
            prices_str = market.get('outcomePrices', '[]')
            if isinstance(prices_str, str):
                prices = json.loads(prices_str)
            else:
                prices = prices_str
            
            if not prices or len(prices) < 1:
                return None
            
            yes_price = float(prices[0])
            
            # Skip if closed
            if market.get('closed', False):
                return None
            
            signal = None
            
            # Favorite overpriced (YES too high, e.g. 85%) - bet NO
            # The NO price will be cheap (15%), expecting reversion
            if yes_price >= self.favorite_threshold:
                mispricing = (yes_price - 0.5) * 100
                if mispricing >= self.min_mispricing_pct:
                    signal = {
                        'side': 'NO',
                        'price': 1 - yes_price,
                        'yes_price': yes_price,
                        'mispricing_pct': mispricing,
                        'strength': mispricing / 50,
                        'reason': f"Overpriced YES at {yes_price*100:.0f}%"
                    }
            
            # Longshot underpriced (YES too low, e.g. 5%) - bet YES
            # The YES price is cheap, expecting reversion up
            elif yes_price <= self.longshot_threshold:
                mispricing = (0.5 - yes_price) * 100
                if mispricing >= self.min_mispricing_pct:
                    signal = {
                        'side': 'YES',
                        'price': yes_price,
                        'yes_price': yes_price,
                        'mispricing_pct': mispricing,
                        'strength': mispricing / 50,
                        'reason': f"Underpriced YES at {yes_price*100:.0f}%"
                    }
            
            return signal
            
        except Exception as e:
            logger.debug(f"Error analyzing market: {e}")
            return None
    
    def calculate_position_size(self, signal: Dict) -> float:
        """Calculate position size using Kelly criterion."""
        edge = signal['mispricing_pct'] / 100
        kelly_size = self.kelly_fraction * edge * self.bankroll
        size = min(kelly_size, self.max_position_usd)
        size = min(size, self.bankroll * 0.25)
        return max(size, 10.0)
    
    def open_position(self, market: Dict, signal: Dict) -> bool:
        """Open a new position."""
        try:
            market_id = market.get('id', market.get('conditionId', 'unknown'))
            
            # Check if already have position
            if market_id in self.positions:
                return False
            
            # Check max positions
            if len(self.positions) >= self.max_positions:
                return False
            
            # Calculate size
            size_usd = self.calculate_position_size(signal)
            entry_price = signal['price']
            shares = size_usd / entry_price
            
            # Check bankroll
            if size_usd > self.bankroll:
                logger.info(f"Insufficient bankroll: need ${size_usd:.2f}, have ${self.bankroll:.2f}")
                return False
            
            self.bankroll -= size_usd
            
            # Save to database
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO trades (
                    timestamp, model, market_id, market_question, side,
                    entry_price, size_usd, shares, status, signal_strength, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'open', ?, ?)
            ''', (
                datetime.now().isoformat(),
                self.model_name,
                market_id,
                market.get('question', 'Unknown'),
                signal['side'],
                entry_price,
                size_usd,
                shares,
                signal['strength'],
                signal['reason']
            ))
            trade_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # Track position
            self.positions[market_id] = {
                'trade_id': trade_id,
                'market_id': market_id,
                'market_question': market.get('question', 'Unknown'),
                'side': signal['side'],
                'entry_price': entry_price,
                'size_usd': size_usd,
                'shares': shares
            }
            
            logger.info(f"POSITION OPENED: {signal['side']} ${size_usd:.2f} on '{market.get('question', 'Unknown')[:50]}'")
            logger.info(f"  Entry price: {entry_price:.4f}, Reason: {signal['reason']}")
            logger.info(f"  Bankroll: ${self.bankroll:.2f}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to open position: {e}")
            return False
    
    async def check_and_close_positions(self, markets: List[Dict]) -> int:
        """Check all open positions and close if conditions met."""
        closed = 0
        
        # Create market lookup by ID
        market_lookup = {}
        for m in markets:
            mid = m.get('id', m.get('conditionId'))
            if mid:
                market_lookup[mid] = m
        
        # Check each open position
        positions_to_check = list(self.positions.values())
        for position in positions_to_check:
            market_id = position['market_id']
            market = market_lookup.get(market_id)
            
            if not market:
                logger.debug(f"Market {market_id} not found in current data")
                continue
            
            current_price = self.get_market_price(market, position['side'])
            if current_price is None:
                continue
            
            sell_signal = self.should_sell(position, current_price, market)
            if sell_signal:
                self.close_position(position, sell_signal['exit_price'], sell_signal['reason'])
                closed += 1
        
        return closed
    
    async def run_scan_cycle(self) -> Dict:
        """Run one complete scan cycle - check exits, then entries with smart filtering."""
        logger.info(f"[{self.model_name}] === Starting scan cycle ===")
        
        # Fetch markets
        all_markets = await self.fetch_markets()
        logger.info(f"[{self.model_name}] Fetched {len(all_markets)} markets from API")
        
        # FIRST: Check existing positions for exits (use all markets for price data)
        logger.info(f"[{self.model_name}] Checking {len(self.positions)} open positions...")
        positions_closed = await self.check_and_close_positions(all_markets)
        
        # THEN: Smart filtering for new entry opportunities
        skipped_cached = 0
        skipped_stale = 0
        skipped_inactive = 0
        analyzed = 0
        signals_found = 0
        trades_opened = 0
        
        for market in all_markets:
            market_id = market.get('id', market.get('conditionId', 'unknown'))
            
            # Skip if recently ruled out (use cache)
            if self.market_cache.is_ruled_out(market_id):
                skipped_cached += 1
                continue
            
            # Get current price for cache invalidation
            current_price = self.get_market_price(market, 'YES')
            if current_price:
                self.market_cache.clear_if_price_changed(market_id, current_price)
            
            # Check if market is stale
            stale_reason = self.is_stale_market(market)
            if stale_reason:
                self.market_cache.rule_out(market_id, stale_reason, current_price)
                skipped_stale += 1
                continue
            
            # Check if market has activity
            activity_reason = self.has_sufficient_activity(market)
            if activity_reason:
                self.market_cache.rule_out(market_id, activity_reason, current_price)
                skipped_inactive += 1
                continue
            
            # Analyze for entry signal
            analyzed += 1
            signal = self.analyze_market_for_entry(market)
            
            if signal:
                signals_found += 1
                question = market.get('question', 'Unknown')[:50]
                logger.info(f"[{self.model_name}] SIGNAL: {signal['side']} on '{question}'")
                
                if self.open_position(market, signal):
                    trades_opened += 1
            else:
                # Cache as no signal (but will re-check if price moves)
                self.market_cache.rule_out(market_id, "No signal at current price", current_price)
        
        # Log results
        cache_stats = self.market_cache.get_stats()
        logger.info(f"[{self.model_name}] Filtering: {skipped_cached} cached, {skipped_stale} stale, {skipped_inactive} inactive")
        logger.info(f"[{self.model_name}] Analyzed {analyzed} markets → {signals_found} signals, {trades_opened} trades")
        logger.info(f"[{self.model_name}] Positions: {len(self.positions)} open, {positions_closed} closed this cycle")
        logger.info(f"[{self.model_name}] Bankroll: ${self.bankroll:.2f}, Cache size: {cache_stats['ruled_out_count']}")
        
        return {
            'markets_fetched': len(all_markets),
            'markets_analyzed': analyzed,
            'skipped_cached': skipped_cached,
            'skipped_stale': skipped_stale,
            'skipped_inactive': skipped_inactive,
            'signals_found': signals_found,
            'trades_opened': trades_opened,
            'positions_closed': positions_closed
        }
    
    async def run(self):
        """Main trading loop."""
        logger.info(f"[{self.model_name}] Trading loop started")
        logger.info(f"[{self.model_name}] Bankroll: ${self.bankroll:.2f}")
        logger.info(f"[{self.model_name}] Check interval: {self.check_interval}s")
        
        cycle = 0
        while True:
            cycle += 1
            try:
                await self.run_scan_cycle()
            except Exception as e:
                logger.error(f"[{self.model_name}] Error in cycle {cycle}: {e}")
            
            logger.info(f"[{self.model_name}] Sleeping {self.check_interval}s...")
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
    logger.info("=" * 60)
    
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
