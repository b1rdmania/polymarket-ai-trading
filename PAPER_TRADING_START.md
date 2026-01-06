# 3-Model Paper Trading - Quick Start Guide

## What This Does

Runs **3 different trading strategies simultaneously** in paper trading mode:

### 1. **Conservative** 💎
- Only trades strongest signals (STRONG)
- Small positions ($200 max)
- Strict risk limits
- Kelly 0.15 (very cautious)
- **Best for**: Seeing if the core idea works

### 2. **Moderate** ⚖️
- Balanced approach (MODERATE signals)
- Medium positions ($500 max)
- Standard Kelly (0.25)
- **Best for**: Expected baseline performance

### 3. **Aggressive** 🚀
- Trades more frequently (WEAK+ signals)
- Larger positions ($800 max)
- Kelly 0.35
- **Best for**: Testing maximum throughput

## Why 3 Models?

@the_smart_ape's lesson:
> Conservative params: **+86% ROI** ✅  
> Aggressive params: **-50% ROI** ❌

**We don't know which will work best until we test!**

## Quick Start

### 1. Install Dependencies

```bash
cd /Users/andy/PolymarketTests/aztec-auction-analysis
pip3 install --user pyyaml
```

### 2. Start All 3 Models

```bash
python3 scripts/start_models.py
```

**Output**:
```
=============================================================
MULTI-MODEL PAPER TRADING LAUNCHER
=============================================================

Starting Model: CONSERVATIVE
✅ Config: config/active_conservative.yaml
✅ Started with PID: 12345

Starting Model: MODERATE  
✅ Config: config/active_moderate.yaml
✅ Started with PID: 12346

Starting Model: AGGRESSIVE
✅ Config: config/active_aggressive.yaml
✅ Started with PID: 12347

✅ All models running!
```

### 3. Monitor Performance

```bash
# One-time check
python3 scripts/monitor_models.py

# Continuous monitoring (refreshes every 30s)
python3 scripts/monitor_models.py --loop
```

**Example output**:
```
=============================================================
COMPARISON
=============================================================

Model           Trades     Win %      P&L             Today     
-------------------------------------------------------------
✅ conservative  8          75.0%      $+125.40        $+23.50
✅ moderate      15         60.0%      $+287.20        $+45.00
❌ aggressive    24         45.8%      $-52.10         $-18.00
-------------------------------------------------------------
TOTAL           47                    $+360.50        $+50.50
```

### 4. Stop All Models

```bash
python3 scripts/stop_models.py
```

## What Gets Recorded

### Separate Databases

Each model has its own database:
- `data/trades_conservative.db`
- `data/trades_moderate.db`
- `data/trades_aggressive.db`

### Separate Recordings

Market data recorded separately:
- `data/recordings_conservative/`
- `data/recordings_moderate/`
- `data/recordings_aggressive/`

### Separate Logs

Detailed logs for each:
- `logs/conservative/*.log`
- `logs/moderate/*.log`
- `logs/aggressive/*.log`

## After 30 Days

### 1. Check Results

```bash
python3 scripts/monitor_models.py
```

### 2. Analyze Best Performer

```bash
# Query specific model
sqlite3 data/trades_moderate.db

sqlite> SELECT COUNT(*), SUM(pnl), AVG(pnl) FROM trades WHERE status='CLOSED';
sqlite> SELECT * FROM trades ORDER BY pnl DESC LIMIT 10;  -- Best trades
sqlite> SELECT * FROM trades ORDER BY pnl ASC LIMIT 10;   -- Worst trades
```

### 3. Decision Matrix

| Model Results | Decision |
|--------------|----------|
| **All 3 profitable** | Pick best one, go live with small size |
| **1-2 profitable** | Use only profitable models live |
| **All 3 losing** | ❌ Don't go live, revise strategy |
| **Mixed** | Blend winning strategies |

## Model Differences

| Parameter | Conservative | Moderate | Aggressive |
|-----------|-------------|----------|------------|
| **Signal Strength** | STRONG only | MODERATE+ | WEAK+ (all) |
| **Longshot Threshold** | <25% | <30% | <35% |
| **Max Position** | $200 | $500 | $800 |
| **Max Exposure** | $1,000 | $2,000 | $3,000 |
| **Kelly Fraction** | 0.15 | 0.25 | 0.35 |
| **Check Interval** | 10 min | 5 min | 3 min |
| **Max Slippage** | 1.5% | 2.0% | 3.0% |

## Expected Behavior

### Conservative
- **Trades**: 2-5 per day
- **Win rate target**: >70%
- **P&L**: Steady but slow
- **Risk**: Lowest

### Moderate
- **Trades**: 5-10 per day
- **Win rate target**: >60%
- **P&L**: Balanced growth
- **Risk**: Medium

### Aggressive
- **Trades**: 10-20 per day
- **Win rate target**: >55%
- **P&L**: Fast but volatile
- **Risk**: Highest

## Troubleshooting

### Models won't start

```bash
# Check if already running
ps aux | grep systematic_trader

# Stop existing processes
python3 scripts/stop_models.py

# Try again
python3 scripts/start_models.py
```

### No trades happening

**Normal!** It may take hours/days before signals fire. Check:

```bash
# View logs
tail -f logs/moderate/*.log

# Look for "Found X signals"
```

### How to check if running

```bash
# Quick check
ps aux | grep systematic_trader

# Or check PID file
cat data/model_pids.txt
```

## Timeline

### Day 1-7: Setup Phase
- Models start recording
- First trades execute
- Verify everything works

### Week 2-3: Data Collection
- Models accumulate trades
- Patterns emerge
- Early performance indicators

### Week 4-5: Evaluation
- Statistical significance reached
- Clear winner may emerge
- Decision point approaching

### Day 30+: Go/No-Go
- Analyze 30-day results
- Pick winning model(s)
- Consider live trading

## The Race is On! 🏁

All 3 models compete head-to-head:
- Same markets
- Same time period
- Different strategies
- **Best one wins** and goes live

May the best model win! 🏆

---

## Commands Reference

```bash
# Start all models
python3 scripts/start_models.py

# Monitor (one-time)
python3 scripts/monitor_models.py

# Monitor (continuous)
python3 scripts/monitor_models.py --loop --interval 60

# Stop all models
python3 scripts/stop_models.py

# Check logs
tail -f logs/moderate/*.log

# Query database
sqlite3 data/trades_moderate.db "SELECT * FROM trades LIMIT 10"
```

---

**Ready to start?**

```bash
python3 scripts/start_models.py
```

Let the 30-day race begin! 🚀


