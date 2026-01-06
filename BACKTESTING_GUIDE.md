# Historical Backtesting Guide

## Overview

Test your trading strategy on past markets to validate before going live.

## Challenge: Limited Historical Data

As @the_smart_ape discovered, **Polymarket's historical API is incomplete** for many markets. We have several workarounds:

## Data Sources (In Order of Quality)

### 1. Adjacent API (Best) 💰
- **Pros**: Complete OHLCV data, reliable
- **Cons**: Paid service ($)
- **Setup**: Get API key from https://adjacent.finance

```bash
export ADJACENT_API_KEY="your_key_here"
```

### 2. Polymarket CLOB API (Free) 📊
- **Pros**: Free, official
- **Cons**: Often returns empty data
- **Works for**: Recent, high-volume markets only

### 3. Recorded Data (Your Own) 📹
- **Pros**: Accurate, custom
- **Cons**: Need to record for weeks/months first
- **Setup**: Run paper trader to start recording

### 4. Manual Test Markets 🎯
- **Pros**: Can control scenario
- **Cons**: Limited scope

## Quick Start

### Step 1: Find Testable Markets

```bash
python scripts/find_testable_markets.py
```

This will:
- Find recently resolved markets
- Check which have historical data
- Give you ready-to-test commands

Example output:
```
✅ Markets ready for backtesting:

python toolkit/execution-engine/src/execution_engine/backtester.py \
    --market trump-popular-vote-2024

python toolkit/execution-engine/src/execution_engine/backtester.py \
    --market bitcoin-above-100k-2024
```

### Step 2: Run Backtest

```bash
cd toolkit/execution-engine

python src/execution_engine/backtester.py \
    --market trump-popular-vote-2024 \
    --config ../../config/trading.yaml
```

### Step 3: Analyze Results

The backtest will output:
```
BACKTEST RESULTS
============================================================

Markets Tested: 1
Total Trades: 12
Winning Trades: 8
Win Rate: 66.7%
Total P&L: $145.50
ROI: 7.3%

============================================================
```

## Running Multiple Markets

### Test a Batch

Create `data/test_markets.txt`:
```
trump-popular-vote-2024
bitcoin-above-100k-2024
fed-rate-decision-december
```

Run batch test:
```bash
while read market; do
    python src/execution_engine/backtester.py --market "$market"
done < ../../data/test_markets.txt
```

## Understanding Results

### Win Rate
- **Target**: >55%
- **Good**: 55-65%
- **Excellent**: >65%

### ROI
- **Remember**: This is per market, not annualized
- **Compare**: Against buy-and-hold
- **Validate**: Consistent across markets?

### Trade Count
- **Too few** (<5): Not enough data to judge
- **Good** (10-20): Solid sample
- **Many** (>20): Strong evidence

## Limitations (Important!)

### What Backtests DON'T Account For:

1. **Slippage Variation**
   - Backtest assumes constant slippage
   - Reality: varies with market conditions

2. **Market Impact**
   - Your orders move prices
   - Bigger positions = more impact
   - Not simulated in backtest

3. **Execution Failures**
   - Orders can be rejected
   - API can go down
   - Network issues

4. **Fee Changes**
   - Fees may vary by market
   - Maker vs taker differences

5. **Liquidity**
   - Historical orderbook depth not available
   - Can't simulate partial fills

6. **Look-Ahead Bias**
   - We know the market resolved
   - Real trading has uncertainty

### Making Backtests More Realistic

Add conservative assumptions:
```yaml
# config/backtest_conservative.yaml
backtest:
  slippage_pct: 0.5        # Pessimistic
  fee_pct: 0.5             # Include fees
  partial_fill_pct: 80     # Assume 80% fill rate
  execution_failure_pct: 5  # 5% of trades fail
```

## Adjacent API Setup (Optional)

### 1. Get API Key
Sign up at: https://adjacent.finance/api

### 2. Configure
```bash
# Add to .env
ADJACENT_API_KEY="adj_..."
```

### 3. Test
```python
import os
import httpx

api_key = os.getenv("ADJACENT_API_KEY")

response = httpx.get(
    "https://api.adjacent.finance/v1/polymarket/markets",
    headers={"Authorization": f"Bearer {api_key}"}
)

print(response.status_code)  # Should be 200
```

## Using Your Own Recorded Data

If you've been running the paper trader with data recording:

### 1. Check Recordings
```bash
ls -lh data/recordings/
```

### 2. Find Markets
```bash
# See what markets you've recorded
zcat data/recordings/snapshots_*.jsonl.gz | \
    jq -r '.market_question' | \
    sort -u
```

### 3. Backtest
The backtester will automatically find and use your recorded data.

## Interpreting Results

### ✅ Green Flags
- Win rate >55% consistently
- Positive ROI across different market types
- Results similar between backtest and paper trading
- Strategy works in both bull and bear markets

### ⚠️ Yellow Flags
- Win rate 50-55% (marginal edge)
- High variance in results
- Works on some markets, fails on others
- Needs perfect execution to be profitable

### 🚫 Red Flags
- Win rate <50%
- Negative ROI overall
- Only 1-2 winning markets out of many
- Results dramatically different from paper trading

## Example Workflow

```bash
# 1. Find testable markets
python scripts/find_testable_markets.py

# 2. Test top 3 markets
python toolkit/execution-engine/src/execution_engine/backtester.py \
    --market market-1

python toolkit/execution-engine/src/execution_engine/backtester.py \
    --market market-2

python toolkit/execution-engine/src/execution_engine/backtester.py \
    --market market-3

# 3. Aggregate and analyze
# (Results saved to data/backtest_results/)

# 4. If results good (>55% win rate):
#    → Continue with paper trading
# 5. If results poor (<50% win rate):
#    → Adjust parameters and retest
```

## Next Steps After Backtesting

### If Results are Good (>55% Win Rate)
1. ✅ Run paper trading for 30 days
2. ✅ Compare paper trading to backtest
3. ✅ If both good → consider going live

### If Results are Mixed (50-55%)
1. 🔄 Test different parameters
2. 🔄 Focus on market types that work
3. 🔄 Refine signal logic

### If Results are Poor (<50%)
1. ⚠️ Don't trade this strategy
2. ⚠️ Go back to research
3. ⚠️ Test completely different approach

## Limitations Summary

**Backtesting ≠ Real Trading**

- ✅ Good for: Finding obviously bad strategies
- ✅ Good for: Parameter optimization
- ✅ Good for: Understanding strategy behavior

- ❌ Not enough: Must paper trade
- ❌ Not perfect: Real world has more friction
- ❌ Not guarantee: Past ≠ future

**Always validate with paper trading before live!**

## Troubleshooting

### "No historical data available"

Try:
1. Different market (use `find_testable_markets.py`)
2. Adjacent API (paid but reliable)
3. Wait and record your own data

### "Only X trades found"

- Normal if market had limited volatility
- Try markets with more volume
- Check if signals are too strict

### Results seem too good

- Check for look-ahead bias
- Verify slippage is included
- Test on out-of-sample markets
- Be skeptical!

---

**Remember**: @the_smart_ape made +86% with the RIGHT parameters and -50% with the WRONG ones. Backtest to find what works! 🎯


