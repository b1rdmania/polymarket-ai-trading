"""
Trade Orchestrator

Main coordinator that runs the trading loop.
"""

import logging
import asyncio
from typing import List, Optional
from datetime import datetime
import sys
import os

# Add toolkit packages to path
toolkit_path = os.path.join(os.path.dirname(__file__), "../../..")
sys.path.insert(0, toolkit_path)

from .models import TradingConfig, Trade, Position, PositionStatus, TradeStatus
from .executor import PolymarketExecutor
from .risk_manager import RiskManager
from .position_sizer import PositionSizer
from .trade_logger import TradeLogger
from .data_recorder import MarketDataRecorder

logger = logging.getLogger(__name__)


class TradeOrchestrator:
    """
    Main trading coordinator.
    
    Responsibilities:
    1. Scan for signals from all sources
    2. Apply risk checks
    3. Size positions using Kelly criterion
    4. Execute approved trades
    5. Monitor open positions
    6. Log everything
    """
    
    def __init__(self, config: TradingConfig):
        self.config = config
        self.executor = PolymarketExecutor(config)
        self.risk_manager = RiskManager(config)
        self.position_sizer = PositionSizer(config)
        self.trade_logger = TradeLogger()
        self.data_recorder = MarketDataRecorder()  # NEW: Record live data
        
        self.positions: List[Position] = []
        self.bankroll = config.max_total_exposure_usd  # Initial bankroll
        self.is_running = False
        
        logger.info(f"TradeOrchestrator initialized in {config.mode.value} mode")
        logger.info("Data recording enabled for backtesting")
    
    async def run_forever(self):
        """Run the trading loop continuously."""
        self.is_running = True
        logger.info("Starting trading loop...")
        
        try:
            while self.is_running:
                await self._trading_cycle()
                await asyncio.sleep(self.config.check_interval_seconds)
        except KeyboardInterrupt:
            logger.info("Trading loop interrupted by user")
        except Exception as e:
            logger.error(f"Trading loop crashed: {e}")
            raise
        finally:
            await self.shutdown()
    
    async def _trading_cycle(self):
        """Execute one cycle of the trading loop."""
        try:
            logger.info("=== Trading Cycle Start ===")
            
            # Check for emergency stop
            if self.risk_manager.should_emergency_stop():
                logger.critical("EMERGENCY STOP TRIGGERED")
                await self._close_all_positions()
                self.is_running = False
                return
            
            # Update positions
            await self._update_positions()
            
            # Scan for signals
            signals = await self._scan_signals()
            logger.info(f"Found {len(signals)} signals")
            
            # Process each signal
            for signal in signals:
                await self._process_signal(signal)
            
            # Check stop losses / take profits
            await self._check_exits()
            
            logger.info("=== Trading Cycle Complete ===\n")
            
        except Exception as e:
            logger.error(f"Error in trading cycle: {e}")
    
    async def _scan_signals(self) -> List:
        """
        Scan all signal sources.
        
        Returns list of Signal objects from:
        - Mean reversion generator
        - Volatility monitor
        - Whale tracker
        """
        signals = []
        
        try:
            # Import signal generators
            from mean_reversion import SignalGenerator, SignalConfig
            
            # Scan mean reversion signals
            generator = SignalGenerator(SignalConfig())
            mr_signals = await generator.scan(limit=20)
            signals.extend(mr_signals)
            
            logger.info(f"Mean reversion: {len(mr_signals)} signals")
            
        except Exception as e:
            logger.error(f"Failed to scan signals: {e}")
        
        return signals
    
    async def _process_signal(self, signal):
        """
        Process a single signal.
        
        Steps:
        1. Check if already have position in this market
        2. Calculate position size
        3. Run risk checks
        4. Execute if approved
        5. Log everything
        6. Record market data for backtesting
        """
        
        # Check if we already have a position
        existing = [p for p in self.positions if p.market_id == signal.market_id and p.status == PositionStatus.OPEN]
        if existing:
            logger.debug(f"Already have position in {signal.market_question}")
            return
        
        # Get current spread (would query API in real implementation)
        current_spread = 2.0  # Mock value
        
        # Record market data for future backtesting
        orderbook_data = {
            'best_bid': signal.current_price * (1 - current_spread/200),  # Estimate
            'best_ask': signal.current_price * (1 + current_spread/200),  # Estimate
            'spread_pct': current_spread,
            'volume_24h': 0,  # Would get from API
        }
        self.data_recorder.record_signal_context(signal, orderbook_data)
        
        # Calculate position size
        position_size_usd = self.position_sizer.calculate_from_signal(
            current_price=signal.current_price,
            fair_value=signal.fair_value_estimate,
            mispricing_pct=signal.mispricing_pct,
            bankroll=self.bankroll
        )
        
        # Run risk checks
        risk_check = self.risk_manager.check_trade(
            size_usd=position_size_usd,
            positions=self.positions,
            current_spread_pct=current_spread
        )
        
        if not risk_check.passed:
            logger.info(f"Risk check failed: {risk_check.reason}")
            self.trade_logger.log_signal(signal, rejected=True, reason=risk_check.reason)
            return
        
        # Create trade
        shares = self.position_sizer.shares_for_usd(position_size_usd, signal.current_price)
        
        trade = Trade(
            market_id=signal.market_id,
            market_question=signal.market_question,
            token_id=signal.token_id,
            side="BUY" if signal.direction.value == "BUY" else "SELL",
            size=shares,
            price=signal.current_price,
            value_usd=shares * signal.current_price,
            signal_id=signal.id,
            signal_type=signal.type.value,
            signal_strength=signal.strength.value,
        )
        
        # Execute trade
        result = await self.executor.execute_trade(trade)
        
        # Record execution quality (lesson from @the_smart_ape)
        if result.success and trade.metadata:
            self.data_recorder.record_execution(
                trade=trade,
                actual_price=trade.metadata.get('actual_price', trade.price),
                expected_price=trade.metadata.get('expected_price', trade.price),
                slippage_pct=trade.metadata.get('slippage_pct', 0)
            )
        
        # Log execution
        self.trade_logger.log_trade(trade, result)
        
        if result.success:
            # Create position
            position = Position(
                trade_id=trade.id,
                market_id=trade.market_id,
                market_question=trade.market_question,
                token_id=trade.token_id,
                side=trade.side,
                size=trade.filled_size,
                entry_price=trade.average_price,
                current_price=trade.average_price,
            )
            self.positions.append(position)
            logger.info(f"✅ Position opened: {trade.market_question}")
        else:
            logger.warning(f"❌ Trade failed: {result.error}")
    
    async def _update_positions(self):
        """Update prices and P&L for all open positions."""
        for position in self.positions:
            if position.status == PositionStatus.OPEN:
                # Would query current price from API
                # For now, keep same
                position.unrealized_pnl = (position.current_price - position.entry_price) * position.size
                self.trade_logger.log_position_update(position)
    
    async def _check_exits(self):
        """Check stop losses and take profits."""
        for position in self.positions:
            if position.status != PositionStatus.OPEN:
                continue
            
            # Check stop loss
            if position.stop_loss and position.current_price <= position.stop_loss:
                logger.info(f"Stop loss hit for {position.market_question}")
                await self._close_position(position, reason="stop_loss")
            
            # Check take profit
            if position.take_profit and position.current_price >= position.take_profit:
                logger.info(f"Take profit hit for {position.market_question}")
                await self._close_position(position, reason="take_profit")
    
    async def _close_position(self, position: Position, reason: str = "manual"):
        """Close a position."""
        logger.info(f"Closing position: {position.market_question} (reason: {reason})")
        
        # Create closing trade
        trade = Trade(
            market_id=position.market_id,
            market_question=position.market_question,
            token_id=position.token_id,
            side="SELL" if position.side == "BUY" else "BUY",
            size=position.size,
            price=position.current_price,
            value_usd=position.size * position.current_price,
        )
        
        result = await self.executor.execute_trade(trade)
        
        if result.success:
            position.status = PositionStatus.CLOSED
            position.closed_at = datetime.utcnow()
            position.realized_pnl = position.unrealized_pnl
            logger.info(f"Position closed. P&L: ${position.realized_pnl:.2f}")
    
    async def _close_all_positions(self):
        """Emergency: close all open positions."""
        logger.warning("Closing all positions...")
        for position in self.positions:
            if position.status == PositionStatus.OPEN:
                await self._close_position(position, reason="emergency_stop")
    
    async def shutdown(self):
        """Graceful shutdown."""
        logger.info("Shutting down...")
        self.is_running = False
        # Could save state here
        logger.info("Shutdown complete")

