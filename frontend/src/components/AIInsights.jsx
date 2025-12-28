import React from 'react';

const AIInsights = ({ analysis, ticker, loading }) => {
    if (loading) {
        return (
            <div className="glass-panel-elevated" style={{ height: '100%', padding: '20px' }}>
                <div className="skeleton" style={{ width: '60%', height: '24px', marginBottom: '20px' }} />
                <div className="skeleton" style={{ width: '100%', height: '120px', marginBottom: '16px' }} />
                <div className="skeleton" style={{ width: '80%', height: '16px', marginBottom: '8px' }} />
                <div className="skeleton" style={{ width: '90%', height: '16px' }} />
            </div>
        );
    }

    if (!analysis) {
        return (
            <div className="glass-panel-elevated" style={{
                height: '100%',
                padding: '24px',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                textAlign: 'center'
            }}>
                <div style={{ fontSize: '3rem', marginBottom: '16px', opacity: 0.5 }}>🧠</div>
                <h3 style={{ color: 'var(--text-secondary)', margin: 0 }}>AI Insight Engine</h3>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '8px' }}>
                    Waiting for analysis data...
                </p>
            </div>
        );
    }

    const getDecisionColor = (decision) => {
        switch (decision) {
            case 'BUY': return 'var(--bullish)';
            case 'SELL': return 'var(--bearish)';
            case 'TRACK': return 'var(--warning-yellow)';
            default: return 'var(--neutral-cyan)';
        }
    };

    const getGaugeRotation = (confidence) => {
        // Map 0-100 confidence to -90deg to 90deg rotation
        return -90 + (confidence / 100) * 180;
    };

    const getSentimentLabel = (confidence, decision) => {
        if (decision === 'BUY' && confidence >= 80) return 'STRONG BULLISH';
        if (decision === 'BUY' && confidence >= 60) return 'BULLISH';
        if (decision === 'SELL' && confidence >= 80) return 'STRONG BEARISH';
        if (decision === 'SELL' && confidence >= 60) return 'BEARISH';
        if (decision === 'TRACK') return 'WATCHING';
        return 'NEUTRAL';
    };

    // Parse reasoning into bullet points
    const reasoningPoints = analysis.reasoning
        ? analysis.reasoning.split(/[.;]/).filter(s => s.trim().length > 5).slice(0, 3)
        : [];

    return (
        <div className="glass-panel-elevated" style={{
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
            position: 'relative'
        }}>
            {/* Ambient Glow */}
            <div style={{
                position: 'absolute',
                top: '-50%',
                right: '-30%',
                width: '250px',
                height: '250px',
                background: getDecisionColor(analysis.decision),
                filter: 'blur(100px)',
                opacity: 0.15,
                borderRadius: '50%',
                pointerEvents: 'none'
            }} />

            {/* Header */}
            <div style={{
                padding: '16px 20px',
                borderBottom: '1px solid var(--border-secondary)',
                display: 'flex',
                alignItems: 'center',
                gap: '10px'
            }}>
                <span style={{ fontSize: '1.2rem' }}>🧠</span>
                <h3 style={{
                    margin: 0,
                    fontSize: '0.85rem',
                    fontWeight: '700',
                    textTransform: 'uppercase',
                    letterSpacing: '0.08em',
                    color: 'var(--text-secondary)'
                }}>
                    AI Insight Engine
                </h3>
            </div>

            {/* Content */}
            <div style={{ flex: 1, padding: '20px', overflow: 'auto' }}>
                {/* Gauge */}
                <div style={{
                    position: 'relative',
                    width: '180px',
                    height: '100px',
                    margin: '0 auto 20px auto'
                }}>
                    {/* Gauge Background Arc */}
                    <div style={{
                        position: 'absolute',
                        width: '180px',
                        height: '90px',
                        borderRadius: '90px 90px 0 0',
                        background: `conic-gradient(
                            from 180deg,
                            var(--bearish) 0deg,
                            var(--warning-yellow) 60deg,
                            var(--bullish) 120deg,
                            var(--bullish) 180deg
                        )`,
                        opacity: 0.3
                    }} />

                    {/* Gauge Fill (inner circle) */}
                    <div style={{
                        position: 'absolute',
                        top: '15px',
                        left: '15px',
                        width: '150px',
                        height: '75px',
                        borderRadius: '75px 75px 0 0',
                        background: 'var(--bg-primary)'
                    }} />

                    {/* Needle */}
                    <div style={{
                        position: 'absolute',
                        bottom: '5px',
                        left: '50%',
                        width: '3px',
                        height: '70px',
                        background: `linear-gradient(to top, ${getDecisionColor(analysis.decision)}, transparent)`,
                        transformOrigin: 'center bottom',
                        transform: `translateX(-50%) rotate(${getGaugeRotation(analysis.confidence)}deg)`,
                        transition: 'transform 1s cubic-bezier(0.34, 1.56, 0.64, 1)',
                        borderRadius: '2px',
                        boxShadow: `0 0 10px ${getDecisionColor(analysis.decision)}`
                    }} />

                    {/* Center Dot */}
                    <div style={{
                        position: 'absolute',
                        bottom: '0',
                        left: '50%',
                        transform: 'translateX(-50%)',
                        width: '16px',
                        height: '16px',
                        background: 'var(--bg-elevated)',
                        border: `2px solid ${getDecisionColor(analysis.decision)}`,
                        borderRadius: '50%',
                        boxShadow: `0 0 15px ${getDecisionColor(analysis.decision)}40`
                    }} />

                    {/* Sentiment Label */}
                    <div style={{
                        position: 'absolute',
                        bottom: '-30px',
                        left: '50%',
                        transform: 'translateX(-50%)',
                        fontSize: '0.75rem',
                        fontWeight: '700',
                        color: getDecisionColor(analysis.decision),
                        textShadow: `0 0 10px ${getDecisionColor(analysis.decision)}60`,
                        letterSpacing: '0.1em'
                    }}>
                        {getSentimentLabel(analysis.confidence, analysis.decision)}
                    </div>
                </div>

                {/* Confidence Score */}
                <div style={{
                    textAlign: 'center',
                    marginTop: '30px',
                    marginBottom: '20px'
                }}>
                    <div style={{
                        fontSize: '0.75rem',
                        color: 'var(--text-muted)',
                        textTransform: 'uppercase',
                        letterSpacing: '0.1em',
                        marginBottom: '4px'
                    }}>
                        Confidence Score
                    </div>
                    <div style={{
                        fontFamily: 'var(--font-mono)',
                        fontSize: '2.5rem',
                        fontWeight: '800',
                        color: getDecisionColor(analysis.decision),
                        textShadow: `0 0 30px ${getDecisionColor(analysis.decision)}60`
                    }}>
                        {analysis.confidence}%
                    </div>
                </div>

                {/* Decision Badge */}
                <div style={{
                    display: 'flex',
                    justifyContent: 'center',
                    marginBottom: '20px'
                }}>
                    <div style={{
                        padding: '12px 24px',
                        background: `linear-gradient(135deg, ${getDecisionColor(analysis.decision)}30 0%, ${getDecisionColor(analysis.decision)}10 100%)`,
                        border: `1px solid ${getDecisionColor(analysis.decision)}60`,
                        borderRadius: 'var(--radius-lg)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '10px'
                    }}>
                        <span style={{ fontSize: '1.3rem' }}>
                            {analysis.decision === 'BUY' ? '🚀' :
                                analysis.decision === 'SELL' ? '🔻' :
                                    analysis.decision === 'TRACK' ? '👁️' : '⏸️'}
                        </span>
                        <span style={{
                            fontWeight: '800',
                            fontSize: '1.2rem',
                            color: getDecisionColor(analysis.decision),
                            letterSpacing: '0.05em'
                        }}>
                            {analysis.decision}
                        </span>
                    </div>
                </div>

                {/* Price Targets */}
                {(analysis.entry_price || analysis.target_price || analysis.stop_loss) && (
                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: '1fr 1fr 1fr',
                        gap: '8px',
                        marginBottom: '20px'
                    }}>
                        <div style={{
                            background: 'var(--bg-secondary)',
                            padding: '12px',
                            borderRadius: 'var(--radius-md)',
                            textAlign: 'center',
                            borderTop: '2px solid var(--neutral-cyan)'
                        }}>
                            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: '4px' }}>ENTRY</div>
                            <div style={{ fontFamily: 'var(--font-mono)', fontWeight: '600', fontSize: '0.9rem' }}>
                                {analysis.entry_price || '-'}
                            </div>
                        </div>
                        <div style={{
                            background: 'var(--bg-secondary)',
                            padding: '12px',
                            borderRadius: 'var(--radius-md)',
                            textAlign: 'center',
                            borderTop: '2px solid var(--bullish)'
                        }}>
                            <div style={{ fontSize: '0.7rem', color: 'var(--bullish)', marginBottom: '4px' }}>TARGET</div>
                            <div style={{ fontFamily: 'var(--font-mono)', fontWeight: '600', fontSize: '0.9rem', color: 'var(--bullish)' }}>
                                {analysis.target_price || '-'}
                            </div>
                        </div>
                        <div style={{
                            background: 'var(--bg-secondary)',
                            padding: '12px',
                            borderRadius: 'var(--radius-md)',
                            textAlign: 'center',
                            borderTop: '2px solid var(--bearish)'
                        }}>
                            <div style={{ fontSize: '0.7rem', color: 'var(--bearish)', marginBottom: '4px' }}>STOP</div>
                            <div style={{ fontFamily: 'var(--font-mono)', fontWeight: '600', fontSize: '0.9rem', color: 'var(--bearish)' }}>
                                {analysis.stop_loss || '-'}
                            </div>
                        </div>
                    </div>
                )}

                {/* AI Reasoning Summary */}
                <div style={{
                    background: 'rgba(0, 0, 0, 0.3)',
                    borderRadius: 'var(--radius-md)',
                    padding: '16px',
                    borderLeft: `3px solid ${getDecisionColor(analysis.decision)}`
                }}>
                    <h4 style={{
                        margin: '0 0 12px 0',
                        fontSize: '0.8rem',
                        color: 'var(--text-secondary)',
                        textTransform: 'uppercase',
                        letterSpacing: '0.08em'
                    }}>
                        AI Reasoning Summary
                    </h4>
                    {reasoningPoints.length > 0 ? (
                        <ul style={{
                            margin: 0,
                            paddingLeft: '20px',
                            listStyle: 'none'
                        }}>
                            {reasoningPoints.map((point, index) => (
                                <li key={index} style={{
                                    color: 'var(--text-secondary)',
                                    fontSize: '0.85rem',
                                    lineHeight: '1.6',
                                    marginBottom: '8px',
                                    display: 'flex',
                                    alignItems: 'flex-start',
                                    gap: '8px'
                                }}>
                                    <span style={{
                                        color: 'var(--bullish)',
                                        fontSize: '0.9rem'
                                    }}>✓</span>
                                    <span>{point.trim()}</span>
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <p style={{
                            margin: 0,
                            color: 'var(--text-secondary)',
                            fontSize: '0.85rem',
                            lineHeight: '1.6'
                        }}>
                            {analysis.reasoning || analysis.analysis_english || 'Analysis pending...'}
                        </p>
                    )}
                </div>

                {/* Action Button */}
                {analysis.decision === 'BUY' && analysis.confidence >= 70 && (
                    <button className="btn btn-buy" style={{
                        width: '100%',
                        marginTop: '16px',
                        padding: '14px'
                    }}>
                        🚀 EXECUTE BUY ORDER
                    </button>
                )}
            </div>
        </div>
    );
};

export default AIInsights;
