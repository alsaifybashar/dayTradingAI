import feedparser
import requests
from datetime import datetime

class NewsService:
    def __init__(self):
        self.rss_feeds = {
            "CNBC": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114",
            "YahooFinance": "https://finance.yahoo.com/news/rssindex",
            # Placera often doesn't have a public RSS, might need scraping, but for now we stick to standard feeds or generic ones.
        }

    def get_news(self, ticker: str = None):
        """
        Fetches news. If ticker is provided, filters or searches for it.
        """
        all_news = []
        for source, url in self.rss_feeds.items():
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries:
                    # Basic filtering if ticker is provided
                    if ticker:
                        if ticker.lower() not in entry.title.lower() and ticker.lower() not in entry.summary.lower():
                            continue
                    
                    all_news.append({
                        "title": entry.title,
                        "link": entry.link,
                        "published": entry.get("published", datetime.now().isoformat()),
                        "source": source,
                        "summary": entry.get("summary", "")[:200] + "..."
                    })
            except Exception as e:
                print(f"Error fetching {source}: {e}")
        
        # Sort by date (naive approach, assume published is parseable or just return as is)
        return all_news[:10]  # Return top 10

news_service = NewsService()
