# Political Betting Markets: Complete Research Guide

**A Framework for Exploiting Emotional Volatility in Political Prediction Markets**

---

## Table of Contents

1. [Why Political Markets](#1-why-political-markets)
2. [News Sources That Move Markets](#2-news-sources-that-move-markets)
3. [Historical Volatility Case Studies](#3-historical-volatility-case-studies)
4. [Partisan Bias Detection](#4-partisan-bias-detection)
5. [Polls vs. Markets](#5-polls-vs-markets)
6. [Data Sources & APIs](#6-data-sources--apis)
7. [The Political Aggregator Concept](#7-the-political-aggregator-concept)

---

## 1. Why Political Markets

### Research Findings

Political prediction markets are **more irrational** than sports markets:

| Factor | Sports | Political |
|--------|--------|-----------|
| Partisan bias | Minimal | Strong |
| Liquidity | Higher | Lower |
| Manipulation risk | Lower | Higher |
| Emotional attachment | Some | Intense |
| Historical accuracy | Better | Worse |

### Key Inefficiencies

1. **Partisan traders** bet their politics, not probabilities
2. **Low liquidity** means single large bets can move markets significantly
3. **Emotional overreaction** to news that doesn't change fundamentals
4. **Echo chambers** create divergent beliefs

### 2024 Evidence

- Polymarket 2024 election: $572M traded
- Single $3M bet caused "significant slippage"
- Trump odds: 46% → 66% → 46% → 66% over months
- Harris briefly led at 52%, collapsed to 35%

**Conclusion:** These swings create trading opportunities.

---

## 2. News Sources That Move Markets

### Tier 1: Fastest Market Movers

These accounts/sources cause **immediate** price action on Polymarket:

| Source | Type | Why They Move Markets |
|--------|------|----------------------|
| **@elikimerling (Elon Musk)** | X/Twitter | 200M+ followers, pro-Trump, owns the platform |
| **@Polymarket** | X/Twitter | Official account, market creation announcements |
| **Nate Silver / Silver Bulletin** | Substack | 538 founder, Polymarket advisor, polling analysis |
| **@DonaldJTrumpJr** | X/Twitter | Polymarket advisor, MAGA influencer |
| **@AP / @Reuters** | Breaking News | Election calls, major political news |
| **@WSJ / @nytimes** | Breaking News | Policy announcements, investigations |

### Tier 2: Strong Influence

| Source | Type | Notes |
|--------|------|-------|
| **RealClearPolitics** | Polling Aggregator | Includes betting odds average |
| **FiveThirtyEight (538)** | Polling Model | Statistical forecast, CSV data available |
| **Politico** | Political News | DC insider coverage |
| **CNBC / Bloomberg** | Financial News | Market-moving policy coverage |

### Tier 3: Sentiment Indicators

| Source | Type | Notes |
|--------|------|-------|
| **Crypto Twitter** | Social | Polymarket user base is crypto-native |
| **r/politics / r/Conservative** | Reddit | Partisan sentiment |
| **Cable News (Fox/MSNBC/CNN)** | TV | Lag indicator, but influences retail |

### Twitter Lists to Build

```
Political Market Movers:
- @Polymarket
- @NateSilver538
- @ElonMusk
- @RealClearNews
- @AP_Politics
- @WSJPolitics
- @PoliticoPlaybook

Breaking News (Fast):
- @AP
- @Reuters
- @Breaking911
- @disclosetv

Political Journalists:
- @maggieNYT (Maggie Haberman - Trump access)
- @Acosta (Jim Acosta - CNN)
- @jonathanvswan (Jonathan Swan - Axios)
```

---

## 3. Historical Volatility Case Studies

### Case Study 1: 2024 Election Night

**Timeline:**

| Date | Event | Trump Odds | Harris Odds |
|------|-------|------------|-------------|
| July 2024 | Biden withdraws | 66% | N/A |
| Aug 2024 (peak) | Harris momentum | 46% | 52% |
| Oct 2024 (late) | Trump surge | 63-66% | 34-37% |
| Nov 5 (election) | Results | 95%+ | <5% |

**Key Observations:**
- 20+ point swings over weeks
- Markets reacted faster than polls to Harris momentum
- Final week showed extreme partisan trading

### Case Study 2: Biden Withdrawal (July 2024)

**What happened:**
- Polymarket predicted Biden withdrawal **weeks before** announcement
- "Biden to drop out" market moved from ~20% to 60%+ before news broke
- Smart money was positioned early

**Lesson:** Markets can front-run news. Watch for unusual volume on low-probability events.

### Case Study 3: First Trump-Harris Debate (Sept 2024)

**Market reaction:**
- Trump Media (DJT) stock tumbled post-debate
- Clean energy stocks rallied (Harris policy proxy)
- Polymarket odds shifted ~5% toward Harris

**Lesson:** Debates cause immediate volatility. Post-debate is often overreaction.

### Case Study 4: January 6 Capitol Attack (2021)

**Surprising finding:**
- Stock market RALLIED during Capitol breach
- Dow, S&P, Nasdaq all hit record highs the next day
- Market focused on: Biden's certification, Georgia runoffs, stimulus expectations

**Lesson:** Markets don't always react to political chaos as expected. Follow the money flow.

### Case Study 5: Large Single Bets

**Example:** A single $3M bet on Trump caused "significant slippage"
- Odds moved noticeably on just one trade
- Then partially reverted

**Lesson:** Low liquidity = opportunity for mean reversion after whale trades.

---

## 4. Partisan Bias Detection

### The Problem

Political bettors bet their preferences, not objective probabilities.

### Research Findings

| Finding | Source |
|---------|--------|
| Republican partisans show stronger "position persistence" | Aalto University study |
| Partisan sentiment causes mispricing, especially for Republican assets | ResearchGate |
| Despite financial incentives, political identity influences betting behavior | Academic research |

### Detecting Partisan Lean

**Method 1: Trading Pattern Analysis**

```python
def calculate_partisan_score(trader_transactions):
    """
    Calculate partisan lean from transaction history.
    
    Returns: -1 (strong Democrat) to +1 (strong Republican)
    """
    dem_buys = sum(t.volume for t in transactions if t.favors == 'Democrat')
    rep_buys = sum(t.volume for t in transactions if t.favors == 'Republican')
    total = dem_buys + rep_buys
    
    if total == 0:
        return 0  # Neutral
    
    return (rep_buys - dem_buys) / total
```

**Method 2: Polls vs. Market Divergence**

```
If Market_Probability > Poll_Probability + 10%:
    → Market may be biased toward that outcome
    
If Market_Probability < Poll_Probability - 10%:
    → Market may be underweighting that outcome
```

**Method 3: Platform Lean**

| Platform | Known Lean | Notes |
|----------|------------|-------|
| Polymarket | Pro-crypto, mixed | Crypto users skew libertarian/Republican |
| Kalshi | Unknown | US-regulated, potentially more institutional |
| PredictIt | Research-oriented | More Democrat participation historically |

### Trading Implications

1. **When market is "too Republican":** Look for Democrat buying opportunities
2. **When market is "too Democrat":** Look for Republican buying opportunities
3. **Cross-reference polls:** If 538/RCP shows X but market shows Y, investigate the gap

---

## 5. Polls vs. Markets

### Key Differences

| Aspect | Polls (538/RCP) | Markets (Polymarket) |
|--------|-----------------|---------------------|
| Measures | Voting intention | Outcome probability |
| Updates | Days/weeks | Seconds |
| Sample | Survey respondents | People with money at stake |
| Biases | Sampling, response | Partisan, manipulation |

### Historical Accuracy

| Year | Polls | Markets | Winner |
|------|-------|---------|--------|
| 2016 | Clinton +3 | Trump ~30% | Trump won |
| 2020 | Biden +8 | Biden ~60% | Biden won |
| 2024 | Harris +1 (late) | Trump ~65% | Trump won |

**Pattern:** Markets often diverge from polls. When they do, **markets have been more accurate** in recent elections.

### Arbitrage Opportunity

```
If Poll_Average shows 50/50 race
But Market shows 65/35

Either:
1. Market knows something polls don't (insider info)
2. Market is biased (partisan trading)
3. Market is pricing risk polls can't capture

Action: Analyze WHY the divergence exists
```

---

## 6. Data Sources & APIs

### Polling Data

| Source | Access | Notes |
|--------|--------|-------|
| **FiveThirtyEight** | CSV files on GitHub | Historical polling data, model outputs |
| **RealClearPolitics** | Web scraping (Python package) | Polling averages, betting odds average |
| **270toWin** | Web | Electoral map, historical data |

**FiveThirtyEight Data:**
```
https://github.com/fivethirtyeight/data
- polls/
- election-forecasts/
```

**RCP Scraping (Python):**
```python
# pip install realclearpolitics
from realclearpolitics import get_polls
polls = get_polls('president')
```

### Prediction Market Data

| Source | Access | Notes |
|--------|--------|-------|
| **Polymarket API** | Free (real-time) | No historical for closed markets |
| **Adjacent API** | Free tier limited, paid for history | OHLCV data, news matching |
| **Kalshi API** | US-only, regulated | CFTC supervised |
| **PredictIt API** | Limited | Shutting down |

### News APIs

| Source | Access | Speed |
|--------|--------|-------|
| **Twitter/X API** | Paid ($100+/mo) | Fastest |
| **NewsAPI.org** | Free tier exists | 5-15 min delay |
| **CryptoPanic** | Free | Crypto-focused |
| **Adjacent News API** | Paid | News-to-market matching |

### Real-Time Alerts

| Source | Method | Notes |
|--------|--------|-------|
| **Nevua Markets** | Telegram/Discord/Webhook | Polymarket price alerts |
| **Custom Twitter scraper** | API or Nitter | Breaking news detection |
| **RSS feeds** | Free | Slower, but comprehensive |

---

## 7. The Political Aggregator Concept

### Vision

A **Political Betting Aggregator** that:

1. **Aggregates polling data** from 538, RCP, other sources
2. **Tracks prediction market odds** from Polymarket, Kalshi
3. **Detects divergence** between polls and markets
4. **Identifies partisan bias** in market pricing
5. **Monitors news sources** for market-moving events
6. **Generates trading signals** when emotional overreaction is detected

### Data Flows

```
                    ┌─────────────────┐
                    │   POLLING DATA   │
                    │  (538, RCP)      │
                    └────────┬────────┘
                             │
                             ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  MARKET DATA    │  │   AGGREGATOR    │  │   NEWS FEED     │
│  (Polymarket)   │──│   (Our Tool)    │──│  (Twitter/RSS)  │
└─────────────────┘  └────────┬────────┘  └─────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  SIGNAL ENGINE   │
                    │                  │
                    │  - Divergence    │
                    │  - Overreaction  │
                    │  - Partisan Bias │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  ALERTS/TRADES   │
                    └─────────────────┘
```

### Key Screens

1. **Dashboard:** Current polls vs. markets for major races
2. **Divergence Tracker:** Where polls and markets disagree
3. **Volatility Monitor:** Markets with recent large moves
4. **News Feed:** Breaking political news with market impact
5. **Signal Log:** Generated trading opportunities

### Unique Value Propositions

1. **Polls + Markets in one view:** No one else does this well
2. **Partisan bias scoring:** Identify when markets are irrational
3. **Overreaction detection:** Mean reversion opportunities
4. **Historical backtesting:** Learn from past political events

---

## Summary: The Political Betting Edge

### What We Know

1. **Political markets are inefficient** — partisan bias, low liquidity, emotional trading
2. **News moves markets fast** — Elon Musk, Nate Silver, breaking news
3. **Large trades cause slippage** — then mean revert
4. **Polls and markets diverge** — and markets are often right
5. **Historical patterns exist** — debates, withdrawals, major events

### What We'd Build

A **Political Betting Aggregator** that:
- Combines polls + markets + news
- Detects emotional overreaction
- Identifies partisan bias
- Generates mean reversion signals
- Alerts to trading opportunities

### Why It Could Work

- 86% of Polymarket users lose money
- The winners are systematic, not emotional
- We have the framework (Munger + quant models)
- We have the data sources (APIs, scrapers)
- Political markets are the most irrational

---

## Appendix: Key Accounts to Follow

### Twitter/X

```
@Polymarket - Official platform
@NateSilver538 - 538 founder, PM advisor
@ElonMusk - Market mover
@RealClearNews - Polling aggregator
@AP - Fastest election calls
@Reuters - Breaking news
@WSJPolitics - Policy news
@maggieNYT - Trump insider access
```

### Telegram

```
@AdjacentNews - Market-focused political news
@Polymarket_official - (if exists)
```

### Data Sources

```
- FiveThirtyEight GitHub: github.com/fivethirtyeight/data
- Adjacent API: api.data.adj.news
- Polymarket API: gamma-api.polymarket.com
- RealClearPolitics: realclearpolling.com
```

---

*Document created: 2025-12-06*
*For: Political Prediction Market Strategy Research*
