import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import './AggregatorLayout.css';

const AggregatorLayout = () => {
  return (
    <div className="aggregator-layout">
      <nav className="sidebar aggregator-sidebar">
        <div className="sidebar-header">
          <div className="logo-link">
            <span className="logo-icon">🏪</span>
            <span className="logo-text">KiranaChain</span>
          </div>
          <div className="dashboard-badge aggregator-badge">
            <span className="badge-icon">🤝</span>
            <span className="badge-text">Cooperative Dashboard</span>
          </div>
        </div>
        
        <div className="sidebar-nav">
          <div className="nav-section">
            <span className="nav-section-title">Cooperative</span>
            <ul className="nav-menu">
              <li>
                <NavLink to="/" end className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                  <span className="nav-icon">📊</span>
                  <span className="nav-text">Cooperative Overview</span>
                  <span className="nav-subtitle">Health + Member Credit Scores</span>
                </NavLink>
              </li>
              <li>
                <NavLink to="/map" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                  <span className="nav-icon">🗺️</span>
                  <span className="nav-text">Geographic Map</span>
                  <span className="nav-subtitle">Service area + Members</span>
                </NavLink>
              </li>
            </ul>
          </div>
          
          <div className="nav-section">
            <span className="nav-section-title">Operations</span>
            <ul className="nav-menu">
              <li>
                <NavLink to="/orders" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                  <span className="nav-icon">📦</span>
                  <span className="nav-text">Cooperative Orders</span>
                  <span className="nav-subtitle">Management + Fulfillment</span>
                </NavLink>
              </li>
              <li>
                <NavLink to="/blockchain" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                  <span className="nav-icon">⛓️</span>
                  <span className="nav-text">Blockchain Logs</span>
                  <span className="nav-subtitle">Cooperative transactions</span>
                </NavLink>
              </li>
            </ul>
          </div>
        </div>
        
        <div className="sidebar-footer">
          <div className="coop-info">
            <span className="coop-icon">🏢</span>
            <div className="coop-text">
              <span className="coop-name">Delhi Kirana Network</span>
              <span className="coop-members">42 Active Members</span>
            </div>
          </div>
        </div>
      </nav>
      
      <main className="main-content aggregator-main">
        <Outlet />
      </main>
    </div>
  );
};

export default AggregatorLayout;

