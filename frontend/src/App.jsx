import React, { useState, useEffect } from 'react';
import Dashboard from './components/Dashboard';

const API_URL = 'http://localhost:8000/api';

function App() {
  const [indices, setIndices] = useState({
    sp500: { value: '4,500.21', change: '+0.45%', bullish: true },
    nasdaq: { value: '14,100.50', change: '+0.80%', bullish: true }
  });
  const [portfolio, setPortfolio] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('connecting');

  useEffect(() => {
    // Check API connection
    const checkConnection = async () => {
      try {
        const response = await fetch(`${API_URL.replace('/api', '')}/health`);
        if (response.ok) {
          setConnectionStatus('online');
        } else {
          setConnectionStatus('offline');
        }
      } catch {
        setConnectionStatus('offline');
      }
    };

    checkConnection();
    const interval = setInterval(checkConnection, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="app" style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Top Global Navigation Bar */}
      <nav style={{
        background: 'linear-gradient(180deg, rgba(18, 18, 24, 0.98) 0%, rgba(18, 18, 24, 0.9) 100%)',
        backdropFilter: 'blur(20px)',
        borderBottom: '1px solid rgba(0, 212, 255, 0.15)',
        padding: '0 24px',
        height: '60px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        position: 'sticky',
        top: 0,
        zIndex: 1000,
        boxShadow: '0 4px 30px rgba(0, 0, 0, 0.3)'
      }}>
        {/* Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '36px',
            height: '36px',
            background: 'linear-gradient(135deg, var(--neutral-cyan) 0%, var(--neutral-purple) 100%)',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 20px rgba(0, 212, 255, 0.3)'
          }}>
            <span style={{ fontSize: '20px' }}>🧠</span>
          </div>
          <div>
            <span style={{
              fontSize: '1.4rem',
              fontWeight: '800',
              letterSpacing: '-0.02em',
              background: 'linear-gradient(90deg, #fff 0%, var(--neutral-cyan) 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}>
              dayTradingAI
            </span>
            <span style={{
              fontSize: '1.4rem',
              fontWeight: '800',
              color: 'var(--neutral-cyan)',
              textShadow: '0 0 20px rgba(0, 212, 255, 0.5)'
            }}> AI</span>
          </div>
        </div>

        {/* Market Indices (Center) */}
        <div style={{
          display: 'flex',
          gap: '32px',
          fontFamily: 'var(--font-mono)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>S&P 500</span>
            <span style={{ fontWeight: '600', color: '#fff' }}>{indices.sp500.value}</span>
            <span style={{
              color: indices.sp500.bullish ? 'var(--bullish)' : 'var(--bearish)',
              fontSize: '0.85rem',
              fontWeight: '600',
              textShadow: indices.sp500.bullish ? '0 0 10px var(--bullish-glow)' : '0 0 10px var(--bearish-glow)'
            }}>
              {indices.sp500.change} {indices.sp500.bullish ? '▲' : '▼'}
            </span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>NASDAQ</span>
            <span style={{ fontWeight: '600', color: '#fff' }}>{indices.nasdaq.value}</span>
            <span style={{
              color: indices.nasdaq.bullish ? 'var(--bullish)' : 'var(--bearish)',
              fontSize: '0.85rem',
              fontWeight: '600',
              textShadow: indices.nasdaq.bullish ? '0 0 10px var(--bullish-glow)' : '0 0 10px var(--bearish-glow)'
            }}>
              {indices.nasdaq.change} {indices.nasdaq.bullish ? '▲' : '▼'}
            </span>
          </div>
        </div>

        {/* User Portfolio Summary (Right) */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Total Equity
            </div>
            <div style={{
              fontSize: '1.1rem',
              fontWeight: '700',
              fontFamily: 'var(--font-mono)',
              color: '#fff'
            }}>
              $54,300.25
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Day P&L
            </div>
            <div style={{
              fontSize: '1.1rem',
              fontWeight: '700',
              fontFamily: 'var(--font-mono)',
              color: 'var(--bullish)',
              textShadow: '0 0 15px var(--bullish-glow)'
            }}>
              +$1,250.00
            </div>
          </div>
          {/* Connection Status */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px 12px',
            background: connectionStatus === 'online' ? 'var(--bullish-dim)' : 'var(--bearish-dim)',
            borderRadius: '8px',
            border: `1px solid ${connectionStatus === 'online' ? 'rgba(0, 255, 136, 0.3)' : 'rgba(255, 59, 92, 0.3)'}`
          }}>
            <div className={`status-dot ${connectionStatus}`}></div>
            <span style={{
              fontSize: '0.8rem',
              fontWeight: '600',
              color: connectionStatus === 'online' ? 'var(--bullish)' : 'var(--bearish)',
              textTransform: 'uppercase',
              letterSpacing: '0.05em'
            }}>
              {connectionStatus === 'online' ? 'LIVE' : 'OFFLINE'}
            </span>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main style={{ flex: 1, padding: '20px', overflow: 'hidden' }}>
        <Dashboard />
      </main>
    </div>
  );
}

export default App;
