from datetime import datetime
from colorama import Fore, Style, init
from backend.services.paper_trading_service import paper_trading_service
import csv
import os

init(autoreset=True)

class Trader:
    def __init__(self):
        self.log_file = os.path.join(os.path.dirname(__file__), '../data/trade_log.csv')

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
        else:
            print(f"[{level}] {timestamp} {message}")

    def execute_strategy(self, ticker, ai_result, current_price):
        """
        Executes the main trading logic based on AI decision and Risk Rules.
        """
        confidence = float(ai_result.get("confidence", 0))
        decision = ai_result.get("decision", "IGNORE").upper()
        reasoning = ai_result.get("reasoning", "")
        suggested_qty = ai_result.get("suggested_quantity", 0)

        # 1. BUY LOGIC
        if decision == "BUY":
            if confidence > 75:
                # Execute Buy
                trade = paper_trading_service.evaluate_trade(
                    ticker, 
                    "BUY", 
                    current_price, 
                    confidence, 
                    reasoning, 
                    quantity=suggested_qty
                )
                if trade:
                    self.log_event("TRADE", f"BUY Executed: {trade['qty']} {ticker} @ ${current_price:.2f}")
                else:
                    self.log_event("ALERT", f"BUY Rejected for {ticker} (Insufficient Funds or Rules)")
            else:
                self.log_event("INFO", f"BUY Signal for {ticker} weak (Conf: {confidence}%), skipping.")

        # 2. SELL LOGIC
        elif decision == "SELL":
            # Check if we own it
            holdings = paper_trading_service.holdings
            if ticker in holdings:
                # Force sell if AI says SELL
                trade = paper_trading_service.evaluate_trade(
                    ticker, 
                    "SELL", 
                    current_price, 
                    confidence, 
                    reasoning
                )
                if trade:
                     self.log_event("TRADE", f"SELL Executed: {trade['qty']} {ticker} @ ${current_price:.2f} | P/L: ${trade['profit']:.2f}")
            else:
                self.log_event("INFO", f"SELL Signal for {ticker} but no position held.")

        # 3. IGNORE / HOLD
        else:
             self.log_event("INFO", f"AI Decision for {ticker}: {decision} (Conf: {confidence}%)")

        # 4. MONITOR EXISTING POSITIONS (Stop Loss / Take Profit)
        # This logic scans current holdings and auto-sells if criteria met
        self.check_positions(ticker, current_price)

    def check_positions(self, ticker, current_price):
        holdings = paper_trading_service.holdings
        if ticker in holdings:
            avg_price = holdings[ticker]['entry_price']
            pct_change = ((current_price - avg_price) / avg_price) * 100
            
            # Stop Loss: -2% 
            if pct_change <= -2.0:
                self.log_event("ALERT", f"Stop Loss Triggered for {ticker} ({pct_change:.2f}%)")
                paper_trading_service.sell_stock(ticker, current_price, "Stop Loss Triggered")
            
            # Take Profit: +4%
            elif pct_change >= 4.0:
                self.log_event("TRADE", f"Take Profit Triggered for {ticker} (+{pct_change:.2f}%)")
                paper_trading_service.sell_stock(ticker, current_price, "Take Profit Triggered")

trader = Trader()
