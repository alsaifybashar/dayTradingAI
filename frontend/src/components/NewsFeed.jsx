import React from 'react';

const NewsFeed = ({ news = [], loading }) => {
    // Source icons mapping
    const getSourceIcon = (source) => {
        const sourceMap = {
            'cnbc': '📺',
            'reuters': '📰',
            'bloomberg': '💹',
            'yahoo': '🟣',
            'wsj': '📊',
            'marketwatch': '📈',
            'di.se': '🇸🇪',
            'default': '📄'
        };

        const sourceLower = (source || '').toLowerCase();
        for (const [key, icon] of Object.entries(sourceMap)) {
            if (sourceLower.includes(key)) return icon;
        }
        return sourceMap.default;
    };

    // Highlight keywords in headlines
    const highlightKeywords = (text) => {
        const positiveKeywords = ['beat', 'surge', 'soar', 'rally', 'gain', 'strong', 'bullish', 'record', 'growth', 'profit'];
        const negativeKeywords = ['miss', 'drop', 'fall', 'decline', 'weak', 'bearish', 'loss', 'concern', 'risk'];

        let result = text;

        positiveKeywords.forEach(keyword => {
            const regex = new RegExp(`(${keyword}[s]?|${keyword}ed|${keyword}ing)`, 'gi');
            result = result.replace(regex, `<span class="highlight-positive">$1</span>`);
        });

        negativeKeywords.forEach(keyword => {
            const regex = new RegExp(`(${keyword}[s]?|${keyword}ed|${keyword}ing)`, 'gi');
            result = result.replace(regex, `<span class="highlight-negative">$1</span>`);
        });

        return result;
    };

    // Format time ago
    const timeAgo = (dateString) => {
        if (!dateString) return 'Just now';
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
        return `${Math.floor(diffMins / 1440)}d ago`;
    };

    // Mock news if empty
    const displayNews = news.length > 0 ? news : [
        {
            title: 'Tesla deliveries beat expectations for Q3',
            source: 'CNBC',
            published: new Date().toISOString(),
            sentiment: 'positive'
        },
        {
            title: 'EV sector sees strong momentum amid policy support',
            source: 'Reuters',
            published: new Date(Date.now() - 3600000).toISOString(),
            sentiment: 'positive'
        },
        {
            title: 'Swedish market opens strong following EU data',
            source: 'Di.se',
            published: new Date(Date.now() - 7200000).toISOString(),
            sentiment: 'neutral'
        }
    ];

    if (loading) {
        return (
            <div className="glass-panel-elevated" style={{ height: '100%', padding: '20px' }}>
                <div className="skeleton" style={{ width: '50%', height: '20px', marginBottom: '20px' }} />
                {[1, 2, 3].map(i => (
                    <div key={i} className="skeleton" style={{ width: '100%', height: '60px', marginBottom: '12px' }} />
                ))}
            </div>
        );
    }

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
                    <span style={{ fontSize: '1.2rem' }}>📡</span>
                    <h3 style={{
                        margin: 0,
                        fontSize: '0.85rem',
                        fontWeight: '700',
                        textTransform: 'uppercase',
                        letterSpacing: '0.08em',
                        color: 'var(--text-secondary)'
                    }}>
                        Real-Time Intelligence
                    </h3>
                </div>
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    fontSize: '0.75rem',
                    color: 'var(--bullish)'
                }}>
                    <div className="status-dot online" style={{ width: '6px', height: '6px' }} />
                    LIVE
                </div>
            </div>

            {/* Custom styles for highlighting */}
            <style>{`
                .highlight-positive {
                    color: var(--warning-yellow);
                    font-weight: 700;
                    text-shadow: 0 0 10px rgba(251, 191, 36, 0.5);
                }
                .highlight-negative {
                    color: var(--bearish);
                    font-weight: 700;
                    text-shadow: 0 0 10px rgba(255, 59, 92, 0.3);
                }
            `}</style>

            {/* News Items */}
            <div style={{
                flex: 1,
                overflow: 'auto',
                padding: '12px'
            }}>
                {displayNews.map((item, index) => {
                    const sentiment = item.sentiment ||
                        (item.title?.toLowerCase().match(/beat|surge|strong|rally|gain/) ? 'positive' :
                            item.title?.toLowerCase().match(/miss|drop|fall|weak|decline/) ? 'negative' : 'neutral');

                    return (
                        <div
                            key={index}
                            style={{
                                padding: '14px 16px',
                                marginBottom: '8px',
                                background: 'var(--bg-secondary)',
                                borderRadius: 'var(--radius-md)',
                                borderLeft: `3px solid ${sentiment === 'positive' ? 'var(--bullish)' :
                                        sentiment === 'negative' ? 'var(--bearish)' :
                                            'var(--neutral-cyan)'
                                    }`,
                                cursor: 'pointer',
                                transition: 'all 0.2s ease'
                            }}
                            onMouseEnter={(e) => {
                                e.currentTarget.style.background = 'var(--bg-elevated)';
                                e.currentTarget.style.transform = 'translateX(4px)';
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.background = 'var(--bg-secondary)';
                                e.currentTarget.style.transform = 'translateX(0)';
                            }}
                        >
                            {/* Source & Time */}
                            <div style={{
                                display: 'flex',
                                justifyContent: 'space-between',
                                alignItems: 'center',
                                marginBottom: '8px'
                            }}>
                                <div style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '6px'
                                }}>
                                    <span style={{ fontSize: '1rem' }}>{getSourceIcon(item.source)}</span>
                                    <span style={{
                                        fontSize: '0.75rem',
                                        color: 'var(--neutral-cyan)',
                                        fontWeight: '600',
                                        textTransform: 'uppercase',
                                        letterSpacing: '0.05em'
                                    }}>
                                        {item.source || 'News'}
                                    </span>
                                </div>
                                <span style={{
                                    fontSize: '0.7rem',
                                    color: 'var(--text-muted)'
                                }}>
                                    {timeAgo(item.published)}
                                </span>
                            </div>

                            {/* Headline */}
                            <p
                                style={{
                                    margin: 0,
                                    fontSize: '0.9rem',
                                    lineHeight: '1.4',
                                    color: 'var(--text-primary)'
                                }}
                                dangerouslySetInnerHTML={{ __html: highlightKeywords(item.title || '') }}
                            />

                            {/* Sentiment Indicator */}
                            {sentiment !== 'neutral' && (
                                <div style={{
                                    marginTop: '10px',
                                    display: 'inline-flex',
                                    alignItems: 'center',
                                    gap: '4px',
                                    padding: '4px 8px',
                                    borderRadius: '4px',
                                    fontSize: '0.7rem',
                                    fontWeight: '600',
                                    background: sentiment === 'positive' ? 'var(--bullish-dim)' : 'var(--bearish-dim)',
                                    color: sentiment === 'positive' ? 'var(--bullish)' : 'var(--bearish)'
                                }}>
                                    {sentiment === 'positive' ? '📈 Bullish Signal' : '📉 Bearish Signal'}
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>

            {/* Footer */}
            <div style={{
                padding: '12px 16px',
                borderTop: '1px solid var(--border-secondary)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
            }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    {displayNews.length} articles monitored
                </span>
                <button style={{
                    background: 'none',
                    border: 'none',
                    color: 'var(--neutral-cyan)',
                    fontSize: '0.75rem',
                    fontWeight: '600',
                    cursor: 'pointer',
                    padding: '4px 8px',
                    borderRadius: '4px',
                    transition: 'background 0.2s'
                }}
                    onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(0, 212, 255, 0.1)'}
                    onMouseLeave={(e) => e.currentTarget.style.background = 'none'}
                >
                    View All →
                </button>
            </div>
        </div>
    );
};

export default NewsFeed;
