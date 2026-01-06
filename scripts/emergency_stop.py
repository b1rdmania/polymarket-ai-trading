#!/usr/bin/env python3
"""
Emergency Stop Script

Immediately stops all trading activity:
1. Closes all open positions
2. Cancels pending orders
3. Disables the trading loop
4. Logs shutdown reason

Usage:
    python scripts/emergency_stop.py
    python scripts/emergency_stop.py --reason "Manual shutdown for maintenance"
"""

import asyncio
import sqlite3
import logging
import sys
import os
from pathlib import Path
from datetime import datetime
import argparse

# Add toolkit to path
toolkit_path = Path(__file__).parent.parent / "toolkit"
sys.path.insert(0, str(toolkit_path))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EmergencyStop:
    """Emergency shutdown manager."""
    
    def __init__(self, db_path: str = "data/trades.db"):
        self.db_path = db_path
        self.positions_closed = 0
        self.orders_cancelled = 0
    
    async def execute(self, reason: str = "Emergency stop triggered"):
        """Execute emergency shutdown."""
        logger.critical("="*60)
        logger.critical("EMERGENCY STOP INITIATED")
        logger.critical(f"Reason: {reason}")
        logger.critical("="*60)
        
        try:
            # 1. Get all open positions
            open_positions = self._get_open_positions()
            logger.info(f"Found {len(open_positions)} open positions")
            
            # 2. Close all positions
            if open_positions:
                await self._close_all_positions(open_positions)
            
            # 3. Cancel pending orders
            await self._cancel_all_orders()
            
            # 4. Create shutdown flag
            self._create_shutdown_flag(reason)
            
            # 5. Log final state
            self._log_shutdown(reason)
            
            logger.critical("="*60)
            logger.critical("EMERGENCY STOP COMPLETE")
            logger.critical(f"Positions closed: {self.positions_closed}")
            logger.critical(f"Orders cancelled: {self.orders_cancelled}")
            logger.critical("="*60)
            
            return True
            
        except Exception as e:
            logger.error(f"Error during emergency stop: {e}", exc_info=True)
            return False
    
    def _get_open_positions(self):
        """Get all open positions from database."""
        if not os.path.exists(self.db_path):
            logger.warning(f"Database not found: {self.db_path}")
            return []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, market_id, market_question, side, size, entry_price, current_price
            FROM positions
            WHERE status = 'open'
        """)
        
        positions = cursor.fetchall()
        conn.close()
        
        return positions
    
    async def _close_all_positions(self, positions):
        """Close all open positions."""
        logger.info("Closing all positions...")
        
        for pos in positions:
            pos_id, market_id, market_question, side, size, entry_price, current_price = pos
            
            logger.info(f"Closing: {market_question}")
            
            # Calculate P&L
            if side == "BUY":
                pnl = (current_price - entry_price) * size
            else:
                pnl = (entry_price - current_price) * size
            
            # Mark as closed in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE positions
                SET status = 'closed',
                    closed_at = ?,
                    realized_pnl = ?
                WHERE id = ?
            """, (datetime.utcnow().isoformat(), pnl, pos_id))
            
            conn.commit()
            conn.close()
            
            self.positions_closed += 1
            logger.info(f"✓ Closed with P&L: ${pnl:.2f}")
    
    async def _cancel_all_orders(self):
        """Cancel all pending orders."""
        logger.info("Cancelling pending orders...")
        
        if not os.path.exists(self.db_path):
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE trades
            SET status = 'cancelled'
            WHERE status IN ('pending', 'submitted')
        """)
        
        self.orders_cancelled = cursor.rowcount
        conn.commit()
        conn.close()
        
        logger.info(f"✓ Cancelled {self.orders_cancelled} orders")
    
    def _create_shutdown_flag(self, reason: str):
        """Create a flag file to prevent restart."""
        flag_path = Path("data/EMERGENCY_STOP")
        flag_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(flag_path, 'w') as f:
            f.write(f"Emergency stop executed at {datetime.utcnow().isoformat()}\n")
            f.write(f"Reason: {reason}\n")
            f.write("\nTo resume trading, delete this file and restart the agent.\n")
        
        logger.info(f"✓ Created shutdown flag: {flag_path}")
    
    def _log_shutdown(self, reason: str):
        """Log shutdown details."""
        log_path = Path("logs/emergency_stops.log")
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(log_path, 'a') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Emergency Stop: {datetime.utcnow().isoformat()}\n")
            f.write(f"Reason: {reason}\n")
            f.write(f"Positions closed: {self.positions_closed}\n")
            f.write(f"Orders cancelled: {self.orders_cancelled}\n")
            f.write(f"{'='*60}\n")
        
        logger.info(f"✓ Logged to {log_path}")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Emergency Stop - Shutdown Trading")
    parser.add_argument(
        '--reason',
        default="Manual emergency stop",
        help='Reason for shutdown'
    )
    parser.add_argument(
        '--db',
        default="data/trades.db",
        help='Path to trades database'
    )
    
    args = parser.parse_args()
    
    # Confirm shutdown
    print("\n" + "="*60)
    print("⚠️  EMERGENCY STOP")
    print("="*60)
    print("\nThis will:")
    print("  • Close all open positions")
    print("  • Cancel all pending orders")
    print("  • Stop the trading agent")
    print(f"\nReason: {args.reason}")
    print("\n" + "="*60)
    
    response = input("\nAre you sure? Type 'STOP' to confirm: ")
    
    if response != "STOP":
        print("Emergency stop cancelled.")
        return
    
    # Execute emergency stop
    stopper = EmergencyStop(db_path=args.db)
    success = await stopper.execute(reason=args.reason)
    
    if success:
        print("\n✅ Emergency stop completed successfully")
        print("\nTo resume trading:")
        print("  1. Delete data/EMERGENCY_STOP flag file")
        print("  2. Restart the trading agent")
    else:
        print("\n❌ Emergency stop encountered errors")
        print("Check logs for details")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())


