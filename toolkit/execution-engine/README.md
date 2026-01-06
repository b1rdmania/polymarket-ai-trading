# Execution Engine

Trade execution layer for systematic Polymarket trading strategies.

## Overview

This package bridges your signal generation (mean reversion, volatility, whale tracking) with actual trade execution via the Polymarket Agents framework.

## Components

- **Orchestrator**: Main coordinator that runs the trading loop
- **Executor**: Wrapper around Polymarket Agents for trade execution
- **Risk Manager**: Enforces position limits and exposure rules
- **Position Sizer**: Implements Kelly criterion for optimal sizing
- **Paper Trader**: Simulates trades without real money
- **Trade Logger**: Comprehensive logging to SQLite and JSON

## Installation

```bash
cd toolkit/execution-engine
pip install -e .
```

## Usage

### Paper Trading (Recommended First Step)

```python
from execution_engine import TradeOrchestrator, TradingConfig

config = TradingConfig(
    mode="paper",
    max_position_usd=500,
    max_total_exposure_usd=2000,
    kelly_fraction=0.25,
)

orchestrator = TradeOrchestrator(config)
await orchestrator.run_forever()
```

### Live Trading

```python
config = TradingConfig(
    mode="live",
    # ... same config ...
)
```

## Configuration

Edit `config/trading.yaml` to adjust:
- Position limits
- Risk parameters
- Signal sources
- Execution settings

## Safety Features

- Hard position limits enforced in code
- Spread threshold checks
- Maximum drawdown monitoring
- Emergency stop mechanism


