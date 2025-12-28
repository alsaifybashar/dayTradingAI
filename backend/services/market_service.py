from backend.config import config
import requests
import yfinance as yf
from datetime import datetime

class MarketService:
    def __init__(self):
        self.polygon_api_key = config.POLYGON_IO_API_KEY

    def get_stock_data(self, ticker: str):
        """
        Fetches stock data. Tries Polygon first if key exists, then YFinance.
        """
        # Enforce Yahoo Finance as the sole source
        print(f"[{datetime.now().strftime('%H:%M:%S')}] MARKET SERVICE: Fetching data for {ticker} using Yahoo Finance...")
        try:
             data = self._get_yfinance_data(ticker)
             print(f"[{datetime.now().strftime('%H:%M:%S')}] MARKET SERVICE: Successfully fetched data for {ticker} from YFinance.")
             return data
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] MARKET SERVICE: Error with YFinance: {e}")
            raise e

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
        print(f"[{datetime.now().strftime('%H:%M:%S')}] YFINANCE: Initializing Ticker object for {ticker}...")
        try:
            stock = yf.Ticker(ticker)

            # Get intraday data for candlesticks
            print(f"[{datetime.now().strftime('%H:%M:%S')}] YFINANCE: Downloading 1-day history (5m intervals) for {ticker}...")
            hist = stock.history(period="1d", interval="5m")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] YFINANCE: History download complete. Found {len(hist)} candles.")
            
            candles = []
            for index, row in hist.iterrows():
                candles.append({
                    "time": index.isoformat(),
                    "open": float(row['Open']),
                    "high": float(row['High']),
                    "low": float(row['Low']),
                    "close": float(row['Close']),
                    "volume": int(row['Volume']),
                    "bullish": bool(row['Close'] >= row['Open'])
                })

            # Get latest info
            info = stock.fast_info
            
            return {
                "symbol": ticker.upper(),
                "price": info.last_price,
                "open": info.open,
                "high": info.day_high,
                "low": info.day_low,
                "volume": info.last_volume,
                "change": info.last_price - info.previous_close,
                "change_percent": ((info.last_price - info.previous_close) / info.previous_close) * 100,
                "candles": candles,
                "timestamp": datetime.now().isoformat(),
                "source": "YFinance"
            }
        except Exception as e:
            print(f"YFinance error: {e}")
            raise Exception("Failed to fetch stock data")

    def get_batch_data(self, tickers: list):
        """
        Fetches simplified data for a list of tickers (Price, Change, Sparkline).
        """
        results = []
        print(f"[{datetime.now().strftime('%H:%M:%S')}] MARKET SERVICE: Fetching batch data for {tickers}...")
        
        try:
            # yfinance allows fetching multiple tickers at once
            tickers_str = " ".join(tickers)
            batch = yf.Tickers(tickers_str)
            
            for ticker in tickers:
                try:
                    # Access specific ticker object
                    stock = batch.tickers[ticker]
                    
                    # Fast info for price/change
                    info = stock.fast_info
                    price = info.last_price
                    prev_close = info.previous_close
                    change = price - prev_close
                    change_percent = (change / prev_close) * 100
                    
                    # History for sparkline (last 20 candles of 1h or 5m?)
                    # Let's grab 1d history with 1h interval for a smooth sparkline
                    hist = stock.history(period="5d", interval="60m")
                    sparkline = hist['Close'].tail(20).tolist() # Last 20 data points
                    
                    results.append({
                        "ticker": ticker.upper(),
                        "price": price,
                        "change": change,
                        "changePercent": change_percent,
                        "sparkline": [float(x) for x in sparkline] # Cast to float for JSON
                    })
                except Exception as e:
                    print(f"Error fetching batch data for {ticker}: {e}")
                    # Provide fallback/error entry to avoid breaking UI
                    results.append({
                        "ticker": ticker.upper(),
                        "price": 0.0,
                        "change": 0.0,
                        "changePercent": 0.0,
                        "sparkline": []
                    })
                    
            return results
        except Exception as e:
            print(f"Batch fetch error: {e}")
            return []

market_service = MarketService()
