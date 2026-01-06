#!/usr/bin/env python3
"""
Find Recent Resolved Markets for Backtesting

Since Polymarket's historical API is incomplete, we'll focus on:
1. Recently resolved markets (better data availability)
2. Popular markets (more likely to have data)
3. Markets we can still query
"""

import asyncio
import httpx
import logging
from datetime import datetime, timedelta
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def find_testable_markets() -> List[Dict]:
    """Find markets we can potentially backtest."""
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Get active markets with high volume (we can still analyze historical behavior)
        response = await client.get(
            "https://gamma-api.polymarket.com/markets",
            params={
                "active": "true",
                "_limit": 100,
                "_sort": "volume24hr",
                "_order": "DESC"
            }
        )
        
        if response.status_code != 200:
            logger.error("Failed to fetch markets")
            return []
        
        all_markets = response.json()
        
        # Filter for testable markets
        testable = []
        
        for market in all_markets:
            # Check criteria
            volume = float(market.get("volume", 0) or 0)
            volume_24h = float(market.get("volume24hr", 0) or 0)
            end_date_str = market.get("endDate")
            
            if not end_date_str:
                continue
            
            try:
                end_date = datetime.fromisoformat(end_date_str.replace("Z", "+00:00"))
            except:
                continue
            
            # Want markets that:
            # 1. Active (still trading)
            # 2. Have decent volume (>$10k)
            # 3. Have token IDs (needed for data)
            # 4. End date in future (so we can analyze volatility)
            
            days_until_close = (end_date - datetime.now(end_date.tzinfo)).days
            
            if days_until_close > 0 and volume > 10000 and market.get("clobTokenIds"):
                testable.append({
                    "slug": market.get("slug"),
                    "question": market.get("question"),
                    "volume": volume,
                    "volume_24h": volume_24h,
                    "end_date": end_date_str,
                    "days_until_close": days_until_close,
                    "token_ids": market.get("clobTokenIds"),
                })
        
        # Sort by volume (most liquid first)
        testable.sort(key=lambda x: x["volume"], reverse=True)
        
        return testable


async def test_data_availability(market_slug: str, token_id: str) -> bool:
    """Check if we can actually get historical data for this market."""
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(
                "https://clob.polymarket.com/prices-history",
                params={
                    "market": token_id,
                    "interval": "1h",
                    "fidelity": 100
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                history = data.get("history", [])
                
                if len(history) > 10:  # At least 10 data points
                    logger.info(f"✅ {market_slug}: {len(history)} data points available")
                    return True
                else:
                    logger.warning(f"⚠️  {market_slug}: Only {len(history)} data points")
                    return False
            
        except Exception as e:
            logger.error(f"❌ {market_slug}: {e}")
    
    return False


async def main():
    """Find and test markets."""
    
    print("\n" + "="*60)
    print("FINDING TESTABLE MARKETS")
    print("="*60 + "\n")
    
    logger.info("Searching for recently resolved markets...")
    markets = await find_testable_markets()
    
    logger.info(f"Found {len(markets)} potentially testable markets")
    
    print("\nTop 10 Markets by Volume:")
    print("-" * 60)
    
    testable_count = 0
    testable_markets = []
    
    for i, market in enumerate(markets[:20], 1):  # Check top 20
        print(f"\n{i}. {market['question'][:60]}...")
        print(f"   Volume: ${market['volume']:,.0f} (24h: ${market['volume_24h']:,.0f})")
        print(f"   Closes: in {market['days_until_close']} days")
        print(f"   Slug: {market['slug']}")
        
        # Test data availability
        has_data = await test_data_availability(
            market['slug'],
            market['token_ids'][0]
        )
        
        if has_data:
            testable_count += 1
            testable_markets.append(market)
        
        # Rate limit
        await asyncio.sleep(0.5)
    
    print("\n" + "="*60)
    print(f"TESTABLE MARKETS: {testable_count}/{len(markets[:20])}")
    print("="*60)
    
    if testable_markets:
        print("\n✅ Markets ready for backtesting:\n")
        for market in testable_markets[:10]:
            print(f"python toolkit/execution-engine/src/execution_engine/backtester.py \\")
            print(f"    --market {market['slug']}\n")
    else:
        print("\n⚠️  No markets with sufficient historical data found.")
        print("\nOptions:")
        print("1. Get Adjacent API key (paid) for better historical data")
        print("2. Use recorded data (run live recording first)")
        print("3. Wait for more markets to close")
    
    # Save results
    import json
    with open("data/testable_markets.json", 'w') as f:
        json.dump(testable_markets, f, indent=2, default=str)
    
    print(f"\n📁 Results saved to: data/testable_markets.json")


if __name__ == "__main__":
    asyncio.run(main())

