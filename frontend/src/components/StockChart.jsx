import React from 'react';

const StockChart = ({ data, ticker, analysis, loading }) => {
    // Generate mock candlestick data for visualization
    const generateCandleData = () => {
        const candles = [];
        let basePrice = data?.price || 245;

        for (let i = 0; i < 40; i++) {
            const volatility = Math.random() * 4 - 2;
            const open = basePrice + volatility;
            const close = open + (Math.random() * 6 - 3);
            const high = Math.max(open, close) + Math.random() * 2;
            const low = Math.min(open, close) - Math.random() * 2;
            basePrice = close;

            candles.push({ open, close, high, low, bullish: close > open });
        }
        return candles;
    };

    // Use real data if available, otherwise mock for initial state
    const candles = data?.candles && data.candles.length > 0 ? data.candles : generateCandleData();

    const currentPrice = data?.price || candles[candles.length - 1]?.close || 245.50;
    const priceChange = data?.change || 3.24;
    const priceChangePercent = data?.change_percent || 1.34;
    const isBullish = priceChange >= 0;

    // Calculate chart dimensions
    const prices = candles.flatMap(c => [c.high, c.low]);
    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);
    const priceRange = maxPrice - minPrice || 1;

    const getY = (price) => {
        return 100 - ((price - minPrice) / priceRange) * 100;
    };

    return (
        <div className="glass-panel-elevated" style={{
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
            position: 'relative'
        }}>
            {/* Ambient Glow Background */}
            <div style={{
                position: 'absolute',
                top: '20%',
                right: '10%',
                width: '300px',
                height: '300px',
                background: isBullish ? 'var(--bullish)' : 'var(--bearish)',
                filter: 'blur(120px)',
                opacity: 0.1,
                borderRadius: '50%',
                pointerEvents: 'none'
            }} />

            {/* Chart Header */}
            <div style={{
                padding: '20px 24px',
                borderBottom: '1px solid var(--border-secondary)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'flex-start'
            }}>
                <div>
                    {/* Ticker & Company */}
                    <div style={{ display: 'flex', alignItems: 'baseline', gap: '12px', marginBottom: '8px' }}>
                        <h2 style={{
                            margin: 0,
                            fontSize: '1.5rem',
                            fontWeight: '800',
                            color: 'var(--neutral-cyan)',
                            textShadow: '0 0 20px var(--neutral-cyan-glow)'
                        }}>
                            {ticker}
                        </h2>
                        <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                            {ticker === 'TSLA' ? 'Tesla Inc.' :
                                ticker === 'AAPL' ? 'Apple Inc.' :
                                    ticker === 'NVDA' ? 'NVIDIA Corporation' :
                                        ticker === 'AMD' ? 'Advanced Micro Devices' : 'Stock'}
                        </span>
                        <span style={{
                            fontSize: '0.75rem',
                            padding: '4px 10px',
                            background: 'var(--bg-secondary)',
                            borderRadius: '4px',
                            color: 'var(--text-muted)'
                        }}>
                            5M
                        </span>
                    </div>

                    {/* Price Display */}
                    <div style={{ display: 'flex', alignItems: 'baseline', gap: '16px' }}>
                        <span style={{
                            fontFamily: 'var(--font-mono)',
                            fontSize: '3rem',
                            fontWeight: '800',
                            color: 'var(--text-primary)',
                            letterSpacing: '-0.02em'
                        }}>
                            ${currentPrice.toFixed(2)}
                        </span>
                        <span style={{
                            fontFamily: 'var(--font-mono)',
                            fontSize: '1.2rem',
                            fontWeight: '600',
                            padding: '6px 12px',
                            borderRadius: '6px',
                            background: isBullish ? 'var(--bullish-dim)' : 'var(--bearish-dim)',
                            color: isBullish ? 'var(--bullish)' : 'var(--bearish)',
                            textShadow: isBullish
                                ? '0 0 15px var(--bullish-glow)'
                                : '0 0 15px var(--bearish-glow)'
                        }}>
                            {isBullish ? '+' : ''}{priceChange.toFixed(2)} ({isBullish ? '+' : ''}{priceChangePercent.toFixed(2)}%) {isBullish ? '▲' : '▼'}
                        </span>
                    </div>
                </div>

                {/* Timeframe Selector */}
                <div style={{ display: 'flex', gap: '8px' }}>
                    {['1M', '5M', '15M', '1H', '1D'].map((tf, i) => (
                        <button
                            key={tf}
                            style={{
                                padding: '8px 14px',
                                background: tf === '5M' ? 'var(--neutral-cyan)' : 'var(--bg-secondary)',
                                color: tf === '5M' ? '#000' : 'var(--text-secondary)',
                                border: 'none',
                                borderRadius: 'var(--radius-sm)',
                                fontSize: '0.8rem',
                                fontWeight: '600',
                                cursor: 'pointer',
                                transition: 'all 0.2s'
                            }}
                        >
                            {tf}
                        </button>
                    ))}
                </div>
            </div>

            {/* Main Chart Area */}
            <div style={{ flex: 1, position: 'relative', padding: '20px', minHeight: '300px' }}>
                {loading ? (
                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        height: '100%'
                    }}>
                        <div className="skeleton" style={{ width: '100%', height: '100%' }} />
                    </div>
                ) : (
                    <>
                        {/* Candlestick Chart */}
                        <div style={{
                            display: 'flex',
                            alignItems: 'flex-end',
                            justifyContent: 'space-between',
                            height: '100%',
                            paddingBottom: '60px'
                        }}>
                            {candles.map((candle, index) => {
                                const bodyTop = getY(Math.max(candle.open, candle.close));
                                const bodyBottom = getY(Math.min(candle.open, candle.close));
                                const wickTop = getY(candle.high);
                                const wickBottom = getY(candle.low);
                                const isRecent = index >= candles.length - 5;

                                return (
                                    <div
                                        key={index}
                                        style={{
                                            position: 'relative',
                                            width: '12px',
                                            height: '100%',
                                            display: 'flex',
                                            flexDirection: 'column',
                                            alignItems: 'center'
                                        }}
                                    >
                                        {/* Wick */}
                                        <div style={{
                                            position: 'absolute',
                                            top: `${wickTop}%`,
                                            height: `${wickBottom - wickTop}%`,
                                            width: '2px',
                                            background: candle.bullish ? 'var(--bullish)' : 'var(--bearish)',
                                            opacity: isRecent ? 1 : 0.6
                                        }} />

                                        {/* Body */}
                                        <div style={{
                                            position: 'absolute',
                                            top: `${bodyTop}%`,
                                            height: `${Math.max(bodyBottom - bodyTop, 2)}%`,
                                            width: '10px',
                                            background: candle.bullish ? 'var(--bullish)' : 'var(--bearish)',
                                            borderRadius: '2px',
                                            opacity: isRecent ? 1 : 0.7,
                                            boxShadow: isRecent && candle.bullish
                                                ? '0 0 15px var(--bullish-glow)'
                                                : isRecent ? '0 0 15px var(--bearish-glow)' : 'none'
                                        }} />
                                    </div>
                                );
                            })}
                        </div>

                        {/* AI Signal Badge */}
                        {analysis && analysis.decision !== 'ERROR' && (
                            <div style={{
                                position: 'absolute',
                                top: '30%',
                                right: '15%',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '10px',
                                padding: '12px 18px',
                                background: analysis.decision === 'BUY'
                                    ? 'linear-gradient(135deg, rgba(0, 255, 136, 0.2) 0%, rgba(0, 255, 136, 0.05) 100%)'
                                    : analysis.decision === 'SELL'
                                        ? 'linear-gradient(135deg, rgba(255, 59, 92, 0.2) 0%, rgba(255, 59, 92, 0.05) 100%)'
                                        : 'linear-gradient(135deg, rgba(0, 212, 255, 0.2) 0%, rgba(0, 212, 255, 0.05) 100%)',
                                border: `1px solid ${analysis.decision === 'BUY' ? 'rgba(0, 255, 136, 0.5)' :
                                    analysis.decision === 'SELL' ? 'rgba(255, 59, 92, 0.5)' :
                                        'rgba(0, 212, 255, 0.5)'
                                    }`,
                                borderRadius: 'var(--radius-lg)',
                                backdropFilter: 'blur(10px)',
                                boxShadow: analysis.decision === 'BUY'
                                    ? '0 0 30px var(--bullish-glow)'
                                    : analysis.decision === 'SELL'
                                        ? '0 0 30px var(--bearish-glow)'
                                        : '0 0 30px var(--neutral-cyan-glow)',
                                animation: 'fadeIn 0.5s ease'
                            }}>
                                <span style={{ fontSize: '1.5rem' }}>
                                    {analysis.decision === 'BUY' ? '🧠' : analysis.decision === 'SELL' ? '⚠️' : '📊'}
                                </span>
                                <div>
                                    <div style={{
                                        fontSize: '0.7rem',
                                        color: 'var(--text-secondary)',
                                        textTransform: 'uppercase',
                                        letterSpacing: '0.1em'
                                    }}>
                                        AI Signal
                                    </div>
                                    <div style={{
                                        fontWeight: '800',
                                        fontSize: '1.1rem',
                                        color: analysis.decision === 'BUY' ? 'var(--bullish)' :
                                            analysis.decision === 'SELL' ? 'var(--bearish)' :
                                                'var(--neutral-cyan)',
                                        textShadow: analysis.decision === 'BUY'
                                            ? '0 0 15px var(--bullish-glow)'
                                            : analysis.decision === 'SELL'
                                                ? '0 0 15px var(--bearish-glow)'
                                                : '0 0 15px var(--neutral-cyan-glow)'
                                    }}>
                                        {analysis.decision} SIGNAL
                                    </div>
                                </div>
                                {analysis.decision === 'BUY' && (
                                    <span style={{ fontSize: '1.5rem' }}>↗</span>
                                )}
                            </div>
                        )}

                        {/* Volume Histogram */}
                        <div style={{
                            position: 'absolute',
                            bottom: '20px',
                            left: '20px',
                            right: '20px',
                            height: '50px',
                            display: 'flex',
                            alignItems: 'flex-end',
                            gap: '2px'
                        }}>
                            {candles.map((candle, index) => {
                                const volume = 20 + Math.random() * 80;
                                const isRecent = index >= candles.length - 5;

                                return (
                                    <div
                                        key={index}
                                        style={{
                                            flex: 1,
                                            height: `${volume}%`,
                                            background: candle.bullish ? 'var(--bullish)' : 'var(--bearish)',
                                            opacity: isRecent ? 0.6 : 0.25,
                                            borderRadius: '2px 2px 0 0'
                                        }}
                                    />
                                );
                            })}
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

export default StockChart;
