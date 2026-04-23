import { useState } from 'react'
import BurstCalculator from './components/BurstCalculator.jsx'
import TrajectoryPredictor from './components/TrajectoryPredictor.jsx'
import './App.css'

const TABS = ['Burst Calculator', 'Trajectory Predictor']

export default function App() {
  const [activeTab, setActiveTab] = useState(0)

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-inner">
          <span className="logo">🎈</span>
          <h1>Balloon Predictor</h1>
        </div>
      </header>

      <nav className="tab-nav">
        {TABS.map((tab, i) => (
          <button
            key={tab}
            className={`tab-btn${activeTab === i ? ' active' : ''}`}
            onClick={() => setActiveTab(i)}
          >
            {tab}
          </button>
        ))}
      </nav>

      <main className="app-main">
        {activeTab === 0 && <BurstCalculator />}
        {activeTab === 1 && <TrajectoryPredictor />}
      </main>
    </div>
  )
}
