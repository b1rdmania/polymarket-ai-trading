#!/usr/bin/env python3
"""
Real Historical Backtest

This fetches ACTUAL Polymarket data and runs our mean reversion strategy.
We'll use multiple approaches to get data.
"""

import asyncio
import httpx
import json
from datetime import datetime
from typing import List, Dict
from collections import defaultdict

# Strategy parameters
LONGSHOT_THRESHOLD = 0.30
TAKE_PROFIT_PCT = 10.0
STOP_LOSS_PCT = 20.0
POSITION_SIZE = 100  # shares


async def fetch_market_info(slug: str) -> Dict:
    """Get market info from Gamma API."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"https://gamma-api.polymarket.com/markets/{slug}"
        )
        if response.status_code == 200:
            return response.json()
    return None


async def fetch_price_snapshots_clob(token_id: str) -> List[Dict]:
    """Try to get price history from CLOB API."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(
                "https://clob.polymarket.com/prices-history",
                params={
                    "market": token_id,
                    "interval": "1h",
                    "fidelity": 200
                }
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("history", [])
        except Exception as e:
            print(f"CLOB API error: {e}")
    return []


async def fetch_current_price(token_id: str) -> float:
    """Get current price from CLOB."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(
                f"https://clob.polymarket.com/midpoint?token_id={token_id}"
            )
            if response.status_code == 200:
                data = response.json()
                return float(data.get("mid", 0))
        except Exception as e:
            print(f"Price fetch error: {e}")
    return 0


def simulate_mean_reversion(data: List[Dict], market_name: str) -> Dict:
    """
    Simulate mean reversion strategy on historical data.
    
    Entry: Price < 30% (longshot)
    Exit: +10% profit OR -20% stop loss
    """
    if not data:
        return {
            "market": market_name,
            "error": "No data available",
            "total_trades": 0,
            "win_rate": 0,
            "total_pnl": 0
        }
    
    trades = []
    position = None
    
    for i, point in enumerate(data):
        timestamp = point.get('t', 0)
        price = point.get('p', 0)
        
        if price == 0:
            continue
        
        # Entry logic
        if position is None and price < LONGSHOT_THRESHOLD:
            position = {
                'entry_price': price,
                'entry_time': timestamp,
                'entry_index': i,
                'shares': POSITION_SIZE
            }
        
        # Exit logic
        elif position is not None:
            entry_price = position['entry_price']
            
            # Take profit
            if price >= entry_price * (1 + TAKE_PROFIT_PCT/100):
                pnl = (price - entry_price) * POSITION_SIZE
                trades.append({
                    'entry_price': entry_price,
                    'exit_price': price,
                    'pnl': pnl,
                    'entry_time': position['entry_time'],
                    'exit_time': timestamp,
                    'bars_held': i - position['entry_index'],
                    'exit_reason': 'take_profit'
                })
                position = None
            
            # Stop loss
            elif price <= entry_price * (1 - STOP_LOSS_PCT/100):
                pnl = (price - entry_price) * POSITION_SIZE
                trades.append({
                    'entry_price': entry_price,
                    'exit_price': price,
                    'pnl': pnl,
                    'entry_time': position['entry_time'],
                    'exit_time': timestamp,
                    'bars_held': i - position['entry_index'],
                    'exit_reason': 'stop_loss'
                })
                position = None
    
    # Close remaining position
    if position is not None and data:
        last_price = data[-1].get('p', 0)
        if last_price > 0:
            pnl = (last_price - position['entry_price']) * POSITION_SIZE
            trades.append({
                'entry_price': position['entry_price'],
                'exit_price': last_price,
                'pnl': pnl,
                'entry_time': position['entry_time'],
                'exit_time': data[-1].get('t', 0),
                'bars_held': len(data) - position['entry_index'],
                'exit_reason': 'market_close'
            })
    
    # Calculate metrics
    if not trades:
        return {
            "market": market_name,
            "total_trades": 0,
            "win_rate": 0,
            "total_pnl": 0,
            "note": "No entry signals (price never went below 30%)"
        }
    
    winners = [t for t in trades if t['pnl'] > 0]
    total_pnl = sum(t['pnl'] for t in trades)
    avg_pnl = total_pnl / len(trades)
    avg_bars = sum(t['bars_held'] for t in trades) / len(trades)
    
    return {
        "market": market_name,
        "total_trades": len(trades),
        "winning_trades": len(winners),
        "losing_trades": len(trades) - len(winners),
        "win_rate": len(winners) / len(trades) * 100,
        "total_pnl": total_pnl,
        "avg_pnl_per_trade": avg_pnl,
        "avg_bars_held": avg_bars,
        "best_trade": max(t['pnl'] for t in trades),
        "worst_trade": min(t['pnl'] for t in trades),
        "trades": trades
    }


async def backtest_market(slug: str):
    """Backtest a single market."""
    print(f"\n{'='*70}")
    print(f"BACKTESTING: {slug}")
    print('='*70)
    
    # Get market info
    print("Fetching market info...")
    market = await fetch_market_info(slug)
    
    if not market:
        print(f"❌ Could not fetch market info")
        return None
    
    question = market.get('question', 'Unknown')
    token_ids = market.get('clobTokenIds', [])
    
    if not token_ids:
        print(f"❌ No token IDs available")
        return None
    
    print(f"Market: {question[:60]}...")
    print(f"Token ID: {token_ids[0][:20]}...")
    
    # Try to get historical data
    print("\nFetching historical data from CLOB API...")
    history = await fetch_price_snapshots_clob(token_ids[0])
    
    if history:
        print(f"✅ Found {len(history)} historical data points!")
        
        # Show data range
        if history:
            first_time = datetime.fromtimestamp(history[0].get('t', 0))
            last_time = datetime.fromtimestamp(history[-1].get('t', 0))
            print(f"Data range: {first_time.strftime('%Y-%m-%d')} to {last_time.strftime('%Y-%m-%d')}")
            
            # Show price range
            prices = [p.get('p', 0) for p in history if p.get('p', 0) > 0]
            if prices:
                print(f"Price range: {min(prices):.1%} to {max(prices):.1%}")
        
        # Run backtest
        print("\n🤖 Running mean reversion strategy...")
        print(f"Strategy: Buy < {LONGSHOT_THRESHOLD:.0%}, TP at +{TAKE_PROFIT_PCT}%, SL at -{STOP_LOSS_PCT}%\n")
        
        results = simulate_mean_reversion(history, question)
        return results
    else:
        print(f"❌ No historical data available from CLOB API")
        
        # Try to get current price at least
        print("\nAttempting to get current price...")
        current_price = await fetch_current_price(token_ids[0])
        if current_price:
            print(f"Current price: {current_price:.1%}")
            if current_price < LONGSHOT_THRESHOLD:
                print(f"💡 This IS a longshot opportunity (< {LONGSHOT_THRESHOLD:.0%})!")
            else:
                print(f"📊 Not a longshot (> {LONGSHOT_THRESHOLD:.0%})")
        
        return None


def print_results(results: Dict):
    """Pretty print backtest results."""
    if not results or "error" in results or results.get("total_trades", 0) == 0:
        print(f"\n⚠️  {results.get('note', results.get('error', 'No trades'))}")
        return
    
    print(f"\n{'='*70}")
    print("BACKTEST RESULTS")
    print('='*70)
    print(f"\nMarket: {results['market'][:60]}...")
    print(f"\nTotal Trades: {results['total_trades']}")
    print(f"Winners: {results['winning_trades']} | Losers: {results['losing_trades']}")
    print(f"Win Rate: {results['win_rate']:.1f}%")
    print(f"Total P&L: ${results['total_pnl']:.2f}")
    print(f"Avg P&L per Trade: ${results['avg_pnl_per_trade']:.2f}")
    print(f"Avg Hold Time: {results['avg_bars_held']:.0f} periods")
    print(f"Best Trade: ${results['best_trade']:.2f}")
    print(f"Worst Trade: ${results['worst_trade']:.2f}")
    
    if results['total_pnl'] > 0:
        print(f"\n✅ Profitable strategy! (+${results['total_pnl']:.2f})")
    else:
        print(f"\n❌ Losing strategy (${results['total_pnl']:.2f})")
    
    # Show individual trades
    trades = results.get('trades', [])
    if trades:
        print(f"\nIndividual Trades (showing first 10):")
        print("-"*70)
        for i, trade in enumerate(trades[:10], 1):
            emoji = "💰" if trade['pnl'] > 0 else "📉"
            reason = trade['exit_reason'].replace('_', ' ').title()
            print(f"{i:2}. Entry: {trade['entry_price']:5.1%} → "
                  f"Exit: {trade['exit_price']:5.1%} = ${trade['pnl']:+7.2f} {emoji} "
                  f"({reason})")


async def main():
    """Run backtests on multiple markets."""
    
    print("="*70)
    print("POLYMARKET HISTORICAL BACKTEST")
    print("="*70)
    print("\nStrategy: Mean Reversion on Longshots")
    print(f"  - Entry: Price < {LONGSHOT_THRESHOLD:.0%}")
    print(f"  - Take Profit: +{TAKE_PROFIT_PCT}%")
    print(f"  - Stop Loss: -{STOP_LOSS_PCT}%")
    print(f"  - Position Size: {POSITION_SIZE} shares")
    
    # Markets to test (mix of historical interesting ones)
    test_markets = [
        "will-trump-win-the-2020-us-presidential-election",  # Huge volume
        "will-btc-break-15k-before-2021-1",  # Volatile
        "will-airbnb-begin-publicly-trading-before-jan-1-2021",  # Binary event
    ]
    
    all_results = []
    
    for slug in test_markets:
        result = await backtest_market(slug)
        if result:
            all_results.append(result)
            print_results(result)
        
        # Rate limit
        await asyncio.sleep(1)
    
    # Aggregate results
    if all_results:
        print(f"\n{'='*70}")
        print("AGGREGATE RESULTS")
        print('='*70)
        
        total_trades = sum(r['total_trades'] for r in all_results)
        total_winners = sum(r['winning_trades'] for r in all_results)
        total_pnl = sum(r['total_pnl'] for r in all_results)
        
        print(f"\nMarkets Tested: {len(all_results)}")
        print(f"Total Trades: {total_trades}")
        print(f"Overall Win Rate: {total_winners/total_trades*100:.1f}%")
        print(f"Total P&L: ${total_pnl:.2f}")
        print(f"Average P&L per Market: ${total_pnl/len(all_results):.2f}")
        
        if total_pnl > 0:
            print(f"\n✅ Overall Profitable!")
        else:
            print(f"\n❌ Overall Unprofitable")
        
        print(f"\n{'='*70}\n")
    else:
        print("\n❌ No markets had sufficient data for backtesting")
        print("\nAs @the_smart_ape warned: Polymarket's historical API is incomplete.")
        print("\nOptions:")
        print("  1. Get Adjacent API key (paid but works)")
        print("  2. Start paper trading to record your own data")
        print("  3. Use synthetic demo to validate strategy logic")


if __name__ == "__main__":
    asyncio.run(main())


