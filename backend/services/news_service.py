"""
Enhanced News Service

Aggregates financial news from multiple sources:
- Yahoo Finance (ticker-specific)
- CNBC (market news)
- Dagens Industri (Swedish market)
- Reuters (global financial news)
- MarketWatch (stock-specific news)
- Seeking Alpha (analysis & news)
- Benzinga (real-time news)
- Financial Times (global markets)
- Bloomberg (market news)
- Investopedia (educational + news)
"""

import feedparser
import requests
import yfinance as yf
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import time


class NewsService:
    def __init__(self):
        # RSS feed sources
        self.rss_feeds = {
            # US Market News
            "CNBC": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114",
            "CNBC-Markets": "https://www.cnbc.com/id/20910258/device/rss/rss.html",
            "YahooFinance": "https://finance.yahoo.com/news/rssindex",
            "MarketWatch": "https://feeds.marketwatch.com/marketwatch/topstories/",
            "MarketWatch-Stocks": "https://feeds.marketwatch.com/marketwatch/marketpulse/",
            "Reuters-Business": "https://feeds.reuters.com/reuters/businessNews",
            "Reuters-Markets": "https://feeds.reuters.com/reuters/companyNews",
            "Investing-News": "https://www.investing.com/rss/news.rss",
            "Investing-Stock": "https://www.investing.com/rss/stock_news_stock.rss",

            # Nordic/European Markets
            "DagensIndustri": "https://www.di.se/rss",

            # Crypto & Tech overlap (often has stock market relevance)
            "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
        }

        # Web scraping sources (for ticker-specific news)
        self.web_sources = {
            "SeekingAlpha": "https://seekingalpha.com/symbol/{ticker}/news",
            "Benzinga": "https://www.benzinga.com/quote/{ticker}",
            "FinViz": "https://finviz.com/quote.ashx?t={ticker}",
        }

        # Company name mapping for better search
        self.company_map = {
            "TSLA": ["Tesla", "Elon Musk", "EV maker"],
            "AAPL": ["Apple", "iPhone", "Tim Cook", "Mac"],
            "NVDA": ["Nvidia", "NVIDIA", "Jensen Huang", "GPU", "AI chips"],
            "AMD": ["Advanced Micro Devices", "AMD", "Lisa Su"],
            "MSFT": ["Microsoft", "Satya Nadella", "Azure", "Windows"],
            "GOOGL": ["Google", "Alphabet", "Sundar Pichai"],
            "GOOG": ["Google", "Alphabet", "Sundar Pichai"],
            "AMZN": ["Amazon", "AWS", "Jeff Bezos", "Andy Jassy"],
            "META": ["Meta", "Facebook", "Mark Zuckerberg", "Instagram", "WhatsApp"],
            "NFLX": ["Netflix", "streaming"],
            "DIS": ["Disney", "Disney+"],
            "BA": ["Boeing", "aircraft"],
            "JPM": ["JPMorgan", "JP Morgan", "Jamie Dimon"],
            "V": ["Visa", "payments"],
            "MA": ["Mastercard", "payments"],
            "WMT": ["Walmart", "retail"],
            "PG": ["Procter & Gamble", "P&G"],
            "JNJ": ["Johnson & Johnson", "J&J"],
            "UNH": ["UnitedHealth", "healthcare"],
            "HD": ["Home Depot"],
            "BAC": ["Bank of America", "BofA"],
            "XOM": ["Exxon", "ExxonMobil", "oil"],
            "CVX": ["Chevron", "oil"],
            "PFE": ["Pfizer", "vaccine"],
            "ABBV": ["AbbVie", "pharma"],
            "KO": ["Coca-Cola", "Coke"],
            "PEP": ["PepsiCo", "Pepsi"],
            "MRK": ["Merck", "pharma"],
            "COST": ["Costco", "retail"],
            "TMO": ["Thermo Fisher"],
            "AVGO": ["Broadcom", "semiconductors"],
            "CRM": ["Salesforce", "CRM"],
            "ACN": ["Accenture", "consulting"],
            "MCD": ["McDonald's", "fast food"],
            "CSCO": ["Cisco", "networking"],
            "ABT": ["Abbott", "medical devices"],
            "DHR": ["Danaher", "life sciences"],
            "LIN": ["Linde", "industrial gases"],
            "ADBE": ["Adobe", "creative software"],
            "NKE": ["Nike", "sportswear"],
            "TXN": ["Texas Instruments", "semiconductors"],
            "ORCL": ["Oracle", "database"],
            "NEE": ["NextEra Energy", "utilities"],
            "PM": ["Philip Morris", "tobacco"],
            "VZ": ["Verizon", "telecom"],
            "T": ["AT&T", "telecom"],
            "INTC": ["Intel", "semiconductors", "chips"],
            "QCOM": ["Qualcomm", "mobile chips"],
            "IBM": ["IBM", "enterprise"],
            "GS": ["Goldman Sachs", "investment bank"],
            "MS": ["Morgan Stanley", "investment bank"],
            "BLK": ["BlackRock", "asset management"],
            "SCHW": ["Charles Schwab", "brokerage"],
            "C": ["Citigroup", "Citi", "banking"],
            "AXP": ["American Express", "Amex"],
        }

        # Request headers
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

        # Cache for rate limiting
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes

    def get_news(self, ticker: str = None, max_articles: int = 15) -> List[Dict]:
        """
        Fetches news from all sources. If ticker is provided, filters relevant articles.
        Uses parallel fetching for speed.

        Args:
            ticker: Stock ticker symbol (e.g., "TSLA")
            max_articles: Maximum number of articles to return

        Returns:
            List of news articles sorted by relevance/recency
        """
        cache_key = f"news_{ticker}_{max_articles}"
        if cache_key in self._cache:
            cached_time, cached_data = self._cache[cache_key]
            if time.time() - cached_time < self._cache_ttl:
                return cached_data

        all_news = []
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] NEWS SERVICE: Fetching news for {ticker if ticker else 'General Market'}...")

        # Parallel fetch from all sources
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = []

            # 1. Yahoo Finance ticker-specific news (primary source for tickers)
            if ticker:
                futures.append(executor.submit(self._fetch_yfinance_news, ticker))

            # 2. RSS Feeds
            for source, url in self.rss_feeds.items():
                futures.append(executor.submit(self._fetch_rss, source, url, ticker))

            # 3. Web scraping sources (for tickers only)
            if ticker:
                futures.append(executor.submit(self._scrape_finviz, ticker))

            # Collect results
            for future in as_completed(futures, timeout=15):
                try:
                    result = future.result()
                    if result:
                        all_news.extend(result)
                except Exception as e:
                    pass  # Silently skip failed sources

        # Filter by ticker if provided
        if ticker:
            all_news = self._filter_by_ticker(all_news, ticker)

        # Remove duplicates based on title similarity
        all_news = self._deduplicate(all_news)

        # Sort by relevance score, then by date
        all_news.sort(key=lambda x: (x.get('relevance_score', 0), x.get('published', '')), reverse=True)

        result = all_news[:max_articles]

        # Cache the result
        self._cache[cache_key] = (time.time(), result)

        print(f"[{datetime.now().strftime('%H:%M:%S')}] NEWS SERVICE: Found {len(result)} relevant articles.")
        return result

    def _fetch_yfinance_news(self, ticker: str) -> List[Dict]:
        """Fetch news directly from Yahoo Finance API"""
        try:
            stock = yf.Ticker(ticker)
            yf_news = stock.news

            articles = []
            for item in yf_news:
                articles.append({
                    "title": item.get('title', ''),
                    "link": item.get('link', ''),
                    "published": str(datetime.fromtimestamp(item.get('providerPublishTime', 0)))
                                if item.get('providerPublishTime') else datetime.now().isoformat(),
                    "source": f"Yahoo-{item.get('publisher', 'Finance')}",
                    "summary": item.get('title', ''),
                    "relevance_score": 100  # Highest relevance for ticker-specific
                })
            return articles
        except Exception as e:
            return []

    def _fetch_rss(self, source: str, url: str, ticker: str = None) -> List[Dict]:
        """Fetch and parse RSS feed"""
        try:
            feed = feedparser.parse(url)
            articles = []

            for entry in feed.entries[:10]:  # Limit per source
                summary = entry.get("summary", entry.get("description", ""))

                # Clean HTML from summary
                if summary:
                    summary = BeautifulSoup(summary, 'html.parser').get_text()[:300]

                # Calculate relevance score
                relevance = 50  # Base score
                if ticker:
                    text = (entry.title + " " + summary).lower()
                    search_terms = self._get_search_terms(ticker)
                    matches = sum(1 for term in search_terms if term.lower() in text)
                    relevance = min(100, 50 + matches * 20)

                articles.append({
                    "title": entry.title,
                    "link": entry.link,
                    "published": entry.get("published", datetime.now().isoformat()),
                    "source": source,
                    "summary": summary[:200] + "..." if len(summary) > 200 else summary,
                    "relevance_score": relevance
                })

            return articles
        except Exception as e:
            return []

    def _scrape_finviz(self, ticker: str) -> List[Dict]:
        """Scrape news headlines from FinViz"""
        try:
            url = f"https://finviz.com/quote.ashx?t={ticker}"
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code != 200:
                return []

            soup = BeautifulSoup(response.content, 'html.parser')
            news_table = soup.find('table', {'id': 'news-table'})

            if not news_table:
                return []

            articles = []
            for row in news_table.find_all('tr')[:8]:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    link_tag = cells[1].find('a')
                    if link_tag:
                        articles.append({
                            "title": link_tag.get_text().strip(),
                            "link": link_tag.get('href', ''),
                            "published": cells[0].get_text().strip(),
                            "source": "FinViz",
                            "summary": link_tag.get_text().strip(),
                            "relevance_score": 90  # High relevance for ticker page
                        })

            return articles
        except Exception as e:
            return []

    def _get_search_terms(self, ticker: str) -> List[str]:
        """Get search terms for a ticker"""
        terms = [ticker.lower()]
        if ticker.upper() in self.company_map:
            terms.extend([t.lower() for t in self.company_map[ticker.upper()]])
        return terms

    def _filter_by_ticker(self, articles: List[Dict], ticker: str) -> List[Dict]:
        """Filter articles to only include ticker-relevant ones"""
        search_terms = self._get_search_terms(ticker)
        filtered = []

        for article in articles:
            text = (article.get('title', '') + " " + article.get('summary', '')).lower()

            # Check if any search term matches
            if any(term in text for term in search_terms):
                # Boost relevance for matches
                matches = sum(1 for term in search_terms if term in text)
                article['relevance_score'] = min(100, article.get('relevance_score', 50) + matches * 10)
                filtered.append(article)
            elif article.get('relevance_score', 0) >= 70:
                # Keep high-relevance articles even without term match
                filtered.append(article)

        return filtered

    def _deduplicate(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles based on title similarity"""
        seen_titles = set()
        unique = []

        for article in articles:
            # Normalize title for comparison
            title_key = re.sub(r'[^\w\s]', '', article.get('title', '').lower())[:50]

            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique.append(article)

        return unique

    def get_sentiment_keywords(self) -> Dict[str, List[str]]:
        """Returns sentiment keywords for quick analysis without AI"""
        return {
            "bullish": [
                "surge", "soar", "jump", "rally", "gain", "rise", "climb", "up",
                "beat", "exceed", "outperform", "bullish", "buy", "upgrade",
                "record high", "all-time high", "breakthrough", "strong",
                "growth", "profit", "earnings beat", "revenue up", "positive",
                "expansion", "acquisition", "partnership", "deal", "contract",
                "innovation", "launch", "success", "momentum", "optimistic"
            ],
            "bearish": [
                "drop", "fall", "plunge", "sink", "crash", "decline", "down",
                "miss", "disappoint", "underperform", "bearish", "sell",
                "downgrade", "cut", "warning", "weak", "loss", "deficit",
                "layoff", "lawsuit", "investigation", "probe", "scandal",
                "recession", "concern", "risk", "trouble", "struggle",
                "miss estimates", "guidance cut", "pessimistic", "slump"
            ],
            "neutral": [
                "hold", "stable", "unchanged", "steady", "flat", "mixed",
                "uncertain", "wait", "monitor", "sideways", "range"
            ]
        }

    def analyze_sentiment(self, articles: List[Dict]) -> Dict:
        """
        Quick sentiment analysis without AI.
        Returns sentiment scores based on keyword matching.
        """
        keywords = self.get_sentiment_keywords()

        bullish_count = 0
        bearish_count = 0
        neutral_count = 0
        total_articles = len(articles)

        article_sentiments = []

        for article in articles:
            text = (article.get('title', '') + " " + article.get('summary', '')).lower()

            bull_matches = sum(1 for kw in keywords['bullish'] if kw in text)
            bear_matches = sum(1 for kw in keywords['bearish'] if kw in text)

            if bull_matches > bear_matches:
                sentiment = "bullish"
                bullish_count += 1
            elif bear_matches > bull_matches:
                sentiment = "bearish"
                bearish_count += 1
            else:
                sentiment = "neutral"
                neutral_count += 1

            article_sentiments.append({
                **article,
                "sentiment": sentiment,
                "sentiment_score": bull_matches - bear_matches
            })

        # Calculate overall sentiment
        if total_articles == 0:
            overall = "neutral"
            confidence = 0
        else:
            bullish_pct = bullish_count / total_articles
            bearish_pct = bearish_count / total_articles

            if bullish_pct > bearish_pct + 0.2:
                overall = "bullish"
                confidence = int(bullish_pct * 100)
            elif bearish_pct > bullish_pct + 0.2:
                overall = "bearish"
                confidence = int(bearish_pct * 100)
            else:
                overall = "neutral"
                confidence = 50

        return {
            "overall_sentiment": overall,
            "confidence": confidence,
            "bullish_count": bullish_count,
            "bearish_count": bearish_count,
            "neutral_count": neutral_count,
            "total_articles": total_articles,
            "articles": article_sentiments[:10]  # Return top 10 with sentiment
        }


# Singleton instance
news_service = NewsService()
