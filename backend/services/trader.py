"""
Trading Execution Service

Executes trades based on signals from the algorithmic analysis.
Only consults AI when signal confidence is low or signals are contradictory.

Key Features:
- Pattern-based decision making (reduces AI costs)
- Risk management (stop-loss, take-profit)
- Position sizing based on confidence
- Trade logging for analysis
"""

from datetime import datetime
from colorama import Fore, Style, init
from backend.services.paper_trading_service import paper_trading_service
from backend.services.data_manager import data_manager
from backend.services.ai_engine import ai_engine
from backend.services.quant_engine import quant_engine
import csv
import os
import numpy as np

init(autoreset=True)


class Trader:
    def __init__(self):
        self.log_file = os.path.join(os.path.dirname(__file__), '../data/trade_log.csv')

        # Trading parameters
        self.min_confidence_for_trade = 65  # Minimum confidence to execute trade
        self.ai_consultation_threshold = 60  # Below this, consult AI
        
        # Risk Limits
        self.max_var_percent = 2.0  # Max 2% Portfolio VaR

        # Statistics
        self.trades_executed = 0
        self.ai_consultations = 0
        self.algorithmic_decisions = 0

    def log_event(self, level, message):
        timestamp = datetime.now().strftime('%H:%M:%S')
        if level == "INFO":
            print(f"{Fore.BLUE}[INFO] {timestamp} {message}")
        elif level == "NEWS":
            print(f"{Fore.GREEN}[NEWS] {timestamp} {message}")
        elif level == "AI":
            print(f"{Fore.MAGENTA}[AI] {timestamp} {message}")
        elif level == "TRADE":
            print(f"{Fore.YELLOW}[TRADE] {timestamp} {message}")
        elif level == "ALERT":
            print(f"{Fore.RED}[ALERT] {timestamp} {message}")
        elif level == "PATTERN":
            print(f"{Fore.CYAN}[PATTERN] {timestamp} {message}")
        elif level == "SCAN":
            print(f"{Fore.WHITE}[SCAN] {timestamp} {message}")
        elif level == "QUANT":
             print(f"{Fore.LIGHTMAGENTA_EX}[QUANT] {timestamp} {message}")
        else:
            print(f"[{level}] {timestamp} {message}")

    def process_ticker(self, ticker: str, portfolio_balance: float = None) -> dict:
        """
        Process a ticker through the full analysis pipeline.
        Uses algorithmic analysis first, AI only when needed.

        Returns:
            Dict with analysis results and action taken
        """
        # Get portfolio balance if not provided
        if portfolio_balance is None:
            portfolio_balance = paper_trading_service.balance

        # Get full analysis (patterns, indicators, sentiment)
        analysis = data_manager.get_full_analysis(ticker, portfolio_balance)

        if "error" in analysis:
            self.log_event("ALERT", f"Analysis failed for {ticker}: {analysis['error']}")
            return {"error": analysis["error"], "action": "NONE"}

        signal = analysis.get("signal", {})
        market_data = analysis.get("market_data", {})
        current_price = market_data.get("price", 0)

        # Log detected patterns
        patterns = signal.get("patterns_detected", [])
        if patterns:
            pattern_names = [p["name"] for p in patterns[:3]]
            self.log_event("PATTERN", f"{ticker}: Detected {', '.join(pattern_names)}")

        # Decision logic
        use_ai = signal.get("use_ai", True)
        confidence = signal.get("confidence", 0)
        decision = signal.get("decision", "HOLD")

        # Check if we should consult AI
        if use_ai and confidence < self.ai_consultation_threshold:
            self.log_event("INFO", f"{ticker}: Low confidence ({confidence}%), consulting AI...")
            self.ai_consultations += 1

            # Get portfolio context for AI
            portfolio_context = {
                "balance": paper_trading_service.balance,
                "holdings": paper_trading_service.holdings,
                "total_equity": paper_trading_service.get_total_equity(
                    {ticker: current_price}
                )
            }

            # Consult AI with algorithmic signal
            ai_result = ai_engine.analyze_situation(
                ticker,
                market_data,
                analysis.get("news", []),
                portfolio_context,
                algorithmic_signal=signal
            )

            # Use AI decision if it overrides
            if ai_result.get("override_algorithm", False):
                self.log_event("AI", f"{ticker}: AI overrides algorithm -> {ai_result['decision']}")
                decision = ai_result.get("decision", decision)
                confidence = ai_result.get("confidence", confidence)
                reasoning = ai_result.get("reasoning", "")
            else:
                self.log_event("AI", f"{ticker}: AI confirms algorithm -> {decision}")
                reasoning = signal.get("reasoning", "")
        else:
            self.algorithmic_decisions += 1
            reasoning = signal.get("reasoning", "")
            self.log_event("INFO", f"{ticker}: Algorithmic decision ({confidence}% conf) -> {decision}")
            
        # === QUANT ENGINE: Stat Arb Check ===
        # Use OU Mean Reversion to confirm/reject
        if market_data.get("sparkline") and len(market_data["sparkline"]) > 10:
             ou_params = quant_engine.estimate_ou_parameters(market_data["sparkline"])
             if ou_params.get("mean_reverting"):
                 z_score = ou_params["z_score"]
                 self.log_event("QUANT", f"{ticker} OU Z-Score: {z_score:.2f}")
                 
                 # Mean Reversion Logic:
                 # If we want to BUY but Z > 2 (Overbought), reconsider
                 if decision == "BUY" and z_score > 2.0:
                     self.log_event("QUANT", f"{ticker} Z-Score > 2.0 (Overbought). Downgrading BUY.")
                     decision = "HOLD"
                     reasoning += " | [Quant] Rejected by OU Z-Score > 2.0"
                 # If we want to SELL but Z < -2 (Oversold), reconsider
                 elif decision == "SELL" and z_score < -2.0:
                     self.log_event("QUANT", f"{ticker} Z-Score < -2.0 (Oversold). Downgrading SELL.")
                     decision = "HOLD"
                     reasoning += " | [Quant] Rejected by OU Z-Score < -2.0"

        # Execute the strategy
        result = self.execute_strategy(
            ticker,
            decision,
            confidence,
            reasoning,
            current_price,
            signal.get("suggested_quantity", 0)
        )

        return {
            "ticker": ticker,
            "decision": decision,
            "confidence": confidence,
            "reasoning": reasoning,
            "action_taken": result.get("action", "NONE"),
            "used_ai": use_ai and confidence < self.ai_consultation_threshold,
            "patterns": patterns,
            "price": current_price
        }

    def _calculate_performance_metrics(self):
        """Calculates Win Rate and W/L Ratio from history"""
        history = paper_trading_service.trade_history
        completed_trades = [t for t in history if t['type'] == 'SELL']
        
        if not completed_trades:
            return 0.55, 1.5 # Defaults for startup
            
        wins = [t for t in completed_trades if t['profit'] > 0]
        losses = [t for t in completed_trades if t['profit'] <= 0]
        
        win_rate = len(wins) / len(completed_trades) if completed_trades else 0.5
        
        avg_win = np.mean([t['profit'] for t in wins]) if wins else 1.0
        avg_loss = abs(np.mean([t['profit'] for t in losses])) if losses else 1.0
        
        if avg_loss == 0: avg_loss = 1.0
        
        return win_rate, avg_win / avg_loss

    def execute_strategy(self, ticker: str, decision: str, confidence: float,
                         reasoning: str, current_price: float,
                         suggested_qty: int = 0) -> dict:
        """
        Executes the trading logic based on decision and confidence.
        Now uses Kelly Criterion for sizing and VaR for risk.
        """
        result = {"action": "NONE"}
        portfolio_val = paper_trading_service.balance + sum(h['qty']*h['entry_price'] for h in paper_trading_service.holdings.values())

        # 1. RISK CHECK: Value At Risk
        # (Simplified: using dummy returns for now as we don't have full hist)
        # In prod: fetch daily returns for portfolio
        var_metrics = quant_engine.calculate_var(portfolio_val, [0.01, -0.01, 0.02, 0.005, -0.005]) 
        if var_metrics['var_percent'] > self.max_var_percent:
             self.log_event("ALERT", f"Portfolio VaR ({var_metrics['var_percent']:.2f}%) exceeds limit {self.max_var_percent}%. Halting new buys.")
             decision = "HOLD" if decision == "BUY" else decision

        # 1. BUY LOGIC
        if decision == "BUY":
            if confidence >= self.min_confidence_for_trade:
                # === QUANT ENGINE: Kelly Sizing ===
                win_rate, wl_ratio = self._calculate_performance_metrics()
                kelly_fraction = quant_engine.calculate_kelly_criterion(win_rate, wl_ratio, half_kelly=True)
                
                # Cap max allocation to 25% for safety regardless of Kelly
                max_allocation = 0.25 
                allocation_fraction = min(max(0.02, kelly_fraction), max_allocation) # Min 2%, Max 25%
                
                target_value = portfolio_val * allocation_fraction
                quant_qty = int(target_value / current_price)
                
                # Log the quant sizing details
                if quant_qty != suggested_qty:
                    self.log_event("QUANT", f"Kelly Sizing ({allocation_fraction*100:.1f}%) suggests {quant_qty} shares (Base: {suggested_qty})")
                    suggested_qty = quant_qty
                
                trade = paper_trading_service.evaluate_trade(
                    ticker,
                    "BUY",
                    current_price,
                    confidence,
                    reasoning,
                    quantity=max(1, suggested_qty)
                )
                if trade:
                    self.trades_executed += 1
                    self.log_event("TRADE", f"BUY Executed: {trade['qty']} {ticker} @ ${current_price:.2f}")
                    result = {"action": "BUY", "quantity": trade['qty'], "price": current_price}
                else:
                    self.log_event("ALERT", f"BUY Rejected for {ticker} (Insufficient Funds or Rules)")
                    result = {"action": "REJECTED"}
            else:
                self.log_event("INFO", f"BUY Signal for {ticker} weak (Conf: {confidence}%), skipping.")
                result = {"action": "SKIPPED", "reason": "low_confidence"}

        # 2. SELL LOGIC
        elif decision == "SELL":
            holdings = paper_trading_service.holdings
            if ticker in holdings:
                trade = paper_trading_service.evaluate_trade(
                    ticker,
                    "SELL",
                    current_price,
                    confidence,
                    reasoning
                )
                if trade:
                    self.trades_executed += 1
                    self.log_event("TRADE", f"SELL Executed: {trade['qty']} {ticker} @ ${current_price:.2f} | P/L: ${trade['profit']:.2f}")
                    result = {"action": "SELL", "quantity": trade['qty'], "profit": trade['profit']}
            else:
                self.log_event("INFO", f"SELL Signal for {ticker} but no position held.")
                result = {"action": "NO_POSITION"}

        # 3. HOLD
        else:
            self.log_event("INFO", f"HOLD for {ticker} (Conf: {confidence}%)")
            result = {"action": "HOLD"}

        # 4. Check existing positions for stop-loss/take-profit
        self.check_positions(ticker, current_price)

        return result

    def check_positions(self, ticker: str, current_price: float):
        """
        Monitor existing positions for stop-loss and take-profit triggers.
        """
        holdings = paper_trading_service.holdings
        if ticker in holdings:
            avg_price = holdings[ticker]['entry_price']
            pct_change = ((current_price - avg_price) / avg_price) * 100

            # Stop Loss: -2%
            if pct_change <= -2.0:
                self.log_event("ALERT", f"Stop Loss Triggered for {ticker} ({pct_change:.2f}%)")
                paper_trading_service.sell_stock(ticker, current_price, "Stop Loss Triggered")
                self.trades_executed += 1

            # Take Profit: +4%
            elif pct_change >= 4.0:
                self.log_event("TRADE", f"Take Profit Triggered for {ticker} (+{pct_change:.2f}%)")
                paper_trading_service.sell_stock(ticker, current_price, "Take Profit Triggered")
                self.trades_executed += 1

    def quick_scan(self, tickers: list) -> list:
        """
        Quick pattern scan without AI for multiple tickers.
        Use for real-time monitoring.

        Returns:
            List of tickers with actionable signals
        """
        actionable = []

        for ticker in tickers:
            try:
                quick_signal = data_manager.quick_pattern_check(ticker)

                if quick_signal.get("decision") in ["BUY", "SELL"]:
                    confidence = quick_signal.get("confidence", 0)
                    if confidence >= 60:
                        actionable.append({
                            "ticker": ticker,
                            "decision": quick_signal["decision"],
                            "confidence": confidence,
                            "pattern": quick_signal.get("pattern", "Unknown")
                        })
            except Exception as e:
                continue

        return actionable

    def get_statistics(self) -> dict:
        """Get trading statistics"""
        total_decisions = self.ai_consultations + self.algorithmic_decisions
        ai_percentage = (self.ai_consultations / total_decisions * 100) if total_decisions > 0 else 0

        return {
            "trades_executed": self.trades_executed,
            "ai_consultations": self.ai_consultations,
            "algorithmic_decisions": self.algorithmic_decisions,
            "ai_usage_percentage": round(ai_percentage, 2),
            "ai_savings": f"{100 - ai_percentage:.1f}% decisions made without AI"
        }


trader = Trader()

