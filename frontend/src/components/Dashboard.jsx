import React, { useState, useEffect, useCallback } from 'react';
import StockChart from './StockChart';
import AIInsights from './AIInsights';
import NewsFeed from './NewsFeed';
import Watchlist from './Watchlist';

const API_URL = 'http://localhost:8000/api';

const Dashboard = () => {
    const [searchTerm, setSearchTerm] = useState('TSLA');
    const [ticker, setTicker] = useState('TSLA');
    const [marketData, setMarketData] = useState(null);
    const [newsData, setNewsData] = useState([]);
    const [aiAnalysis, setAiAnalysis] = useState(null);
    const [portfolio, setPortfolio] = useState(null);
    const [loading, setLoading] = useState(false);
    const [systemStatus, setSystemStatus] = useState('Idle');

    // Initial watchlist tickers to track
    const [watchlistTickers, setWatchlistTickers] = useState(['TSLA', 'AAPL', 'NVDA', 'AMD', 'META']);
    const [watchlist, setWatchlist] = useState([]);

    // Fetch Watchlist Data
    const fetchWatchlistData = useCallback(async () => {
        try {
            const response = await fetch(`${API_URL}/batch_market_data`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(watchlistTickers)
            });
            if (response.ok) {
                const data = await response.json();
                setWatchlist(data);
            }
        } catch (error) {
            console.error("Error fetching watchlist data:", error);
        }
    }, [watchlistTickers]);

    // Initial load and interval for watchlist
    useEffect(() => {
        fetchWatchlistData();
        const interval = setInterval(fetchWatchlistData, 60000); // Update every minute
        return () => clearInterval(interval);
    }, [fetchWatchlistData]);

    // Debounce search
    useEffect(() => {
        const delayDebounceFn = setTimeout(() => {
            if (searchTerm !== ticker && searchTerm.trim() !== '') {
                setSystemStatus('Input stabilized. Initiating search...');
                console.log(`[System] Debounce triggered for: ${searchTerm}`);
                setTicker(searchTerm);
            }
        }, 3000);

        if (searchTerm !== ticker && searchTerm.trim() !== '') {
            setSystemStatus('⏳ Waiting for input to stabilize...');
        } else if (!loading) {
            setSystemStatus('✅ System Ready');
        }

        return () => clearTimeout(delayDebounceFn);
    }, [searchTerm, ticker, loading]);

    const fetchData = useCallback(async () => {
        if (!ticker) return;
        setLoading(true);
        setSystemStatus(`🔍 Starting data collection for ${ticker}...`);

        // Clear previous data
        setMarketData(null);
        setNewsData([]);
        setAiAnalysis(null);

        try {
            console.log(`[System] Fetching analysis for ${ticker}...`);
            setSystemStatus(`📡 Fetching market data, news, and AI insights for ${ticker}...`);

            const response = await fetch(`${API_URL}/analyze/${ticker}`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            setSystemStatus('🧠 Processing with AI Engine...');
            const data = await response.json();

            setMarketData(data.market_data);
            setNewsData(data.news_data || []);
            setAiAnalysis(data.analysis);
            setPortfolio(data.portfolio);

            setSystemStatus(`✅ Analysis complete for ${ticker}`);
            console.log("[System] Data updated successfully.");
        } catch (error) {
            console.error("Error fetching data", error);
            setSystemStatus('❌ Error: Failed to fetch data');
        }
        setLoading(false);
    }, [ticker]);

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 60000);
        return () => clearInterval(interval);
    }, [ticker, fetchData]);

    const handleSearch = (e) => {
        e.preventDefault();
        if (searchTerm.trim() === '') return;
        if (ticker === searchTerm) {
            fetchData();
        } else {
            setTicker(searchTerm);
        }
    };

    const handleWatchlistSelect = (selectedTicker) => {
        setSearchTerm(selectedTicker);
        setTicker(selectedTicker);
    };

    return (
        <div style={{
            display: 'grid',
            gridTemplateColumns: '260px 1fr 380px',
            gridTemplateRows: 'auto 1fr',
            gap: '20px',
            height: 'calc(100vh - 120px)',
            overflow: 'hidden'
        }}>
            {/* Left Sidebar - Watchlist */}
            <div style={{ gridRow: 'span 2', overflow: 'hidden' }}>
                <Watchlist
                    items={watchlist}
                    activeTicker={ticker}
                    onSelect={handleWatchlistSelect}
                />
            </div>

            {/* Center Stage - Search + Chart + News */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', overflow: 'hidden' }}>
                {/* Search Bar & Status */}
                <div className="glass-panel" style={{ padding: '16px', display: 'flex', gap: '16px', alignItems: 'center', flexShrink: 0 }}>
                    <form onSubmit={handleSearch} style={{ display: 'flex', gap: '12px', flex: 1 }}>
                        <input
                            type="text"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value.toUpperCase())}
                            placeholder="Enter stock ticker (e.g., TSLA, AAPL)..."
                            style={{
                                flex: 1,
                                background: 'var(--bg-secondary)',
                                border: '1px solid var(--border-primary)',
                                borderRadius: 'var(--radius-md)',
                                padding: '12px 16px',
                                color: 'var(--text-primary)',
                                fontFamily: 'var(--font-mono)',
                                fontSize: '1rem',
                                fontWeight: '600'
                            }}
                        />
                        <button type="submit" className="btn btn-primary">
                            🔍 Analyze
                        </button>
                    </form>

                    {/* System Status */}
                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '10px',
                        padding: '10px 16px',
                        background: loading ? 'rgba(0, 212, 255, 0.1)' : 'rgba(0, 255, 136, 0.1)',
                        border: `1px solid ${loading ? 'rgba(0, 212, 255, 0.3)' : 'rgba(0, 255, 136, 0.3)'}`,
                        borderRadius: 'var(--radius-md)',
                        fontFamily: 'var(--font-mono)',
                        fontSize: '0.85rem',
                        color: loading ? 'var(--neutral-cyan)' : 'var(--bullish)',
                        minWidth: '300px'
                    }}>
                        {loading && (
                            <div style={{
                                width: '8px',
                                height: '8px',
                                background: 'var(--neutral-cyan)',
                                borderRadius: '50%',
                                animation: 'pulse 1s infinite'
                            }}></div>
                        )}
                        <span>{systemStatus}</span>
                    </div>
                </div>

                {/* Main Chart */}
                <div style={{ height: '55%', overflow: 'hidden' }}>
                    <StockChart data={marketData} ticker={ticker} analysis={aiAnalysis} loading={loading} />
                </div>

                {/* News Feed (Below Chart) */}
                <div style={{ flex: 1, overflow: 'hidden' }}>
                    <NewsFeed news={newsData} loading={loading} />
                </div>
            </div>

            {/* Right Panel - AI Insights & Portfolio */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', overflow: 'hidden', gridRow: 'span 2' }}>
                {/* AI Insight Engine */}
                <div style={{ flex: 1, minHeight: 0, overflow: 'auto' }}>
                    <AIInsights analysis={aiAnalysis} ticker={ticker} loading={loading} />
                </div>

                {/* Portfolio Summary */}
                {portfolio && (
                    <div className="glass-panel" style={{ padding: '16px', flexShrink: 0 }}>
                        <div style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            marginBottom: '12px'
                        }}>
                            <h3 style={{ margin: 0, fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                                💼 PAPER TRADING
                            </h3>
                            <span style={{
                                fontFamily: 'var(--font-mono)',
                                fontWeight: '700',
                                color: 'var(--bullish)',
                                textShadow: '0 0 10px var(--bullish-glow)'
                            }}>
                                ${portfolio.total_equity?.toFixed(2)}
                            </span>
                        </div>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                            <div style={{
                                background: 'var(--bg-secondary)',
                                padding: '10px',
                                borderRadius: 'var(--radius-sm)',
                                borderLeft: '3px solid var(--neutral-cyan)'
                            }}>
                                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Cash</div>
                                <div style={{ fontWeight: '600', fontFamily: 'var(--font-mono)' }}>
                                    ${portfolio.balance?.toFixed(2)}
                                </div>
                            </div>
                            <div style={{
                                background: 'var(--bg-secondary)',
                                padding: '10px',
                                borderRadius: 'var(--radius-sm)',
                                borderLeft: '3px solid var(--neutral-purple)'
                            }}>
                                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Positions</div>
                                <div style={{ fontWeight: '600' }}>
                                    {Object.keys(portfolio.holdings || {}).length} Active
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Dashboard;
