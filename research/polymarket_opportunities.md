# Polymarket Opportunities Scanner

**Based on Berg & Rietz (2018) "Longshots, Overconfidence and Efficiency"**

> At intermediate horizons, low-priced contracts (5-20c) are systematically **underpriced** — they pay off more often than prices suggest. High-priced contracts (>90c) are **overpriced** — they fail more often than prices suggest.

---

## 🎯 OPPORTUNITY ZONE: Low-Priced (5-20c) with Volume > $100k

These contracts may be **underpriced** based on the overconfidence bias. Consider buying at intermediate horizons (1-3 weeks before resolution).

| Market | Yes Price | Volume | End Date |
|--------|-----------|--------|----------|
| Maduro out in 2025? | **14%** | $14.8M | 2025-12-31 |
| New England Patriots win Super Bowl 2026? | **9%** | $7.4M | 2026-02-08 |
| Bitcoin dip to $70,000 by Dec 31, 2025? | **10%** | $5.7M | 2025-12-31 |
| 2 Fed rate cuts in 2025? | **6%** | $3.4M | 2025-12-10 |
| Seattle Seahawks win Super Bowl 2026? | **8%** | $3.2M | 2026-02-08 |
| Los Angeles Rams win Super Bowl 2026? | **15%** | $2.4M | 2026-02-08 |
| Denver Broncos win Super Bowl 2026? | **7%** | $2.4M | 2026-02-08 |
| Green Bay Packers win Super Bowl 2026? | **8%** | $2.3M | 2026-02-08 |
| Apple largest company by market cap on Dec 31? | **9%** | $2.2M | 2025-12-31 |
| Baltimore Ravens win Super Bowl 2026? | **6%** | $2.1M | 2026-02-08 |
| Philadelphia Eagles win Super Bowl 2026? | **10%** | $2.1M | 2026-02-08 |
| Buffalo Bills win Super Bowl 2026? | **10%** | $2.1M | 2026-02-08 |
| TikTok sale announced in 2025? | **6%** | $1.6M | 2025-12-31 |
| Trump's approval rating hit 40% in 2025? | **18%** | $799K | 2025-12-31 |
| Trump pardon Bob Menendez in 2025? | **5%** | $122K | 2025-12-31 |

---

## ⚠️ FADE ZONE: High-Priced (>90c) with Volume > $100k

These contracts may be **overpriced**. Consider selling or avoiding "sure things."

| Market | Yes Price | Volume | End Date |
|--------|-----------|--------|----------|
| A Minecraft Movie top grossing 2025? | **93%** | $3.3M | 2025-12-31 |
| 3 Fed rate cuts in 2025? | **92%** | $3.2M | 2025-12-10 |
| LLA holds most seats in Argentina 2025? | **99%** | $2.4M | 2025-10-26 |
| Trump sell 0 Gold Cards in 2025? | **90%** | $1.5M | TBD |
| Minecraft Movie best opening weekend 2025? | **95%** | $1.4M | 2025-12-31 |
| Gold close above $4000 end of 2025? | **92%** | $908K | 2025-12-31 |
| Elon/DOGE cut less than $50B in 2025? | **97%** | $254K | 2025-12-31 |

---

## Strategy Notes

### Entry Criteria (from Berg & Rietz)
1. **Price**: 5-20c (underpriced zone)
2. **Horizon**: 1-3 weeks before resolution (bias is strongest)
3. **Volume**: >$100k (liquidity for exit)
4. **Information Edge**: Have some reason to believe true probability is higher

### Exit Criteria
1. **Before final 24-48 hours** — bias evaporates near resolution
2. **When price reaches fair value** — take profit early
3. **If thesis breaks** — cut losses

### Risk Management
- Never bet more than you can lose
- Position size based on edge conviction
- Diversify across uncorrelated markets

---

## Data Source

- API: `https://gamma-api.polymarket.com/markets`
- Last Updated: 2025-12-06
- Full data: `research/polymarket_markets.json` (500 markets)

---

## Related Reading

- [Berg & Rietz (2018) Summary](./berg-rietz-2018-longshots-overconfidence.md)
