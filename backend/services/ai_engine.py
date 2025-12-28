import json
from backend.config import config
# from openai import OpenAI # Uncomment if using OpenAI

class AIEngine:
    def __init__(self):
        self.api_key = config.OPENAI_API_KEY
        # self.client = OpenAI(api_key=self.api_key) if self.api_key else None
    
    def analyze_stock(self, ticker, market_data, news_data):
        """
        Analyzes stock data and news to provide a recommendation.
        """
        if not self.api_key:
            return self._mock_analysis(ticker, market_data, news_data)

        # Implementation for real AI call would go here
        # prompt = f"Analyze {ticker} based on {market_data} and {news_data}..."
        # response = self.client.chat.completions.create(...)
        
        return self._mock_analysis(ticker, market_data, news_data)

    def _mock_analysis(self, ticker, market_data, news_data):
        price = market_data.get('price', 100)
        # Simple logic for mock decision
        decision = "HOLD"
        if price < 150:
            decision = "BUY"
        elif price > 180:
            decision = "SELL"
            
        return {
            "ticker": ticker,
            "decision": decision,
            "confidence": 85,
            "reasoning": f"Based on market price of {price} and {len(news_data)} news articles, the stock shows potential. (AI MOCK ANALYSIS)",
            "timestamp": market_data.get('timestamp')
        }

ai_engine = AIEngine()
