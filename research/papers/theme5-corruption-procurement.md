# Theme 5: Corruption, Public Procurement & Predictive Analytics

> Using data analytics and network science to detect and predict corruption risk in public spending.
>
> **🎯 Relevance:** Supports the thesis that prediction/analytics can be governance infrastructure — specifically for anti-corruption. If corruption is predictable, capital can be allocated away from it.

---

## 1. Data Analytics for Anti-Corruption in Public Procurement

| Field | Value |
|-------|-------|
| **Authors** | Viktoriia Poltoratskaia, Mihály Fazekas |
| **Year** | 2024 |
| **Venue** | Chapter in *Routledge Handbook of Public Procurement Corruption* |
| **Links** | [Preprint PDF](https://www.govtransparency.eu/wp-content/uploads/2023/12/DataanalyticsanticorrinPP_chapter_preprint_2023.pdf) • [ResearchGate](https://www.researchgate.net/publication/376721654_Data_Analytics_for_Anti-Corruption_in_Public_Procurement) |

### Summary
Reviews how **statistical and ML methods** can flag corruption risk in procurement data.

### Key Findings
- **Red flags** from data: bid patterns, price anomalies, award structures, timing
- Risk scoring systems can flag high-risk contracts before award
- Examples: opentender.eu, ProZorro (Ukraine), various national portals
- Human oversight still needed — analytics augments, doesn't replace

### Corruption Prediction Signals
| Signal | What It Indicates |
|--------|-------------------|
| Single-bid tenders | Rigged specification |
| Winner's curse avoidance | Collusion |
| Price clustering | Bid-rigging |
| Short bidding windows | Insider advantage |
| Repeat winner patterns | Capture |

---

## 2. Corruption Risk in Contracting Markets: A Network Science Perspective

| Field | Value |
|-------|-------|
| **Authors** | Johannes Wachs, Mihály Fazekas, János Kertész |
| **Year** | 2021 |
| **Venue** | *International Journal of Data Science and Analytics* |
| **Link** | [Springer](https://link.springer.com/article/10.1007/s41060-019-00204-1) |

### Summary
Uses **network measures** over firms, buyers, and contracts to detect anomalous structures linked to corruption.

### Key Findings
- Corruption creates **signatures in network topology**
- Detectable patterns: clustering, bridge nodes, unusual connectivity
- Bid-rigging cartels leave network fingerprints
- Graph analytics can surface hidden relationships

### Network Corruption Signals
| Pattern | Interpretation |
|---------|----------------|
| Unusually dense clusters | Cartel activity |
| Bridge firms | Corruption brokers |
| Isolated buyer-seller pairs | Captive relationships |
| Temporal clustering | Rotating scheme |

### Implication
**Corruption risk is quantifiable from transactional graphs** — supports on-chain analytics for DAO/protocol corruption detection.

---

## 3. Predictive Factors for Assessing Corruption Risk in Public Procurement During Emergency Situations

| Field | Value |
|-------|-------|
| **Author** | Elaine Vasquez |
| **Year** | 2024 |
| **Venue** | Linköping University thesis |
| **Links** | [Full Text PDF](https://www.diva-portal.org/smash/get/diva2%3A1904936/FULLTEXT01.pdf) • [Record](https://liu.diva-portal.org/smash/record.jsf?pid=diva2%3A1904936) |

### Summary
Builds **predictive models** for corruption risk in emergency procurement (e.g., COVID response).

### Key Findings
- Emergency procurement is **higher risk** — relaxed oversight, urgency pressure
- Predictive features: competition level, bidding time, supplier history, contract modifications
- ML models can score corruption risk **ex ante** (before contract award)
- COVID procurement showed elevated risk indicators globally

### Emergency Procurement Red Flags
| Feature | Risk Direction |
|---------|----------------|
| Low competition | ↑ Higher risk |
| Short bidding window | ↑ Higher risk |
| New/unknown supplier | ↑ Higher risk |
| Post-award modifications | ↑ Higher risk |
| Large contract value | ↑ Higher risk |

---

## 4. What Predicts Corruption?

| Field | Value |
|-------|-------|
| **Authors** | Emanuele Colonnelli, Jorge A. Gallego, Mounu Prem |
| **Year** | 2020 |
| **Venue** | Working paper |
| **Links** | [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3330651) • [OSF PDF](https://osf.io/download/fq2xb) |

### Summary
Uses **large administrative datasets** to identify drivers of corruption and test predictability.

### Key Findings
- Corruption is **predictable from observable factors**
- Institutional context matters: weak oversight → more corruption
- Individual-level and structural factors both predict
- "Corruption risk metrics" can be built and validated

### Predictive Factors
| Factor Type | Examples |
|-------------|----------|
| Institutional | Oversight strength, audit frequency, transparency laws |
| Structural | Sector (construction high risk), contract type, geography |
| Individual | Official's tenure, prior history, network position |
| Temporal | Election cycles, budget deadlines, emergency periods |

### Implication
**"Corruption risk metrics" can be built and tied into capital allocation** — supports prediction-market-style scoring for public spending.

---

## Cross-Cutting Themes for Governance Applications

| Approach | Method | Application |
|----------|--------|-------------|
| **Red flag analytics** | Statistical anomaly detection | Score contracts pre-award |
| **Network analysis** | Graph measures | Detect cartels, capture |
| **Predictive modeling** | ML on procurement data | Ex ante risk scoring |
| **Transparency portals** | Public data + analytics | Watchdog monitoring |

### What This Means for Prediction Markets / Crypto
- On-chain analytics can apply similar techniques to protocol governance
- Prediction markets on governance proposals could surface corruption risk
- "Corruption futures" — markets on audit outcomes, treasury misuse
- Graph analytics on DAO voting patterns to detect capture

---

## Citation Block

```bibtex
@incollection{poltoratskaia2024data,
  title={Data analytics for anti-corruption in public procurement},
  author={Poltoratskaia, Viktoriia and Fazekas, Mih{\'a}ly},
  booktitle={Routledge Handbook of Public Procurement Corruption},
  year={2024}
}

@article{wachs2021corruption,
  title={Corruption risk in contracting markets: A network science perspective},
  author={Wachs, Johannes and Fazekas, Mih{\'a}ly and Kert{\'e}sz, J{\'a}nos},
  journal={International Journal of Data Science and Analytics},
  volume={12},
  number={1},
  pages={45--60},
  year={2021}
}

@mastersthesis{vasquez2024predictive,
  title={Predictive factors for assessing corruption risk in public procurement during emergency situations},
  author={Vasquez, Elaine},
  year={2024},
  school={Link{\"o}ping University}
}

@techreport{colonnelli2020predicts,
  title={What predicts corruption?},
  author={Colonnelli, Emanuele and Gallego, Jorge A and Prem, Mounu},
  year={2020}
}
```
