# Volatility Alerts

Real-time price movement detection and alerting for Polymarket.

## Features

- ✅ Threshold alerts (>X% moves)
- ✅ Volume spike detection
- ✅ Spread widening alerts
- ✅ Multiple output channels (console, webhook, file)
- ✅ Configurable watchlists
- ✅ Background monitoring

## Installation

```bash
pip install -e toolkit/volatility-alerts
```

## Quick Start

```python
from volatility_alerts import AlertMonitor, AlertConfig

# Configure alerts
config = AlertConfig(
    price_threshold_pct=10.0,    # Alert on >10% moves
    check_interval_sec=60,        # Check every minute
    markets=["trump", "bitcoin"]  # Markets to watch (keywords)
)

# Start monitoring
monitor = AlertMonitor(config)
monitor.add_handler(console_handler)  # Print to console
monitor.add_handler(webhook_handler)  # POST to webhook

await monitor.start()
```

## CLI Usage

```bash
# Monitor specific markets
volatility-alert watch "trump" "bitcoin" --threshold 10

# Monitor all trending markets
volatility-alert trending --threshold 5

# Monitor and send to webhook
volatility-alert watch "trump" --webhook https://your-webhook.com
```

## Alert Types

| Alert | Trigger | Use Case |
|-------|---------|----------|
| `PRICE_SPIKE` | Price moves >X% | Emotional overreaction |
| `VOLUME_SURGE` | Volume >3x average | Increased interest |
| `SPREAD_WIDE` | Spread >5% | Liquidity thinning |
| `CLOSING_SOON` | <24h to resolution | Near-resolution efficiency |

## License

MIT
