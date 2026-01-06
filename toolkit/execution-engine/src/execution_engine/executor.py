"""
Polymarket Executor

Wraps Polymarket Agents framework for trade execution.
Supports both paper trading and live trading modes.
"""

import logging
import sys
import os
from typing import Optional
from datetime import datetime

# Add polymarket-agent to path
agent_path = os.path.join(os.path.dirname(__file__), "../../../polymarket-agent")
if os.path.exists(agent_path):
    sys.path.insert(0, agent_path)

from .models import (
    TradingConfig,
    Trade,
    TradeStatus,
    ExecutionResult,
)

logger = logging.getLogger(__name__)


class PolymarketExecutor:
    """
    Execute trades via Polymarket Agents framework.
    
    Modes:
    - paper: Simulates execution, no real trades
    - live: Executes real trades on Polymarket
    """
    
    def __init__(self, config: TradingConfig):
        self.config = config
        self.polymarket_client = None
        
        if config.mode.value == "live":
            self._init_live_client()
    
    def _init_live_client(self):
        """Initialize Polymarket client for live trading."""
        try:
            # Try to import Polymarket Agents
            from agents.polymarket import Polymarket
            
            private_key = os.getenv("POLYGON_WALLET_PRIVATE_KEY")
            if not private_key:
                raise ValueError("POLYGON_WALLET_PRIVATE_KEY not set")
            
            self.polymarket_client = Polymarket(private_key)
            logger.info("Polymarket client initialized for LIVE trading")
        except ImportError:
            logger.error("Polymarket Agents not properly installed")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Polymarket client: {e}")
            raise
    
    async def execute_trade(self, trade: Trade) -> ExecutionResult:
        """
        Execute a trade.
        
        Args:
            trade: Trade object with all parameters
        
        Returns:
            ExecutionResult with success status and details
        """
        
        if self.config.dry_run:
            logger.info(f"[DRY RUN] Would execute: {trade.side} {trade.size} shares of {trade.market_question} @ ${trade.price}")
            trade.status = TradeStatus.FILLED
            trade.filled_size = trade.size
            trade.average_price = trade.price
            return ExecutionResult(
                success=True,
                trade=trade,
                message="Dry run - not executed"
            )
        
        if self.config.mode.value == "paper":
            return await self._execute_paper_trade(trade)
        else:
            return await self._execute_live_trade(trade)
    
    async def _execute_paper_trade(self, trade: Trade) -> ExecutionResult:
        """Simulate trade execution for paper trading."""
        logger.info(f"[PAPER] Executing: {trade.side} {trade.size} shares @ ${trade.price}")
        
        # Simulate realistic slippage (lesson from @the_smart_ape)
        # They used 2% spread assumption - we'll simulate 0.2-0.5% slippage
        import random
        slippage_pct = random.uniform(0.002, 0.005)  # 0.2-0.5%
        
        if trade.side == "BUY":
            execution_price = trade.price * (1 + slippage_pct)
        else:
            execution_price = trade.price * (1 - slippage_pct)
        
        # Track slippage
        actual_slippage = ((execution_price - trade.price) / trade.price) * 100
        logger.info(f"[PAPER] Simulated slippage: {actual_slippage:.3f}%")
        
        # Simulate execution
        trade.status = TradeStatus.FILLED
        trade.filled_size = trade.size
        trade.average_price = execution_price
        trade.timestamp = datetime.utcnow()
        trade.metadata = {
            "expected_price": trade.price,
            "actual_price": execution_price,
            "slippage_pct": actual_slippage,
        }
        
        return ExecutionResult(
            success=True,
            trade=trade,
            message=f"Paper trade executed (slippage: {actual_slippage:.3f}%)"
        )
    
    async def _execute_live_trade(self, trade: Trade) -> ExecutionResult:
        """Execute real trade on Polymarket."""
        if not self.polymarket_client:
            return ExecutionResult(
                success=False,
                trade=trade,
                message="Polymarket client not initialized",
                error="Client not initialized"
            )
        
        try:
            logger.info(f"[LIVE] Executing: {trade.side} {trade.size} shares @ ${trade.price}")
            
            # Build order using Polymarket Agents
            # This is a simplified version - actual implementation would use
            # the full Polymarket order building and signing logic
            
            # For now, return not implemented
            logger.warning("Live trading not fully implemented yet - use paper mode")
            trade.status = TradeStatus.FAILED
            trade.error = "Live trading not yet implemented"
            
            return ExecutionResult(
                success=False,
                trade=trade,
                message="Live trading not implemented",
                error="Not implemented"
            )
            
        except Exception as e:
            logger.error(f"Trade execution failed: {e}")
            trade.status = TradeStatus.FAILED
            trade.error = str(e)
            
            return ExecutionResult(
                success=False,
                trade=trade,
                message=f"Execution failed: {e}",
                error=str(e)
            )
    
    async def cancel_order(self, trade_id: str) -> bool:
        """Cancel a pending order."""
        logger.info(f"Cancelling order {trade_id}")
        # Implementation depends on Polymarket Agents API
        return True
    
    async def get_order_status(self, trade_id: str) -> Optional[TradeStatus]:
        """Check status of an order."""
        # Implementation depends on Polymarket Agents API
        return None

