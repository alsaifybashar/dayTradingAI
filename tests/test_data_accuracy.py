import requests
import yfinance as yf
import time
import sys

# Constants
API_URL = "http://localhost:8000/api/stock"
TICKERS = ["AAPL", "TSLA", "NVDA", "MSFT"]
TOLERANCE = 0.01  # 1% tolerance for price difference (due to slight timing diffs)

def get_real_price(ticker):
    """Fetches the real-time price directly from Yahoo Finance."""
    try:
        stock = yf.Ticker(ticker)
        # Try fast_info first (real-time-ish)
        price = stock.fast_info.last_price
        return price
    except Exception as e:
        print(f"Error fetching real price for {ticker}: {e}")
        return None

def get_api_price(ticker):
    """Fetches the price from our local Day Trading API."""
    try:
        response = requests.get(f"{API_URL}/{ticker}")
        if response.status_code == 200:
            data = response.json()
            return data.get("price")
        else:
            print(f"API Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"Error calling API for {ticker}: {e}")
        return None

def test_data_accuracy():
    print("="*60)
    print("🔍 RUNNING DATA ACCURACY TEST")
    print(f"Comparing Local API vs Direct Yahoo Finance Source")
    print("="*60)
    
    failures = []
    
    for ticker in TICKERS:
        print(f"\nChecking {ticker}...")
        
        # 1. Get Real Price
        real_price = get_real_price(ticker)
        if real_price is None:
            print(f"⚠️  Skipping {ticker}: Could not fetch real price.")
            continue
            
        # 2. Get API Price
        api_price = get_api_price(ticker)
        if api_price is None:
            print(f"❌  Failure {ticker}: API returned no data.")
            failures.append(ticker)
            continue
            
        # 3. Compare
        diff = abs(real_price - api_price)
        diff_percent = (diff / real_price) * 100
        
        print(f"   - Yahoo Direct:  ${real_price:,.2f}")
        print(f"   - Local API:     ${api_price:,.2f}")
        print(f"   - Difference:    ${diff:.4f} ({diff_percent:.4f}%)")
        
        if diff_percent <= TOLERANCE * 100:
            print(f"✅  MATCH: Price is accurate within {TOLERANCE*100}%")
        else:
            print(f"❌  MISMATCH: Difference exceeds tolerance!")
            failures.append(ticker)
            
    print("\n" + "="*60)
    if failures:
        print(f"🚨  TEST FAILED for: {', '.join(failures)}")
        sys.exit(1)
    else:
        print("🎉  TEST PASSED: All tickers match real-time data.")
        sys.exit(0)

if __name__ == "__main__":
    # Ensure backend is running first!
    try:
        requests.get("http://localhost:8000/health")
    except:
        print("🚨  CRITICAL: Backend is not running! Start it with 'python -m uvicorn backend.main:app' first.")
        sys.exit(1)
        
    test_data_accuracy()
