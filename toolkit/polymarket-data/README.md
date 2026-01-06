# Polymarket Data Fetcher

Read-only Python library for fetching Polymarket data without authentication.

## Features

- ✅ Market search by keyword, category, event
- ✅ Trending markets by 24h/7d/30d volume
- ✅ Price and orderbook data
- ✅ Markets closing soon
- ✅ Rate limiting built-in
- ✅ No API keys required

## Installation

```bash
pip install -e toolkit/polymarket-data
```

## Quick Start

```python
from polymarket_data import PolymarketClient

client = PolymarketClient()

# Search markets
markets = await client.search("trump")

# Get trending
trending = await client.get_trending(timeframe="24h", limit=10)

# Get market details
market = await client.get_market("will-trump-win-2024")

# Get orderbook
orderbook = await client.get_orderbook(token_id="...")
```

## CLI Usage

```bash
# Search markets
polymarket search "bitcoin"

# Get trending
polymarket trending --timeframe 24h --limit 10

# Monitor price
polymarket watch <market_id> --interval 60
```

## API Reference

See [docs/api.md](docs/api.md) for full API reference.

## License

MIT
