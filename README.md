# dayTradingAI - Professional Day Trading Dashboard

**dayTradingAI** is an advanced, AI-powered day trading assistant designed to analyze real-time market data, aggregate news, and provide actionable trading insights using **Google Gemini 2.5**. It features a futuristic, "professional cyberpunk" dashboard built with React and a robust FastAPI backend.

The system is designed for a **$1000 Paper Trading Challenge**, with the goal of doubling the portfolio through autonomous, risk-managed day trades.

## 🚀 Key Features

*   **Real-Time Data (Yahoo Finance)**:
    *   **Live Charts**: Fetches intraday candlestick data (1-minute/5-minute intervals) directly from Yahoo Finance.
    *   **Accurate Watchlist**: Uses a batch processing endpoint (`/api/batch_market_data`) to update the watchlist with real-time prices and sparkline trends every 60 seconds.
*   **AI Insight Engine**:
    *   Uses **Google Gemini 2.5** to analyze market structure, volume anomalies, and news sentiment.
    *   Generates **BUY/SELL/HOLD/TRACK** decisions with confidence scores (0-100%).
    *   Provides specific entry, target, and stop-loss levels.
*   **Autonomous Paper Trading**:
    *   **Risk Management**: Strictly limits position sizes (default 20% of portfolio) to prevent blow-ups.
    *   **Smart Sizing**: The AI suggests specific share quantities based on the setup's quality.
    *   **Performance Tracking**: Logs every trade in `data/trade_log.csv` and updates `data/portfolio.json`.
*   **Live News Feed**: Aggregates real-time news from major financial outlets via Yahoo Finance, highlighting positive/negative sentiment keywords.
*   **Professional UI/UX**:
    *   Dark mode "cyberpunk" aesthetic with glassmorphism effects.
    *   Interactive visualizations (Sparklines, Speedometers, Candlestick Charts).
    *   Responsive and high-performance React frontend.

## 🛠️ Technology Stack

*   **Frontend**: React, Vite, CSS Modules (Custom Design System).
*   **Backend**: FastAPI, Uvicorn, Python 3.9+.
*   **AI**: Google Gemini API (`google-generativeai`).
*   **Data Sources**: `yfinance` (Yahoo Finance), `feedparser`.

## 📦 Installation & Setup

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd dayTradingAI
    ```

2.  **Backend Setup**:
    ```bash
    cd backend
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Frontend Setup**:
    ```bash
    cd frontend
    npm install
    ```

4.  **Environment Variables**:
    Create a `.env` file in `backend/` or ensure `backend/config.py` has your keys:
    ```env
    GEMINI_API_KEY=your_gemini_key_here
    ```

## 🏃‍♂️ Running the Application

Use the startup script or run manually:

**Backend** (API runs on port 8000):
```bash
# In dayTradingAI root
source backend/venv/bin/activate
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend** (Dashboard runs on port 5173):
```bash
# In dayTradingAI/frontend
npm run dev
```

Access the dashboard at `http://localhost:5173`.

## 📊 Logging & Analysis

*   **Console Logs**: The backend prints detailed, time-stamped logs of every action ("Fetching batch data...", "AI Thinking...", "Trade Executed...").
*   **Trade Log**: Check `data/trade_log.csv` for a CSV record of all automated trades.
*   **Portfolio State**: `data/portfolio.json` persists your current balance and holdings across restarts.

## 🧪 Testing

To verify data accuracy against Yahoo Finance:
```bash
python tests/test_data_accuracy.py
```
To verify batch data fetching:
```bash
python tests/test_batch.py
```