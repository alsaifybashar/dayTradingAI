import feedparser
import requests
import yfinance as yf
from datetime import datetime

class NewsService:
    def __init__(self):
        self.rss_feeds = {
            "CNBC": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114",
            "YahooFinance": "https://finance.yahoo.com/news/rssindex",
            "DagensIndustri": "https://www.di.se/rss", # Added for Swedish market coverage
        }

    def get_news(self, ticker: str = None):
        """
        Fetches news. If ticker is provided, filters or searches for it.
        """
        all_news = []
        print(f"[{datetime.now().strftime('%H:%M:%S')}] NEWS SERVICE: Fetching news for {ticker if ticker else 'General Market'}...")

        # 1. Try YFinance Stock News (Primary Source for Tickers)
        if ticker:
            try:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] NEWS SERVICE: Fetching from YFinance for {ticker}...")
                stock = yf.Ticker(ticker)
                yf_news = stock.news
                for item in yf_news:
                    all_news.append({
                        "title": item.get('title'),
                        "link": item.get('link'),
                        "published": str(datetime.fromtimestamp(item.get('providerPublishTime', 0))) if item.get('providerPublishTime') else datetime.now().isoformat(),
                        "source": f"YF-{item.get('publisher', 'Unknown')}",
                        "summary": item.get('title') # YF often doesn't give a summary, so use title
                    })
                print(f"[{datetime.now().strftime('%H:%M:%S')}] NEWS SERVICE: Found {len(yf_news)} articles from YFinance.")
            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] NEWS SERVICE: YFinance News Error: {e}")

        if ticker:
            # Add specific Yahoo Finance feed for this ticker
            yahoo_ticker_url = f"https://finance.yahoo.com/rss/headline?s={ticker}"
            # We treat this as a temporary addition to the loop, or just iterate it
            feeds_to_check = self.rss_feeds.copy()
            feeds_to_check[f"Yahoo-{ticker}"] = yahoo_ticker_url
        else:
            feeds_to_check = self.rss_feeds

        for source, url in feeds_to_check.items():
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries:
                    # Basic filtering if ticker is provided
                    summary = entry.get("summary", entry.get("description", ""))
                    if ticker:
                        # Map common tickers to company names for better search
                        company_map = {
                            "TSLA": "Tesla",
                            "AAPL": "Apple",
                            "NVDA": "Nvidia",
                            "AMD": "Advanced Micro Devices",
                            "MSFT": "Microsoft",
                            "GOOGL": "Google",
                            "GOOG": "Google",
                            "AMZN": "Amazon",
                            "META": "Meta"
                        }
                        search_terms = [ticker.lower()]
                        if ticker.upper() in company_map:
                            search_terms.append(company_map[ticker.upper()].lower())
                        
                        text_to_search = (entry.title + " " + summary).lower()
                        if not any(term in text_to_search for term in search_terms):
                            continue
                    
                    all_news.append({
                        "title": entry.title,
                        "link": entry.link,
                        "published": entry.get("published", datetime.now().isoformat()),
                        "source": source,
                        "summary": summary[:200] + "..."
                    })
            except Exception as e:
                print(f"Error fetching {source}: {e}")
        
        # Sort by date (naive approach, assume published is parseable or just return as is)
        return all_news[:10]  # Return top 10

news_service = NewsService()
