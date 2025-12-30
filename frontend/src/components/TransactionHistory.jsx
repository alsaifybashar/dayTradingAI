import React from 'react';

const TransactionHistory = ({ trades }) => {
    if (!trades || trades.length === 0) {
        return (
            <div className="glass-panel" style={{ height: '100%', padding: '20px', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: '10px' }}>
                <span style={{ fontSize: '2rem' }}>📜</span>
                <span style={{ color: 'var(--text-secondary)' }}>No trades recorded yet.</span>
            </div>
        );
    }

    // Sort by timestamp descending
    const sortedTrades = [...trades].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

    return (
        <div className="glass-panel" style={{ height: '100%', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
            <div style={{
                padding: '16px',
                borderBottom: '1px solid var(--border-primary)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                background: 'rgba(255, 255, 255, 0.02)'
            }}>
                <h3 style={{ margin: 0, fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span>📜</span> Transaction History
                </h3>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                    {trades.length} Total Trades
                </span>
            </div>

            <div style={{ flex: 1, overflowY: 'auto', padding: '0' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                    <thead style={{
                        position: 'sticky',
                        top: 0,
                        background: 'var(--bg-secondary)',
                        zIndex: 10
                    }}>
                        <tr>
                            <th style={{ padding: '12px 16px', textAlign: 'left', color: 'var(--text-secondary)', fontWeight: '600' }}>Time</th>
                            <th style={{ padding: '12px 16px', textAlign: 'left', color: 'var(--text-secondary)', fontWeight: '600' }}>Ticker</th>
                            <th style={{ padding: '12px 16px', textAlign: 'center', color: 'var(--text-secondary)', fontWeight: '600' }}>Type</th>
                            <th style={{ padding: '12px 16px', textAlign: 'right', color: 'var(--text-secondary)', fontWeight: '600' }}>Price</th>
                            <th style={{ padding: '12px 16px', textAlign: 'right', color: 'var(--text-secondary)', fontWeight: '600' }}>Qty</th>
                            <th style={{ padding: '12px 16px', textAlign: 'right', color: 'var(--text-secondary)', fontWeight: '600' }}>P/L</th>
                        </tr>
                    </thead>
                    <tbody>
                        {sortedTrades.map((trade, index) => {
                            const isBuy = trade.type === 'BUY';
                            const date = new Date(trade.timestamp);
                            const profit = trade.profit || 0;

                            return (
                                <tr key={index} style={{
                                    borderBottom: '1px solid var(--border-light)',
                                    transition: 'background 0.2s'
                                }}
                                    className="table-row-hover"
                                >
                                    <td style={{ padding: '12px 16px', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                                        {date.toLocaleTimeString()} <span style={{ fontSize: '0.75em', opacity: 0.7 }}>{date.toLocaleDateString()}</span>
                                    </td>
                                    <td style={{ padding: '12px 16px', fontWeight: '600' }}>
                                        {trade.ticker}
                                    </td>
                                    <td style={{ padding: '12px 16px', textAlign: 'center' }}>
                                        <span style={{
                                            padding: '4px 8px',
                                            borderRadius: '4px',
                                            fontSize: '0.75rem',
                                            fontWeight: '700',
                                            background: isBuy ? 'rgba(0, 255, 136, 0.1)' : 'rgba(255, 59, 92, 0.1)',
                                            color: isBuy ? 'var(--bullish)' : 'var(--bearish)',
                                            border: `1px solid ${isBuy ? 'rgba(0, 255, 136, 0.2)' : 'rgba(255, 59, 92, 0.2)'}`
                                        }}>
                                            {trade.type}
                                        </span>
                                    </td>
                                    <td style={{ padding: '12px 16px', textAlign: 'right', fontFamily: 'var(--font-mono)' }}>
                                        ${trade.price.toFixed(2)}
                                    </td>
                                    <td style={{ padding: '12px 16px', textAlign: 'right', fontFamily: 'var(--font-mono)' }}>
                                        {trade.qty}
                                    </td>
                                    <td style={{
                                        padding: '12px 16px',
                                        textAlign: 'right',
                                        fontFamily: 'var(--font-mono)',
                                        color: isBuy ? 'var(--text-muted)' : (profit >= 0 ? 'var(--bullish)' : 'var(--bearish)'),
                                        fontWeight: !isBuy ? '700' : '400'
                                    }}>
                                        {isBuy ? '-' : (profit > 0 ? `+$${profit.toFixed(2)}` : `$${profit.toFixed(2)}`)}
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default TransactionHistory;
