# Polymarket Data Research Summary

## What Data Is Available?

### ✅ Available
| Data | API Endpoint | Notes |
|------|--------------|-------|
| **Current markets** | `gamma-api.polymarket.com/markets` | 500+ markets |
| **Current prices** | Via markets endpoint | Real-time |
| **Volume & liquidity** | Via markets endpoint | Cumulative |
| **Price history (ACTIVE)** | `clob.polymarket.com/prices-history?market={tokenId}` | Works for open markets |
| **Real-time WebSocket** | `real-time-data-client` library | Live trades, price changes |

### ❌ Not Available (Purged)
| Data | Issue |
|------|-------|
| **Price history (CLOSED)** | Returns empty array — historical data is deleted |
| **Trade-by-trade history** | Not exposed via public API |
| **Order book snapshots** | Not available historically |

---

## Key Finding: Historical Data Is Gone

We cannot backtest on closed markets like:
- Trump 2020 ($30M volume)
- Biden inauguration ($8.5M volume)  
- COVID vaccine milestones ($7M volume)

**The price history endpoint returns `{"history": []}` for all closed markets.**

---

## Options Moving Forward

### Option 1: Build Our Own Dataset (From Now)
- Start logging price data for all active markets today
- In 30-60 days, we'll have our own historical dataset
- Can backtest on markets that close in that period

### Option 2: Find Alternative Data Sources
- **Dune Analytics**: May have on-chain trade data
- **The Graph**: Polymarket subgraph might have historical data
- **Archive.org / Wayback**: Might have cached API responses
- **Academic datasets**: Researchers may have collected historical data

### Option 3: Sports Markets (In-Game)
- Sports markets with live odds adjustments might still be active
- Could capture real-time volatility during games
- Example: Goal scored → odds spike → mean reversion

### Option 4: Study Current Volatility
- Don't backtest — study live markets
- Wait for the next big news event
- Manually track price movements in real-time

---

## What We CAN Do Now

1. **Start Logging Active Markets**
   - Run a cron job every minute
   - Store: timestamp, market, price, volume
   - Build our own dataset for future use

2. **Set Up Real-Time Alerts**
   - WebSocket connection to Polymarket
   - Alert when any market moves >10% in 1 hour
   - Study the events that cause moves

3. **Manual Case Studies**
   - Next time a big event happens (Fed meeting, election, etc.)
   - Manually track prices before/during/after
   - Document the volatility pattern

---

## Next Steps

- [ ] Set up price logging cron job
- [ ] Test WebSocket for real-time data
- [ ] Check Dune Analytics for on-chain data
- [ ] Research academic datasets on prediction markets
- [ ] Wait for next major event to study live

---

## Appendix: High-Volume Closed Markets (For Reference)

| Market | Volume | Notes |
|--------|--------|-------|
| Trump 2020 inauguration | $30.2M | No price history |
| Trump win 2020 | $10.8M | No price history |
| Biden inauguration | $8.6M | No price history |
| 100M COVID vaccines | $7.1M | No price history |
| BTC $20k 2021 | $1.5M | No price history |
| Arizona 2020 | $1.5M | No price history |
| Pennsylvania 2020 | $1.4M | No price history |
