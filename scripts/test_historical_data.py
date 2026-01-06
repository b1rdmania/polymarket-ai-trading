#!/usr/bin/env python3
"""Test if we can get historical data for a specific market"""

import asyncio
import httpx

async def main():
    # Try the Trump 2020 market - highest volume
    token_id = "44804726753601178293652604511461891232965799888489574021036312274240304608626"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print(f"Fetching historical data for token: {token_id[:20]}...")
        
        response = await client.get(
            "https://clob.polymarket.com/prices-history",
            params={
                "market": token_id,
                "interval": "1d",  # Daily data
                "fidelity": 200     # Max points
            }
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            history = data.get("history", [])
            
            print(f"\n✅ Found {len(history)} historical data points!")
            
            if history:
                print("\nFirst 5 data points:")
                for point in history[:5]:
                    print(f"  Time: {point.get('t')}, Price: {point.get('p')}")
                
                print(f"\nLast 5 data points:")
                for point in history[-5:]:
                    print(f"  Time: {point.get('t')}, Price: {point.get('p')}")
        else:
            print(f"❌ Failed: {response.text}")

asyncio.run(main())


