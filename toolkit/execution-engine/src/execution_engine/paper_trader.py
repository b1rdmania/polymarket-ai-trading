"""
Paper Trader

Simulates trades without real money for strategy validation.
"""

import logging
from typing import List, Dict
from datetime import datetime
import json
from pathlib import Path

from .models import Trade, Position, TradingConfig, PositionStatus, TradeStatus
from .trade_logger import TradeLogger

logger = logging.getLogger(__name__)


class PaperTrader:
    """
    Paper trading engine for strategy validation.
    
    Tracks:
    - Hypothetical trades
    - P&L based on actual price movements
    - Performance metrics
    - Slippage simulation
    """
    
    def __init__(self, config: TradingConfig):
        self.config = config
        self.logger = TradeLogger(
            db_path="data/paper_trades.db",
            log_dir="logs/paper"
        )
        
        self.positions: List[Position] = []
        self.closed_positions: List[Position] = []
        self.initial_capital = config.max_total_exposure_usd
        self.current_capital = self.initial_capital
        self.peak_capital = self.initial_capital
        
        logger.info(f"Paper trader initialized with ${self.initial_capital}")
    
    def execute_trade(self, trade: Trade) -> bool:
        """
        Execute a simulated trade.
        
        Args:
            trade: Trade to execute
        
        Returns:
            True if successful
        """
        # Simulate slippage (0.1-0.5%)
        slippage = 0.002  # 0.2% average
        if trade.side == "BUY":
            execution_price = trade.price * (1 + slippage)
        else:
            execution_price = trade.price * (1 - slippage)
        
        # Update trade
        trade.status = TradeStatus.FILLED
        trade.filled_size = trade.size
        trade.average_price = execution_price
        trade.value_usd = trade.size * execution_price
        trade.timestamp = datetime.utcnow()
        
        # Log trade
        from .models import ExecutionResult
        self.logger.log_trade(trade, ExecutionResult(
            success=True,
            trade=trade,
            message=f"Paper trade executed with {slippage*100:.2f}% slippage"
        ))
        
        # Create or close position
        if trade.side == "BUY":
            self._open_position(trade)
        else:
            self._close_position(trade)
        
        logger.info(
            f"📝 Paper trade: {trade.side} {trade.size} shares @ ${execution_price:.4f} "
            f"(slippage: {slippage*100:.2f}%)"
        )
        
        return True
    
    def _open_position(self, trade: Trade):
        """Open a new position."""
        position = Position(
            trade_id=trade.id,
            market_id=trade.market_id,
            market_question=trade.market_question,
            token_id=trade.token_id,
            side=trade.side,
            size=trade.filled_size,
            entry_price=trade.average_price,
            current_price=trade.average_price,
            status=PositionStatus.OPEN,
        )
        
        self.positions.append(position)
        self.current_capital -= trade.value_usd
        
        logger.info(f"✅ Position opened: {trade.market_question}")
        logger.info(f"💰 Remaining capital: ${self.current_capital:.2f}")
    
    def _close_position(self, trade: Trade):
        """Close an existing position."""
        # Find matching open position
        position = next(
            (p for p in self.positions 
             if p.market_id == trade.market_id and p.status == PositionStatus.OPEN),
            None
        )
        
        if not position:
            logger.warning(f"No open position found for {trade.market_id}")
            return
        
        # Calculate P&L
        if position.side == "BUY":
            pnl = (trade.average_price - position.entry_price) * position.size
        else:
            pnl = (position.entry_price - trade.average_price) * position.size
        
        position.realized_pnl = pnl
        position.status = PositionStatus.CLOSED
        position.closed_at = datetime.utcnow()
        
        self.current_capital += (position.size * position.entry_price) + pnl
        self.closed_positions.append(position)
        self.positions.remove(position)
        
        # Update peak
        if self.current_capital > self.peak_capital:
            self.peak_capital = self.current_capital
        
        logger.info(f"✅ Position closed: {trade.market_question}")
        logger.info(f"💵 P&L: ${pnl:.2f}")
        logger.info(f"💰 Current capital: ${self.current_capital:.2f}")
    
    def update_prices(self, price_updates: Dict[str, float]):
        """
        Update current prices for open positions.
        
        Args:
            price_updates: Dict mapping token_id to current price
        """
        for position in self.positions:
            if position.token_id in price_updates:
                position.current_price = price_updates[position.token_id]
                
                # Calculate unrealized P&L
                if position.side == "BUY":
                    position.unrealized_pnl = (
                        position.current_price - position.entry_price
                    ) * position.size
                else:
                    position.unrealized_pnl = (
                        position.entry_price - position.current_price
                    ) * position.size
                
                self.logger.log_position_update(position)
    
    def get_performance_report(self) -> dict:
        """
        Generate comprehensive performance report.
        
        Returns:
            Dict with performance metrics
        """
        total_trades = len(self.closed_positions)
        
        if total_trades == 0:
            return {
                "total_trades": 0,
                "status": "No closed positions yet"
            }
        
        winning_trades = [p for p in self.closed_positions if p.realized_pnl > 0]
        losing_trades = [p for p in self.closed_positions if p.realized_pnl <= 0]
        
        total_pnl = sum(p.realized_pnl for p in self.closed_positions)
        win_rate = (len(winning_trades) / total_trades) * 100
        
        avg_win = sum(p.realized_pnl for p in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(p.realized_pnl for p in losing_trades) / len(losing_trades) if losing_trades else 0
        
        # Calculate drawdown
        drawdown_pct = ((self.peak_capital - self.current_capital) / self.peak_capital) * 100 if self.peak_capital > 0 else 0
        
        # ROI
        roi_pct = ((self.current_capital - self.initial_capital) / self.initial_capital) * 100
        
        report = {
            "initial_capital": self.initial_capital,
            "current_capital": self.current_capital,
            "peak_capital": self.peak_capital,
            "total_pnl": total_pnl,
            "roi_pct": roi_pct,
            "total_trades": total_trades,
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": win_rate,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "profit_factor": abs(avg_win / avg_loss) if avg_loss != 0 else 0,
            "max_drawdown_pct": drawdown_pct,
            "open_positions": len(self.positions),
        }
        
        return report
    
    def print_report(self):
        """Print performance report to console."""
        report = self.get_performance_report()
        
        if report.get("status"):
            logger.info(report["status"])
            return
        
        print("\n" + "="*60)
        print("PAPER TRADING PERFORMANCE REPORT")
        print("="*60)
        print(f"\n💰 Capital")
        print(f"   Initial:  ${report['initial_capital']:,.2f}")
        print(f"   Current:  ${report['current_capital']:,.2f}")
        print(f"   Peak:     ${report['peak_capital']:,.2f}")
        print(f"   P&L:      ${report['total_pnl']:,.2f} ({report['roi_pct']:+.2f}%)")
        
        print(f"\n📊 Trading Statistics")
        print(f"   Total Trades:    {report['total_trades']}")
        print(f"   Winning:         {report['winning_trades']} ({report['win_rate']:.1f}%)")
        print(f"   Losing:          {report['losing_trades']}")
        print(f"   Open Positions:  {report['open_positions']}")
        
        print(f"\n💵 P&L Metrics")
        print(f"   Average Win:     ${report['avg_win']:.2f}")
        print(f"   Average Loss:    ${report['avg_loss']:.2f}")
        print(f"   Profit Factor:   {report['profit_factor']:.2f}")
        
        print(f"\n📉 Risk Metrics")
        print(f"   Max Drawdown:    {report['max_drawdown_pct']:.2f}%")
        
        print("\n" + "="*60 + "\n")
        
        # Save report to file
        report_path = Path("logs/paper/performance_report.json")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump({
                **report,
                "generated_at": datetime.utcnow().isoformat()
            }, f, indent=2)
        
        logger.info(f"Report saved to {report_path}")


