"""
Trade Logger

Comprehensive logging to SQLite and JSON.
"""

import logging
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

from .models import Trade, Position, ExecutionResult

logger = logging.getLogger(__name__)


class TradeLogger:
    """
    Log trades and positions to multiple outputs.
    
    Outputs:
    - SQLite database (queryable history)
    - JSON files (human-readable logs)
    - Python logging (real-time monitoring)
    """
    
    def __init__(self, db_path: str = "data/trades.db", log_dir: str = "logs/trades"):
        self.db_path = db_path
        self.log_dir = Path(log_dir)
        
        # Create directories
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_db()
        
        logger.info(f"TradeLogger initialized: DB={db_path}, Logs={log_dir}")
    
    def _init_db(self):
        """Initialize SQLite database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Signals table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS signals (
                id TEXT PRIMARY KEY,
                timestamp DATETIME,
                market_id TEXT,
                market_question TEXT,
                signal_type TEXT,
                strength TEXT,
                direction TEXT,
                current_price REAL,
                fair_value REAL,
                mispricing_pct REAL,
                position_size REAL,
                rejected BOOLEAN,
                rejection_reason TEXT
            )
        """)
        
        # Trades table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id TEXT PRIMARY KEY,
                signal_id TEXT,
                timestamp DATETIME,
                market_id TEXT,
                market_question TEXT,
                token_id TEXT,
                side TEXT,
                size REAL,
                price REAL,
                value_usd REAL,
                status TEXT,
                filled_size REAL,
                average_price REAL,
                error TEXT,
                FOREIGN KEY(signal_id) REFERENCES signals(id)
            )
        """)
        
        # Positions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS positions (
                id TEXT PRIMARY KEY,
                trade_id TEXT,
                market_id TEXT,
                market_question TEXT,
                side TEXT,
                size REAL,
                entry_price REAL,
                current_price REAL,
                unrealized_pnl REAL,
                realized_pnl REAL,
                status TEXT,
                opened_at DATETIME,
                closed_at DATETIME,
                last_updated DATETIME,
                FOREIGN KEY(trade_id) REFERENCES trades(id)
            )
        """)
        
        # Performance summary table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance (
                date DATE PRIMARY KEY,
                total_trades INTEGER,
                winning_trades INTEGER,
                losing_trades INTEGER,
                total_pnl REAL,
                win_rate REAL,
                avg_win REAL,
                avg_loss REAL,
                sharpe_ratio REAL,
                max_drawdown REAL
            )
        """)
        
        conn.commit()
        conn.close()
        
        logger.info("Database schema initialized")
    
    def log_signal(self, signal, rejected: bool = False, reason: Optional[str] = None):
        """Log a signal (whether acted on or not)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO signals VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            signal.id,
            datetime.utcnow().isoformat(),
            signal.market_id,
            signal.market_question,
            signal.type.value,
            signal.strength.value,
            signal.direction.value,
            signal.current_price,
            signal.fair_value_estimate,
            signal.mispricing_pct,
            signal.position_size,
            rejected,
            reason
        ))
        
        conn.commit()
        conn.close()
        
        # JSON log
        log_file = self.log_dir / f"signals_{datetime.utcnow().strftime('%Y%m%d')}.json"
        with open(log_file, 'a') as f:
            json.dump({
                "timestamp": datetime.utcnow().isoformat(),
                "signal_id": signal.id,
                "market": signal.market_question,
                "type": signal.type.value,
                "strength": signal.strength.value,
                "price": signal.current_price,
                "fair_value": signal.fair_value_estimate,
                "mispricing": f"{signal.mispricing_pct:.2f}%",
                "rejected": rejected,
                "reason": reason
            }, f)
            f.write('\n')
    
    def log_trade(self, trade: Trade, result: ExecutionResult):
        """Log a trade execution."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO trades VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            trade.id,
            trade.signal_id,
            trade.timestamp.isoformat(),
            trade.market_id,
            trade.market_question,
            trade.token_id,
            trade.side,
            trade.size,
            trade.price,
            trade.value_usd,
            trade.status.value,
            trade.filled_size,
            trade.average_price,
            trade.error
        ))
        
        conn.commit()
        conn.close()
        
        # JSON log
        log_file = self.log_dir / f"trades_{datetime.utcnow().strftime('%Y%m%d')}.json"
        with open(log_file, 'a') as f:
            json.dump({
                "timestamp": trade.timestamp.isoformat(),
                "trade_id": trade.id,
                "market": trade.market_question,
                "side": trade.side,
                "size": trade.size,
                "price": trade.price,
                "value": f"${trade.value_usd:.2f}",
                "status": trade.status.value,
                "success": result.success,
                "message": result.message
            }, f)
            f.write('\n')
        
        logger.info(f"Trade logged: {trade.id} - {trade.side} {trade.size} @ ${trade.price}")
    
    def log_position_update(self, position: Position):
        """Log position P&L update."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update or insert
        cursor.execute("""
            INSERT OR REPLACE INTO positions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            position.id,
            position.trade_id,
            position.market_id,
            position.market_question,
            position.side,
            position.size,
            position.entry_price,
            position.current_price,
            position.unrealized_pnl,
            position.realized_pnl,
            position.status.value,
            position.opened_at.isoformat(),
            position.closed_at.isoformat() if position.closed_at else None,
            datetime.utcnow().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def get_performance_summary(self) -> dict:
        """Get performance statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get closed positions
        cursor.execute("""
            SELECT 
                COUNT(*) as total_trades,
                SUM(CASE WHEN realized_pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                SUM(CASE WHEN realized_pnl < 0 THEN 1 ELSE 0 END) as losing_trades,
                SUM(realized_pnl) as total_pnl,
                AVG(CASE WHEN realized_pnl > 0 THEN realized_pnl END) as avg_win,
                AVG(CASE WHEN realized_pnl < 0 THEN realized_pnl END) as avg_loss
            FROM positions
            WHERE status = 'closed'
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        if row and row[0] > 0:
            total, wins, losses, pnl, avg_win, avg_loss = row
            win_rate = (wins / total * 100) if total > 0 else 0
            
            return {
                "total_trades": total,
                "winning_trades": wins,
                "losing_trades": losses,
                "win_rate": win_rate,
                "total_pnl": pnl,
                "avg_win": avg_win or 0,
                "avg_loss": avg_loss or 0,
            }
        
        return {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": 0,
            "total_pnl": 0,
            "avg_win": 0,
            "avg_loss": 0,
        }


