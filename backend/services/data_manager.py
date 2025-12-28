import yfinance as yf
import pandas as pd
import pandas_ta as ta
import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import random

class DataManager:
    def __init__(self):
        self.tickers = ["AAPL", "TSLA", "NVDA", "AMD", "META", "MSFT", "GOOGL", "AMZN"]
        self.indices = ["^GSPC", "^IXIC", "^OMXS30"] # S&P 500, Nasdaq, OMX Stockholm 30

    def get_batch_data(self, tickers: list):
        """
        Fetches simplified data for a list of tickers (Price, Change, Sparkline).
        """
        results = []
        try:
            tickers_str = " ".join(tickers)
            batch = yf.Tickers(tickers_str)
            
            for ticker in tickers:
                try:
                    stock = batch.tickers[ticker]
                    info = stock.fast_info
                    price = info.last_price
                    prev_close = info.previous_close
                    change = price - prev_close
                    change_percent = (change / prev_close) * 100
                    
                    hist = stock.history(period="5d", interval="60m")
                    sparkline = hist['Close'].tail(20).tolist()
                    
                    results.append({
                        "ticker": ticker.upper(),
                        "price": price,
                        "change": change,
                        "changePercent": change_percent,
                        "sparkline": [float(x) for x in sparkline]
                    })
                except:
                    results.append({
                        "ticker": ticker.upper(),
                        "price": 0.0,
                        "change": 0.0,
                        "changePercent": 0.0,
                        "sparkline": []
                    })
            return results
        except:
            return []

    def get_market_data(self, ticker: str):
        """
        Fetches comprehensive market data: Price, Volume, OHLC, and Technical Indicators.
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.fast_info
            
            # Fetch history for Technical Analysis (RSI, MACD)
            # We need enough data points for indicators (e.g., 20)
            hist = stock.history(period="5d", interval="15m") 
            
            if hist.empty:
                return None

            # Calculate Indicators using pandas_ta
            hist.ta.rsi(length=14, append=True)
            hist.ta.macd(append=True)
            
            latest = hist.iloc[-1]
            
            # Format candles for frontend
            candles = []
            for index, row in hist.iterrows():
                candles.append({
                    "time": index.isoformat(),
                    "open": float(row['Open']),
                    "high": float(row['High']),
                    "low": float(row['Low']),
                    "close": float(row['Close']),
                    "volume": int(row['Volume']),
                })

            data = {
                "symbol": ticker,
                "price": info.last_price,
                "change": info.last_price - info.previous_close,
                "change_percent": ((info.last_price - info.previous_close) / info.previous_close) * 100,
                "volume": info.last_volume,
                "open": info.open,
                "high": info.day_high,
                "low": info.day_low,
                "rsi": latest.get('RSI_14'),
                "macd": latest.get('MACD_12_26_9'),
                "macd_signal": latest.get('MACDs_12_26_9'),
                "sparkline": hist['Close'].tail(20).tolist(),
                "candles": candles,
                "timestamp": datetime.now().isoformat()
            }
            return data
        except Exception as e:
            print(f"[DataManager] Error fetching market data for {ticker}: {e}")
            return None

    def get_order_book(self, ticker: str):
        """
        Simulates Level 2 Order Book data based on market activity.
        Real L2 data usually requires paid APIs.
        """
        try:
            # Random variation for simulation
            spread = random.uniform(0.01, 0.05)
            depth_factor = random.randint(100, 500)
            
            stock = yf.Ticker(ticker)
            price = stock.fast_info.last_price or 100.0
            
            bids = [
                {"price": price - (i * spread), "size": depth_factor * (5-i)} 
                for i in range(1, 6)
            ]
            asks = [
                {"price": price + (i * spread), "size": depth_factor * (5-i)} 
                for i in range(1, 6)
            ]
            
            return {"bids": bids, "asks": asks}
        except:
            return {"bids": [], "asks": []}

    def get_news(self, ticker: str = None):
        """
        Aggregates news from Yahoo, CNBC, and Placera.
        """
        news_items = []
        
        # 1. Yahoo Finance (Specific Ticker)
        if ticker:
            try:
                stock = yf.Ticker(ticker)
                for item in stock.news[:3]:
                    news_items.append({
                        "source": "Yahoo Finance",
                        "title": item.get('title'),
                        "link": item.get('link'),
                        "published": str(datetime.fromtimestamp(item.get('providerPublishTime', 0)))
                    })
            except Exception as e:
                print(f"[DataManager] Yahoo News Error: {e}")

        # 2. CNBC (General Market) - RSS
        try:
            feed = feedparser.parse("https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114")
            for entry in feed.entries[:2]:
                news_items.append({
                    "source": "CNBC",
                    "title": entry.title,
                    "link": entry.link,
                    "published": entry.published
                })
        except Exception:
            pass

        # 3. Placera (Swedish - General)
        # Scrape headline from Placera
        try:
            response = requests.get("https://www.placera.se/placera/nyheter.html")
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                headlines = soup.select('.news-list-item h2 a') # Adjust selector based on actual site structure
                for h in headlines[:2]:
                    news_items.append({
                        "source": "Placera.se",
                        "title": h.get_text().strip(),
                        "link": "https://www.placera.se" + h['href'],
                        "published": datetime.now().strftime("%Y-%m-%d %H:%M")
                    })
        except Exception as e:
            pass
            
        return news_items

    def get_macro_context(self):
        """
        Fetches major indices status.
        """
        context = {}
        try:
            batch = yf.Tickers(" ".join(self.indices))
            for idx in self.indices:
                info = batch.tickers[idx].fast_info
                context[idx] = {
                    "price": info.last_price,
                    "change_pct": ((info.last_price - info.previous_close) / info.previous_close) * 100
                }
        except:
            pass
        return context

data_manager = DataManager()
