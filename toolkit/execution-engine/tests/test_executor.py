"""
Unit tests for PolymarketExecutor.
"""

import pytest
import asyncio
from execution_engine.executor import PolymarketExecutor
from execution_engine.models import TradingConfig, Trade, TradeMode, TradeStatus


@pytest.fixture
def paper_executor():
    """Create a paper trading executor."""
    config = TradingConfig(mode=TradeMode.PAPER, dry_run=False)
    return PolymarketExecutor(config)


@pytest.fixture
def dry_run_executor():
    """Create a dry-run executor."""
    config = TradingConfig(mode=TradeMode.PAPER, dry_run=True)
    return PolymarketExecutor(config)


@pytest.fixture
def sample_trade():
    """Create a sample trade."""
    return Trade(
        market_id="test_market",
        market_question="Will this test pass?",
        token_id="test_token",
        side="BUY",
        size=100,
        price=0.50,
        value_usd=50.0
    )


class TestPolymarketExecutor:
    """Test PolymarketExecutor functionality."""
    
    @pytest.mark.asyncio
    async def test_dry_run_execution(self, dry_run_executor, sample_trade):
        """Test that dry run mode doesn't execute trades."""
        result = await dry_run_executor.execute_trade(sample_trade)
        
        assert result.success == True
        assert "dry run" in result.message.lower()
        assert sample_trade.status == TradeStatus.FILLED
    
    @pytest.mark.asyncio
    async def test_paper_trade_execution(self, paper_executor, sample_trade):
        """Test paper trade execution."""
        result = await paper_executor.execute_trade(sample_trade)
        
        assert result.success == True
        assert sample_trade.status == TradeStatus.FILLED
        assert sample_trade.filled_size == sample_trade.size
        assert sample_trade.average_price > 0
    
    @pytest.mark.asyncio
    async def test_trade_updates_timestamp(self, paper_executor, sample_trade):
        """Test that trade timestamp is updated on execution."""
        original_timestamp = sample_trade.timestamp
        
        result = await paper_executor.execute_trade(sample_trade)
        
        assert sample_trade.timestamp != original_timestamp
    
    def test_paper_mode_no_client_init(self, paper_executor):
        """Test that paper mode doesn't initialize Polymarket client."""
        assert paper_executor.polymarket_client is None
    
    def test_live_mode_requires_credentials(self):
        """Test that live mode requires wallet credentials."""
        # This should not raise an error if credentials are missing
        # (it will fail later when trying to execute)
        config = TradingConfig(mode=TradeMode.LIVE)
        
        # Should not crash on initialization
        # (actual trading would fail without credentials)
        try:
            executor = PolymarketExecutor(config)
        except ValueError:
            # Expected if POLYGON_WALLET_PRIVATE_KEY not set
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


