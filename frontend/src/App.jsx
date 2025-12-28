import React from 'react'
import Dashboard from './components/Dashboard'

function App() {
  return (
    <div className="app">
      <nav className="glass">
        <div className="container" style={{ padding: '1rem 2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1>DayTrade<span style={{ color: 'var(--accent)' }}>AI</span></h1>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <span>Status: <span className="text-success">System Online</span></span>
          </div>
        </div>
      </nav>
      <main className="container">
        <Dashboard />
      </main>
    </div>
  )
}

export default App
