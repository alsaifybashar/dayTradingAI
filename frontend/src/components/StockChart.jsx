import React from 'react';

const StockChart = ({ data }) => {
    if (!data) return null;

    const isPositive = data.price >= data.open;
    const color = isPositive ? 'var(--success)' : 'var(--danger)';

    return (
        <div className="card glass">
            <h2 style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                {data.symbol}
                <span className="text-secondary" style={{ fontSize: '0.8em', fontWeight: 'normal' }}>Market Overview</span>
            </h2>

            <div style={{ display: 'flex', alignItems: 'baseline', gap: '1rem', marginBottom: '1rem' }}>
                <span style={{ fontSize: '3rem', fontWeight: 'bold' }}>
                    ${data.price?.toFixed(2)}
                </span>
                <span style={{ color: color, fontSize: '1.2rem', fontWeight: '600' }}>
                    {isPositive ? '▲' : '▼'} {((data.price - data.open) / data.open * 100).toFixed(2)}%
                </span>
            </div>

            <div className="grid grid-cols-3" style={{ gap: '1rem' }}>
                <div style={{ background: 'rgba(255,255,255,0.03)', padding: '10px', borderRadius: '8px' }}>
                    <div className="text-secondary" style={{ fontSize: '0.9rem' }}>Open</div>
                    <div style={{ fontSize: '1.2rem', fontWeight: '600' }}>${data.open?.toFixed(2)}</div>
                </div>
                <div style={{ background: 'rgba(255,255,255,0.03)', padding: '10px', borderRadius: '8px' }}>
                    <div className="text-secondary" style={{ fontSize: '0.9rem' }}>High</div>
                    <div style={{ fontSize: '1.2rem', fontWeight: '600' }}>${data.high?.toFixed(2)}</div>
                </div>
                <div style={{ background: 'rgba(255,255,255,0.03)', padding: '10px', borderRadius: '8px' }}>
                    <div className="text-secondary" style={{ fontSize: '0.9rem' }}>Low</div>
                    <div style={{ fontSize: '1.2rem', fontWeight: '600' }}>${data.low?.toFixed(2)}</div>
                </div>
                <div style={{ background: 'rgba(255,255,255,0.03)', padding: '10px', borderRadius: '8px' }}>
                    <div className="text-secondary" style={{ fontSize: '0.9rem' }}>Volume</div>
                    <div style={{ fontSize: '1.2rem', fontWeight: '600' }}>{(data.volume / 1000000).toFixed(2)}M</div>
                </div>
                <div style={{ background: 'rgba(255,255,255,0.03)', padding: '10px', borderRadius: '8px' }}>
                    <div className="text-secondary" style={{ fontSize: '0.9rem' }}>Source</div>
                    <div style={{ fontSize: '1.2rem', fontWeight: '600' }}>{data.source}</div>
                </div>
            </div>
        </div>
    );
};

export default StockChart;
