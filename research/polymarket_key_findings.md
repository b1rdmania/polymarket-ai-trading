# Polymarket Research: Key Findings

## 1. Top Traders / Whales (2024 Data)

| Trader | Net Profit | Notes |
|--------|------------|-------|
| **Theo4** | $22M+ | Highest known individual profit |
| **Fredi9999** | $16M+ | Large election bets |
| **"French Whale"** | $80M+ | Anonymous, wagered $30M+ on Trump |
| **PrincessCaro** | $6.1M | Multiple accounts suspected |
| **walletmobile** | $5.9M | |
| **BetTom42** | $5.6M | |
| **mikatrade77** | $5.1M | |
| **alexmulti** | $4.8M | |
| **GCottrell93** | $4.2M | |
| **Jenzigo** | $4M+ | |

### Key Statistic
- **86.4% of users lost money**
- Only 13.6% profitable
- Most winners made <$100

**Implication:** The edge exists, but it's concentrated in the top traders. The question is: what do they know?

---

## 2. Adjacent News API

### Free Tier Limitations
- Markets less than 1 day old only
- Max 100 markets per query
- Price history requires paid API key

### Paid Tier Gives
- **Full OHLCV price history** — this is what we need for backtesting
- Multi-platform (Polymarket, Kalshi, Metaculus)
- News-to-market linking
- Custom indices

**Next Step:** Contact lucas@adj.news for API access pricing

---

## 3. Ecosystem Summary

| Tool | What It Does | Access |
|------|--------------|--------|
| **Polymarket API** | Real-time prices, no history | Free |
| **Adjacent API** | History + news | Paid for history |
| **PredictFolio** | Whale tracking | Free (web scrape) |
| **Nevua Markets** | Alerts | Free (Telegram/Discord) |
| **PolyFund** | Managed funds | Free to use |
| **Dune Analytics** | On-chain trades | Free (SQL queries) |

---

## 4. Research Gaps Remaining

| Gap | How to Fill |
|-----|-------------|
| Historical price data | Adjacent API (paid) or Dune |
| News-to-price causation | Adjacent API or manual study |
| Whale behavior patterns | PredictFolio + on-chain analysis |
| Volatility mean-reversion proof | Need historical data to backtest |

---

## 5. Next Actions

### Immediate (Free)
- [ ] Set up Nevua alerts for >10% price moves
- [ ] Start logging Polymarket prices manually
- [ ] Query Dune for on-chain trade data
- [ ] Study top trader profiles on PredictFolio

### Requires Investment
- [ ] Get Adjacent API key ($TBD)
- [ ] Build historical database
- [ ] Run backtests on volatility strategy

### Longer Term
- [ ] Build automated volatility detector
- [ ] Paper trade for 30 days
- [ ] Launch PolyFund if strategy works

---

## 6. The Core Insight

Most people lose on Polymarket. The winners are:
1. **Whales** with information/conviction (French Whale on Trump)
2. **Systematic traders** who trade volatility, not outcomes
3. **Market makers** who profit from spreads

We're targeting #2 — systematic volatility trading based on behavioral biases.

The Berg & Rietz + Munger framework gives us the theory.
The Adjacent API + Dune gives us the data.
The Nevua alerts give us the signals.

We just need to connect them.
