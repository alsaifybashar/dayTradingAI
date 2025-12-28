from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Day Trading AI API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Day Trading AI API is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

from backend.services.market_service import market_service
from backend.services.news_service import news_service
from backend.services.ai_engine import ai_engine

@app.get("/api/stock/{ticker}")
def get_stock(ticker: str):
    return market_service.get_stock_data(ticker)

@app.get("/api/news/{ticker}")
def get_news(ticker: str):
    return news_service.get_news(ticker)

@app.get("/api/analyze/{ticker}")
def analyze_stock(ticker: str):
    stock_data = market_service.get_stock_data(ticker)
    news_data = news_service.get_news(ticker)
    analysis = ai_engine.analyze_stock(ticker, stock_data, news_data)
    return {
        "market_data": stock_data,
        "news_data": news_data,
        "analysis": analysis
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
