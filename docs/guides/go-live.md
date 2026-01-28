# Go-Live Checklist

## Pre-Launch Validation ✓

### Paper Trading Results
- [ ] Ran paper trading for minimum 30 days
- [ ] Win rate ≥ 55%
- [ ] Average profit per trade > average loss
- [ ] Max drawdown < 20%
- [ ] Sharpe ratio > 1.0
- [ ] No execution errors
- [ ] All risk limits respected

### System Validation
- [ ] All tests passing (`pytest`)
- [ ] Database working correctly
- [ ] Logging functioning
- [ ] Dashboard displaying data
- [ ] Emergency stop tested
- [ ] Backup system in place

### Security Checks
- [ ] Private key secured in `.env`
- [ ] `.env` in `.gitignore`
- [ ] Backup of private key stored safely
- [ ] Wallet funded with initial capital
- [ ] Test transaction successful

## Phase 1: Micro Positions (Week 1-2)

### Configuration
```yaml
# config/trading_micro.yaml
trading:
  mode: live

risk:
  max_position_usd: 100
  max_total_exposure_usd: 300
  max_positions: 3
  max_drawdown_pct: 15.0

execution:
  dry_run: false  # IMPORTANT: Set to false for live trading
```

### Launch Steps

1. **Final Confirmation**:
   ```bash
   python agents/systematic_trader.py --config config/trading_micro.yaml
   ```

2. **Monitor Hourly**:
   - Check dashboard every hour
   - Verify trades executing correctly
   - Watch for any errors in logs

3. **Daily Review**:
   - Total P&L
   - Number of trades
   - Any risk limit breaches
   - Slippage analysis

### Success Criteria
- [ ] At least 5 trades executed
- [ ] No technical errors
- [ ] Risk limits respected
- [ ] P&L within expectations

### Red Flags (Stop if seen)
- ❌ Trades not executing
- ❌ Risk limits violated
- ❌ Unexpected losses > $50
- ❌ System crashes/errors

## Phase 2: Small Positions (Week 3-4)

### Configuration
```yaml
# config/trading_small.yaml
risk:
  max_position_usd: 250
  max_total_exposure_usd: 750
  max_positions: 5
```

### Transition Checklist
- [ ] Phase 1 completed successfully
- [ ] No critical issues encountered
- [ ] P&L positive or within acceptable drawdown
- [ ] Comfortable with system operation

### Monitor Daily
- Total exposure
- Win rate tracking
- Slippage vs paper trading
- Performance comparison

## Phase 3: Full Positions (Week 5+)

### Configuration
```yaml
# config/trading.yaml
risk:
  max_position_usd: 500
  max_total_exposure_usd: 2000
  max_positions: 10
```

### Transition Checklist
- [ ] Phase 2 completed successfully
- [ ] Cumulative performance meets targets
- [ ] No major incidents
- [ ] System stable and reliable

### Ongoing Monitoring

#### Daily
- Dashboard check
- P&L review
- Open positions status
- Log review for errors

#### Weekly
- Performance report
- Risk metrics analysis
- Strategy effectiveness
- Rebalancing needs

#### Monthly
- Full performance review
- Strategy optimization
- Risk limit adjustments
- Capacity analysis

## Key Performance Indicators

Track these metrics continuously:

| Metric | Target | Current | Action if Outside Range |
|--------|--------|---------|-------------------------|
| Win Rate | > 55% | TBD | Review signal quality |
| Avg Profit/Trade | > $25 | TBD | Adjust position sizing |
| Sharpe Ratio | > 1.0 | TBD | Evaluate risk/reward |
| Max Drawdown | < 20% | TBD | Emergency stop if > 25% |
| Execution Rate | > 98% | TBD | Check connectivity |
| Daily Uptime | > 99% | TBD | Improve monitoring |

## Emergency Procedures

### When to Emergency Stop

Trigger emergency stop if:
- Drawdown exceeds 25%
- Unexpected losses > $200 in one day
- System behaving erratically
- Security concerns
- Major market disruption

### How to Emergency Stop

```bash
python scripts/emergency_stop.py --reason "Describe reason here"
```

This will:
1. Close all open positions
2. Cancel pending orders
3. Create shutdown flag
4. Log incident

### Recovery Process

1. **Investigate** what went wrong
2. **Fix** the issue
3. **Test** in paper mode again
4. **Validate** fix works
5. **Resume** trading at lower scale

## Scaling Beyond Initial Phase

### When to Increase Capital

Consider increasing capital allocation if:
- [ ] 3+ months of profitable live trading
- [ ] Sharpe ratio consistently > 1.5
- [ ] Drawdowns well managed (< 15%)
- [ ] System reliability proven
- [ ] Strategy still has edge

### Capital Scaling Plan

| Phase | Capital | Max Position | Timeline |
|-------|---------|--------------|----------|
| Micro | $500 | $100 | Week 1-2 |
| Small | $2,000 | $250 | Week 3-4 |
| Medium | $5,000 | $500 | Month 2-3 |
| Full | $10,000+ | $1,000 | Month 4+ |

### Risk Management as You Scale

- Keep max drawdown limit constant (20-25%)
- Maintain position size as % of capital
- Don't exceed 10 simultaneous positions
- Preserve Kelly fraction (0.25)
- Regular strategy reviews

## Post-Launch Documentation

### Daily Log Template

```markdown
## Date: [YYYY-MM-DD]

### Performance
- Total P&L: $X.XX
- Today's P&L: $X.XX
- Win Rate: XX%
- Trades: X

### Observations
- [Any notable events]
- [Market conditions]
- [System performance]

### Actions Taken
- [Any manual interventions]
- [Configuration changes]
- [Issues resolved]

### Tomorrow's Plan
- [Monitoring focus]
- [Any adjustments needed]
```

## Support Contacts

- **Technical Issues**: Check logs first
- **Emergency**: Run emergency stop script
- **Strategy Questions**: Review research docs

## Final Reminders

- 🔒 **Security**: Never share private keys
- 📊 **Monitoring**: Check daily, no exceptions
- 🛑 **Emergency Stop**: Don't hesitate to use it
- 📝 **Documentation**: Log everything
- 🧪 **Testing**: When in doubt, test in paper mode first

---

## Sign-Off

Before going live, confirm:

- [ ] I have read and understand this entire document
- [ ] I have completed all pre-launch validation
- [ ] I am comfortable with the risk of loss
- [ ] I know how to emergency stop
- [ ] I have secure backups of all keys
- [ ] I will monitor the system actively

**Date**: _______________
**Signature**: _______________

---

Good luck! 🚀


