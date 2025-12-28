import React from 'react';

const NewsFeed = ({ news }) => {
    if (!news) return null;

    return (
        <div className="card glass" style={{ gridColumn: 'span 2' }}>
            <h2>Market News</h2>
            <div className="grid grid-cols-2" style={{ gap: '1rem' }}>
                {news.length === 0 ? (
                    <p className="text-secondary">No recent news found.</p>
                ) : (
                    news.map((item, index) => (
                        <a
                            key={index}
                            href={item.link}
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{
                                textDecoration: 'none',
                                color: 'inherit',
                                display: 'block'
                            }}
                        >
                            <div style={{
                                background: 'rgba(255,255,255,0.03)',
                                padding: '15px',
                                borderRadius: '8px',
                                height: '100%',
                                transition: 'background 0.2s',
                                border: '1px solid rgba(255,255,255,0.02)'
                            }}
                                onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.06)'}
                                onMouseLeave={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.03)'}
                            >
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                    <span style={{ fontSize: '0.8rem', color: 'var(--accent)' }}>{item.source}</span>
                                    <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                                        {new Date(item.published).toLocaleDateString()}
                                    </span>
                                </div>
                                <h3 style={{ fontSize: '1.1rem', marginBottom: '8px', lineHeight: '1.4' }}>{item.title}</h3>
                                <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', margin: 0 }}>
                                    {item.summary}
                                </p>
                            </div>
                        </a>
                    ))
                )}
            </div>
        </div>
    );
};

export default NewsFeed;
