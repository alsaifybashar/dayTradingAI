from backend.config import config
import requests
import yfinance as yf
import random
from datetime import datetime

class MarketService:
    def __init__(self):
        self.polygon_api_key = config.POLYGON_IO_API_KEY
        self.use_mock = config.USE_MOCK_DATA

    def get_stock_data(self, ticker: str):
        """
        Fetches stock data. Tries Polygon first if key exists, then YFinance, or Mock.
        """
        if self.use_mock:
            return self._get_mock_data(ticker)
        
        if self.polygon_api_key:
            try:
                return self._get_polygon_data(ticker)
            except Exception as e:
                print(f"Polygon error: {e}. Falling back to YFinance.")
        
        return self._get_yfinance_data(ticker)

    def _get_polygon_data(self, ticker: str):
        # Example: Previous close
        url = f"https://api.polygon.io/v2/aggs/ticker/{ticker.upper()}/prev?adjusted=true&apiKey={self.polygon_api_key}"
        response = requests.get(url)
        data = response.json()
        if data.get('resultsCount', 0) > 0:
            result = data['results'][0]
            return {
                "symbol": ticker.upper(),
                "price": result.get('c'),
                "open": result.get('o'),
                "high": result.get('h'),
                "low": result.get('l'),
                "volume": result.get('v'),
                "timestamp": datetime.now().isoformat(),
                "source": "Polygon"
            }
        raise Exception("No data from Polygon")

    def _get_yfinance_data(self, ticker: str):
        try:
            stock = yf.Ticker(ticker)
            # fast_info is often faster than history
            info = stock.fast_info
            price = info.last_price
            return {
                "symbol": ticker.upper(),
                "price": price,
                "open": info.open,
                "high": info.day_high,
                "low": info.day_low,
                "volume": info.last_volume,
                "timestamp": datetime.now().isoformat(),
                "source": "YFinance"
            }
        except Exception as e:
            print(f"YFinance error: {e}")
            return self._get_mock_data(ticker)

    def _get_mock_data(self, ticker: str):
        base_price = random.uniform(100, 200)
        return {
            "symbol": ticker.upper(),
            "price": base_price,
            "open": base_price - random.uniform(0, 5),
            "high": base_price + random.uniform(0, 5),
            "low": base_price - random.uniform(0, 5),
            "volume": int(random.uniform(10000, 1000000)),
            "timestamp": datetime.now().isoformat(),
            "source": "Mock"
        }

market_service = MarketService()
