"""
Unit tests for PositionSizer.
"""

import pytest
from execution_engine.position_sizer import PositionSizer
from execution_engine.models import TradingConfig


@pytest.fixture
def position_sizer():
    """Create a position sizer for testing."""
    config = TradingConfig(
        max_position_usd=500,
        min_position_usd=50,
        kelly_fraction=0.25,
    )
    return PositionSizer(config)


class TestPositionSizer:
    """Test PositionSizer functionality."""
    
    def test_kelly_calculation(self, position_sizer):
        """Test basic Kelly criterion calculation."""
        # With 10% edge on a 50% price, expect meaningful position
        size = position_sizer.calculate_size(
            edge=0.10,
            current_price=0.50,
            fair_value=0.60,
            bankroll=2000
        )
        
        assert size >= position_sizer.config.min_position_usd
        assert size <= position_sizer.config.max_position_usd
    
    def test_min_position_floor(self, position_sizer):
        """Test that position size doesn't go below minimum."""
        # Very small edge should still return min position
        size = position_sizer.calculate_size(
            edge=0.001,
            current_price=0.50,
            fair_value=0.501,
            bankroll=2000
        )
        
        assert size == position_sizer.config.min_position_usd
    
    def test_max_position_cap(self, position_sizer):
        """Test that position size doesn't exceed maximum."""
        # Very large edge should cap at max position
        size = position_sizer.calculate_size(
            edge=0.50,
            current_price=0.20,
            fair_value=0.70,
            bankroll=10000
        )
        
        assert size <= position_sizer.config.max_position_usd
    
    def test_signal_based_calculation(self, position_sizer):
        """Test calculation from signal parameters."""
        size = position_sizer.calculate_from_signal(
            current_price=0.30,
            fair_value=0.40,
            mispricing_pct=10.0,
            bankroll=2000
        )
        
        assert size > 0
        assert size >= position_sizer.config.min_position_usd
    
    def test_shares_calculation(self, position_sizer):
        """Test conversion of USD to shares."""
        shares = position_sizer.shares_for_usd(
            usd_amount=100,
            price=0.50
        )
        
        assert shares == 200  # 100 / 0.50 = 200 shares
    
    def test_shares_floor_rounding(self, position_sizer):
        """Test that shares are rounded down (floor)."""
        shares = position_sizer.shares_for_usd(
            usd_amount=100,
            price=0.333
        )
        
        # 100 / 0.333 = 300.3, should floor to 300
        assert shares == 300
    
    def test_zero_price_handling(self, position_sizer):
        """Test that zero price returns zero shares."""
        shares = position_sizer.shares_for_usd(
            usd_amount=100,
            price=0
        )
        
        assert shares == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


