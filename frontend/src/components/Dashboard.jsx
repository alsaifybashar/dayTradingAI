import React, { useState, useEffect } from 'react';
import StockChart from './StockChart';
import AIInsights from './AIInsights';
import NewsFeed from './NewsFeed';

const API_URL = 'http://localhost:8000/api';

const Dashboard = () => {
    const [ticker, setTicker] = useState('AAPL');
    const [marketData, setMarketData] = useState(null);
    const [newsData, setNewsData] = useState([]);
    const [aiAnalysis, setAiAnalysis] = useState(null);
    const [loading, setLoading] = useState(false);

    const fetchData = async () => {
        setLoading(true);
        try {
            // Fetch analysis which includes market and news data in our updated backend endpoint
            // OR fetch individually. Let's fetch the aggregate endpoint I created.
            const response = await fetch(`${API_URL}/analyze/${ticker}`);
            const data = await response.json();

            setMarketData(data.market_data);
            setNewsData(data.news_data);
            setAiAnalysis(data.analysis);
        } catch (error) {
            console.error("Error fetching data", error);
        }
        setLoading(false);
    };

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 60000); // Poll every minute
        return () => clearInterval(interval);
    }, [ticker]);

    const handleSearch = (e) => {
        e.preventDefault();
        fetchData();
    };

    return (
        <div>
            <div className="card glass" style={{ marginBottom: '2rem', display: 'flex', gap: '1rem', alignItems: 'center' }}>
                <form onSubmit={handleSearch} style={{ display: 'flex', gap: '1rem', width: '100%' }}>
                    <input
                        type="text"
                        value={ticker}
                        onChange={(e) => setTicker(e.target.value.toUpperCase())}
                        placeholder="Enter Stock Ticker..."
                    />
                    <button type="submit" className="btn">Analyze</button>
                </form>
            </div>

            {loading && !marketData ? (
                <div style={{ textAlign: 'center', padding: '2rem' }}>Loading AI Systems...</div>
            ) : (
                <div className="grid grid-cols-2">
                    <div style={{ gridColumn: 'span 2' }}>
                        <StockChart data={marketData} />
                    </div>
                    <AIInsights analysis={aiAnalysis} />
                    <NewsFeed news={newsData} />
                </div>
            )}
        </div>
    );
};

export default Dashboard;
