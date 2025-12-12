import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Overview from './pages/Overview';
import StoreManagement from './pages/StoreManagement';
import Cooperatives from './pages/Cooperatives';
import Analytics from './pages/Analytics';
import BlockchainLogs from './pages/BlockchainLogs';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="sidebar">
          <div className="sidebar-header">
            <h2 className="sidebar-title">Admin Dashboard</h2>
          </div>
          <ul className="sidebar-menu">
            <li>
              <Link to="/" className="sidebar-link">
                📊 Overview
              </Link>
            </li>
            <li>
              <Link to="/stores" className="sidebar-link">
                🏪 Stores
              </Link>
            </li>
            <li>
              <Link to="/cooperatives" className="sidebar-link">
                👥 Cooperatives
              </Link>
            </li>
            <li>
              <Link to="/analytics" className="sidebar-link">
                📈 Analytics
              </Link>
            </li>
            <li>
              <Link to="/blockchain" className="sidebar-link">
                ⛓️ Blockchain Logs
              </Link>
            </li>
          </ul>
        </nav>
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Overview />} />
            <Route path="/stores" element={<StoreManagement />} />
            <Route path="/cooperatives" element={<Cooperatives />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/blockchain" element={<BlockchainLogs />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;

