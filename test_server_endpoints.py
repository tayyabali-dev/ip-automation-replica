#!/usr/bin/env python3
"""
Simple test to check what endpoints are available on the server.
"""

import asyncio
import aiohttp

async def test_server_endpoints():
    """Test various endpoints to see what's available."""
    
    base_urls = [
        "http://localhost:8000",
        "http://localhost:3000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:3000"
    ]
    
    endpoints = [
        "/",
        "/docs",
        "/health",
        "/auth/login",
        "/enhanced-applications"
    ]
    
    async with aiohttp.ClientSession() as session:
        for base_url in base_urls:
            print(f"\n🔍 Testing {base_url}")
            print("-" * 40)
            
            for endpoint in endpoints:
                url = f"{base_url}{endpoint}"
                try:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=2)) as response:
                        print(f"✅ {endpoint}: {response.status}")
                        if response.status == 200 and endpoint == "/":
                            text = await response.text()
                            if "FastAPI" in text or "API" in text:
                                print(f"   Found API server at {base_url}")
                except Exception as e:
                    print(f"❌ {endpoint}: {str(e)}")
            
            # If we found a working server, break
            try:
                async with session.get(f"{base_url}/docs", timeout=aiohttp.ClientTimeout(total=2)) as response:
                    if response.status == 200:
                        print(f"\n🎉 Found working API server at {base_url}")
                        return base_url
            except:
                pass
    
    print("\n❌ No working API server found")
    return None

if __name__ == "__main__":
    result = asyncio.run(test_server_endpoints())
    if result:
        print(f"\nUse this base URL: {result}")