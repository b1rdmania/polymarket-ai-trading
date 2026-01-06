"""
Unit tests for RiskManager.
"""

import pytest
from datetime import datetime
from execution_engine.risk_manager import RiskManager
from execution_engine.models import TradingConfig, Position, PositionStatus


@pytest.fixture
def risk_manager():
    """Create a risk manager for testing."""
    config = TradingConfig(
        max_position_usd=500,
        max_total_exposure_usd=2000,
        max_positions=10,
        max_drawdown_pct=25.0,
        max_spread_pct=5.0,
    )
    return RiskManager(config)


@pytest.fixture
def sample_positions():
    """Create sample positions for testing."""
    return [
        Position(
            market_id="market1",
            market_question="Test Market 1",
            token_id="token1",
            side="BUY",
            size=100,
            entry_price=0.50,
            current_price=0.55,
            status=PositionStatus.OPEN,
        ),
        Position(
            market_id="market2",
            market_question="Test Market 2",
            token_id="token2",
            side="BUY",
            size=200,
            entry_price=0.30,
            current_price=0.32,
            status=PositionStatus.OPEN,
        ),
    ]


class TestRiskManager:
    """Test RiskManager functionality."""
    
    def test_position_size_limit(self, risk_manager):
        """Test that position size limits are enforced."""
        # Should reject oversized position
        result = risk_manager.check_trade(
            size_usd=600,  # Exceeds max of 500
            positions=[],
            current_spread_pct=2.0
        )
        
        assert result.passed == False
        assert "exceeds max" in result.reason.lower()
        assert result.max_size_allowed == 500
    
    def test_minimum_position_size(self, risk_manager):
        """Test that minimum position size is enforced."""
        result = risk_manager.check_trade(
            size_usd=10,  # Below min of 50
            positions=[],
            current_spread_pct=2.0
        )
        
        assert result.passed == False
        assert "below minimum" in result.reason.lower()
    
    def test_total_exposure_limit(self, risk_manager, sample_positions):
        """Test that total exposure limits are enforced."""
        # Existing exposure is 50 + 60 = 110
        # Trying to add 1900 more would exceed 2000 limit
        result = risk_manager.check_trade(
            size_usd=1900,
            positions=sample_positions,
            current_spread_pct=2.0
        )
        
        assert result.passed == False
        assert "total exposure" in result.reason.lower()
    
    def test_max_positions_limit(self, risk_manager):
        """Test that max positions limit is enforced."""
        # Create 10 open positions
        positions = [
            Position(
                market_id=f"market{i}",
                market_question=f"Test {i}",
                token_id=f"token{i}",
                side="BUY",
                size=10,
                entry_price=0.5,
                current_price=0.5,
                status=PositionStatus.OPEN,
            )
            for i in range(10)
        ]
        
        result = risk_manager.check_trade(
            size_usd=100,
            positions=positions,
            current_spread_pct=2.0
        )
        
        assert result.passed == False
        assert "max" in result.reason.lower()
        assert "position" in result.reason.lower()
    
    def test_spread_check(self, risk_manager):
        """Test that wide spreads are rejected."""
        result = risk_manager.check_trade(
            size_usd=100,
            positions=[],
            current_spread_pct=6.0  # Exceeds max of 5%
        )
        
        assert result.passed == False
        assert "spread" in result.reason.lower()
    
    def test_valid_trade(self, risk_manager):
        """Test that valid trade passes all checks."""
        result = risk_manager.check_trade(
            size_usd=200,
            positions=[],
            current_spread_pct=2.0
        )
        
        assert result.passed == True
        assert result.can_proceed == True
        assert result.max_size_allowed == 200
    
    def test_drawdown_calculation(self, risk_manager):
        """Test drawdown tracking."""
        risk_manager.update_equity(1000)
        assert risk_manager.peak_equity == 1000
        
        risk_manager.update_equity(750)  # 25% drawdown
        assert risk_manager.should_emergency_stop() == True
    
    def test_peak_equity_tracking(self, risk_manager):
        """Test that peak equity is tracked correctly."""
        risk_manager.update_equity(1000)
        risk_manager.update_equity(1200)
        risk_manager.update_equity(1100)
        
        assert risk_manager.peak_equity == 1200
    
    def test_daily_pnl_tracking(self, risk_manager):
        """Test daily P&L tracking."""
        risk_manager.update_daily_pnl(-50)
        risk_manager.update_daily_pnl(-100)
        
        assert risk_manager.daily_pnl == -150


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


