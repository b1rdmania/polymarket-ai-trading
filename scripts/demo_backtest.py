#!/usr/bin/env python3
"""
Demo Backtester with Synthetic Data

Since Polymarket's historical API returns no data (as @the_smart_ape warned),
this demonstrates the backtester with synthetic market data.

Real backtesting options:
1. Adjacent API (paid service)
2. Record your own data with DataRecorder
3. Wait for Polymarket to improve their API
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Dict


def generate_synthetic_market_data(
    days: int = 30,
    base_price: float = 0.45,
    volatility: float = 0.15
) -> list:
    """
    Generate synthetic market data that simulates mean-reverting behavior.
    
    This simulates:
    - Random price movements
    - Occasional "longshot" opportunities (price < 0.30)
    - Mean reversion back to ~50%
    """
    data = []
    current_price = base_price
    start_time = datetime.now() - timedelta(days=days)
    
    for hour in range(days * 24):
        timestamp = start_time + timedelta(hours=hour)
        
        # Random walk with mean reversion
        drift = (0.50 - current_price) * 0.05  # Pull toward 50%
        shock = random.gauss(0, volatility / 24)  # Random shock
        
        current_price = max(0.05, min(0.95, current_price + drift + shock))
        
        data.append({
            "t": int(timestamp.timestamp()),
            "p": round(current_price, 4)
        })
    
    return data


def simulate_mean_reversion_strategy(data: List[Dict]) -> Dict:
    """
    Simulate a simple mean reversion strategy.
    
    Rules:
    - Buy when price < 0.30 (longshot)
    - Sell at +10% gain OR -20% stop loss
    - Track all trades
    """
    trades = []
    position = None
    
    for i, point in enumerate(data):
        price = point['p']
        timestamp = datetime.fromtimestamp(point['t'])
        
        # Entry logic: Buy longshots
        if position is None and price < 0.30:
            position = {
                'entry_price': price,
                'entry_time': timestamp,
                'shares': 100
            }
        
        # Exit logic: Check stops
        elif position is not None:
            entry_price = position['entry_price']
            
            # Take profit at +10%
            if price >= entry_price * 1.10:
                pnl = (price - entry_price) * position['shares']
                trades.append({
                    'entry_price': entry_price,
                    'exit_price': price,
                    'pnl': pnl,
                    'entry_time': position['entry_time'],
                    'exit_time': timestamp
                })
                position = None
            
            # Stop loss at -20%
            elif price <= entry_price * 0.80:
                pnl = (price - entry_price) * position['shares']
                trades.append({
                    'entry_price': entry_price,
                    'exit_price': price,
                    'pnl': pnl,
                    'entry_time': position['entry_time'],
                    'exit_time': timestamp
                })
                position = None
    
    # Close any remaining position
    if position is not None:
        last_price = data[-1]['p']
        pnl = (last_price - position['entry_price']) * position['shares']
        trades.append({
            'entry_price': position['entry_price'],
            'exit_price': last_price,
            'pnl': pnl,
            'entry_time': position['entry_time'],
            'exit_time': datetime.fromtimestamp(data[-1]['t'])
        })
    
    # Calculate metrics
    total_pnl = sum(t['pnl'] for t in trades)
    winning_trades = [t for t in trades if t['pnl'] > 0]
    
    return {
        'market': 'demo-synthetic-market',
        'total_trades': len(trades),
        'winning_trades': len(winning_trades),
        'win_rate': len(winning_trades) / len(trades) * 100 if trades else 0,
        'total_pnl': total_pnl,
        'trades': trades
    }


async def demo_backtest():
    """Run a demo backtest with synthetic data."""
    
    print("="*70)
    print("BACKTESTING DEMO")
    print("="*70)
    print("\n⚠️  Using SYNTHETIC data (Polymarket's historical API is empty)")
    print("Real backtesting requires:")
    print("  1. Adjacent API key (paid)")
    print("  2. Your own recorded data (run DataRecorder)")
    print("  3. Wait for Polymarket API improvements")
    print("\n" + "="*70 + "\n")
    
    # Generate synthetic data
    print("📊 Generating synthetic market data...")
    market_data = generate_synthetic_market_data(days=30, volatility=0.20)
    
    # Show some sample data
    print(f"Generated {len(market_data)} hourly data points\n")
    print("Sample prices:")
    for i, point in enumerate(market_data[::168], 1):  # Weekly samples
        dt = datetime.fromtimestamp(point["t"])
        print(f"  Week {i}: {point['p']:.1%} ({dt.strftime('%Y-%m-%d')})")
    
    # Simulate trading
    print("\n🤖 Simulating mean reversion strategy...\n")
    print("Strategy Rules:")
    print("  - Buy when price < 30% (longshots)")
    print("  - Take profit at +10%")
    print("  - Stop loss at -20%")
    print()
    
    results = simulate_mean_reversion_strategy(market_data)
    
    # Print results
    print("="*70)
    print("BACKTEST RESULTS")
    print("="*70)
    print(f"\nMarket: {results['market']}")
    print(f"Total Trades: {results['total_trades']}")
    print(f"Winning Trades: {results['winning_trades']}")
    print(f"Win Rate: {results['win_rate']:.1f}%")
    print(f"Total P&L: ${results['total_pnl']:.2f}")
    
    if results['total_pnl'] > 0:
        print(f"\n✅ Strategy was profitable!")
    else:
        print(f"\n❌ Strategy lost money")
    
    print("\n" + "="*70)
    
    # Show individual trades
    if results['trades']:
        print("\nIndividual Trades (first 10):")
        print("-"*70)
        for i, trade in enumerate(results['trades'][:10], 1):
            pnl_symbol = "💰" if trade['pnl'] > 0 else "📉"
            print(f"{i}. Entry: {trade['entry_price']:.2%} → "
                  f"Exit: {trade['exit_price']:.2%} | "
                  f"P&L: ${trade['pnl']:+.2f} {pnl_symbol}")
    
    print("\n" + "="*70)
    print("\n💡 Next Steps:")
    print("  1. Get Adjacent API key for real historical data")
    print("  2. Or run paper trader with DataRecorder to build your own dataset")
    print("  3. Then re-run this backtest on REAL market data")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(demo_backtest())

