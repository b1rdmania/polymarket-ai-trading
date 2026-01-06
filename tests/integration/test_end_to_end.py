"""
End-to-end integration tests.

Tests the complete flow from signal generation to trade execution.
"""

import pytest
import asyncio
import json
from pathlib import Path

from execution_engine import TradeOrchestrator, TradingConfig, TradeMode
from execution_engine.models import Position, PositionStatus


@pytest.fixture
def test_config():
    """Create test configuration."""
    return TradingConfig(
        mode=TradeMode.PAPER,
        max_position_usd=500,
        max_total_exposure_usd=2000,
        kelly_fraction=0.25,
        dry_run=False,
    )


@pytest.fixture
def orchestrator(test_config):
    """Create orchestrator for testing."""
    return TradeOrchestrator(test_config)


class TestEndToEnd:
    """End-to-end integration tests."""
    
    @pytest.mark.asyncio
    async def test_complete_trading_cycle(self, orchestrator):
        """Test a complete trading cycle."""
        # This would run a full cycle in test mode
        # For now, just verify orchestrator can be created
        assert orchestrator is not None
        assert orchestrator.is_running == False
    
    @pytest.mark.asyncio
    async def test_signal_to_execution_flow(self, orchestrator):
        """Test flow from signal generation to execution."""
        # Mock a signal
        from mean_reversion.models import Signal, SignalType, SignalDirection, SignalStrength
        
        mock_signal = Signal(
            id="test_signal_1",
            type=SignalType.BUY_LONGSHOT,
            direction=SignalDirection.BUY,
            strength=SignalStrength.STRONG,
            market_id="test_market",
            market_question="Test market?",
            market_slug="test",
            token_id="0x123",
            current_price=0.25,
            fair_value_estimate=0.35,
            mispricing_pct=10.0,
            edge_estimate=0.10,
            kelly_size=300,
            position_size=250,
            horizon_days=14,
            rationale="Test signal"
        )
        
        # Process the signal
        await orchestrator._process_signal(mock_signal)
        
        # Check that position was created
        assert len(orchestrator.positions) > 0
        position = orchestrator.positions[0]
        assert position.market_id == "test_market"
        assert position.status == PositionStatus.OPEN
    
    @pytest.mark.asyncio
    async def test_risk_rejection(self, orchestrator):
        """Test that risky trades are rejected."""
        from mean_reversion.models import Signal, SignalType, SignalDirection, SignalStrength
        
        # Create signal with very large position
        risky_signal = Signal(
            id="risky_signal",
            type=SignalType.BUY_LONGSHOT,
            direction=SignalDirection.BUY,
            strength=SignalStrength.STRONG,
            market_id="risky_market",
            market_question="Risky market?",
            market_slug="risky",
            token_id="0x456",
            current_price=0.25,
            fair_value_estimate=0.35,
            mispricing_pct=10.0,
            edge_estimate=0.10,
            kelly_size=3000,  # Way too large
            position_size=3000,
            horizon_days=14,
            rationale="Risky test signal"
        )
        
        initial_positions = len(orchestrator.positions)
        await orchestrator._process_signal(risky_signal)
        
        # Position count should not increase (trade rejected)
        assert len(orchestrator.positions) == initial_positions
    
    @pytest.mark.asyncio
    async def test_position_update(self, orchestrator):
        """Test that positions are updated correctly."""
        # Create a test position
        position = Position(
            market_id="test",
            market_question="Test?",
            token_id="0x123",
            side="BUY",
            size=100,
            entry_price=0.50,
            current_price=0.50,
            status=PositionStatus.OPEN,
        )
        
        orchestrator.positions.append(position)
        
        # Update positions
        await orchestrator._update_positions()
        
        # Verify position still exists
        assert len(orchestrator.positions) == 1
    
    def test_logger_initialization(self, orchestrator):
        """Test that logging is properly initialized."""
        assert orchestrator.trade_logger is not None
    
    def test_risk_manager_initialization(self, orchestrator):
        """Test that risk manager is properly initialized."""
        assert orchestrator.risk_manager is not None
    
    def test_position_sizer_initialization(self, orchestrator):
        """Test that position sizer is properly initialized."""
        assert orchestrator.position_sizer is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


