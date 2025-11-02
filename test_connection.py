#!/usr/bin/env python3
"""
Test script to verify API connections and configuration
"""

import os
from dotenv import load_dotenv
from src.config import Config
from src.market_data import AlphaVantageClient
from src.news_analysis import NewsClient

load_dotenv()

def test_config():
    """Test configuration"""
    print("=" * 50)
    print("Testing Configuration")
    print("=" * 50)

    try:
        Config.validate()
        print("✓ Configuration is valid")
        print(f"  - Alpha Vantage API Key: {'*' * 20}{Config.ALPHA_VANTAGE_API_KEY[-4:]}")
        print(f"  - NewsData API Key: {'*' * 20}{Config.NEWSDATA_API_KEY[-4:]}")
        return True
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False


def test_alpha_vantage():
    """Test Alpha Vantage connection"""
    print("\n" + "=" * 50)
    print("Testing Alpha Vantage Connection")
    print("=" * 50)

    try:
        client = AlphaVantageClient()
        print("Fetching current price for AAPL...")

        result = client.get_current_price("AAPL")

        print("✓ Alpha Vantage connection successful")
        print(f"  - Symbol: {result['symbol']}")
        print(f"  - Price: ${result['price']}")
        print(f"  - Timestamp: {result['timestamp']}")
        return True
    except Exception as e:
        print(f"✗ Alpha Vantage connection failed: {e}")
        return False


def test_newsdata():
    """Test NewsData.io connection"""
    print("\n" + "=" * 50)
    print("Testing NewsData.io Connection")
    print("=" * 50)

    try:
        client = NewsClient()
        print("Fetching news about AAPL...")

        result = client.get_financial_news("AAPL", limit=5)

        print("✓ NewsData.io connection successful")
        print(f"  - Articles retrieved: {len(result)}")
        if result:
            print(f"  - Latest article: {result[0]['title'][:50]}...")
        return True
    except Exception as e:
        print(f"✗ NewsData.io connection failed: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 50)
    print("MCP Trading Server - Connection Test")
    print("=" * 50 + "\n")

    results = []

    # Test configuration
    results.append(("Configuration", test_config()))

    # Test Alpha Vantage
    results.append(("Alpha Vantage", test_alpha_vantage()))

    # Test NewsData.io
    results.append(("NewsData.io", test_newsdata()))

    # Print summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)

    for name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status} - {name}")

    # Overall result
    all_passed = all(result[1] for result in results)

    print("\n" + "=" * 50)
    if all_passed:
        print("✓ All tests passed! Server is ready to use.")
    else:
        print("✗ Some tests failed. Please check your configuration.")
    print("=" * 50 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
