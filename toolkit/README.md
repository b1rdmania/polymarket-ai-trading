# Prediction Market Toolkit

Modular, open-source tools for prediction market research and trading.

## Components

| Tool | Description | Status |
|------|-------------|--------|
| [polymarket-data](./polymarket-data/) | Read-only Polymarket data fetcher | ✅ Ready |
| [volatility-alerts](./volatility-alerts/) | Price movement detection & alerts | ✅ Ready |
| [mean-reversion](./mean-reversion/) | Mean reversion signal generator | ✅ Ready |
| [whale-tracker](./whale-tracker/) | Large trade monitoring | ✅ Ready |

## Quick Start

```bash
# Clone the repo
git clone https://github.com/b1rdmania/aztec-auction-analysis.git
cd aztec-analysis/toolkit

# Install all tools
pip install -e polymarket-data
pip install -e volatility-alerts
pip install -e mean-reversion
pip install -e whale-tracker

# Use CLIs
polymarket trending --timeframe 24h
polymarket movers --threshold 10

volatility-alert trending --threshold 5

mean-reversion scan --min-mispricing 5

whale-tracker large-trades --min-size 1000
```

## No API Keys Required

All tools work with public APIs only. No authentication needed for read-only data.

## Architecture

```
toolkit/
├── polymarket-data/      # Data fetching layer
├── volatility-alerts/    # Real-time monitoring
├── mean-reversion/       # Trading signals
└── whale-tracker/        # Smart money tracking
```

## License

MIT
