"""
Market Data Recorder

Records live market data for future backtesting.
Lesson from @the_smart_ape: Polymarket's historical API is incomplete,
so you need to record your own data.
"""

import json
import gzip
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class MarketDataRecorder:
    """
    Records live market snapshots for backtesting.
    
    Stores:
    - Timestamp
    - Market ID and question
    - Current best bid/ask
    - Spread
    - Volume
    - Token IDs
    
    Data is compressed and stored in daily files.
    """
    
    def __init__(self, data_dir: str = "data/recordings"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.current_file = None
        self.snapshots_today = 0
        logger.info(f"MarketDataRecorder initialized: {data_dir}")
    
    def record_snapshot(
        self,
        market_id: str,
        market_question: str,
        token_id: str,
        best_bid: float,
        best_ask: float,
        spread_pct: float,
        volume_24h: float,
        metadata: Dict[str, Any] = None
    ):
        """Record a single market snapshot."""
        snapshot = {
            "timestamp": datetime.utcnow().isoformat(),
            "market_id": market_id,
            "market_question": market_question,
            "token_id": token_id,
            "best_bid": best_bid,
            "best_ask": best_ask,
            "mid_price": (best_bid + best_ask) / 2,
            "spread_pct": spread_pct,
            "volume_24h": volume_24h,
            "metadata": metadata or {}
        }
        
        # Write to daily file
        date_str = datetime.utcnow().strftime("%Y%m%d")
        filepath = self.data_dir / f"snapshots_{date_str}.jsonl.gz"
        
        # Append to compressed file
        with gzip.open(filepath, 'at', encoding='utf-8') as f:
            f.write(json.dumps(snapshot) + '\n')
        
        self.snapshots_today += 1
        
        if self.snapshots_today % 100 == 0:
            logger.debug(f"Recorded {self.snapshots_today} snapshots today")
    
    def record_signal_context(
        self,
        signal,
        orderbook_data: Dict[str, Any]
    ):
        """Record market state when a signal is generated."""
        self.record_snapshot(
            market_id=signal.market_id,
            market_question=signal.market_question,
            token_id=signal.token_id,
            best_bid=orderbook_data.get('best_bid', 0),
            best_ask=orderbook_data.get('best_ask', 0),
            spread_pct=orderbook_data.get('spread_pct', 0),
            volume_24h=orderbook_data.get('volume_24h', 0),
            metadata={
                "signal_id": signal.id,
                "signal_type": signal.type.value,
                "signal_strength": signal.strength.value,
                "current_price": signal.current_price,
                "fair_value": signal.fair_value_estimate,
                "mispricing_pct": signal.mispricing_pct,
            }
        )
    
    def record_execution(
        self,
        trade,
        actual_price: float,
        expected_price: float,
        slippage_pct: float
    ):
        """Record execution quality data."""
        execution_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "trade_id": trade.id,
            "market_id": trade.market_id,
            "side": trade.side,
            "expected_price": expected_price,
            "actual_price": actual_price,
            "slippage_pct": slippage_pct,
            "size": trade.size,
            "value_usd": trade.value_usd,
        }
        
        # Write to executions file
        date_str = datetime.utcnow().strftime("%Y%m")
        filepath = self.data_dir / f"executions_{date_str}.jsonl.gz"
        
        with gzip.open(filepath, 'at', encoding='utf-8') as f:
            f.write(json.dumps(execution_record) + '\n')
    
    def get_stats(self) -> Dict[str, Any]:
        """Get recording statistics."""
        total_size = sum(f.stat().st_size for f in self.data_dir.glob("*.jsonl.gz"))
        file_count = len(list(self.data_dir.glob("*.jsonl.gz")))
        
        return {
            "total_files": file_count,
            "total_size_mb": total_size / (1024 * 1024),
            "snapshots_today": self.snapshots_today,
            "data_directory": str(self.data_dir)
        }


