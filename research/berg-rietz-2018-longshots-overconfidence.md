# Longshots, Overconfidence and Efficiency on the Iowa Electronic Market

**Authors:** Joyce E. Berg and Thomas A. Rietz  
**Institution:** Tippie College of Business, University of Iowa  
**Date:** February 2018  
**Published:** International Journal of Forecasting

---

## Abstract

We study the forecast accuracy and efficiency of popular "binary" prediction markets. Such markets forecast probabilities for future states of the world (e.g., election winners) by paying off $0 or $1 depending on the realized state (e.g., who actually won). To assess accuracy, forecast probabilities must be compared to realization frequencies, not individual realizations. We use Iowa Electronic Market (IEM) data to test efficiency against two alternative propositions from behavioral finance: the longshot bias and the overconfidence bias (which yield opposing predictions). No longshot bias appears in IEM markets. Nor does overconfidence influence prices at short horizons. However, overconfident traders may bias prices at intermediate horizons. While the markets are efficient at short horizons, non-market data indicate some intermediate-horizon inefficiency. We calculate Sharpe ratios for static trading strategies and document returns for dynamic trading strategies to assess the economic content of the inefficiencies.

**Keywords:** Prediction Markets, Market Efficiency, Longshot Bias, Overconfidence

---

## Key Concepts

### The Core Problem with Binary Prediction Markets

In binary contract markets, people often have the mistaken belief that the market is "right" if the outcome forecast as most likely actually occurs. If not, the market is "wrong."

**Example:** In the 2004 US Presidential Election, InTrade ran 51 markets on the election winner in each individual State and the District of Columbia. They famously claimed to have predicted every race correctly. However, this does not indicate that the market was efficient. In fact, if the market was perfectly efficient, we should observe Obama taking Florida nearly 1/3 of the time when priced at 69%.

> **The question isn't whether prediction markets "miss" from time to time, but whether they "miss" at the right rate.**

---

## Two Competing Biases

### 1. Longshot Bias
- Over-pricing low probability contracts
- Under-pricing high probability contracts
- Similar to "over-betting" on longshots in racetrack betting
- Consistent with Prospect Theory's overweighting of low probability events

### 2. Overconfidence Bias
- Under-pricing low probability contracts
- Over-pricing high probability contracts
- Results from traders overestimating probabilities for events they deem likely
- Can also result from overreacting to information

---

## Key Findings

### No Longshot Bias
The data shows **no evidence** of a longshot bias affecting IEM prices.

### Transitory Overconfidence Bias
Evidence shows a **transitory overconfidence bias at intermediate horizons**:

| Horizon | Effect |
|---------|--------|
| **Short (1-2 days)** | Markets appear efficient, no significant bias |
| **Intermediate (4-21 days)** | Overconfidence bias present - highest priced contracts pay off less often than predicted |
| **Approaching liquidation** | Bias disappears as uncertainty resolves |

### Price-Frequency Relationships (Table 1 Summary)

| Price Range | Actual Payoff vs. Price |
|-------------|------------------------|
| $0.00-$0.20 | Payoffs **exceed** prices (contracts under-priced) |
| $0.20-$0.40 | Roughly efficient |
| $0.40-$0.60 | Roughly efficient |
| $0.60-$0.80 | Roughly efficient |
| $0.80-$1.00 | Payoffs **below** prices (contracts over-priced) |

> **Critical insight:** The effect at extremes is concentrated on **very low priced contracts (lowest quintile)**. Mid-range probabilities (where Trump/Brexit were priced) show **no significant bias**.

---

## The Daniel, Hirshleifer and Subrahmanyam (1998) Dynamic

The paper confirms a pattern consistent with DHS (1998):

1. **Initial trading:** Prices are noisy but unbiased (little information available)
2. **Intermediate horizons:** Overconfidence bias develops as information arrives but uncertainty remains
3. **Near liquidation:** Bias disappears as more information arrives and uncertainty resolves

> Traders appear to have a **transitory overreaction** to outside information at intermediate horizons.

---

## Trading Strategy Implications

