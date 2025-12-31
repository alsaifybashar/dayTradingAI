"""
Enhanced Data Manager

Aggregates market data, news, and technical analysis.
Now includes candlestick pattern detection and signal generation
to reduce AI dependency for trading decisions.
"""

import yfinance as yf
import pandas as pd
import pandas_ta as ta
import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import random
from typing import Dict, List, Optional

from backend.services.candlestick_patterns import pattern_detector
from backend.services.signal_generator import signal_generator
from backend.services.news_service import news_service
from colorama import Fore, Style, init

init(autoreset=True)

class DataManager:
    def __init__(self):
        print(f"{Fore.CYAN}[DATA] Data Manager initialized.")
        # Dow Jones Industrial Average (Approximate 2024/2025)
        self.dow_tickers = [
            "AAPL", "AMGN", "AXP", "BA", "CAT", "CRM", "CSCO", "CVX", "DIS", "GS", 
            "HD", "HON", "IBM", "JNJ", "JPM", "KO", "MCD", "MMM", "MRK", "MSFT", 
            "NKE", "NVDA", "PG", "SHW", "TRV", "UNH", "V", "VZ", "WMT", "AMZN"
        ]
        
        # OMX Stockholm 30 (Approximate)
        self.omx30_tickers = [
            "ABB.ST", "ALFA.ST", "ASSA-B.ST", "AZN.ST", "ATCO-A.ST", "ATCO-B.ST", 
            "BOL.ST", "ELUX-B.ST", "ERIC-B.ST", "ESSITY-B.ST", "EVO.ST", "GETI-B.ST", 
            "HEXA-B.ST", "HM-B.ST", "INVE-B.ST", "KIN-B.ST", "NDA-SE.ST", "NIBE-B.ST", 
            "SAAB-B.ST", "SBB-B.ST", "SCA-B.ST", "SEB-A.ST", "SINCH.ST", "SKF-B.ST", 
            "SSAB-A.ST", "SWED-A.ST", "SHB-A.ST", "TEL2-B.ST", "TELIA.ST", "VOLV-B.ST"
        ]
        
        self.tickers = self.dow_tickers + self.omx30_tickers
        self.indices = ["^GSPC", "^IXIC", "^OMXS30"]  # S&P 500, Nasdaq, OMX Stockholm 30

    def get_monitored_tickers(self) -> List[str]:
        """Returns the list of all monitored tickers."""
        return self.tickers

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

    def get_market_data(self, ticker: str) -> Optional[Dict]:
        """
        Fetches comprehensive market data with pattern analysis.
        Includes: Price, Volume, OHLC, Technical Indicators, and Candlestick Patterns.
        """
        print(f"{Fore.CYAN}[DATA] Fetching market data for {ticker}...")
        try:
            stock = yf.Ticker(ticker)
            info = stock.fast_info

            # Fetch history for Technical Analysis
            hist = stock.history(period="5d", interval="15m")

            if hist.empty:
                return None

            # Calculate Technical Indicators using pandas_ta
            hist.ta.rsi(length=14, append=True)
            hist.ta.macd(append=True)

            # Additional indicators for better analysis
            hist.ta.sma(length=20, append=True)
            hist.ta.ema(length=9, append=True)
            hist.ta.bbands(length=20, append=True)

            latest = hist.iloc[-1]

            # Format candles for frontend and pattern analysis
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

            # Analyze candlestick patterns
            candle_objects = pattern_detector.candles_from_list(candles)
            patterns = pattern_detector.analyze(candle_objects)

            # Get pattern signal
            pattern_signal = pattern_detector.get_trading_signal(
                candle_objects,
                rsi=latest.get('RSI_14'),
                macd=latest.get('MACD_12_26_9'),
                macd_signal=latest.get('MACDs_12_26_9')
            )

            # === QUANT ENGINE: Microstructure (Simulated L2) ===
            # Since we don't have real L2, we synthesize it to demonstrate the architecture
            # In production, replace with self.get_order_book(ticker)
            from backend.services.quant_engine import quant_engine
            # Simulate slight imbalance based on price trend
            bias = 1.0 if info.last_price > info.open else -1.0
            sim_book = self.get_order_book(ticker) # We'll assume this method exists and returns dict
            obi = quant_engine.calculate_obi(sim_book['bids'], sim_book['asks'])
            
            # Additional OBI logic: If price is up but OBI is negative -> divergences?
            
            # Calculate average volume for comparison
            avg_volume = hist['Volume'].mean() if 'Volume' in hist else 0

            data = {
                "symbol": ticker,
                "price": info.last_price,
                "change": info.last_price - info.previous_close,
                "change_percent": ((info.last_price - info.previous_close) / info.previous_close) * 100,
                "volume": info.last_volume,
                "avg_volume": int(avg_volume),
                "open": info.open,
                "high": info.day_high,
                "low": info.day_low,
                
                # Quantitative Metrics
                "obi": obi,

                # Technical Indicators
                "rsi": latest.get('RSI_14'),
                "macd": latest.get('MACD_12_26_9'),
                "macd_signal": latest.get('MACDs_12_26_9'),
                "macd_hist": latest.get('MACDh_12_26_9'),
                "sma_20": latest.get('SMA_20'),
                "ema_9": latest.get('EMA_9'),
                "bb_upper": latest.get('BBU_20_2.0'),
                "bb_middle": latest.get('BBM_20_2.0'),
                "bb_lower": latest.get('BBL_20_2.0'),

                # Pattern Analysis
                "patterns": [
                    {
                        "name": p.name,
                        "type": p.pattern_type.value,
                        "strength": p.strength.name,
                        "confidence": p.confidence,
                        "action": p.action_suggestion
                    }
                    for p in patterns[:5]  # Top 5 patterns
                ],
                "pattern_signal": pattern_signal,

                # Raw data
                "sparkline": hist['Close'].tail(20).tolist(),
                "candles": candles,
                "timestamp": datetime.now().isoformat()
            }
            return data
        except Exception as e:
            print(f"[DataManager] Error fetching market data for {ticker}: {e}")
            return None

    def get_full_analysis(self, ticker: str, portfolio_balance: float = 1000) -> Dict:
        """
        Get complete analysis including market data, news, patterns, and trading signal.
        This is the main method for trading decisions.

        Returns a signal that indicates whether AI should be consulted.
        """
        # Get market data with patterns
        market_data = self.get_market_data(ticker)

        if not market_data:
            return {
                "error": "Failed to fetch market data",
                "use_ai": True
            }

        # Get news and sentiment
        news_articles = news_service.get_news(ticker, max_articles=10)
        sentiment = news_service.analyze_sentiment(news_articles)

        # Generate trading signal
        signal = signal_generator.generate_signal(
            ticker=ticker,
            candles=market_data.get("candles", []),
            rsi=market_data.get("rsi"),
            macd=market_data.get("macd"),
            macd_signal=market_data.get("macd_signal"),
            volume=market_data.get("volume"),
            avg_volume=market_data.get("avg_volume"),
            news_articles=news_articles,
            portfolio_balance=portfolio_balance
        )

        return {
            "ticker": ticker,
            "market_data": market_data,
            "news": news_articles[:5],  # Top 5 news
            "sentiment": sentiment,
            "signal": {
                "decision": signal.decision,
                "confidence": signal.confidence,
                "use_ai": signal.use_ai,
                "reasoning": signal.reasoning,
                "suggested_quantity": signal.suggested_quantity,
                "patterns_detected": signal.patterns_detected,
                "scores": {
                    "pattern": signal.pattern_score,
                    "indicator": signal.indicator_score,
                    "sentiment": signal.sentiment_score,
                    "volume": signal.volume_score
                }
            },
            "timestamp": datetime.now().isoformat()
        }

    def get_order_book(self, ticker: str):
        """
        Simulates Level 2 Order Book data based on market activity.
        Real L2 data usually requires paid APIs.
        """
        try:
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

    def get_news(self, ticker: str, limit: int = 5) -> List[Dict]:
        """
        Wrapper to get news from NewsService
        """
        print(f"{Fore.CYAN}[DATA] Collecting news for {ticker}...")
        return news_service.get_news(ticker, limit)

    def get_news_with_sentiment(self, ticker: str = None) -> Dict:
        """
        Get news with sentiment analysis (no AI needed).
        """
        articles = news_service.get_news(ticker, max_articles=15)
        sentiment = news_service.analyze_sentiment(articles)
        return {
            "articles": articles,
            "sentiment": sentiment
        }

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

    def quick_pattern_check(self, ticker: str) -> Dict:
        """
        Ultra-fast pattern check for real-time monitoring.
        No news, no AI - just pattern analysis.
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="2d", interval="5m")

            if hist.empty:
                return {"decision": "HOLD", "confidence": 0}

            candles = []
            for index, row in hist.iterrows():
                candles.append({
                    "open": float(row['Open']),
                    "high": float(row['High']),
                    "low": float(row['Low']),
                    "close": float(row['Close']),
                    "volume": int(row['Volume'])
                })

            return signal_generator.get_quick_decision(candles[-20:])
        except Exception as e:
            return {"decision": "HOLD", "confidence": 0, "error": str(e)}


data_manager = DataManager()
