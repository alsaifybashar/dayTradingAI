# 🦅 dayTradingAI - Autonomous Hybrid Trading System

**dayTradingAI** is a professional-grade, autonomous trading assistant designed to conquer the "Paper Trading Challenge". It combines **traditional algorithmic analysis** (Technical Indicators & Candlestick Patterns) with **Generative AI** (Gemini, OpenAI, Claude) to make high-probability trading decisions.

The system features a futuristic "Cyberpunk" React dashboard for real-time monitoring and a robust FastAPI backend that handles data aggregation, signal generation, and autonomous execution.

![Dashboard Preview](https://placehold.co/800x400?text=Dashboard+Preview) 

## 🚀 Key Features

### 🧠 Hybrid Intelligence Engine
The system uses a cost-efficient "Algorithm First" approach:
1.  **Algorithmic Core**: Analyzes technicals (RSI, MACD, Bollinger Bands) and Candlestick Patterns (Engulfing, Hammers, Morning Stars) to generate base signals.
2.  **AI Validation**: If the algorithm is unsure (low confidence) or signals are mixed, it consults an LLM agent to analyze the context (News + Market Structure).
3.  **Multi-Model Fallback**: Guaranteed uptime with smart fallback routing:
    *   **Primary**: Google Gemini 2.0 Flash (Fast & Free tier)
    *   **Backup 1**: Gemini 1.5 Flash / Pro
    *   **Backup 2**: OpenAI GPT-4o-mini
    *   **Backup 3**: Anthropic Claude 3 Haiku

### ⚡ Real-Time Data & Execution
*   **Live Market Data**: Fetches 15-minute candles and real-time quotes via `yfinance`.
*   **News Aggregator**: Scrapes and analyzes news from CNBC, Reuters, Yahoo Finance, and more.
*   **Sentiment Analysis**: Keyword-based sentiment scoring + AI context analysis.
*   **Smart Risk Management**:
    *   Kelly Criterion-style position sizing.
    *   Automatic Stop-Loss (-2%) and Take-Profit (+4%) monitoring.
    *   Portfolio caps to prevent over-leverage.

### 🖥️ Professional Dashboard
*   **Tech Stack**: React 18, Vite, Custom CSS ("Glassmorphism").
*   **Visualizations**: Real-time sparklines, confident gauges, and live trade logs.
*   **Manual Override**: Ability to trigger manual AI analysis and trades.

---

## 🛠️ Technology Stack

*   **Backend**: Python 3.9+, FastAPI, Uvicorn
*   **Analysis**: `pandas`, `pandas_ta`, `numpy`
*   **AI Integration**: `google-generativeai`, `openai`, `anthropic`
*   **Frontend**: React, Vite, Axios
*   **Data**: Yahoo Finance API, RSS Feeds

---

## 📦 Installation

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd dayTradingAI
```

### 2. Configure Environment Variables
Create a `.env` file in the `backend/` directory. You can use multiple providers for resilience.

```env
# backend/.env

# Primary (Required for best performance)
GEMINI_API_KEY=your_google_gemini_key

# Optional (For Fallback)
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

### 3. Install Dependencies
**Backend:**
```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

**Frontend:**
```bash
cd ../frontend
npm install
```

---

## 🏃‍♂️ Usage

We provide a specialized startup script that handles everything (requires Bash/WSL on Windows).

### **The "One-Click" Start**
From the root directory:
```bash
./start.sh
```
This script will:
1.  Start the FastAPI Backend (Port 8000).
2.  Start the Vite Frontend (Port 5173).
3.  Handle graceful shutdown (Ctrl+C).

### **Manual Startup**
If you prefer running terminals separately:

**Terminal 1 (Backend)**
```bash
cd backend
source venv/bin/activate
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 (Frontend)**
```bash
cd frontend
npm run dev
```

ACCESS THE DASHBOARD AT: `http://localhost:5173`

---

## 📊 System Architecture

### **The "Antigravity" Loop**
The system runs a continuous event loop (`antigravity_loop`) that:
1.  **Polls** configured tickers (AAPL, TSLA, NVDA, etc.) every 60 seconds.
2.  **Fetches** fresh market data and news.
3.  **Generates** a `TradingSignal` using the `SignalGenerator`.
4.  **Decides** whether to trade or consult AI.
5.  **Executes** paper trades and logs them to `data/trade_log.csv`.

### **Folder Structure**
```
dayTradingAI/
├── backend/
│   ├── data/               # Portfolio JSON and Trade Logs
│   ├── services/
│   │   ├── ai_engine.py    # LLM Integration & Fallback Logic
│   │   ├── trader.py       # Execution (Buy/Sell) Logic
│   │   ├── signal_generator.py # Hybrid Algorithm
│   │   ├── data_manager.py # Data Aggregation
│   │   └── ...
│   ├── main.py             # FastAPI Entry Point
│   └── config.py           # Env Config
├── frontend/               # React Application
└── start.sh                # Startup Script
```

---

## ⚠️ Disclaimer
This software is for **EDUCATIONAL PURPOSES ONLY**. It is a **paper trading** simulation. Do not use this for real money trading without significant modifications and risk assessment. The creators are not responsible for any financial losses.