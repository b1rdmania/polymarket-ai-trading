# Quantitative Mean Reversion & Emotional Volatility Trading

**A Research Compendium for Prediction Market Strategy Development**

---

## Table of Contents

1. [Mean Reversion Theory](#1-mean-reversion-theory)
2. [The Ornstein-Uhlenbeck Process](#2-the-ornstein-uhlenbeck-process)
3. [Half-Life of Mean Reversion](#3-half-life-of-mean-reversion)
4. [Statistical Tests for Mean Reversion](#4-statistical-tests-for-mean-reversion)
5. [Z-Score Trading System](#5-z-score-trading-system)
6. [Kelly Criterion for Position Sizing](#6-kelly-criterion-for-position-sizing)
7. [Market Overreaction Effect](#7-market-overreaction-effect)
8. [Which Markets Are Most Emotional?](#8-which-markets-are-most-emotional)
9. [Sports Betting Mean Reversion](#9-sports-betting-mean-reversion)
10. [Application to Prediction Markets](#10-application-to-prediction-markets)

---

## 1. Mean Reversion Theory

### Core Concept

Mean reversion is the statistical tendency for extreme values to return toward the average over time. In financial markets, this means prices that deviate significantly from their "fair value" tend to correct.

### Academic Foundation

**De Bondt & Thaler (1985) - "Does the Stock Market Overreact?"**

The seminal paper establishing market overreaction. Key findings:

| Finding | Implication |
|---------|-------------|
| "Loser" portfolios outperform "winner" portfolios over 3-5 years | Past losers are undervalued |
| Extreme price movements are followed by reversals | Overreaction creates opportunity |
| The more extreme the move, the greater the reversal | Bigger panic = bigger opportunity |

### Two Key Hypotheses

1. **Directional Effect:** Extreme movements will be followed by movements in the opposite direction
2. **Magnitude Effect:** The more extreme the initial change, the greater the subsequent reversal

---

## 2. The Ornstein-Uhlenbeck Process

### The Standard Model for Mean Reversion

The OU process is a stochastic differential equation describing mean-reverting behavior:

```
dX = θ(μ - X)dt + σdW
```

### Parameters

| Symbol | Name | Meaning | Trading Implication |
|--------|------|---------|---------------------|
| **μ** | Long-term mean | The equilibrium price | Where price "should" be |
| **θ** | Speed of reversion | How fast it pulls back (higher = faster) | Determines half-life |
| **σ** | Volatility | Random noise magnitude | Affects position sizing |
| **X** | Current value | Current price | Entry/exit point |
| **dW** | Brownian motion | Random walk component | Unpredictable noise |

### Intuition

- When X > μ: Price is above mean → tendency to fall
- When X < μ: Price is below mean → tendency to rise
- θ controls how strong this "pulling" force is
- σ adds randomness that can temporarily push price away

### Why It Matters

The OU process gives us a mathematical framework to:
1. Estimate how long reversion takes
2. Calculate expected price trajectory
3. Set entry/exit thresholds
4. Size positions appropriately

---

## 3. Half-Life of Mean Reversion

### Definition

**Half-life** = Time for price to move halfway back to the mean from its current deviation.

### Formula

```
Half-Life = -ln(2) / λ

Where λ = mean-reversion speed parameter (negative in a mean-reverting series)
```

Or equivalently:
```
Half-Life = ln(2) / θ

Where θ = speed of reversion from OU process
```

### Estimation from Data

```python
import numpy as np
from statsmodels.regression.linear_model import OLS

def calculate_half_life(prices):
    """
    Calculate mean-reversion half-life from price series.
    
    Args:
        prices: Array of historical prices
        
    Returns:
        half_life: Number of periods for 50% reversion
    """
    # Price changes
    delta = np.diff(prices)
    
    # Lagged prices (exclude last)
    lagged = prices[:-1]
    
    # Regress: delta_price = lambda * lagged_price + epsilon
    lagged = lagged.reshape(-1, 1)
    model = OLS(delta, lagged).fit()
    lambda_param = model.params[0]
    
    # Calculate half-life
    if lambda_param >= 0:
        return np.inf  # Not mean-reverting
    
    half_life = -np.log(2) / lambda_param
    return half_life
```

### Trading Implications

| Half-Life | Interpretation | Action |
|-----------|----------------|--------|
| < 1 hour | Very fast reversion | Scalping opportunity |
| 1-6 hours | Fast reversion | Day trade |
| 6-24 hours | Moderate reversion | Swing trade |
| 1-7 days | Slow reversion | Position trade |
| > 7 days | Too slow | Consider avoiding |

### Selection Criterion

Only trade series where half-life is below your patience threshold:

```python
MAX_HALF_LIFE_HOURS = 24  # Don't hold positions > 1 day

if half_life < MAX_HALF_LIFE_HOURS:
    signal = "TRADEABLE"
else:
    signal = "AVOID"
```

---

## 4. Statistical Tests for Mean Reversion

### Augmented Dickey-Fuller (ADF) Test

The standard test for whether a series is mean-reverting (stationary).

**Null Hypothesis:** The series has a unit root (NOT mean-reverting)
**Alternative:** The series is stationary (mean-reverting)

```python
from statsmodels.tsa.stattools import adfuller

def test_mean_reversion(prices, significance=0.05):
    """
    Test if price series is mean-reverting using ADF test.
    
    Args:
        prices: Array of historical prices
        significance: p-value threshold (default 0.05)
        
    Returns:
        dict with test results
    """
    result = adfuller(prices, maxlag=1)
    
    adf_stat = result[0]
    p_value = result[1]
    critical_values = result[4]
    
    is_mean_reverting = p_value < significance
    
    return {
        'adf_statistic': adf_stat,
        'p_value': p_value,
        'critical_values': critical_values,
        'is_mean_reverting': is_mean_reverting,
        'interpretation': 'MEAN-REVERTING' if is_mean_reverting else 'NOT MEAN-REVERTING'
    }
```

### Interpretation

| p-value | Interpretation |
|---------|----------------|
| < 0.01 | Strong evidence of mean reversion |
| 0.01 - 0.05 | Moderate evidence of mean reversion |
| 0.05 - 0.10 | Weak evidence |
| > 0.10 | No evidence of mean reversion |

### Hurst Exponent (Alternative Test)

Another measure of mean reversion tendency:

| Hurst Value | Interpretation |
|-------------|----------------|
| H < 0.5 | Mean-reverting |
| H = 0.5 | Random walk |
| H > 0.5 | Trending/momentum |

---

## 5. Z-Score Trading System

### Definition

Z-score measures how many standard deviations the current price is from the mean:

```
Z-score = (Current Price - Mean) / Standard Deviation
```

### Calculation

```python
def calculate_z_score(prices, lookback=20):
    """
    Calculate rolling Z-score for price series.
    
    Args:
        prices: Array of historical prices
        lookback: Window for mean/std calculation
        
    Returns:
        z_scores: Array of Z-score values
    """
    import pandas as pd
    
    prices = pd.Series(prices)
    rolling_mean = prices.rolling(window=lookback).mean()
    rolling_std = prices.rolling(window=lookback).std()
    
    z_scores = (prices - rolling_mean) / rolling_std
    return z_scores
```

### Trading Rules

| Z-Score | Signal | Action |
|---------|--------|--------|
| Z > +2.0 | Strong Sell | Short / Sell position |
| Z > +1.0 | Weak Sell | Consider selling |
| -1.0 < Z < +1.0 | Neutral | No action |
| Z < -1.0 | Weak Buy | Consider buying |
| Z < -2.0 | Strong Buy | Buy / Go long |

### Entry/Exit Example

```python
def generate_signals(z_scores):
    """
    Generate trading signals from Z-scores.
    """
    signals = []
    
    for z in z_scores:
        if z < -2.0:
            signals.append('STRONG_BUY')
        elif z < -1.0:
            signals.append('WEAK_BUY')
        elif z > 2.0:
            signals.append('STRONG_SELL')
        elif z > 1.0:
            signals.append('WEAK_SELL')
        else:
            signals.append('HOLD')
    
    return signals

# Exit when Z-score returns to neutral
def should_exit(current_z, entry_z):
    """
    Exit when Z-score reverts toward zero.
    """
    # Exit long when Z returns to -0.5
    if entry_z < -1 and current_z > -0.5:
        return True
    
    # Exit short when Z returns to +0.5  
    if entry_z > 1 and current_z < 0.5:
        return True
    
    return False
```

---

## 6. Kelly Criterion for Position Sizing

### The Formula

The Kelly Criterion determines optimal bet size to maximize long-term growth:

```
f* = (bp - q) / b
```

### Variables

| Variable | Meaning | Example |
|----------|---------|---------|
| **f*** | Optimal fraction of bankroll to bet | 0.10 = bet 10% |
| **p** | Probability of winning | 0.60 = 60% win rate |
| **q** | Probability of losing (1 - p) | 0.40 = 40% loss rate |
| **b** | Net odds (payout ratio) | 1.5 = win $1.50 per $1 risked |

### Example Calculation

```
Scenario:
- You estimate 60% chance of winning (p = 0.60)
- Odds offered are 2.0 (b = 1.0, since you win $1 net per $1 risked)

f* = (1.0 × 0.60 - 0.40) / 1.0
f* = (0.60 - 0.40) / 1.0
f* = 0.20

→ Bet 20% of your bankroll
```

### Python Implementation

```python
def kelly_fraction(win_prob, odds):
    """
    Calculate Kelly Criterion optimal bet fraction.
    
    Args:
        win_prob: Probability of winning (0 to 1)
        odds: Net payout ratio (decimal odds - 1)
        
    Returns:
        Optimal fraction of bankroll to bet
    """
    q = 1 - win_prob
    
    kelly = (odds * win_prob - q) / odds
    
    # Never bet negative (no edge)
    return max(0, kelly)

# Example
win_prob = 0.55
decimal_odds = 2.0
net_odds = decimal_odds - 1  # = 1.0

fraction = kelly_fraction(win_prob, net_odds)
print(f"Bet {fraction:.1%} of bankroll")  # Bet 10.0%
```

### Fractional Kelly

Full Kelly is aggressive. Most practitioners use:

| Fraction | Risk Level | Use Case |
|----------|------------|----------|
| 100% Kelly | Very aggressive | Theoretical maximum |
| 50% Kelly | Moderate | Common choice |
| 25% Kelly | Conservative | Risk-averse |

```python
def fractional_kelly(win_prob, odds, fraction=0.5):
    """
    Conservative Kelly betting.
    """
    full_kelly = kelly_fraction(win_prob, odds)
    return full_kelly * fraction
```

### When NOT to Use Kelly

- When probability estimates are uncertain
- When variance matters (short-term)
- When you can't handle large drawdowns
- When correlation between bets exists

---

## 7. Market Overreaction Effect

### The De Bondt-Thaler Effect

Markets systematically overreact to both good and bad news:

| News Type | Immediate Reaction | Long-Term Result |
|-----------|-------------------|------------------|
| Very Good | Extreme rally | Subsequent underperformance |
| Very Bad | Extreme crash | Subsequent outperformance |

### Contrarian Strategy

**Buy losers. Sell winners.**

Based on overreaction research:
1. Identify stocks/assets with extreme recent losses (3-5 year returns)
2. Buy these "loser" portfolios
3. Avoid/short "winner" portfolios
4. Hold for 3-5 years
5. Expect losers to outperform

### Evidence Across Markets

| Market | Overreaction Found? | Notes |
|--------|---------------------|-------|
| US Stocks | ✅ Yes | Original De Bondt-Thaler finding |
| UK Stocks | ✅ Yes | Strongest in small caps |
| Emerging Markets | ✅ Strong | Higher retail participation |
| FX Markets | ✅ Yes | Especially in volatile pairs |
| Prediction Markets | ✅ Yes | Our target |

### Behavioral Causes

| Bias | Effect on Markets |
|------|-------------------|
| Overconfidence | Overreaction to good news |
| Loss aversion | Panic selling on bad news |
| Herding | Amplifies both directions |
| Recency bias | Overweight recent events |
| Representativeness | Pattern-matching errors |

---

## 8. Which Markets Are Most Emotional?

### Research Findings: Market Susceptibility to Emotional Trading

| Market Type | Emotional Susceptibility | Why |
|-------------|-------------------------|-----|
| **Emerging Market Stocks** | 🔴 Very High | Low institutional ownership, high retail, low literacy |
| **Small Cap Stocks** | 🔴 Very High | Less analyst coverage, more volatility |
| **Crypto** | 🔴 Very High | Retail-dominated, 24/7, social media driven |
| **Political Prediction Markets** | 🔴 Very High | Partisan bias, low liquidity, manipulation risk |
| **Sports In-Play** | 🟠 High | Real-time emotion after goals/events |
| **Large Cap Stocks** | 🟡 Moderate | More institutional, but still susceptible to panics |
| **FX Majors** | 🟢 Lower | High institutional, high liquidity |
| **Bonds** | 🟢 Lower | Institutional dominated |

### Political Prediction Markets: Most Irrational?

Research suggests political markets are **more irrational** than sports:

| Factor | Sports Markets | Political Markets |
|--------|---------------|-------------------|
| Liquidity | Higher | Often thin |
| Manipulation risk | Lower | Higher |
| Partisan bias | Minimal | Strong |
| Frequency of events | High (daily games) | Low (elections rarely) |
| Historical accuracy | Better | Worse (wrong on Brexit, 2016, 2020) |

### Prediction Market Specific Biases

1. **Favorite-Longshot Bias:** Longshots overpriced, favorites underpriced
2. **Partisan Bias:** People bet their political preferences
3. **Anchoring:** Stuck on initial odds/polls
4. **Recency Bias:** Overweight recent news

### Target Markets for Our Strategy

**Best opportunities (most emotional):**
1. Political markets with breaking news
2. Crypto-related markets
3. Low-liquidity markets after sudden moves
4. Any market after unexpected event

**Avoid (more efficient):**
1. High-liquidity sports favorites
2. Near-resolution markets (efficient)
3. Markets with strong institutional participation

---

## 9. Sports Betting Mean Reversion

### In-Play Trading Dynamics

When a goal is scored in football:

```
Timeline:
0:00 - Goal scored
0:01 - Market suspended
0:30 - Market reopens with new odds
1:00 - Emotional betting floods in
5:00 - Odds may overshoot fair value
15:00 - Gradual reversion begins
```

### The Overreaction Pattern

| Event | Typical Market Response | Reality |
|-------|------------------------|---------|
| Underdog scores early | Odds collapse massively | Often overcorrection |
| Favorite concedes | Panic, odds lengthen sharply | Usually overdone |
| Red card | Massive adjustment | Often excessive |
| Key player injury | Odds shift hard | Hard to quantify impact |

### Expected Goals (xG) Mean Reversion

**Key insight:** Goals scored vs. xG are mean-reverting

| xG vs. Goals | Interpretation | What Happens Next |
|--------------|----------------|-------------------|
| Goals >> xG | Player/team overperforming | Regression coming |
| Goals << xG | Underperforming (luck) | Positive regression |

**Trading implication:** Bet against streaks that deviate from xG.

### Sports Betting Takeaways

1. In-play markets overreact to goals, cards, injuries
2. The first 5 minutes after an event are most emotional
3. Mean reversion typically occurs within the match
4. Fundamental metrics (xG) help identify true value

---

## 10. Application to Prediction Markets

### Adapting Traditional Quant Models

| Traditional Market | Prediction Market Adaptation |
|-------------------|------------------------------|
| Stock price | Contract price (0-100c) |
| Fair value | True probability based on fundamentals |
| Deviation from value | Panic/FOMO-driven mispricing |
| Mean reversion | Correction as emotions subside |

### Key Difference: Shifting Mean

In stocks, the long-term mean is relatively stable. In prediction markets:

- **News changes the "fair value"**
- We're not betting on reversion to OLD mean
- We're betting on reversion of OVERREACTION to NEW mean

### The Overreaction Model

```
True Price Change = f(News Importance)
Actual Price Change = Observed move

Overreaction = Actual Price Change - True Price Change

If Overreaction > 0: Market moved too far → FADE
If Overreaction < 0: Market underreacted → FOLLOW
```

### Complete Trading System

```python
class PredictionMarketMeanReversionSystem:
    
    def __init__(self, half_life_threshold=24, z_score_entry=2.0):
        self.half_life_threshold = half_life_threshold
        self.z_score_entry = z_score_entry
    
    def analyze_market(self, prices, news_magnitude):
        """
        Full analysis of a prediction market.
        """
        # 1. Test for mean reversion
        adf_result = test_mean_reversion(prices)
        if not adf_result['is_mean_reverting']:
            return {'signal': 'NO_TRADE', 'reason': 'Not mean-reverting'}
        
        # 2. Calculate half-life
        half_life = calculate_half_life(prices)
        if half_life > self.half_life_threshold:
            return {'signal': 'NO_TRADE', 'reason': f'Half-life too long: {half_life:.1f}h'}
        
        # 3. Calculate current Z-score
        z_score = calculate_z_score(prices).iloc[-1]
        
        # 4. Check if overreaction
        if abs(z_score) < self.z_score_entry:
            return {'signal': 'NO_TRADE', 'reason': f'Z-score not extreme: {z_score:.2f}'}
        
        # 5. Assess news magnitude
        expected_move = self.expected_move_for_news(news_magnitude)
        actual_move = prices[-1] - prices[-2]
        overreaction = actual_move - expected_move
        
        # 6. Generate signal
        if z_score > self.z_score_entry and overreaction > 0:
            signal = 'SELL'
            direction = 'Market overshot upward'
        elif z_score < -self.z_score_entry and overreaction < 0:
            signal = 'BUY'
            direction = 'Market overshot downward'
        else:
            signal = 'NO_TRADE'
            direction = 'Move appears justified'
        
        # 7. Calculate position size
        if signal != 'NO_TRADE':
            win_prob = self.estimate_win_probability(z_score, half_life)
            odds = abs(z_score)  # Simplified
            position_size = fractional_kelly(win_prob, odds, fraction=0.25)
        else:
            position_size = 0
        
        return {
            'signal': signal,
            'direction': direction,
            'z_score': z_score,
            'half_life': half_life,
            'position_size_pct': position_size,
            'expected_reversion_time': half_life * 2  # 75% reversion
        }
    
    def expected_move_for_news(self, magnitude):
        """
        Map news magnitude to expected price move.
        
        Magnitude scale:
        1 = Noise (tweet, rumor)
        2 = Minor news (poll, statement)
        3 = Moderate news (policy change)
        4 = Major news (resignation, indictment)
        5 = Extreme news (war, death, disaster)
        """
        expected_moves = {
            1: 0.02,   # 2% move
            2: 0.05,   # 5% move
            3: 0.10,   # 10% move
            4: 0.20,   # 20% move
            5: 0.40,   # 40% move
        }
        return expected_moves.get(magnitude, 0.05)
    
    def estimate_win_probability(self, z_score, half_life):
        """
        Estimate probability that trade will be profitable.
        Based on: higher Z-score and shorter half-life = higher probability.
        """
        # Base probability from Z-score (empirical)
        z_factor = min(abs(z_score) / 3, 1)  # Caps at Z=3
        
        # Adjust for half-life (faster = better)
        half_life_factor = max(0, 1 - half_life / 48)  # Penalize > 48h
        
        # Combined probability (simplified model)
        win_prob = 0.5 + 0.2 * z_factor + 0.1 * half_life_factor
        
        return min(win_prob, 0.75)  # Cap at 75%
```

---

## Summary: The Complete Framework

### Detection Phase
1. Monitor all markets for price spikes (>15% in <2h)
2. Test if market is mean-reverting (ADF test)
3. Calculate half-life (is it tradeable?)
4. Calculate Z-score (how extreme?)

### Evaluation Phase
5. Identify the news trigger
6. Score news magnitude (1-5 scale)
7. Calculate expected vs. actual move
8. Determine if overreaction occurred

### Execution Phase
9. Generate signal (BUY/SELL/NONE)
10. Size position using Kelly criterion
11. Set exit target (Z-score → 0)
12. Set time-based stop (2x half-life)

### Key Metrics to Track

| Metric | Target | Purpose |
|--------|--------|---------|
| Half-life | < 24 hours | Ensure timely reversion |
| Z-score at entry | > 2.0 | Extreme deviation |
| Win rate | > 55% | Edge validation |
| Avg profit/loss | > 1.5x | Positive expectancy |
| Max drawdown | < 20% | Risk management |

---

## References

1. De Bondt, W. & Thaler, R. (1985). "Does the Stock Market Overreact?" Journal of Finance
2. Berg, J. & Rietz, T. (2018). "Longshots, Overconfidence and Efficiency on the Iowa Electronic Market"
3. Munger, C. (1995). "The Psychology of Human Misjudgment"
4. Uhlenbeck, G. & Ornstein, L. (1930). "On the Theory of Brownian Motion"
5. Kelly, J.L. (1956). "A New Interpretation of Information Rate"
6. Kahneman, D. & Tversky, A. (1979). "Prospect Theory"

---

*Document created: 2025-12-06*
*For: Prediction Market Trading Strategy Research*
