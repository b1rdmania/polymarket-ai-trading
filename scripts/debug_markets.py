#!/usr/bin/env python3
"""Quick debug script to see what markets are available"""

import asyncio
import httpx
import json

async def main():
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Get any markets
        response = await client.get(
            "https://gamma-api.polymarket.com/markets",
            params={
                "_limit": 5
            }
        )
        
        print("Status:", response.status_code)
        data = response.json()
        print(f"\nFound {len(data)} markets")
        
        for i, market in enumerate(data, 1):
            print(f"\n{i}. {market.get('question', 'No question')[:80]}")
            print(f"   Slug: {market.get('slug')}")
            print(f"   Volume: ${float(market.get('volume', 0)):,.0f}")
            print(f"   Active: {market.get('active')}")
            print(f"   Closed: {market.get('closed')}")
            print(f"   End Date: {market.get('endDate')}")
            print(f"   Token IDs: {market.get('clobTokenIds')}")

asyncio.run(main())


