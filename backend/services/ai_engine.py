"""
AI Engine - Smart Decision Support

This module provides AI-powered analysis using Google Gemini.
IMPORTANT: AI is now only called for edge cases to reduce costs.

The signal_generator handles most decisions algorithmically.
AI is consulted when:
- Signals are contradictory
- Confidence is low (< 60%)
- Unusual market conditions detected
"""

import json
from google import genai
from google.genai import types
from backend.config import config
from datetime import datetime
from typing import Dict, Optional


class AIEngine:
    def __init__(self):
        self.api_key = config.GEMINI_API_KEY
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

        # Track API calls for cost monitoring
        self.call_count = 0
        self.calls_today = 0
        self.last_reset = datetime.now().date()

    def should_consult(self, signal: Dict) -> bool:
        """
        Determine if AI should be consulted based on signal quality.
        Returns True if AI consultation is recommended.
        """
        # Check if signal generator already said to use AI
        if signal.get("use_ai", True):
            return True

        # Low confidence
        if signal.get("confidence", 0) < 60:
            return True

        # Check for conflicting signals
        scores = signal.get("scores", {})
        pattern = scores.get("pattern", 0)
        indicator = scores.get("indicator", 0)
        sentiment = scores.get("sentiment", 0)

        # If pattern and sentiment disagree strongly
        if pattern * sentiment < -500:  # Strong disagreement
            return True

        return False

    def analyze_situation(self, ticker: str, market_data: Dict,
                          news_data: list, portfolio_context: Dict,
                          algorithmic_signal: Optional[Dict] = None) -> Dict:
        """
        AI analysis with context from algorithmic analysis.

        Args:
            ticker: Stock ticker symbol
            market_data: Market data including patterns
            news_data: News articles
            portfolio_context: Current portfolio state
            algorithmic_signal: Signal from signal_generator (optional)

        Returns:
            AI decision with reasoning
        """
        if not self.client:
            return {"decision": "IGNORE", "confidence": 0, "reasoning": "AI Config Missing"}

        # Reset daily counter
        today = datetime.now().date()
        if today != self.last_reset:
            self.calls_today = 0
            self.last_reset = today

        # Increment counters
        self.call_count += 1
        self.calls_today += 1

        print(f"🟣 [AI] Analyzing context for {ticker} (Call #{self.calls_today} today)...")

        # Build context with algorithmic signal
        context_payload = {
            "ticker": ticker,
            "market_data": self._simplify_market_data(market_data),
            "patterns_detected": market_data.get("patterns", []),
            "pattern_signal": market_data.get("pattern_signal", {}),
            "recent_news": news_data[:5] if news_data else [],
            "portfolio_status": portfolio_context
        }

        # Include algorithmic signal if available
        if algorithmic_signal:
            context_payload["algorithmic_analysis"] = {
                "decision": algorithmic_signal.get("decision"),
                "confidence": algorithmic_signal.get("confidence"),
                "reasoning": algorithmic_signal.get("reasoning"),
                "pattern_score": algorithmic_signal.get("scores", {}).get("pattern"),
                "sentiment_score": algorithmic_signal.get("scores", {}).get("sentiment")
            }

        prompt = f"""
        You are an expert day trader making a final decision.

        IMPORTANT: An algorithmic analysis has already been performed.
        Your role is to VALIDATE or OVERRIDE the algorithmic decision.

        Only override if you see something the algorithm missed:
        - Breaking news that changes the situation
        - Market conditions the patterns don't capture
        - Risk factors not accounted for

        Input Context:
        {json.dumps(context_payload, indent=2, default=str)}

        Task:
        1. Review the algorithmic analysis
        2. Check if any news or market conditions warrant overriding
        3. Rate your confidence (0-100)
        4. Make final decision: BUY, SELL, or IGNORE

        Response Format (JSON ONLY):
        {{
            "decision": "BUY" | "SELL" | "IGNORE",
            "confidence": <integer 0-100>,
            "reasoning": "<string - explain why you agree or disagree with algorithm>",
            "suggested_quantity": <integer>,
            "override_algorithm": <boolean - true if overriding algorithmic decision>
        }}
        """

        # Try models in order of preference
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
                result = json.loads(response.text)
                result["model_used"] = model_name
                result["call_number"] = self.calls_today
                return result
            except Exception as e:
                last_error = e
                continue

        print(f"🔴 [AI] All models failed. Last error: {last_error}")
        return {
            "decision": "IGNORE",
            "confidence": 0,
            "reasoning": f"AI Error: {last_error}",
            "override_algorithm": False
        }

    def _simplify_market_data(self, market_data: Dict) -> Dict:
        """Simplify market data to reduce token usage"""
        if not market_data:
            return {}

        return {
            "price": market_data.get("price"),
            "change_percent": market_data.get("change_percent"),
            "volume": market_data.get("volume"),
            "rsi": market_data.get("rsi"),
            "macd": market_data.get("macd"),
            "macd_signal": market_data.get("macd_signal")
        }

    def quick_sentiment_check(self, news_headlines: list) -> Dict:
        """
        Quick AI sentiment check for news headlines only.
        Uses minimal tokens for cost efficiency.
        """
        if not self.client or not news_headlines:
            return {"sentiment": "neutral", "confidence": 0}

        headlines_text = "\n".join([n.get("title", "") for n in news_headlines[:5]])

        prompt = f"""
        Analyze these headlines for market sentiment.
        Headlines:
        {headlines_text}

        Response (JSON):
        {{"sentiment": "bullish" | "bearish" | "neutral", "confidence": 0-100}}
        """

        try:
            response = self.client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            return json.loads(response.text)
        except:
            return {"sentiment": "neutral", "confidence": 0}

    def get_usage_stats(self) -> Dict:
        """Get AI usage statistics"""
        return {
            "total_calls": self.call_count,
            "calls_today": self.calls_today,
            "last_reset": str(self.last_reset)
        }


ai_engine = AIEngine()