### Sharpe Ratios for Buy-and-Hold Strategies

| Contract Price | Horizon | Sharpe Ratio |
|----------------|---------|--------------|
| $0.10 range | 14 days | **Highest** |
| $0.10 range | 4 days | High |
| Mid-range | Any | Low/Negative |

**Key insight:** Positive reward-to-risk ratio exists for **low-priced contracts at intermediate horizons**.

### Dynamic Trading Returns (Model I)

| Risk Aversion (γ) | Monthly Return | Final Portfolio Value |
|-------------------|----------------|----------------------|
| 0.50 (high) | 0.31% | $120 |
| 0.25 (medium) | 0.64% | $147 |
| 0.10 (low) | 1.24% | $207 |

### With Outside Information (Model III)

| Risk Aversion (γ) | Monthly Return | Final Portfolio Value |
|-------------------|----------------|----------------------|
| 0.50 (high) | 4.76% | $411 |
| 0.25 (medium) | 7.23% | $723 |
| 0.10 (low) | 11.32% | $1,655 |

---

## Lessons for Prediction Market Users

### Caution #1: Don't confuse outcomes with accuracy
- Observing the most likely forecast outcome doesn't mean the forecast was "correct"
- Observing a less likely outcome doesn't mean the forecast was "incorrect"
- **If markets are efficient, we should observe outcomes with frequencies that parallel the forecast probabilities**

### Caution #2: Market and contract design matters
- Markets with transaction/profit fees can lead to mis-pricing
- Markets without clear arbitrage restrictions can lead to mis-pricing
- Mis-specified contracts can lead to misinterpretation

### Caution #3: Horizon effects exist
- Short horizons: Markets appear efficient
- Intermediate horizons: Overconfidence bias may affect prices
- The bias is **transitory** and disappears near resolution

---

## Implications for Our Trading

### What This Paper Suggests

1. **At intermediate horizons (1-3 weeks out):**
   - Low-priced contracts may be **undervalued**
   - High-priced contracts may be **overvalued**
   - Contrarian strategies may have positive expected value

2. **Near resolution (1-2 days):**
   - Markets become efficient
   - Bias disappears
   - Prices reflect true probabilities

3. **The "efficiency" of Polymarket:**
   - If a market prices something at 18% (Trump) or 15% (Brexit), **that's not necessarily wrong**
   - The question is whether outcomes occur at the right *rates* over many trials

### Our Aztec Trade in Context

Our mistake wasn't that we lost—markets should lose sometimes at those odds. Our mistakes were:
1. **Model error:** Applied wrong framework (traditional auction to CCA)
2. **Ignored our own research:** We had the CCA information but didn't apply it
3. **Overconfidence at intermediate horizon:** Exactly the bias this paper documents

---

## Methodology Notes (For Future Reference)

### Testing Binary Market Efficiency

The paper uses **logit models** to estimate true probabilities:

```
q_t^j = e^(X_t * b_t^j) / Σ e^(X_t * b_t^i)
```

If prices are unbiased: β = 1, α = 0

- **β > 1:** Longshot bias (overpaying for low probability)
- **β < 1:** Overconfidence bias (overpaying for high probability)
- **β = 1:** Efficient pricing

### What Makes IEM Good for Testing

1. Real money, real consequences
2. Simple contracts with known liquidation values
3. Repeated under essentially identical conditions
4. No transaction fees
5. Easy arbitrage structure
6. No trader is large relative to market

---

## Citation

```
Berg, J.E. and Rietz, T.A. (2018). "Longshots, Overconfidence and Efficiency 
on the Iowa Electronic Market." International Journal of Forecasting.
```

---

## Related Reading

- Daniel, K., Hirshleifer, D., and Subrahmanyam, A. (1998). "Investor Psychology and Security Market Under- and Overreactions." *Journal of Finance*
- Kahneman, D. and Tversky, A. (1979). "Prospect Theory: An Analysis of Decision Under Risk." *Econometrica*
- Lichtenstein, S., Fischhoff, B., and Phillips, L.D. (1982). "Calibration of Probabilities: The State of the Art to 1980."
