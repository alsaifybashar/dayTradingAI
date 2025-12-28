import React from 'react';

const AIInsights = ({ analysis }) => {
    if (!analysis) return (
        <div className="card glass">
            <h2>AI Analysis</h2>
            <p className="text-secondary">Waiting for data...</p>
        </div>
    );

    const getDecisionColor = (d) => {
        if (d === 'BUY') return 'var(--success)';
        if (d === 'SELL') return 'var(--danger)';
        return 'var(--text-secondary)';
    };

    return (
        <div className="card glass" style={{ position: 'relative', overflow: 'hidden' }}>
            {/* Ambient background glow based on decision */}
            <div style={{
                position: 'absolute',
                top: '-50%',
                right: '-50%',
                width: '200px',
                height: '200px',
                background: getDecisionColor(analysis.decision),
                filter: 'blur(80px)',
                opacity: 0.2,
                borderRadius: '50%'
            }}></div>

            <h2>AI Insights</h2>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span className="text-secondary">Recommendation</span>
                    <span style={{
                        color: getDecisionColor(analysis.decision),
                        fontWeight: '800',
                        fontSize: '1.5rem',
                        letterSpacing: '1px'
                    }}>
                        {analysis.decision}
                    </span>
                </div>

                <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
                        <span className="text-secondary">Confidence</span>
                        <span>{analysis.confidence}%</span>
                    </div>
                    <div style={{ width: '100%', background: 'rgba(255,255,255,0.1)', borderRadius: '10px', height: '6px' }}>
                        <div style={{
                            width: `${analysis.confidence}%`,
                            background: getDecisionColor(analysis.decision),
                            height: '100%',
                            borderRadius: '10px',
                            transition: 'width 1s ease-out'
                        }}></div>
                    </div>
                </div>

                <div style={{ marginTop: '1rem', background: 'rgba(0,0,0,0.2)', padding: '15px', borderRadius: '8px', borderLeft: `3px solid ${getDecisionColor(analysis.decision)}` }}>
                    <p style={{ margin: 0, lineHeight: '1.5', color: 'var(--text-secondary)' }}>
                        "{analysis.reasoning}"
                    </p>
                </div>
            </div>
        </div>
    );
};

export default AIInsights;
