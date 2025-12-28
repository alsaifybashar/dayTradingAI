import React from 'react';

const Watchlist = ({ items = [], activeTicker, onSelect }) => {
    const generateSparkline = (data, isBullish) => {
        const max = Math.max(...data);
        const min = Math.min(...data);
        const range = max - min || 1;

        return data.map((value, index) => {
            const height = ((value - min) / range) * 100;
            return (
                <div
                    key={index}
                    style={{
                        width: '3px',
                        height: `${Math.max(height, 10)}%`,
                        background: isBullish ? 'var(--bullish)' : 'var(--bearish)',
                        borderRadius: '1px',
                        opacity: 0.7 + (index / data.length) * 0.3
                    }}
                />
            );
        });
    };

    return (
        <div className="glass-panel-elevated" style={{
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden'
        }}>
            {/* Header */}
            <div style={{
                padding: '16px 20px',
                borderBottom: '1px solid var(--border-secondary)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <span style={{ fontSize: '1.2rem' }}>👁️</span>
                    <h3 style={{
                        margin: 0,
                        fontSize: '0.85rem',
                        fontWeight: '700',
                        textTransform: 'uppercase',
                        letterSpacing: '0.08em',
                        color: 'var(--text-secondary)'
                    }}>
                        Active Watchlist
                    </h3>
                </div>
                <span style={{
                    fontSize: '0.75rem',
                    color: 'var(--neutral-cyan)',
                    background: 'rgba(0, 212, 255, 0.1)',
                    padding: '4px 8px',
                    borderRadius: '4px',
                    fontWeight: '600'
                }}>
                    {items.length} STOCKS
                </span>
            </div>

            {/* Watchlist Items */}
            <div style={{
                flex: 1,
                overflow: 'auto',
                padding: '8px'
            }}>
                {items.map((item, index) => {
                    const isActive = item.ticker === activeTicker;
                    const isBullish = item.change >= 0;

                    return (
                        <div
                            key={item.ticker}
                            onClick={() => onSelect(item.ticker)}
                            style={{
                                padding: '14px 16px',
                                marginBottom: '6px',
                                borderRadius: 'var(--radius-md)',
                                cursor: 'pointer',
                                transition: 'all 0.2s ease',
                                background: isActive
                                    ? 'linear-gradient(135deg, rgba(0, 212, 255, 0.15) 0%, rgba(168, 85, 247, 0.1) 100%)'
                                    : 'transparent',
                                border: isActive
                                    ? '1px solid rgba(0, 212, 255, 0.4)'
                                    : '1px solid transparent',
                                boxShadow: isActive
                                    ? '0 0 20px rgba(0, 212, 255, 0.15), inset 0 0 20px rgba(0, 212, 255, 0.05)'
                                    : 'none',
                                animation: isActive ? 'glow 3s ease-in-out infinite' : 'none'
                            }}
                            onMouseEnter={(e) => {
                                if (!isActive) {
                                    e.currentTarget.style.background = 'rgba(255, 255, 255, 0.03)';
                                    e.currentTarget.style.border = '1px solid rgba(255, 255, 255, 0.1)';
                                }
                            }}
                            onMouseLeave={(e) => {
                                if (!isActive) {
                                    e.currentTarget.style.background = 'transparent';
                                    e.currentTarget.style.border = '1px solid transparent';
                                }
                            }}
                        >
                            {/* Row 1: Ticker & Sparkline */}
                            <div style={{
                                display: 'flex',
                                justifyContent: 'space-between',
                                alignItems: 'center',
                                marginBottom: '8px'
                            }}>
                                <span style={{
                                    fontWeight: '700',
                                    fontSize: '1.1rem',
                                    color: isActive ? 'var(--neutral-cyan)' : 'var(--text-primary)',
                                    textShadow: isActive ? '0 0 10px var(--neutral-cyan-glow)' : 'none'
                                }}>
                                    {item.ticker}
                                </span>

                                {/* Sparkline */}
                                <div style={{
                                    display: 'flex',
                                    alignItems: 'flex-end',
                                    gap: '1px',
                                    height: '24px'
                                }}>
                                    {generateSparkline(item.sparkline, isBullish)}
                                </div>
                            </div>

                            {/* Row 2: Price & Change */}
                            <div style={{
                                display: 'flex',
                                justifyContent: 'space-between',
                                alignItems: 'center'
                            }}>
                                <span style={{
                                    fontFamily: 'var(--font-mono)',
                                    fontWeight: '600',
                                    fontSize: '1rem',
                                    color: 'var(--text-primary)'
                                }}>
                                    ${item.price.toFixed(2)}
                                </span>
                                <span style={{
                                    fontFamily: 'var(--font-mono)',
                                    fontSize: '0.85rem',
                                    fontWeight: '600',
                                    padding: '4px 8px',
                                    borderRadius: '4px',
                                    background: isBullish ? 'var(--bullish-dim)' : 'var(--bearish-dim)',
                                    color: isBullish ? 'var(--bullish)' : 'var(--bearish)',
                                    textShadow: isBullish
                                        ? '0 0 8px var(--bullish-glow)'
                                        : '0 0 8px var(--bearish-glow)'
                                }}>
                                    {isBullish ? '+' : ''}{item.changePercent.toFixed(2)}% {isBullish ? '▲' : '▼'}
                                </span>
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Footer - Add to Watchlist */}
            <div style={{
                padding: '12px 16px',
                borderTop: '1px solid var(--border-secondary)'
            }}>
                <button style={{
                    width: '100%',
                    padding: '10px',
                    background: 'var(--bg-secondary)',
                    border: '1px dashed var(--border-primary)',
                    borderRadius: 'var(--radius-md)',
                    color: 'var(--text-muted)',
                    fontSize: '0.85rem',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease'
                }}
                    onMouseEnter={(e) => {
                        e.currentTarget.style.borderColor = 'var(--neutral-cyan)';
                        e.currentTarget.style.color = 'var(--neutral-cyan)';
                    }}
                    onMouseLeave={(e) => {
                        e.currentTarget.style.borderColor = 'var(--border-primary)';
                        e.currentTarget.style.color = 'var(--text-muted)';
                    }}
                >
                    + Add Ticker
                </button>
            </div>
        </div>
    );
};

export default Watchlist;
