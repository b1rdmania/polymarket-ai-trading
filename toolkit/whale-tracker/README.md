# Whale Tracker

Monitor large trades and smart money wallets on Polymarket.

## Features

- ✅ Large trade detection (>$X threshold)
- ✅ Wallet watchlist monitoring
- ✅ Top trader tracking (via PredictFolio)
- ✅ Trade flow analysis
- ✅ Alert on whale activity

## Installation

```bash
pip install -e toolkit/whale-tracker
```

## Quick Start

```python
from whale_tracker import WhaleMonitor, WatchlistConfig

config = WatchlistConfig(
    min_trade_size=1000,    # Alert on trades >$1000
    wallets=[               # Specific wallets to watch
        "0xabc...",
        "0xdef..."
    ]
)

monitor = WhaleMonitor(config)

# Get recent large trades
trades = await monitor.get_large_trades(hours=24)

# Track a specific wallet
activity = await monitor.track_wallet("0xabc...")
```

## CLI Usage

```bash
# Find large trades
whale-tracker large-trades --min-size 1000 --hours 24

# Watch specific wallet
whale-tracker watch 0xabc123...

# Get top traders from PredictFolio
whale-tracker top-traders --limit 10
```

## Data Sources

| Source | Data | Auth Required |
|--------|------|---------------|
| Polymarket API | Market data | No |
| Polygon RPC | On-chain trades | No |
| PredictFolio | Top traders | No |
| Dune Analytics | Historical data | API key |

## License

MIT
