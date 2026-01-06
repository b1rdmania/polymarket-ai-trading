# Theme 2: Biases, Incentives & In-Play Betting Behaviour

> Literature on behavioral biases, high-frequency betting dynamics, and exploitable patterns in prediction markets.
> 
> **🎯 Emotional Volatility Arbitrage Focus:** This theme is the core of your trading edge — papers here directly inform when and how to exploit human emotional overreaction.

---

## Volatility Arbitrage Signals Summary

| Signal | Source | Actionable Play |
|--------|--------|-----------------|
| **Overconfidence at intermediate horizons** | Berg & Rietz 2018 | Buy underpriced longshots 1-3 weeks before resolution |
| **Live event overreaction** | Angelini 2022, Easton 2006 | Fade large in-play moves (goals, wickets) after 5-10 min |
| **Favourite-longshot bias** | Bürgi et al 2024 | Systematically bet against extreme longshots on Kalshi |
| **Real money sharpens prices** | Rosenbloom 2006 | Trust high-liquidity markets more; exploit thin markets |
| **Bias clustering** | Abínzano et al 2013 | When one bias appears, look for others — compound edge |

---

## 1. Statistical Tests of Real-Money Versus Play-Money Prediction Markets

| Field | Value |
|-------|-------|
| **Authors** | E.S. Rosenbloom, William Notz |
| **Year** | 2006 |
| **Venue** | *Electronic Markets* |
| **Link** | [Electronic Markets PDF](https://electronicmarkets.org/fileadmin/user_upload/doc/Issues/Volume_16/Issue_01/V16I1_Statistical_Tests_of_Real-Money_versus_Play-Money_Prediction_Markets.pdf) |

### Summary
Directly compares real-money vs play-money markets for forecasting accuracy.

### Key Findings
- Both can be reasonably accurate
- **Stronger monetary incentives + higher volume = sharper forecasts**
- Play-money markets show more noise and slower price discovery

### 🎯 Volatility Arbitrage Implication
- **Trust high-liquidity real-money markets** — prices are more efficient
- **Exploit thin markets** — less capital means more emotional noise to arbitrage
- Low-volume Polymarket contracts may have larger mispricings to trade

---

## 2. Longshots, Overconfidence and Efficiency on the Iowa Electronic Market

| Field | Value |
|-------|-------|
| **Authors** | Joyce E. Berg, Thomas A. Rietz |
| **Year** | 2018 |
| **Venue** | *International Journal of Forecasting* |
| **Link** | [UIowa PDF](https://www.biz.uiowa.edu/faculty/trietz/papers/longshots.pdf) |

### Summary
Examines binary election markets for longshot bias and overconfidence. Classic paper on prediction market efficiency.

### Key Findings
- **No longshot bias** in IEM (unlike racetracks)
- **Transitory overconfidence bias at intermediate horizons (1-3 weeks)**
  - High-priced contracts pay off LESS often than predicted
  - Low-priced contracts pay off MORE often than predicted
- Bias disappears near resolution (1-2 days)
- Dynamic trading strategies show positive Sharpe ratios for low-priced contracts

### 🎯 Volatility Arbitrage Implication — THE KEY FINDING
| Horizon | Bias | Trading Action |
|---------|------|----------------|
| 1-3 weeks out | Overconfidence | **Buy low-priced contracts** (undervalued) |
| 1-3 weeks out | Overconfidence | **Sell/fade high-priced contracts** (overvalued) |
| 1-2 days out | None | Markets efficient — no edge |

**This is your core edge:** Emotional overreaction peaks at intermediate horizons, then corrects.

---

## 3. Informational Efficiency and Behaviour Within In-Play Prediction Markets

| Field | Value |
|-------|-------|
| **Authors** | Giovanni Angelini et al. |
| **Year** | 2022 |
| **Venue** | *International Journal of Forecasting* |
| **Links** | [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0169207021000996) • [Reading WP](https://www.reading.ac.uk/web/files/economics/emdp201920.pdf) |

### Summary
Framework to test mispricing and efficiency using **high-frequency football betting data** around goals.

### Key Findings
- Markets incorporate news **very fast** (within minutes)
- But show **systematic behavioural quirks** during live events
- Overreaction to goals followed by partial correction
- Micro-level behaviour is messy; macro price still carries signal

### 🎯 Volatility Arbitrage Implication — IN-PLAY GOLD
| Event | Reaction | Play |
|-------|----------|------|
| Goal scored | Odds spike sharply | **Wait 5-10 min, then fade** if overreaction evident |
| Late goal | Even larger overreaction | Stronger fade opportunity |
| Red card | Emotional spike | Similar fade pattern |

**Live events = emotional volatility lab.** The spike is emotional; the correction is rational.

---

## 4. Behavioural Biases Never Walk Alone

| Field | Value |
|-------|-------|
| **Authors** | Isabel Abínzano, Luis Muga, Rafael Santamaría |
| **Year** | ~2013 |
| **Venue** | Conference paper (behavioural finance) |
| **Link** | [Unavarra PDF](https://academica-e.unavarra.es/bitstream/handle/2454/18743/BehavioralBiases.pdf) |

### Summary
Looks at how overconfidence interacts with probability judgments; finds biases cluster rather than appearing in isolation.

### Key Findings
- Biases **cluster** — if one is present, others likely are too
- Overconfidence, anchoring, and availability often appear together
- Retail bettors are systematically bad at probability estimation
- Markets work despite individual irrationality — but not perfectly

### 🎯 Volatility Arbitrage Implication
- **When you spot one bias, look for compound effects**
- Emotional volatility events likely trigger multiple biases simultaneously
- Your edge may be larger than single-bias models suggest
- Example: Breaking news → availability bias + recency bias + overconfidence = fat mispricing

---

## 5. An Examination of In-Play Sports Betting Using One-Day Cricket

| Field | Value |
|-------|-------|
| **Author** | Steven A. Easton |
| **Year** | 2006 |
| **Venue** | *Journal of Prediction Markets* / SSRN |
| **Link** | [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=948013) |

### Summary
Uses **ball-by-ball cricket data** to show in-play prices react rapidly to news and have predictive power.

### Key Findings
- Prices update within seconds of wickets/runs
- In-play betting is a **"lab for high-frequency information processing"**
- Prices have predictive power over match outcomes
- Overreaction patterns visible around key events (wickets, big overs)

### 🎯 Volatility Arbitrage Implication
- Sports markets are **cleaner labs** for testing emotional volatility strategies
- High-frequency data allows precise measurement of overreaction/correction cycles
- Findings transfer to political markets around breaking news events
- Consider paper trading on sports to calibrate your mean reversion timing

---

## 6. Information, Prices and Efficiency in an Online Betting Market

| Field | Value |
|-------|-------|
| **Authors** | Gil Elaad et al. |
| **Year** | 2020 |
| **Venue** | *Finance Research Letters* |
| **Link** | [IDEAS/RePEc](https://ideas.repec.org/a/eee/finlet/v35y2020ics1544612319306440.html) |

### Summary
Tests informational efficiency in an online betting market using odds data.

### Key Findings
- **Near-efficiency overall** — markets are right most of the time
- But **some exploitable anomalies** persist
- Bridge between sports betting microstructure and financial markets
- Transaction costs eat into edge but don't eliminate it

### 🎯 Volatility Arbitrage Implication
- Anomalies exist but are **thin margins** — need volume or size to profit
- Transaction costs matter — factor Polymarket fees into position sizing
- The edge is real but small; discipline and repetition required

---

## 7. Makers and Takers: The Economics of the Kalshi Prediction Market

| Field | Value |
|-------|-------|
| **Authors** | Constantin Bürgi, Wanying Deng, Karl Whelan |
| **Year** | 2024–2025 |
| **Venue** | CESifo Working Paper 12122 |
| **Links** | [RePEc](https://ideas.repec.org/p/ces/ceswps/_12122.html) • [Whelan PDF](https://www.karlwhelan.com/Papers/Kalshi.pdf) |

### Summary
**First detailed empirical study of Kalshi** using transaction-level data. Examines efficiency, biases, and platform design effects.

### Key Findings
- Prices are informative and **improve near expiry**
- **Strong favourite-longshot bias** — longshots overpriced, favourites underpriced
- Platform fees + design **systematically fleece certain user profiles** (naive retail)
- Makers (limit orders) do better than takers (market orders)

### 🎯 Volatility Arbitrage Implication — KALSHI-SPECIFIC
| Bias | Direction | Play |
|------|-----------|------|
| Favourite-longshot | Longshots overpriced | **Fade extreme longshots** on Kalshi |
| Fee structure | Hurts takers | **Use limit orders** — be the maker |
| Retail flow | Noise traders | Time entries around retail-driven spikes |

**Kalshi's design creates predictable losers** — position yourself opposite naive retail.

---

## Cross-Cutting Themes for Emotional Volatility Trading

| Pattern | Timing | Action |
|---------|--------|--------|
| **Overconfidence bias** | 1-3 weeks pre-resolution | Buy underpriced longshots |
| **In-play overreaction** | During live events | Fade spikes after 5-10 min |
| **Favourite-longshot bias** | Persistent | Short overpriced longshots (esp. Kalshi) |
| **Bias clustering** | Around breaking news | Look for compound mispricings |
| **Real-money efficiency** | Always | Exploit thin/low-volume markets more aggressively |

---

## Citation Block

```bibtex
@article{rosenbloom2006statistical,
  title={Statistical tests of real-money versus play-money prediction markets},
  author={Rosenbloom, Eric S and Notz, William},
  journal={Electronic Markets},
  volume={16},
  number={1},
  pages={63--69},
  year={2006}
}

@article{berg2018longshots,
  title={Longshots, overconfidence and efficiency on the Iowa Electronic Market},
  author={Berg, Joyce E and Rietz, Thomas A},
  journal={International Journal of Forecasting},
  year={2018}
}

@article{angelini2022informational,
  title={Informational efficiency and behaviour within in-play prediction markets},
  author={Angelini, Giovanni and others},
  journal={International Journal of Forecasting},
  volume={38},
  number={1},
  pages={282--299},
  year={2022}
}

@inproceedings{abinzano2013behavioural,
  title={Behavioural biases never walk alone: An empirical analysis of the effect of overconfidence on probabilities},
  author={Ab{\'\i}nzano, Isabel and Muga, Luis and Santamar{\'\i}a, Rafael},
  year={2013}
}

@article{easton2006examination,
  title={An examination of in-play sports betting using one-day cricket},
  author={Easton, Steven A},
  journal={Journal of Prediction Markets},
  year={2006}
}

@article{elaad2020information,
  title={Information, prices and efficiency in an online betting market},
  author={Elaad, Gil and others},
  journal={Finance Research Letters},
  volume={35},
  year={2020}
}

@techreport{burgi2024kalshi,
  title={Makers and takers: The economics of the Kalshi prediction market},
  author={B{\"u}rgi, Constantin and Deng, Wanying and Whelan, Karl},
  year={2024},
  institution={CESifo Working Paper}
}
```
