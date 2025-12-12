import React from 'react';
import { NavLink, Outlet, Link } from 'react-router-dom';
import './PlatformAdminLayout.css';

const PlatformAdminLayout = () => {
  return (
    <div className="platform-admin-layout">
      <nav className="sidebar platform-sidebar">
        <div className="sidebar-header">
          <Link to="/" className="logo-link">
            <span className="logo-icon">🏪</span>
            <span className="logo-text">KiranaChain</span>
          </Link>
          <div className="dashboard-badge platform-badge">
            <span className="badge-icon">🛡️</span>
            <span className="badge-text">Platform Admin</span>
          </div>
        </div>
        
        <div className="sidebar-nav">
          <div className="nav-section">
            <span className="nav-section-title">Monitoring</span>
            <ul className="nav-menu">
              <li>
                <NavLink to="/platform-admin" end className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                  <span className="nav-icon">📊</span>
                  <span className="nav-text">Overview</span>
                  <span className="nav-subtitle">Platform health + Credit Scores</span>
                </NavLink>
              </li>
              <li>
                <NavLink to="/platform-admin/stores" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                  <span className="nav-icon">🏪</span>
                  <span className="nav-text">Stores</span>
                  <span className="nav-subtitle">View stores + Flag issues</span>
                </NavLink>
              </li>
            </ul>
          </div>
          
          <div className="nav-section">
            <span className="nav-section-title">Transparency</span>
            <ul className="nav-menu">
              <li>
                <NavLink to="/platform-admin/blockchain" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                  <span className="nav-icon">⛓️</span>
                  <span className="nav-text">Blockchain Logs</span>
                  <span className="nav-subtitle">All transactions (read-only)</span>
                </NavLink>
              </li>
              <li>
                <NavLink to="/platform-admin/analytics" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                  <span className="nav-icon">📈</span>
                  <span className="nav-text">Analytics</span>
                  <span className="nav-subtitle">Platform insights + Scores</span>
                </NavLink>
              </li>
            </ul>
          </div>
        </div>
        
        <div className="sidebar-footer">
          <div className="access-info">
            <span className="access-icon">🔒</span>
            <div className="access-text">
              <span className="access-level">Read-Only Access</span>
              <span className="access-desc">View all, modify none</span>
            </div>
          </div>
          <Link to="/" className="switch-dashboard-btn">
            ← Switch Dashboard
          </Link>
        </div>
      </nav>
      
      <main className="main-content platform-main">
        <Outlet />
      </main>
    </div>
  );
};

export default PlatformAdminLayout;

