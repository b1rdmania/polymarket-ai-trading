# Mean Reversion Signals

Trading signals based on behavioral finance research — exploiting emotional overreaction in prediction markets.

## The Strategy

Based on Berg & Rietz (2018) and behavioral finance literature:

| Horizon | Bias | Signal |
|---------|------|--------|
| 1-3 weeks | Overconfidence | Buy underpriced longshots, fade overpriced favorites |
| 1-2 days | Efficient | No edge — markets correct near resolution |
| In-play | Emotional spike | Fade large moves after 5-10 min |

## Installation

```bash
pip install -e toolkit/mean-reversion
```

## Quick Start

```python
from mean_reversion import SignalGenerator, SignalConfig

config = SignalConfig(
    min_mispricing_pct=5.0,    # Minimum 5% deviation
    horizon_days=(7, 21),       # 1-3 week sweet spot
    kelly_fraction=0.25         # Quarter Kelly for safety
)

generator = SignalGenerator(config)

# Get current signals
signals = await generator.scan()

for signal in signals:
    print(f"{signal.direction} {signal.market_question}")
    print(f"  Mispricing: {signal.mispricing_pct:+.1f}%")
    print(f"  Position size: ${signal.position_size:.0f}")
```

## CLI Usage

```bash
# Scan for signals
mean-reversion scan --min-mispricing 5

# Analyze specific market
mean-reversion analyze <market_id>

# Backtest on historical data
mean-reversion backtest --data prices.csv
```

## Signal Types

| Signal | Trigger | Action |
|--------|---------|--------|
| `FADE_SPIKE` | Price spiked >10% recently | Bet against the move |
| `BUY_LONGSHOT` | Low-priced contract undervalued | Buy at <30% |
| `SELL_FAVORITE` | High-priced contract overvalued | Sell at >70% |

## License

MIT
