import json
from google import genai
from google.genai import types
from backend.config import config
from datetime import datetime

class AIEngine:
    def __init__(self):
        self.api_key = config.GEMINI_API_KEY
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None
        
    def analyze_situation(self, ticker, market_data, news_data, portfolio_context):
        """
        Analyzes the full context: Market Data, News, and Portfolio Status.
        """
        if not self.client:
            return {"decision": "IGNORE", "confidence": 0, "reasoning": "AI Config Missing"}

        print(f"🟣 [AI] Analyzing context for {ticker}...")

        # Construct the context payload
        context_payload = {
            "ticker": ticker,
            "market_data": market_data, # Includes Price, Volume, OHLC, RSI, MACD
            "recent_news": news_data,
            "portfolio_status": portfolio_context
        }

        prompt = f"""
        You are an aggressive but risk-managed day trader. 
        Your goal is to grow the portfolio aggressively.
        Analyze the provided data points deeply.
        
        Input Context:
        {json.dumps(context_payload, indent=2)}

        Task:
        1. Rate the setup confidence (0-100).
        2. Decision: BUY, SELL, or IGNORE.
        3. Explain your reasoning briefly.

        Response Format (JSON ONLY):
        {{
            "decision": "BUY" | "SELL" | "IGNORE",
            "confidence": <integer 0-100>,
            "reasoning": "<string>",
            "suggested_quantity": <integer>
        }}
        """
        
        # New Google GenAI Library Logic
        models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp"] 
        last_error = None

        for model_name in models:
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )
                return json.loads(response.text)
            except Exception as e:
                # print(f"🔴 [AI] Model {model_name} failed: {e}")
                last_error = e
                continue
        
        print(f"🔴 [AI] All models failed. Last error: {last_error}")
        return {"decision": "IGNORE", "confidence": 0, "reasoning": f"AI Error: {last_error}"}

ai_engine = AIEngine()
