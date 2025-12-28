from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime

# Import new services
from backend.services.data_manager import data_manager
from backend.services.ai_engine import ai_engine
from backend.services.trader import trader
from backend.services.paper_trading_service import paper_trading_service

async def antigravity_loop():
    """
    The 'Antigravity' Event Loop: Polls data, detects signals, executes trades.
    """
    print("🚀 [SYSTEM] Antigravity Event Loop Started")
    while True:
        try:
            trader.log_event("INFO", "Polling data sources...")
            
            # Simple list of active tickers to monitor
            # In a real system this might be dynamic
            tickers_to_monitor = ["TSLA", "AAPL", "NVDA", "AMD", "META"] 
            
            for ticker in tickers_to_monitor:
                # 1. Fetch Market Data
                market_data = data_manager.get_market_data(ticker)
                
                if market_data:
                    # 2. Check for Signals (Simplified event detection)
                    # For now, we'll relay on a simple periodic check or high volatility
                    # Let's say we just analyze regularly for this demo loop
                    
                    pct_change = abs(market_data.get('change_percent', 0))
                    
                    # Log significant moves
                    if pct_change > 1.0:
                        trader.log_event("INFO", f"Volatility Alert: {ticker} moved {pct_change:.2f}%")

                    # 3. Check News (only if volatility is high or we just want to check)
                    # To save tokens, we might not analyze *every* loop unless something happens.
                    # But the user asked for "Polls... Detects... Trigger".
                    # Let's simple-trigger analysis if change > 0.5% (Event Driven)
                    # OR just on every N loops. For safety/cost in this demo, let's strictly follow "New Info".
                    # Simulation: Let's assume we analyze if price moved significantly OR randomly occasionally.
                    
                    if pct_change > 0.5:
                        trader.log_event("AI", f"Triggering analysis for {ticker} (Volatility detected)...")
                        
                        news = data_manager.get_news(ticker)
                        portfolio = paper_trading_service.get_portfolio()
                        
                        analysis = ai_engine.analyze_situation(ticker, market_data, news, portfolio)
                        
                        # 4. Execute Decision
                        trader.execute_strategy(ticker, analysis, market_data['price'])
                        
            # Wait 60 seconds before next poll cycle
            await asyncio.sleep(60)
            
        except Exception as e:
            print(f"Loop Error: {e}")
            await asyncio.sleep(60)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Launch the background loop
    loop_task = asyncio.create_task(antigravity_loop())
    yield
    # Shutdown: Cancel if needed (not strictly necessary for simple script)
    loop_task.cancel()

app = FastAPI(title="dayTradingAI API", lifespan=lifespan)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "dayTradingAI System Online"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

# --- Endpoints using new DataManager ---

@app.get("/api/stock/{ticker}")
def get_stock(ticker: str):
    return data_manager.get_market_data(ticker)

@app.get("/api/news/{ticker}")
def get_news(ticker: str):
    return data_manager.get_news(ticker)

@app.post("/api/batch_market_data")
def get_batch_market_data(tickers: list[str]):
    return data_manager.get_batch_data(tickers)

@app.get("/api/analyze/{ticker}")
def analyze_stock_manual(ticker: str):
    """
    Manual trigger for analysis (from Frontend button)
    """
    trader.log_event("INFO", f"Manual analysis requested for {ticker}")
    try:
        stock_data = data_manager.get_market_data(ticker)
        news_data = data_manager.get_news(ticker)
        portfolio = paper_trading_service.get_portfolio()
        
        analysis = ai_engine.analyze_situation(ticker, stock_data, news_data, portfolio)
        
        # Execute Strategy Logic (Log trades, handle Buy/Sell orders)
        trader.execute_strategy(ticker, analysis, stock_data['price'])
        
        response = {
            "market_data": stock_data,
            "news_data": news_data,
            "analysis": analysis,
            "portfolio": paper_trading_service.get_portfolio()
        }
        return response
    except Exception as e:
        trader.log_event("ALERT", f"Error in manual analysis: {e}")
        return {"error": str(e)}

@app.get("/api/portfolio")
def get_portfolio():
    return paper_trading_service.get_portfolio()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
