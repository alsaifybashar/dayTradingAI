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
import os
from google import genai
from google.genai import types
from openai import OpenAI
import anthropic
from backend.config import config
from datetime import datetime
from typing import Dict, Optional
import time

class AIEngine:
    def __init__(self):
        # Gemini Init
        self.gemini_key = config.GEMINI_API_KEY
        self.gemini_client = genai.Client(api_key=self.gemini_key) if self.gemini_key else None
        
        # OpenAI Init
        self.openai_key = config.OPENAI_API_KEY
        self.openai_client = OpenAI(api_key=self.openai_key) if self.openai_key else None
        
        # Claude (Anthropic) Init
        self.anthropic_key = config.ANTHROPIC_API_KEY
        self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_key) if self.anthropic_key else None
        
        # Track exhausted providers (persists across requests)
        self.exhausted_providers = set()
        
        # Track usage
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
            
        return False

    def analyze_situation(self, ticker: str, market_data: Dict,
                          news_data: list, portfolio_context: Dict,
                          algorithmic_signal: Optional[Dict] = None) -> Dict:
        """
        AI analysis with context from algorithmic analysis.
        Uses fallback strategy: Gemini 2.0 -> Gemini 1.5 -> OpenAI -> Claude.
        """
        # Reset counters
        today = datetime.now().date()
        if today != self.last_reset:
            self.calls_today = 0
            self.last_reset = today
            self.exhausted_providers.clear() # Retry providers on new day

        self.call_count += 1
        self.calls_today += 1
        
        print(f"🟣 [AI] Analyzing context for {ticker} (Call #{self.calls_today})...")

        # Build context
        context_payload = {
            "ticker": ticker,
            "market_data": self._simplify_market_data(market_data),
            "patterns_detected": market_data.get("patterns", []),
            "recent_news": news_data[:3] if news_data else [], # Limit to 3 to save tokens
            "portfolio_status": portfolio_context
        }

        if algorithmic_signal:
            context_payload["algorithmic_analysis"] = {
                "decision": algorithmic_signal.get("decision"),
                "confidence": algorithmic_signal.get("confidence"),
                "reasoning": algorithmic_signal.get("reasoning")
            }

        # Simplified Prompt
        prompt = f"""
        You are an expert day trader. Validate the algorithmic signal.
        Input: {json.dumps(context_payload, indent=2, default=str)}
        
        Output JSON ONLY:
        {{
            "decision": "BUY" | "SELL" | "IGNORE",
            "confidence": 0-100,
            "reasoning": "brief explanation",
            "suggested_quantity": 0,
            "override_algorithm": false
        }}
        """

        # Priority List of Providers/Models
        providers = []
        
        # 1. Gemini 2.0 Flash (Fastest/Newest)
        if self.gemini_client and "gemini" not in self.exhausted_providers:
            providers.append(("gemini", "gemini-2.0-flash-exp"))
            
        # 2. Gemini 1.5 Flash (Reliable Fallback)
        if self.gemini_client and "gemini" not in self.exhausted_providers:
            providers.append(("gemini", "gemini-1.5-flash-latest"))
            
        # 3. OpenAI GPT-4o-mini (Cheap/Fast)
        if self.openai_client and "openai" not in self.exhausted_providers:
            providers.append(("openai", "gpt-4o-mini"))
            
        # 4. Gemini Pro (Stronger)
        if self.gemini_client and "gemini" not in self.exhausted_providers:
            providers.append(("gemini", "gemini-1.5-pro"))
            
        # 5. Claude Haiku (Fast)
        if self.anthropic_client and "anthropic" not in self.exhausted_providers:
            providers.append(("anthropic", "claude-3-haiku-20240307"))

        if not providers:
            print("🛑 CRITICAL: ALL AI PROVIDERS EXHAUSTED.")
            return {"decision": "IGNORE", "confidence": 0, "reasoning": "AI Service Unreachable", "override_algorithm": False}

        # Try loop
        for provider, model in providers:
            try:
                if provider == "gemini":
                    return self._call_gemini(model, prompt)
                elif provider == "openai":
                    return self._call_openai(model, prompt)
                elif provider == "anthropic":
                    return self._call_anthropic(model, prompt)
                    
            except Exception as e:
                err_str = str(e)
                print(f"⚠️ [AI] {provider.upper()} ({model}) Failed: {err_str[:100]}...")
                
                # Check formatting of Google Errors
                is_quota = "429" in err_str or "quota" in err_str.lower() or "exhausted" in err_str.lower()
                
                if is_quota:
                    print(f"   🔒 {provider.upper()} Quota Exceeded. Marking provider as exhausted.")
                    self.exhausted_providers.add(provider)
                
                continue
                
        return {"decision": "IGNORE", "confidence": 0, "reasoning": "All Models Failed", "override_algorithm": False}

    def _call_gemini(self, model, prompt):
        response = self.gemini_client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        print(f"✅ [AI] Success using Gemini ({model})")
        return json.loads(response.text)

    def _call_openai(self, model, prompt):
        response = self.openai_client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": prompt}],
            response_format={"type": "json_object"}
        )
        print(f"✅ [AI] Success using OpenAI ({model})")
        return json.loads(response.choices[0].message.content)

    def _call_anthropic(self, model, prompt):
        response = self.anthropic_client.messages.create(
            model=model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt + "\nRespond with valid JSON only."}]
        )
        print(f"✅ [AI] Success using Claude ({model})")
        content = response.content[0].text
        start = content.find('{')
        end = content.rfind('}') + 1
        return json.loads(content[start:end]) if start != -1 else {"decision": "IGNORE"}

    def _simplify_market_data(self, market_data: Dict) -> Dict:
        if not market_data: return {}
        return {
            "price": market_data.get("price"),
            "change": market_data.get("change_percent"),
            "rsi": market_data.get("rsi"),
            "macd": market_data.get("macd_signal")
        }
        
    def quick_sentiment_check(self, news_headlines: list) -> Dict:
        # Simplified stubs to prevent errors if called
        return {"sentiment": "neutral", "confidence": 0}

    def get_usage_stats(self) -> Dict:
        return {"calls_today": self.calls_today, "exhausted": list(self.exhausted_providers)}

ai_engine = AIEngine()
