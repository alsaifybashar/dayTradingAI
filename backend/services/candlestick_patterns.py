"""
Candlestick Pattern Detection Module

This module provides algorithmic detection of 18 essential candlestick patterns
for day trading. Eliminates AI dependency for pattern recognition.

Patterns Implemented:
- Bullish (6): Hammer, Inverted Hammer, Bullish Engulfing, Piercing Line, Morning Star, Three White Soldiers
- Bearish (6): Hanging Man, Shooting Star, Bearish Engulfing, Evening Star, Three Black Crows, Dark Cloud Cover
- Continuation (4): Doji, Spinning Top, Falling Three Methods, Rising Three Methods
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum
import pandas as pd
import numpy as np


class PatternType(Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    CONTINUATION = "continuation"
    NEUTRAL = "neutral"


class SignalStrength(Enum):
    STRONG = 3
    MODERATE = 2
    WEAK = 1


@dataclass
class Candle:
    """Represents a single candlestick"""
    open: float
    high: float
    low: float
    close: float
    volume: int = 0
    time: str = ""

    @property
    def body(self) -> float:
        """Absolute body size"""
        return abs(self.close - self.open)

    @property
    def body_percent(self) -> float:
        """Body as percentage of total range"""
        total_range = self.high - self.low
        if total_range == 0:
            return 0
        return (self.body / total_range) * 100

    @property
    def upper_shadow(self) -> float:
        """Upper wick/shadow length"""
        return self.high - max(self.open, self.close)

    @property
    def lower_shadow(self) -> float:
        """Lower wick/shadow length"""
        return min(self.open, self.close) - self.low

    @property
    def total_range(self) -> float:
        """Total high-low range"""
        return self.high - self.low

    @property
    def is_bullish(self) -> bool:
        """True if close > open"""
        return self.close > self.open

    @property
    def is_bearish(self) -> bool:
        """True if close < open"""
        return self.close < self.open

    @property
    def midpoint(self) -> float:
        """Midpoint of the body"""
        return (self.open + self.close) / 2


@dataclass
class PatternResult:
    """Result of pattern detection"""
    name: str
    pattern_type: PatternType
    strength: SignalStrength
    confidence: float  # 0-100
    description: str
    candles_used: int
    action_suggestion: str  # "BUY", "SELL", "HOLD"


class CandlestickPatternDetector:
    """
    Detects candlestick patterns from OHLC data.

    Usage:
        detector = CandlestickPatternDetector()
        patterns = detector.analyze(candles_list)
    """

    def __init__(self,
                 small_body_threshold: float = 0.1,
                 long_shadow_ratio: float = 2.0,
                 engulfing_ratio: float = 1.0):
        """
        Initialize detector with configurable thresholds.

        Args:
            small_body_threshold: Body size relative to range for doji/spinning top (default 10%)
            long_shadow_ratio: Shadow must be X times body for hammer patterns
            engulfing_ratio: How much larger engulfing candle must be
        """
        self.small_body_threshold = small_body_threshold
        self.long_shadow_ratio = long_shadow_ratio
        self.engulfing_ratio = engulfing_ratio

    def candles_from_list(self, candle_list: List[Dict]) -> List[Candle]:
        """Convert list of dicts to Candle objects"""
        candles = []
        for c in candle_list:
            candles.append(Candle(
                open=float(c.get('open', c.get('o', 0))),
                high=float(c.get('high', c.get('h', 0))),
                low=float(c.get('low', c.get('l', 0))),
                close=float(c.get('close', c.get('c', 0))),
                volume=int(c.get('volume', c.get('v', 0))),
                time=str(c.get('time', c.get('t', '')))
            ))
        return candles

    def candles_from_dataframe(self, df: pd.DataFrame) -> List[Candle]:
        """Convert pandas DataFrame to Candle objects"""
        candles = []
        for _, row in df.iterrows():
            candles.append(Candle(
                open=float(row.get('Open', row.get('open', 0))),
                high=float(row.get('High', row.get('high', 0))),
                low=float(row.get('Low', row.get('low', 0))),
                close=float(row.get('Close', row.get('close', 0))),
                volume=int(row.get('Volume', row.get('volume', 0)))
            ))
        return candles

    def analyze(self, candles: List[Candle], lookback: int = 20) -> List[PatternResult]:
        """
        Analyze candles for all patterns.

        Args:
            candles: List of Candle objects (most recent last)
            lookback: How many recent candles to analyze

        Returns:
            List of detected PatternResult objects, sorted by confidence
        """
        if len(candles) < 3:
            return []

        # Use most recent candles
        recent = candles[-lookback:] if len(candles) > lookback else candles
        patterns = []

        # Check all pattern types
        patterns.extend(self._check_single_candle_patterns(recent))
        patterns.extend(self._check_two_candle_patterns(recent))
        patterns.extend(self._check_three_candle_patterns(recent))
        patterns.extend(self._check_multi_candle_patterns(recent))

        # Sort by confidence (highest first)
        patterns.sort(key=lambda x: x.confidence, reverse=True)

        return patterns

    def get_trading_signal(self, candles: List[Candle],
                           rsi: Optional[float] = None,
                           macd: Optional[float] = None,
                           macd_signal: Optional[float] = None) -> Dict:
        """
        Generate trading signal based on pattern analysis + technical indicators.

        Returns:
            {
                "decision": "BUY" | "SELL" | "HOLD",
                "confidence": 0-100,
                "patterns": [list of detected patterns],
                "reasoning": "explanation",
                "use_ai": bool  # Whether AI should be consulted
            }
        """
        patterns = self.analyze(candles)

        if not patterns:
            return {
                "decision": "HOLD",
                "confidence": 0,
                "patterns": [],
                "reasoning": "No clear patterns detected",
                "use_ai": True  # Consult AI when uncertain
            }

        # Score bullish vs bearish signals
        bullish_score = 0
        bearish_score = 0
        continuation_score = 0

        for p in patterns:
            weight = p.strength.value * (p.confidence / 100)
            if p.pattern_type == PatternType.BULLISH:
                bullish_score += weight
            elif p.pattern_type == PatternType.BEARISH:
                bearish_score += weight
            else:
                continuation_score += weight

        # Add technical indicator confirmation
        indicator_confirmation = 0
        indicator_notes = []

        if rsi is not None:
            if rsi < 30:
                bullish_score += 1.5
                indicator_notes.append(f"RSI oversold ({rsi:.1f})")
            elif rsi > 70:
                bearish_score += 1.5
                indicator_notes.append(f"RSI overbought ({rsi:.1f})")
            elif 40 <= rsi <= 60:
                indicator_notes.append(f"RSI neutral ({rsi:.1f})")

        if macd is not None and macd_signal is not None:
            if macd > macd_signal:
                bullish_score += 1.0
                indicator_notes.append("MACD bullish crossover")
            elif macd < macd_signal:
                bearish_score += 1.0
                indicator_notes.append("MACD bearish crossover")

        # Determine decision
        total_score = bullish_score + bearish_score + continuation_score
        if total_score == 0:
            total_score = 1  # Avoid division by zero

        # Calculate confidence based on score difference
        score_diff = abs(bullish_score - bearish_score)
        base_confidence = min(85, (score_diff / total_score) * 100 + 20)

        # Boost confidence if top pattern is strong
        if patterns and patterns[0].confidence > 70:
            base_confidence = min(90, base_confidence + 10)

        # Decision logic
        if bullish_score > bearish_score * 1.3:  # Clear bullish
            decision = "BUY"
            confidence = base_confidence
            reasoning = self._build_reasoning(patterns[:3], indicator_notes, "bullish")
            use_ai = confidence < 60  # Only use AI if uncertain
        elif bearish_score > bullish_score * 1.3:  # Clear bearish
            decision = "SELL"
            confidence = base_confidence
            reasoning = self._build_reasoning(patterns[:3], indicator_notes, "bearish")
            use_ai = confidence < 60
        elif continuation_score > max(bullish_score, bearish_score):
            decision = "HOLD"
            confidence = 50
            reasoning = self._build_reasoning(patterns[:3], indicator_notes, "continuation")
            use_ai = True  # Continuation patterns are ambiguous
        else:
            decision = "HOLD"
            confidence = 30
            reasoning = "Mixed signals - no clear direction"
            use_ai = True  # Consult AI for ambiguous cases

        return {
            "decision": decision,
            "confidence": int(confidence),
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
            "reasoning": reasoning,
            "bullish_score": round(bullish_score, 2),
            "bearish_score": round(bearish_score, 2),
            "use_ai": use_ai
        }

    def _build_reasoning(self, patterns: List[PatternResult],
                         indicators: List[str],
                         direction: str) -> str:
        """Build human-readable reasoning"""
        parts = []

        if patterns:
            pattern_names = [p.name for p in patterns]
            parts.append(f"Detected {direction} patterns: {', '.join(pattern_names)}")

        if indicators:
            parts.append(f"Technical confirmation: {', '.join(indicators)}")

        return ". ".join(parts) if parts else f"Weak {direction} signal"

    # =====================================================
    # SINGLE CANDLE PATTERNS
    # =====================================================

    def _check_single_candle_patterns(self, candles: List[Candle]) -> List[PatternResult]:
        """Check patterns that use only the most recent candle"""
        patterns = []
        if len(candles) < 1:
            return patterns

        current = candles[-1]
        prev_candles = candles[:-1] if len(candles) > 1 else []

        # Determine trend context from previous candles
        trend = self._get_trend(prev_candles[-5:] if len(prev_candles) >= 5 else prev_candles)

        # Doji
        doji = self._check_doji(current)
        if doji:
            patterns.append(doji)

        # Spinning Top
        spinning = self._check_spinning_top(current)
        if spinning:
            patterns.append(spinning)

        # Hammer (bullish - appears in downtrend)
        if trend == "down":
            hammer = self._check_hammer(current)
            if hammer:
                patterns.append(hammer)

        # Inverted Hammer (bullish - appears in downtrend)
        if trend == "down":
            inv_hammer = self._check_inverted_hammer(current)
            if inv_hammer:
                patterns.append(inv_hammer)

        # Hanging Man (bearish - appears in uptrend)
        if trend == "up":
            hanging = self._check_hanging_man(current)
            if hanging:
                patterns.append(hanging)

        # Shooting Star (bearish - appears in uptrend)
        if trend == "up":
            shooting = self._check_shooting_star(current)
            if shooting:
                patterns.append(shooting)

        return patterns

    def _check_doji(self, candle: Candle) -> Optional[PatternResult]:
        """
        Doji: Very small body, shadows on both sides
        Indicates indecision - potential reversal
        """
        if candle.total_range == 0:
            return None

        body_ratio = candle.body / candle.total_range

        if body_ratio < 0.1:  # Body < 10% of range
            # Check for shadows on both sides
            has_upper = candle.upper_shadow > candle.body * 0.5
            has_lower = candle.lower_shadow > candle.body * 0.5

            if has_upper and has_lower:
                confidence = 70 + (1 - body_ratio) * 30
                return PatternResult(
                    name="Doji",
                    pattern_type=PatternType.CONTINUATION,
                    strength=SignalStrength.MODERATE,
                    confidence=min(90, confidence),
                    description="Indecision candle - potential trend reversal",
                    candles_used=1,
                    action_suggestion="HOLD"
                )
        return None

    def _check_spinning_top(self, candle: Candle) -> Optional[PatternResult]:
        """
        Spinning Top: Small body with upper and lower shadows
        Similar to doji but with slightly larger body
        """
        if candle.total_range == 0:
            return None

        body_ratio = candle.body / candle.total_range

        if 0.1 <= body_ratio <= 0.3:  # Body 10-30% of range
            # Shadows should be present on both sides
            upper_ratio = candle.upper_shadow / candle.total_range
            lower_ratio = candle.lower_shadow / candle.total_range

            if upper_ratio > 0.2 and lower_ratio > 0.2:
                return PatternResult(
                    name="Spinning Top",
                    pattern_type=PatternType.CONTINUATION,
                    strength=SignalStrength.WEAK,
                    confidence=60,
                    description="Indecision - market equilibrium",
                    candles_used=1,
                    action_suggestion="HOLD"
                )
        return None

    def _check_hammer(self, candle: Candle) -> Optional[PatternResult]:
        """
        Hammer: Small body at top, long lower shadow (2x body), little/no upper shadow
        Bullish reversal pattern in downtrend
        """
        if candle.total_range == 0 or candle.body == 0:
            return None

        # Body in upper third of range
        body_top = max(candle.open, candle.close)
        upper_third = candle.low + (candle.total_range * 0.67)

        if body_top < upper_third:
            return None

        # Lower shadow at least 2x body
        if candle.lower_shadow < candle.body * self.long_shadow_ratio:
            return None

        # Upper shadow very small (< 10% of range)
        if candle.upper_shadow > candle.total_range * 0.15:
            return None

        confidence = 65 + min(25, (candle.lower_shadow / candle.body - 2) * 10)

        return PatternResult(
            name="Hammer",
            pattern_type=PatternType.BULLISH,
            strength=SignalStrength.STRONG,
            confidence=min(90, confidence),
            description="Bullish reversal - buyers rejected lower prices",
            candles_used=1,
            action_suggestion="BUY"
        )

    def _check_inverted_hammer(self, candle: Candle) -> Optional[PatternResult]:
        """
        Inverted Hammer: Small body at bottom, long upper shadow, little/no lower shadow
        Bullish reversal pattern in downtrend
        """
        if candle.total_range == 0 or candle.body == 0:
            return None

        # Body in lower third of range
        body_bottom = min(candle.open, candle.close)
        lower_third = candle.low + (candle.total_range * 0.33)

        if body_bottom > lower_third:
            return None

        # Upper shadow at least 2x body
        if candle.upper_shadow < candle.body * self.long_shadow_ratio:
            return None

        # Lower shadow very small
        if candle.lower_shadow > candle.total_range * 0.15:
            return None

        return PatternResult(
            name="Inverted Hammer",
            pattern_type=PatternType.BULLISH,
            strength=SignalStrength.MODERATE,
            confidence=65,
            description="Potential bullish reversal - needs confirmation",
            candles_used=1,
            action_suggestion="BUY"
        )

    def _check_hanging_man(self, candle: Candle) -> Optional[PatternResult]:
        """
        Hanging Man: Same shape as hammer but appears in uptrend
        Bearish reversal signal
        """
        if candle.total_range == 0 or candle.body == 0:
            return None

        # Body in upper third
        body_top = max(candle.open, candle.close)
        upper_third = candle.low + (candle.total_range * 0.67)

        if body_top < upper_third:
            return None

        # Long lower shadow
        if candle.lower_shadow < candle.body * self.long_shadow_ratio:
            return None

        # Small upper shadow
        if candle.upper_shadow > candle.total_range * 0.15:
            return None

        return PatternResult(
            name="Hanging Man",
            pattern_type=PatternType.BEARISH,
            strength=SignalStrength.MODERATE,
            confidence=60,
            description="Bearish reversal warning in uptrend",
            candles_used=1,
            action_suggestion="SELL"
        )

    def _check_shooting_star(self, candle: Candle) -> Optional[PatternResult]:
        """
        Shooting Star: Small body at bottom, long upper shadow
        Bearish reversal pattern in uptrend
        """
        if candle.total_range == 0 or candle.body == 0:
            return None

        # Body in lower third
        body_bottom = min(candle.open, candle.close)
        lower_third = candle.low + (candle.total_range * 0.33)

        if body_bottom > lower_third:
            return None

        # Long upper shadow
        if candle.upper_shadow < candle.body * self.long_shadow_ratio:
            return None

        # Small lower shadow
        if candle.lower_shadow > candle.total_range * 0.15:
            return None

        confidence = 65 + min(25, (candle.upper_shadow / candle.body - 2) * 10)

        return PatternResult(
            name="Shooting Star",
            pattern_type=PatternType.BEARISH,
            strength=SignalStrength.STRONG,
            confidence=min(90, confidence),
            description="Bearish reversal - sellers rejected higher prices",
            candles_used=1,
            action_suggestion="SELL"
        )

    # =====================================================
    # TWO CANDLE PATTERNS
    # =====================================================

    def _check_two_candle_patterns(self, candles: List[Candle]) -> List[PatternResult]:
        """Check patterns that use two candles"""
        patterns = []
        if len(candles) < 2:
            return patterns

        prev = candles[-2]
        current = candles[-1]

        # Bullish Engulfing
        engulfing = self._check_bullish_engulfing(prev, current)
        if engulfing:
            patterns.append(engulfing)

        # Bearish Engulfing
        bear_engulf = self._check_bearish_engulfing(prev, current)
        if bear_engulf:
            patterns.append(bear_engulf)

        # Piercing Line
        piercing = self._check_piercing_line(prev, current)
        if piercing:
            patterns.append(piercing)

        # Dark Cloud Cover
        dark_cloud = self._check_dark_cloud_cover(prev, current)
        if dark_cloud:
            patterns.append(dark_cloud)

        return patterns

    def _check_bullish_engulfing(self, prev: Candle, current: Candle) -> Optional[PatternResult]:
        """
        Bullish Engulfing: Bearish candle followed by larger bullish candle
        that completely engulfs the previous body
        """
        # Previous must be bearish, current must be bullish
        if not prev.is_bearish or not current.is_bullish:
            return None

        # Current body must engulf previous body
        if current.open >= prev.close or current.close <= prev.open:
            return None

        # Calculate how much larger current is
        size_ratio = current.body / prev.body if prev.body > 0 else 2

        if size_ratio >= self.engulfing_ratio:
            confidence = 70 + min(20, (size_ratio - 1) * 10)
            return PatternResult(
                name="Bullish Engulfing",
                pattern_type=PatternType.BULLISH,
                strength=SignalStrength.STRONG,
                confidence=min(90, confidence),
                description="Strong bullish reversal - buyers overwhelmed sellers",
                candles_used=2,
                action_suggestion="BUY"
            )
        return None

    def _check_bearish_engulfing(self, prev: Candle, current: Candle) -> Optional[PatternResult]:
        """
        Bearish Engulfing: Bullish candle followed by larger bearish candle
        that completely engulfs the previous body
        """
        # Previous must be bullish, current must be bearish
        if not prev.is_bullish or not current.is_bearish:
            return None

        # Current body must engulf previous body
        if current.open <= prev.close or current.close >= prev.open:
            return None

        size_ratio = current.body / prev.body if prev.body > 0 else 2

        if size_ratio >= self.engulfing_ratio:
            confidence = 70 + min(20, (size_ratio - 1) * 10)
            return PatternResult(
                name="Bearish Engulfing",
                pattern_type=PatternType.BEARISH,
                strength=SignalStrength.STRONG,
                confidence=min(90, confidence),
                description="Strong bearish reversal - sellers overwhelmed buyers",
                candles_used=2,
                action_suggestion="SELL"
            )
        return None

    def _check_piercing_line(self, prev: Candle, current: Candle) -> Optional[PatternResult]:
        """
        Piercing Line: Bearish candle followed by bullish candle that opens
        below previous low and closes above 50% of previous body
        """
        if not prev.is_bearish or not current.is_bullish:
            return None

        # Current opens below previous low
        if current.open >= prev.low:
            return None

        # Current closes above 50% of previous body
        prev_midpoint = (prev.open + prev.close) / 2
        if current.close <= prev_midpoint:
            return None

        # But doesn't completely engulf (that's bullish engulfing)
        if current.close >= prev.open:
            return None

        return PatternResult(
            name="Piercing Line",
            pattern_type=PatternType.BULLISH,
            strength=SignalStrength.MODERATE,
            confidence=70,
            description="Bullish reversal - strong buying pressure",
            candles_used=2,
            action_suggestion="BUY"
        )

    def _check_dark_cloud_cover(self, prev: Candle, current: Candle) -> Optional[PatternResult]:
        """
        Dark Cloud Cover: Bullish candle followed by bearish candle that opens
        above previous high and closes below 50% of previous body
        """
        if not prev.is_bullish or not current.is_bearish:
            return None

        # Current opens above previous high
        if current.open <= prev.high:
            return None

        # Current closes below 50% of previous body
        prev_midpoint = (prev.open + prev.close) / 2
        if current.close >= prev_midpoint:
            return None

        # But doesn't completely engulf
        if current.close <= prev.open:
            return None

        return PatternResult(
            name="Dark Cloud Cover",
            pattern_type=PatternType.BEARISH,
            strength=SignalStrength.MODERATE,
            confidence=70,
            description="Bearish reversal - strong selling pressure",
            candles_used=2,
            action_suggestion="SELL"
        )

    # =====================================================
    # THREE CANDLE PATTERNS
    # =====================================================

    def _check_three_candle_patterns(self, candles: List[Candle]) -> List[PatternResult]:
        """Check patterns that use three candles"""
        patterns = []
        if len(candles) < 3:
            return patterns

        c1, c2, c3 = candles[-3], candles[-2], candles[-1]

        # Morning Star
        morning = self._check_morning_star(c1, c2, c3)
        if morning:
            patterns.append(morning)

        # Evening Star
        evening = self._check_evening_star(c1, c2, c3)
        if evening:
            patterns.append(evening)

        # Three White Soldiers
        soldiers = self._check_three_white_soldiers(c1, c2, c3)
        if soldiers:
            patterns.append(soldiers)

        # Three Black Crows
        crows = self._check_three_black_crows(c1, c2, c3)
        if crows:
            patterns.append(crows)

        return patterns

    def _check_morning_star(self, c1: Candle, c2: Candle, c3: Candle) -> Optional[PatternResult]:
        """
        Morning Star:
        1. Long bearish candle
        2. Small body (gap down ideally) - can be doji
        3. Long bullish candle closing above 50% of first candle
        """
        # First candle bearish with decent body
        if not c1.is_bearish or c1.body < c1.total_range * 0.3:
            return None

        # Second candle has small body (star)
        if c2.body > c1.body * 0.5:
            return None

        # Third candle bullish
        if not c3.is_bullish:
            return None

        # Third closes above midpoint of first
        c1_mid = (c1.open + c1.close) / 2
        if c3.close < c1_mid:
            return None

        return PatternResult(
            name="Morning Star",
            pattern_type=PatternType.BULLISH,
            strength=SignalStrength.STRONG,
            confidence=80,
            description="Strong bullish reversal pattern - trend change likely",
            candles_used=3,
            action_suggestion="BUY"
        )

    def _check_evening_star(self, c1: Candle, c2: Candle, c3: Candle) -> Optional[PatternResult]:
        """
        Evening Star:
        1. Long bullish candle
        2. Small body (gap up ideally) - can be doji
        3. Long bearish candle closing below 50% of first candle
        """
        # First candle bullish with decent body
        if not c1.is_bullish or c1.body < c1.total_range * 0.3:
            return None

        # Second candle has small body
        if c2.body > c1.body * 0.5:
            return None

        # Third candle bearish
        if not c3.is_bearish:
            return None

        # Third closes below midpoint of first
        c1_mid = (c1.open + c1.close) / 2
        if c3.close > c1_mid:
            return None

        return PatternResult(
            name="Evening Star",
            pattern_type=PatternType.BEARISH,
            strength=SignalStrength.STRONG,
            confidence=80,
            description="Strong bearish reversal pattern - trend change likely",
            candles_used=3,
            action_suggestion="SELL"
        )

    def _check_three_white_soldiers(self, c1: Candle, c2: Candle, c3: Candle) -> Optional[PatternResult]:
        """
        Three White Soldiers: Three consecutive bullish candles with:
        - Each opening within previous body
        - Each closing near its high
        - Progressively higher closes
        """
        # All three must be bullish
        if not (c1.is_bullish and c2.is_bullish and c3.is_bullish):
            return None

        # Progressively higher closes
        if not (c1.close < c2.close < c3.close):
            return None

        # Each opens within previous body
        if c2.open < c1.open or c2.open > c1.close:
            return None
        if c3.open < c2.open or c3.open > c2.close:
            return None

        # Bodies should be decent size (not spinning tops)
        min_body_ratio = 0.4
        for c in [c1, c2, c3]:
            if c.total_range > 0 and c.body / c.total_range < min_body_ratio:
                return None

        return PatternResult(
            name="Three White Soldiers",
            pattern_type=PatternType.BULLISH,
            strength=SignalStrength.STRONG,
            confidence=85,
            description="Strong bullish continuation - sustained buying pressure",
            candles_used=3,
            action_suggestion="BUY"
        )

    def _check_three_black_crows(self, c1: Candle, c2: Candle, c3: Candle) -> Optional[PatternResult]:
        """
        Three Black Crows: Three consecutive bearish candles with:
        - Each opening within previous body
        - Each closing near its low
        - Progressively lower closes
        """
        # All three must be bearish
        if not (c1.is_bearish and c2.is_bearish and c3.is_bearish):
            return None

        # Progressively lower closes
        if not (c1.close > c2.close > c3.close):
            return None

        # Each opens within previous body
        if c2.open > c1.open or c2.open < c1.close:
            return None
        if c3.open > c2.open or c3.open < c2.close:
            return None

        # Bodies should be decent size
        min_body_ratio = 0.4
        for c in [c1, c2, c3]:
            if c.total_range > 0 and c.body / c.total_range < min_body_ratio:
                return None

        return PatternResult(
            name="Three Black Crows",
            pattern_type=PatternType.BEARISH,
            strength=SignalStrength.STRONG,
            confidence=85,
            description="Strong bearish continuation - sustained selling pressure",
            candles_used=3,
            action_suggestion="SELL"
        )

    # =====================================================
    # MULTI-CANDLE CONTINUATION PATTERNS
    # =====================================================

    def _check_multi_candle_patterns(self, candles: List[Candle]) -> List[PatternResult]:
        """Check patterns that use 5+ candles"""
        patterns = []
        if len(candles) < 5:
            return patterns

        # Get last 5 candles
        c = candles[-5:]

        # Rising Three Methods
        rising = self._check_rising_three_methods(c)
        if rising:
            patterns.append(rising)

        # Falling Three Methods
        falling = self._check_falling_three_methods(c)
        if falling:
            patterns.append(falling)

        return patterns

    def _check_rising_three_methods(self, candles: List[Candle]) -> Optional[PatternResult]:
        """
        Rising Three Methods (Bullish Continuation):
        1. Long bullish candle
        2-4. Three small bearish candles within range of first
        5. Long bullish candle closing above first candle's close
        """
        c1, c2, c3, c4, c5 = candles[0], candles[1], candles[2], candles[3], candles[4]

        # First and last must be bullish
        if not c1.is_bullish or not c5.is_bullish:
            return None

        # Middle three should be small and generally bearish
        middle = [c2, c3, c4]
        bearish_count = sum(1 for c in middle if c.is_bearish)
        if bearish_count < 2:  # At least 2 of 3 should be bearish
            return None

        # Middle candles stay within first candle's range
        for c in middle:
            if c.high > c1.high or c.low < c1.low:
                return None

        # Last candle closes above first
        if c5.close <= c1.close:
            return None

        return PatternResult(
            name="Rising Three Methods",
            pattern_type=PatternType.CONTINUATION,
            strength=SignalStrength.STRONG,
            confidence=75,
            description="Bullish continuation - consolidation before uptrend resumes",
            candles_used=5,
            action_suggestion="BUY"
        )

    def _check_falling_three_methods(self, candles: List[Candle]) -> Optional[PatternResult]:
        """
        Falling Three Methods (Bearish Continuation):
        1. Long bearish candle
        2-4. Three small bullish candles within range of first
        5. Long bearish candle closing below first candle's close
        """
        c1, c2, c3, c4, c5 = candles[0], candles[1], candles[2], candles[3], candles[4]

        # First and last must be bearish
        if not c1.is_bearish or not c5.is_bearish:
            return None

        # Middle three should be small and generally bullish
        middle = [c2, c3, c4]
        bullish_count = sum(1 for c in middle if c.is_bullish)
        if bullish_count < 2:
            return None

        # Middle candles stay within first candle's range
        for c in middle:
            if c.high > c1.high or c.low < c1.low:
                return None

        # Last candle closes below first
        if c5.close >= c1.close:
            return None

        return PatternResult(
            name="Falling Three Methods",
            pattern_type=PatternType.CONTINUATION,
            strength=SignalStrength.STRONG,
            confidence=75,
            description="Bearish continuation - consolidation before downtrend resumes",
            candles_used=5,
            action_suggestion="SELL"
        )

    # =====================================================
    # HELPER METHODS
    # =====================================================

    def _get_trend(self, candles: List[Candle], threshold: float = 0.01) -> str:
        """
        Determine trend direction from candles.
        Returns: "up", "down", or "sideways"
        """
        if len(candles) < 2:
            return "sideways"

        # Compare first and last close
        first_close = candles[0].close
        last_close = candles[-1].close

        if first_close == 0:
            return "sideways"

        change_pct = (last_close - first_close) / first_close

        if change_pct > threshold:
            return "up"
        elif change_pct < -threshold:
            return "down"
        else:
            return "sideways"


# Singleton instance
pattern_detector = CandlestickPatternDetector()
