#!/usr/bin/env python3
"""
Example: Find volatile markets on Polymarket

This script demonstrates how to use the polymarket-data library
to find markets with large price movements - potential emotional
volatility arbitrage opportunities.
"""

import asyncio
from polymarket_data import PolymarketClient


async def main():
    client = PolymarketClient()
    
    print("=" * 60)
    print("🎯 POLYMARKET VOLATILITY SCANNER")
    print("=" * 60)
    
    # 1. Get trending markets
    print("\n📈 Top 5 Trending Markets (24h volume):")
    print("-" * 40)
    trending = await client.get_trending(timeframe="24h", limit=5)
    for i, m in enumerate(trending, 1):
        print(f"{i}. {m.question[:50]}...")
        print(f"   Volume: ${m.volume_24h:,.0f}")
    
    # 2. Find big movers
    print("\n🚨 Markets Moving >5% (Potential Overreaction):")
    print("-" * 40)
    movers = await client.detect_movers(threshold_pct=5.0, limit=5)
    
    if movers:
        for m in movers:
            direction = "📈" if m["direction"] == "up" else "📉"
            print(f"{direction} {m['market'].question[:45]}...")
            print(f"   Change: {m['price_change_pct']:+.1f}%")
    else:
        print("   No major movers found (markets are calm)")
    
    # 3. Check Politics category
    print("\n🏛️ Political Markets:")
    print("-" * 40)
    politics = await client.get_by_category("Politics", limit=5)
    for m in politics:
        print(f"• {m.question[:55]}...")
    
    # 4. Markets closing soon
    print("\n⏰ Closing Within 48h (Near-Resolution Efficiency):")
    print("-" * 40)
    closing = await client.get_closing_soon(hours=48, limit=5)
    for m in closing:
        end = m.end_date.strftime("%b %d %H:%M") if m.end_date else "?"
        print(f"• {m.question[:45]}... → {end}")
    
    print("\n" + "=" * 60)
    print("✅ Scan complete. Use these signals for mean reversion plays.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
