"""
Test suite for candlestick pattern detection and signal generation.

Run with: python -m pytest tests/test_patterns.py -v
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from backend.services.candlestick_patterns import (
    CandlestickPatternDetector, Candle, PatternType, SignalStrength
)
from backend.services.signal_generator import SignalGenerator


class TestCandleDataclass:
    """Test the Candle dataclass properties"""

    def test_bullish_candle(self):
        candle = Candle(open=100, high=110, low=95, close=108)
        assert candle.is_bullish == True
        assert candle.is_bearish == False
        assert candle.body == 8
        assert candle.upper_shadow == 2
        assert candle.lower_shadow == 5

    def test_bearish_candle(self):
        candle = Candle(open=108, high=110, low=95, close=100)
        assert candle.is_bullish == False
        assert candle.is_bearish == True
        assert candle.body == 8

    def test_doji_candle(self):
        candle = Candle(open=100, high=105, low=95, close=100.5)
        assert candle.body == 0.5
        assert candle.total_range == 10
        assert candle.body_percent == 5.0


class TestPatternDetection:
    """Test individual pattern detection"""

    def setup_method(self):
        self.detector = CandlestickPatternDetector()

    def test_detect_hammer(self):
        """Hammer: Small body at top, long lower shadow"""
        candles = [
            # Downtrend
            Candle(open=110, high=112, low=108, close=109),
            Candle(open=109, high=110, low=106, close=107),
            Candle(open=107, high=108, low=104, close=105),
            # Hammer
            Candle(open=105, high=106, low=98, close=105.5)  # Long lower shadow
        ]

        patterns = self.detector.analyze(candles)
        pattern_names = [p.name for p in patterns]
        assert "Hammer" in pattern_names

    def test_detect_shooting_star(self):
        """Shooting Star: Small body at bottom, long upper shadow"""
        candles = [
            # Uptrend
            Candle(open=100, high=102, low=99, close=101),
            Candle(open=101, high=104, low=100, close=103),
            Candle(open=103, high=106, low=102, close=105),
            # Shooting star
            Candle(open=105, high=115, low=104, close=105.5)  # Long upper shadow
        ]

        patterns = self.detector.analyze(candles)
        pattern_names = [p.name for p in patterns]
        assert "Shooting Star" in pattern_names

    def test_detect_doji(self):
        """Doji: Very small body"""
        candles = [
            Candle(open=100, high=102, low=98, close=101),
            Candle(open=101, high=103, low=99, close=102),
            # Doji
            Candle(open=102, high=105, low=99, close=102.1)  # Tiny body
        ]

        patterns = self.detector.analyze(candles)
        pattern_names = [p.name for p in patterns]
        assert "Doji" in pattern_names

    def test_detect_bullish_engulfing(self):
        """Bullish Engulfing: Bearish candle followed by larger bullish"""
        candles = [
            Candle(open=100, high=102, low=98, close=101),
            # Bearish candle
            Candle(open=102, high=103, low=99, close=100),
            # Bullish engulfing
            Candle(open=98, high=106, low=97, close=105)  # Engulfs previous
        ]

        patterns = self.detector.analyze(candles)
        pattern_names = [p.name for p in patterns]
        assert "Bullish Engulfing" in pattern_names

    def test_detect_bearish_engulfing(self):
        """Bearish Engulfing: Bullish candle followed by larger bearish"""
        candles = [
            Candle(open=100, high=102, low=98, close=99),
            # Bullish candle
            Candle(open=99, high=103, low=98, close=102),
            # Bearish engulfing
            Candle(open=104, high=105, low=96, close=97)  # Engulfs previous
        ]

        patterns = self.detector.analyze(candles)
        pattern_names = [p.name for p in patterns]
        assert "Bearish Engulfing" in pattern_names

    def test_detect_morning_star(self):
        """Morning Star: Bearish, small body (star), bullish"""
        candles = [
            Candle(open=100, high=101, low=95, close=96),  # Long bearish
            Candle(open=94, high=95, low=93, close=94.5),  # Small star
            Candle(open=95, high=102, low=94, close=101)   # Long bullish
        ]

        patterns = self.detector.analyze(candles)
        pattern_names = [p.name for p in patterns]
        assert "Morning Star" in pattern_names

    def test_detect_evening_star(self):
        """Evening Star: Bullish, small body (star), bearish"""
        candles = [
            Candle(open=95, high=101, low=94, close=100),   # Long bullish
            Candle(open=101, high=102, low=100, close=101.5),  # Small star
            Candle(open=100, high=101, low=94, close=95)    # Long bearish
        ]

        patterns = self.detector.analyze(candles)
        pattern_names = [p.name for p in patterns]
        assert "Evening Star" in pattern_names

    def test_detect_three_white_soldiers(self):
        """Three White Soldiers: Three consecutive bullish candles"""
        candles = [
            Candle(open=100, high=105, low=99, close=104),
            Candle(open=103, high=109, low=102, close=108),
            Candle(open=107, high=114, low=106, close=113)
        ]

        patterns = self.detector.analyze(candles)
        pattern_names = [p.name for p in patterns]
        assert "Three White Soldiers" in pattern_names

    def test_detect_three_black_crows(self):
        """Three Black Crows: Three consecutive bearish candles"""
        candles = [
            Candle(open=113, high=114, low=108, close=109),
            Candle(open=110, high=111, low=104, close=105),
            Candle(open=106, high=107, low=100, close=101)
        ]

        patterns = self.detector.analyze(candles)
        pattern_names = [p.name for p in patterns]
        assert "Three Black Crows" in pattern_names


class TestTradingSignal:
    """Test trading signal generation"""

    def setup_method(self):
        self.detector = CandlestickPatternDetector()

    def test_bullish_signal_from_patterns(self):
        """Test that bullish patterns generate BUY signal"""
        # Create bullish engulfing pattern
        candles = [
            Candle(open=100, high=102, low=98, close=101),
            Candle(open=102, high=103, low=99, close=100),
            Candle(open=98, high=106, low=97, close=105)
        ]

        signal = self.detector.get_trading_signal(candles)
        assert signal["decision"] == "BUY"
        assert signal["confidence"] > 50

    def test_bearish_signal_from_patterns(self):
        """Test that bearish patterns generate SELL signal"""
        # Create bearish engulfing pattern
        candles = [
            Candle(open=100, high=102, low=98, close=99),
            Candle(open=99, high=103, low=98, close=102),
            Candle(open=104, high=105, low=96, close=97)
        ]

        signal = self.detector.get_trading_signal(candles)
        assert signal["decision"] == "SELL"
        assert signal["confidence"] > 50

    def test_rsi_affects_signal(self):
        """Test that RSI modifies the signal"""
        candles = [
            Candle(open=100, high=105, low=99, close=104),
            Candle(open=103, high=109, low=102, close=108),
            Candle(open=107, high=114, low=106, close=113)
        ]

        # With oversold RSI, bullish signal should be stronger
        signal_oversold = self.detector.get_trading_signal(candles, rsi=25)
        signal_neutral = self.detector.get_trading_signal(candles, rsi=50)

        assert signal_oversold["bullish_score"] > signal_neutral["bullish_score"]


class TestSignalGenerator:
    """Test the full signal generator"""

    def setup_method(self):
        self.generator = SignalGenerator()

    def test_quick_decision(self):
        """Test quick decision without external data"""
        candles = [
            {"open": 100, "high": 105, "low": 99, "close": 104, "volume": 1000},
            {"open": 103, "high": 109, "low": 102, "close": 108, "volume": 1200},
            {"open": 107, "high": 114, "low": 106, "close": 113, "volume": 1500}
        ]

        decision = self.generator.get_quick_decision(candles)
        assert decision["decision"] in ["BUY", "SELL", "HOLD"]
        assert "use_ai" in decision


class TestPatternTypes:
    """Verify pattern type categorization"""

    def setup_method(self):
        self.detector = CandlestickPatternDetector()

    def test_bullish_patterns_have_correct_type(self):
        """All bullish patterns should return PatternType.BULLISH"""
        # Hammer pattern
        candles = [
            Candle(open=110, high=112, low=108, close=109),
            Candle(open=109, high=110, low=106, close=107),
            Candle(open=107, high=108, low=104, close=105),
            Candle(open=105, high=106, low=98, close=105.5)
        ]

        patterns = self.detector.analyze(candles)
        bullish_patterns = [p for p in patterns if p.pattern_type == PatternType.BULLISH]
        assert len(bullish_patterns) > 0

    def test_bearish_patterns_have_correct_type(self):
        """All bearish patterns should return PatternType.BEARISH"""
        # Three black crows
        candles = [
            Candle(open=113, high=114, low=108, close=109),
            Candle(open=110, high=111, low=104, close=105),
            Candle(open=106, high=107, low=100, close=101)
        ]

        patterns = self.detector.analyze(candles)
        bearish_patterns = [p for p in patterns if p.pattern_type == PatternType.BEARISH]
        assert len(bearish_patterns) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
