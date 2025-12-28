import json
import os
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(__file__), '../data/portfolio.json')
LOG_FILE = os.path.join(os.path.dirname(__file__), '../data/trade_log.csv')

class PaperTradingService:
    def __init__(self):
        self._load_portfolio()

    def _load_portfolio(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as f:
                    data = json.load(f)
                    self.balance = data.get('balance', 1000.0)
                    self.holdings = data.get('holdings', {})
                    self.trade_history = data.get('trade_history', [])
                    self.watchlist = data.get('watchlist', [])
            except:
                self._reset_portfolio()
        else:
            self._reset_portfolio()

    def _reset_portfolio(self):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] PORTFOLIO: Resetting portfolio to $1000.00 initial balance.")
        self.balance = 1000.0
        self.holdings = {} # { "AAPL": { "qty": 10, "avg_price": 150.0 } }
        self.trade_history = []
        self.watchlist = []
        self._save_portfolio()
        
        # Initialize log file header
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, 'w') as f:
            f.write("Timestamp,Ticker,Action,Quantity,Price,Total,Balance_After,Profit,Confidence,Reasoning\n")

    def _save_portfolio(self):
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, 'w') as f:
            json.dump({
                "balance": self.balance,
                "holdings": self.holdings,
                "trade_history": self.trade_history,
                "watchlist": self.watchlist
            }, f, indent=4)

    def _log_trade_csv(self, trade_data):
        try:
            timestamp = trade_data.get('timestamp')
            ticker = trade_data.get('ticker')
            action = trade_data.get('type')
            qty = trade_data.get('qty', 0)
            price = trade_data.get('price', 0)
            total = trade_data.get('total', 0)
            profit = trade_data.get('profit', 0)
            reason = trade_data.get('reasoning', '').replace(',', ';') # Escape commas
            confidence = trade_data.get('confidence', 'N/A')
            
            log_entry = f"{timestamp},{ticker},{action},{qty},{price},{total},{self.balance},{profit},{confidence},{reason}\n"
            
            with open(LOG_FILE, 'a') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Error logging to CSV: {e}")

    def evaluate_trade(self, ticker, decision, price, confidence, reasoning, quantity=None):
        """
        Execute trade based on AI decision if conditions met.
        """
        print(f"[{datetime.now().strftime('%H:%M:%S')}] TRADING: Evaluating {decision} for {ticker} (Conf: {confidence}%)...")
        
        if decision == "BUY" and confidence >= 70:
            return self.buy_stock(ticker, price, reasoning, quantity, confidence)
        elif decision == "SELL":
            return self.sell_stock(ticker, price, reasoning, confidence)
        elif decision == "TRACK":
            return self.add_to_watchlist(ticker, price, reasoning, confidence)
        return None

    def buy_stock(self, ticker, price, reasoning, suggested_qty=None, confidence=0):
        if ticker in self.holdings:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] TRADING: Already holding {ticker}. Skipping BUY.")
            return None 

        qty = 0
        if suggested_qty and isinstance(suggested_qty, int) and suggested_qty > 0:
            # Validate AI suggestion against balance
            cost = suggested_qty * price
            if cost <= self.balance:
                qty = suggested_qty
            else:
                qty = int(self.balance // price)
        else:
            # Default: specific risk allocation (e.g., 20% of portfolio)
            alloc_amount = self.balance * 0.20
            # Ensure minimum trade size 
            if alloc_amount < price: alloc_amount = self.balance # If balance low, go all in
            qty = int(alloc_amount // price)
        
        if qty > 0:
            cost = qty * price
            self.balance -= cost
            self.holdings[ticker] = {
                "qty": qty,
                "entry_price": price,
                "entry_time": datetime.now().isoformat()
            }
            trade = {
                "type": "BUY",
                "ticker": ticker,
                "qty": qty,
                "price": price,
                "total": cost,
                "profit": 0,
                "confidence": confidence,
                "timestamp": datetime.now().isoformat(),
                "reasoning": reasoning
            }
            self.trade_history.append(trade)
            self._save_portfolio()
            self._log_trade_csv(trade)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] TRADING: EXECUTED BUY {qty} {ticker} @ ${price}")
            return trade
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] TRADING: Insufficient funds to buy {ticker}.")
        return None

    def sell_stock(self, ticker, price, reasoning, confidence=0):
        if ticker in self.holdings:
            holding = self.holdings[ticker]
            qty = holding['qty']
            revenue = qty * price
            profit = revenue - (qty * holding['entry_price'])
            
            self.balance += revenue
            del self.holdings[ticker]
            
            trade = {
                "type": "SELL",
                "ticker": ticker,
                "qty": qty,
                "price": price,
                "total": revenue,
                "profit": profit,
                "confidence": confidence,
                "timestamp": datetime.now().isoformat(),
                "reasoning": reasoning
            }
            self.trade_history.append(trade)
            self._save_portfolio()
            self._log_trade_csv(trade)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] TRADING: EXECUTED SELL {qty} {ticker} @ ${price}. Profit: ${profit:.2f}")
            return trade
        return None

    def add_to_watchlist(self, ticker, price, reasoning, confidence):
        # Avoid duplicates
        for item in self.watchlist:
            if item['ticker'] == ticker:
                # Update existing
                item['price'] = price
                item['reasoning'] = reasoning
                item['confidence'] = confidence
                item['timestamp'] = datetime.now().isoformat()
                self._save_portfolio()
                return item

        item = {
            "ticker": ticker,
            "price": price,
            "reasoning": reasoning,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        }
        self.watchlist.append(item)
        self._save_portfolio()
        return item

    def get_portfolio(self):
        return {
            "balance": self.balance,
            "holdings": self.holdings,
            "trade_history": self.trade_history,
            "watchlist": self.watchlist,
            "total_equity": self.balance + sum(h['qty'] * h['entry_price'] for h in self.holdings.values()) # Approx equity
        }

paper_trading_service = PaperTradingService()
