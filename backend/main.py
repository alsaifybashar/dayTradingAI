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
            tickers_to_monitor = [
                "AAPL", "NVDA", "TSLA", "AMD", "MSFT", "JPM", "DIS", "BA", "MSFT", "NFLX", "AMZN", "BKNG", "ASML", ""  # US
                "VOLV-B.ST", "ERIC-B.ST", "HM-B.ST", "AZN.ST", "INVE-B.ST", "SAND.ST", "SAAB-B.ST" # Stockholm
            ] 
            
            for ticker in tickers_to_monitor:
                # Use the Trader service to process the ticker
                # This handles data fetching, analysis (Algo + AI), and execution logic
                result = trader.process_ticker(ticker)
                
                # Check result
                action = result.get("action_taken", "NONE")
                decision = result.get("decision", "HOLD")
                conf = result.get("confidence", 0)
                price = result.get("price", 0)
                
                # Log the scan result to terminal so user sees activity
                if action != "NONE":
                    print(f"✅ [LOOP] Processed {ticker}: {action} ({decision} {conf}%)")
                else:
                    trader.log_event("SCAN", f"{ticker}: ${price:.2f} | Action: {decision} ({conf}%)")
                        
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
        decision = analysis.get("decision", "HOLD")
        confidence = analysis.get("confidence", 0)
        reasoning = analysis.get("reasoning", "")
        suggested_qty = analysis.get("suggested_quantity", 0)
        
        trader.execute_strategy(ticker, decision, confidence, reasoning, stock_data['price'], suggested_qty)
        
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
