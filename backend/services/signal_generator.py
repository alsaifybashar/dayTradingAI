"""
Trading Signal Generator

Combines multiple analysis methods to generate trading signals:
1. Candlestick Pattern Analysis (algorithmic)
2. Technical Indicators (RSI, MACD)
3. News Sentiment Analysis (keyword-based)
4. Volume Analysis

This module is designed to MINIMIZE AI usage by making algorithmic
decisions when signals are clear, and only consulting AI for edge cases.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import pandas as pd

from backend.services.candlestick_patterns import pattern_detector, Candle
from backend.services.news_service import news_service
from colorama import Fore


class TradeDecision(Enum):
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"


@dataclass
class TradingSignal:
    """Complete trading signal with all analysis components"""
    ticker: str
    decision: str  # "BUY", "SELL", "HOLD"
    confidence: int  # 0-100
    use_ai: bool  # Whether AI should be consulted

    # Component scores
    pattern_score: float
    indicator_score: float
    sentiment_score: float
    volume_score: float

    # Detailed analysis
    patterns_detected: List[Dict]
    indicator_analysis: Dict
    sentiment_analysis: Dict
    volume_analysis: Dict

    # Reasoning
    reasoning: str
    suggested_quantity: int


class SignalGenerator:
    """
    Generates trading signals by combining multiple analysis methods.

    Workflow:
    1. Analyze candlestick patterns
    2. Check technical indicators (RSI, MACD)
    3. Analyze news sentiment
    4. Check volume patterns
    5. Combine all signals with weights
    6. Determine if AI consultation is needed

    AI is ONLY consulted when:
    - Signals are contradictory (bullish patterns but bearish sentiment)
    - Confidence is below threshold (< 60%)
    - Unusual market conditions detected
    """

    def __init__(self):
        # Weight configuration for signal components
        self.weights = {
            "patterns": 0.35,     # Candlestick patterns
            "indicators": 0.25,   # RSI, MACD
            "sentiment": 0.20,    # News sentiment
            "volume": 0.20        # Volume analysis
        }

        # Thresholds
        self.confidence_threshold = 60  # Below this, consult AI
        self.strong_signal_threshold = 80  # Above this, very confident

        # RSI thresholds
        self.rsi_oversold = 30
        self.rsi_overbought = 70

    def generate_signal(self,
                        ticker: str,
                        candles: List[Dict],
                        rsi: Optional[float] = None,
                        macd: Optional[float] = None,
                        macd_signal: Optional[float] = None,
                        volume: Optional[int] = None,
                        avg_volume: Optional[int] = None,
                        news_articles: Optional[List[Dict]] = None,
                        portfolio_balance: float = 1000) -> TradingSignal:
        """
        Generate a complete trading signal.

        Args:
            ticker: Stock ticker symbol
            candles: List of OHLCV candle dicts
            rsi: Current RSI value
            macd: Current MACD value
            macd_signal: Current MACD signal line
            volume: Current volume
            avg_volume: Average volume (for comparison)
            news_articles: List of news articles (optional, will fetch if not provided)
            portfolio_balance: Available cash for position sizing

        Returns:
            TradingSignal with decision and analysis
        """
        print(f"{Fore.BLUE}[ANALYSIS] Analyzing {ticker} technicals & patterns...")
        # 1. Convert candles and analyze patterns
        pattern_analysis = self._analyze_patterns(candles, rsi, macd, macd_signal)

        # 2. Analyze technical indicators
        indicator_analysis = self._analyze_indicators(rsi, macd, macd_signal)

        # 3. Analyze news sentiment
        if news_articles is None:
            news_articles = news_service.get_news(ticker, max_articles=10)
        sentiment_analysis = self._analyze_sentiment(news_articles)

        # 4. Analyze volume
        volume_analysis = self._analyze_volume(volume, avg_volume)

        # 5. Calculate component scores (-100 to +100)
        pattern_score = pattern_analysis.get("score", 0)
        indicator_score = indicator_analysis.get("score", 0)
        sentiment_score = sentiment_analysis.get("score", 0)
        volume_score = volume_analysis.get("score", 0)

        # 6. Calculate weighted composite score
        composite_score = (
            pattern_score * self.weights["patterns"] +
            indicator_score * self.weights["indicators"] +
            sentiment_score * self.weights["sentiment"] +
            volume_score * self.weights["volume"]
        )

        # 7. Determine decision and confidence
        decision, confidence = self._calculate_decision(composite_score, pattern_analysis)

        # 8. Check for contradictions (may need AI)
        use_ai = self._should_use_ai(
            pattern_score, indicator_score, sentiment_score, confidence
        )

        # 9. Build reasoning
        reasoning = self._build_reasoning(
            pattern_analysis, indicator_analysis, sentiment_analysis, volume_analysis
        )

        # 10. Calculate suggested quantity
        suggested_qty = self._calculate_quantity(
            decision, confidence, portfolio_balance,
            candles[-1]["close"] if candles else 100
        )

        return TradingSignal(
            ticker=ticker,
            decision=decision,
            confidence=confidence,
            use_ai=use_ai,
            pattern_score=pattern_score,
            indicator_score=indicator_score,
            sentiment_score=sentiment_score,
            volume_score=volume_score,
            patterns_detected=pattern_analysis.get("patterns", []),
            indicator_analysis=indicator_analysis,
            sentiment_analysis=sentiment_analysis,
            volume_analysis=volume_analysis,
            reasoning=reasoning,
            suggested_quantity=suggested_qty
        )

    def _analyze_patterns(self,
                          candles: List[Dict],
                          rsi: Optional[float],
                          macd: Optional[float],
                          macd_signal: Optional[float]) -> Dict:
        """Analyze candlestick patterns using the pattern detector"""
        if not candles or len(candles) < 3:
            return {"score": 0, "patterns": [], "decision": "HOLD"}

        # Convert dict candles to Candle objects
        candle_objects = pattern_detector.candles_from_list(candles)

        # Get trading signal from pattern detector
        signal = pattern_detector.get_trading_signal(
            candle_objects, rsi, macd, macd_signal
        )

        # Convert to score (-100 to +100)
        if signal["decision"] == "BUY":
            score = signal["bullish_score"] * 20  # Scale up
        elif signal["decision"] == "SELL":
            score = -signal["bearish_score"] * 20
        else:
            score = 0

        score = max(-100, min(100, score))  # Clamp

        return {
            "score": score,
            "patterns": signal["patterns"],
            "decision": signal["decision"],
            "confidence": signal["confidence"],
            "reasoning": signal["reasoning"]
        }

    def _analyze_indicators(self,
                            rsi: Optional[float],
                            macd: Optional[float],
                            macd_signal: Optional[float]) -> Dict:
        """Analyze technical indicators (RSI, MACD)"""
        score = 0
        signals = []

        # RSI Analysis
        if rsi is not None:
            if rsi < self.rsi_oversold:
                rsi_score = (self.rsi_oversold - rsi) * 2
                score += rsi_score
                signals.append(f"RSI oversold ({rsi:.1f}) - bullish")
            elif rsi > self.rsi_overbought:
                rsi_score = (rsi - self.rsi_overbought) * 2
                score -= rsi_score
                signals.append(f"RSI overbought ({rsi:.1f}) - bearish")
            else:
                signals.append(f"RSI neutral ({rsi:.1f})")

        # MACD Analysis
        if macd is not None and macd_signal is not None:
            macd_diff = macd - macd_signal

            if macd_diff > 0:
                # Bullish crossover or above signal
                macd_score = min(30, macd_diff * 10)
                score += macd_score
                signals.append("MACD bullish (above signal line)")
            elif macd_diff < 0:
                # Bearish crossover or below signal
                macd_score = min(30, abs(macd_diff) * 10)
                score -= macd_score
                signals.append("MACD bearish (below signal line)")

            # Check for crossover (strong signal)
            if abs(macd_diff) < 0.5:
                signals.append("MACD crossover imminent")

        score = max(-100, min(100, score))

        return {
            "score": score,
            "rsi": rsi,
            "macd": macd,
            "macd_signal": macd_signal,
            "signals": signals,
            "direction": "bullish" if score > 0 else ("bearish" if score < 0 else "neutral")
        }

    def _analyze_sentiment(self, news_articles: List[Dict]) -> Dict:
        """Analyze news sentiment using keyword matching"""
        if not news_articles:
            return {
                "score": 0,
                "overall": "neutral",
                "confidence": 0,
                "article_count": 0
            }

        # Use news service's sentiment analyzer
        sentiment = news_service.analyze_sentiment(news_articles)

        # Convert to score (-100 to +100)
        if sentiment["overall_sentiment"] == "bullish":
            score = sentiment["confidence"]
        elif sentiment["overall_sentiment"] == "bearish":
            score = -sentiment["confidence"]
        else:
            score = 0

        return {
            "score": score,
            "overall": sentiment["overall_sentiment"],
            "confidence": sentiment["confidence"],
            "bullish_count": sentiment["bullish_count"],
            "bearish_count": sentiment["bearish_count"],
            "neutral_count": sentiment["neutral_count"],
            "article_count": sentiment["total_articles"]
        }

    def _analyze_volume(self,
                        volume: Optional[int],
                        avg_volume: Optional[int]) -> Dict:
        """Analyze volume patterns"""
        if volume is None or avg_volume is None or avg_volume == 0:
            return {"score": 0, "ratio": 1.0, "signal": "normal"}

        ratio = volume / avg_volume

        # High volume confirms moves, low volume suggests weakness
        if ratio > 2.0:
            # Very high volume - strong confirmation
            score = 30
            signal = "very_high"
        elif ratio > 1.5:
            score = 20
            signal = "high"
        elif ratio > 1.2:
            score = 10
            signal = "above_average"
        elif ratio < 0.5:
            # Low volume - weak conviction
            score = -20
            signal = "very_low"
        elif ratio < 0.8:
            score = -10
            signal = "below_average"
        else:
            score = 0
            signal = "normal"

        return {
            "score": score,
            "ratio": ratio,
            "signal": signal,
            "volume": volume,
            "avg_volume": avg_volume
        }

    def _calculate_decision(self,
                            composite_score: float,
                            pattern_analysis: Dict) -> Tuple[str, int]:
        """Calculate final decision and confidence from composite score"""

        # Strong thresholds
        if composite_score > 40:
            decision = "BUY"
            confidence = min(95, 60 + int(composite_score))
        elif composite_score > 20:
            decision = "BUY"
            confidence = min(80, 50 + int(composite_score))
        elif composite_score < -40:
            decision = "SELL"
            confidence = min(95, 60 + int(abs(composite_score)))
        elif composite_score < -20:
            decision = "SELL"
            confidence = min(80, 50 + int(abs(composite_score)))
        else:
            decision = "HOLD"
            confidence = 50 - int(abs(composite_score))

        # Boost confidence if strong patterns detected
        if pattern_analysis.get("patterns"):
            top_pattern = pattern_analysis["patterns"][0] if pattern_analysis["patterns"] else None
            if top_pattern and top_pattern.get("confidence", 0) > 75:
                confidence = min(95, confidence + 10)

        return decision, max(0, min(100, confidence))

    def _should_use_ai(self,
                       pattern_score: float,
                       indicator_score: float,
                       sentiment_score: float,
                       confidence: int) -> bool:
        """Determine if AI should be consulted"""

        # Low confidence = consult AI
        if confidence < self.confidence_threshold:
            return True

        # Contradictory signals = consult AI
        signals = [pattern_score, indicator_score, sentiment_score]
        positive = sum(1 for s in signals if s > 10)
        negative = sum(1 for s in signals if s < -10)

        if positive > 0 and negative > 0:
            # Mixed signals
            return True

        # Strong clear signal = no need for AI
        if abs(pattern_score) > 50 and confidence > 70:
            return False

        # Default: don't use AI if confidence is acceptable
        return confidence < 70

    def _build_reasoning(self,
                         pattern_analysis: Dict,
                         indicator_analysis: Dict,
                         sentiment_analysis: Dict,
                         volume_analysis: Dict) -> str:
        """Build human-readable reasoning for the decision"""
        parts = []

        # Pattern reasoning
        if pattern_analysis.get("patterns"):
            pattern_names = [p["name"] for p in pattern_analysis["patterns"][:3]]
            parts.append(f"Patterns: {', '.join(pattern_names)}")

        # Indicator reasoning
        if indicator_analysis.get("signals"):
            parts.append(f"Indicators: {'; '.join(indicator_analysis['signals'][:2])}")

        # Sentiment reasoning
        sentiment_str = sentiment_analysis.get("overall", "neutral")
        article_count = sentiment_analysis.get("article_count", 0)
        if article_count > 0:
            parts.append(f"News: {sentiment_str} ({article_count} articles)")

        # Volume reasoning
        volume_sig = volume_analysis.get("signal", "normal")
        if volume_sig != "normal":
            ratio = volume_analysis.get("ratio", 1.0)
            parts.append(f"Volume: {volume_sig} ({ratio:.1f}x avg)")

        return " | ".join(parts) if parts else "No clear signals detected"

    def _calculate_quantity(self,
                            decision: str,
                            confidence: int,
                            balance: float,
                            price: float) -> int:
        """Calculate suggested position size based on Kelly-style risk management"""
        if decision == "HOLD" or price <= 0:
            return 0

        # Base allocation: 20% of portfolio
        base_allocation = 0.20

        # Adjust by confidence
        if confidence >= 85:
            allocation = base_allocation * 1.5  # 30%
        elif confidence >= 75:
            allocation = base_allocation * 1.25  # 25%
        elif confidence >= 65:
            allocation = base_allocation  # 20%
        else:
            allocation = base_allocation * 0.5  # 10%

        # Calculate quantity
        position_value = balance * allocation
        quantity = int(position_value / price)

        return max(1, quantity)  # At least 1 share

    def get_quick_decision(self, candles: List[Dict]) -> Dict:
        """
        Ultra-fast decision based on patterns only.
        No AI, no news, no external calls.

        Use this for real-time monitoring where speed matters.
        """
        if not candles or len(candles) < 3:
            return {"decision": "HOLD", "confidence": 0, "use_ai": True}

        candle_objects = pattern_detector.candles_from_list(candles)
        patterns = pattern_detector.analyze(candle_objects)

        if not patterns:
            return {"decision": "HOLD", "confidence": 0, "use_ai": True}

        # Use top pattern
        top = patterns[0]

        return {
            "decision": top.action_suggestion,
            "confidence": int(top.confidence),
            "pattern": top.name,
            "type": top.pattern_type.value,
            "use_ai": top.confidence < 65
        }


# Singleton instance
signal_generator = SignalGenerator()
