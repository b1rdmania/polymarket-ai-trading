# Polymarket Ecosystem Deep Dive

## Overview

The Polymarket ecosystem has grown beyond just the core platform. Third-party tools provide analytics, fund management, news aggregation, and alerts that the main platform doesn't offer. These are critical for building our edge.

---

## 1. Adjacent News (adj.news)

**What it is:** "Forward Looking News" — a news platform specifically designed around prediction markets.

### Key Features

| Feature | Description | Our Use Case |
|---------|-------------|--------------|
| **Daily Briefs** | Morning briefings connecting news to market movements | Context for price moves |
| **API** | Comprehensive market + news API | Data source for our bot |
| **Indices** | Aggregated prediction market indices (e.g., UPFI) | Track broad market sentiment |
| **Chrome Extension** | Real-time market overlays | Quick market checks |
| **Observable Notebooks** | Data visualization tools | Research & analysis |

### Adjacent API Capabilities (docs.adj.news)

```
Markets API:
- Multi-platform (Kalshi, Polymarket, Metaculus)
- Real-time probability updates
- Advanced filtering & sorting
- Historical price data with OHLCV format 🔥

Search API:
- Semantic/AI-powered search
- Natural language queries
- Vector embeddings for similarity

News API:
- AI-powered news discovery
- News articles linked to specific markets
- Freshness control

Trade API:
- Real-time trades
- Price history
- Volume & liquidity stats
```

**🔥 Key Finding:** Adjacent API has **historical price data with OHLCV format** — this might solve our backtest data problem!

### Links
- Website: https://adj.news
- API Docs: https://docs.adj.news
- Telegram: https://t.me/AdjacentNews
- Chrome Extension: Available in Chrome Web Store

---

## 2. PredictFolio (predictfolio.com)

**What it is:** Portfolio analytics and trader tracking platform for Polymarket.

### Key Features

| Feature | Description | Our Use Case |
|---------|-------------|--------------|
| **Trader Leaderboard** | Top traders by PnL, win rate | Find smart money to follow |
| **Profile Analysis** | Deep dive into any wallet | Study winning strategies |
| **Performance Tracking** | Track your own portfolio | Measure our edge |
| **Wallet Search** | Search millions of traders | Identify whale behavior |
| **5 Years of Data** | Historical Polymarket data | Backtest material |

### Notable Stats
- **1M+** active Polymarket users tracked
- **30,000+** open markets tracked
- **5 years** of historical data

### Top Trader Example
- **Scottilicious**: $52M volume, ~$996k PnL
- This is the caliber of trader we should study

### Links
- Website: https://predictfolio.com
- Leaderboard: https://predictfolio.com/leaderboard
- Discord: https://discord.gg/polyalpha

---

## 3. PolyFund (polyfund.so)

**What it is:** Decentralized fund management platform built on Polymarket.

### How It Works

```
1. Predictor (fund manager) creates a fund
2. Sets performance fee (e.g., 20% of profits)
3. Investors deposit USDC
4. Predictor trades on Polymarket with pooled capital
5. Profits split according to performance fee
6. Fully on-chain, permissionless
```

### Key Concepts

| Term | Definition |
|------|------------|
| **Predictor** | Fund manager with trading expertise |
| **Depositor** | Investor who contributes capital |
| **Performance Fee** | % of profits paid to predictor |
| **Fund Isolation** | Funds can ONLY be used for Polymarket trades |

### Our Use Case

**Option A: Become a Predictor**
- Create a public fund
- Let others deposit capital
- Trade with our strategy
- Earn performance fee on profits

**Option B: Research Top Predictors**
- Study which funds are profitable
- Reverse-engineer their strategies
- Apply to our own trading

### Links
- Website: https://polyfund.so
- Docs: https://docs.polyfund.so
- Discord: https://discord.polyfund.so

---

## 4. Nevua Markets (nevua.markets)

**What it is:** Watchlist and alert system for Polymarket.

### Key Features

| Feature | Description | Our Use Case |
|---------|-------------|--------------|
| **Watchlists** | Track specific markets | Monitor opportunities |
| **Real-time Alerts** | Price movement notifications | Detect volatility |
| **Multi-channel** | Telegram, Discord, Webhooks | Integration with our bot |

### Alert Types (Likely)
- Price crosses threshold
- Volume spike
- Market created/closed
- Large trades

**This is exactly what we need** — real-time alerts for volatility detection.

### Links
- Website: https://nevua.markets

---

## Ecosystem Map

```
                    ┌─────────────────┐
                    │   POLYMARKET    │
                    │  (Core Platform) │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│   Adjacent    │  │  PredictFolio │  │    PolyFund   │
│   (News API)  │  │  (Analytics)  │  │   (Funds)     │
└───────────────┘  └───────────────┘  └───────────────┘
        │                    │                    
        │                    │                    
        ▼                    ▼                    
┌───────────────┐  ┌───────────────┐  
│  Nevua        │  │  Dune         │  
│  (Alerts)     │  │  (On-chain)   │  
└───────────────┘  └───────────────┘  
```

---

## What This Means For Us

### Data Sources Unlocked

| Need | Solution |
|------|----------|
| Historical prices | Adjacent API (OHLCV format) |
| Whale tracking | PredictFolio leaderboard |
| Real-time alerts | Nevua Markets webhooks |
| News-to-price | Adjacent News API |
| Trade-level data | Dune Analytics (on-chain) |

### Immediate Actions

1. **Test Adjacent API** — see if we can get historical price data
2. **Study PredictFolio leaderboard** — identify top traders to analyze
3. **Set up Nevua alerts** — get notified of big price moves
4. **Consider PolyFund** — if our strategy works, we could manage capital

---

## Next Steps

- [ ] Get Adjacent API access and test historical data endpoint
- [ ] Pull top 10 traders from PredictFolio, study their patterns
- [ ] Set up Nevua alerts for >10% moves
- [ ] Check if Adjacent has news-to-price causation data
