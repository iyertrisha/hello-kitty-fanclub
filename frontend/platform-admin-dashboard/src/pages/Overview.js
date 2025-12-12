import React, { useState, useEffect } from 'react';
import apiService from '../../services/api';
import StatsCard from '../../components/StatsCard';
import CreditScoreWidget from '../../components/CreditScoreWidget';
import SalesChart from '../../components/SalesChart';
import './Overview.css';

const Overview = () => {
  const [stats, setStats] = useState({
    totalStores: 0,
    totalTransactions: { today: 0, week: 0, month: 0 },
    totalRevenue: { today: 0, week: 0, month: 0 },
    activeCooperatives: 0,
  });
  const [creditScoreStats, setCreditScoreStats] = useState({
    average: 0,
    distribution: { high: 0, medium: 0, low: 0 },
    totalStores: 0
  });
  const [recentActivity, setRecentActivity] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [salesTrend, setSalesTrend] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadOverviewData();
  }, []);

  const loadOverviewData = async () => {
    try {
      setLoading(true);
      const data = await apiService.getOverviewStats();
      
      setStats({
        totalStores: data.total_stores || 0,
        totalTransactions: {
          today: data.transactions?.today || 0,
          week: data.transactions?.week || 0,
          month: data.transactions?.month || 0,
        },
        totalRevenue: {
          today: data.revenue?.today || 0,
          week: data.revenue?.week || 0,
          month: data.revenue?.month || 0,
        },
        activeCooperatives: data.active_cooperatives || 0,
      });

      // Credit Score Stats
      if (data.credit_score_stats) {
        setCreditScoreStats(data.credit_score_stats);
      } else {
        // Calculate from stores if not provided
        const stores = data.stores || [];
        const scores = stores.map(s => s.credit_score || 0).filter(s => s > 0);
        const avg = scores.length > 0 ? scores.reduce((a, b) => a + b, 0) / scores.length : 0;
        setCreditScoreStats({
          average: Math.round(avg),
          distribution: {
            high: scores.filter(s => s >= 700).length,
            medium: scores.filter(s => s >= 500 && s < 700).length,
            low: scores.filter(s => s < 500).length
          },
          totalStores: stores.length
        });
      }

      setRecentActivity(data.recent_activity || []);
      setSalesTrend(data.sales_trend || []);
      
      // Generate alerts based on data
      const generatedAlerts = [];
      if (data.flagged_stores_count > 0) {
        generatedAlerts.push({
          type: 'warning',
          message: `${data.flagged_stores_count} stores flagged for review`,
          time: new Date().toISOString()
        });
      }
      if (data.pending_transactions > 0) {
        generatedAlerts.push({
          type: 'info',
          message: `${data.pending_transactions} transactions pending blockchain verification`,
          time: new Date().toISOString()
        });
      }
      setAlerts(data.alerts || generatedAlerts);
      
    } catch (error) {
      console.error('Error loading overview data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="platform-overview">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading platform data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="platform-overview">
      <div className="page-header">
        <div className="header-content">
          <h1 className="page-title">Platform Overview</h1>
          <p className="page-subtitle">Monitor platform health and performance</p>
        </div>
        <div className="header-badge">
          <span className="read-only-badge">
            <span className="badge-icon">🔒</span>
            Read-Only
          </span>
        </div>
      </div>

      {/* Alerts Section */}
      {alerts.length > 0 && (
        <div className="alerts-section">
          {alerts.map((alert, index) => (
            <div key={index} className={`alert-item alert-${alert.type}`}>
              <span className="alert-icon">
                {alert.type === 'warning' ? '⚠️' : alert.type === 'error' ? '🚨' : 'ℹ️'}
              </span>
              <span className="alert-message">{alert.message}</span>
            </div>
          ))}
        </div>
      )}

      {/* Stats Cards */}
      <div className="stats-grid">
        <StatsCard
          title="Total Stores"
          value={stats.totalStores}
          icon="🏪"
          variant="platform"
        />
        <StatsCard
          title="Today's Transactions"
          value={stats.totalTransactions.today}
          icon="📊"
          variant="platform"
        />
        <StatsCard
          title="Today's Revenue"
          value={stats.totalRevenue.today}
          icon="💰"
          variant="platform"
          isCurrency={true}
        />
        <StatsCard
          title="Active Cooperatives"
          value={stats.activeCooperatives}
          icon="👥"
          variant="platform"
        />
      </div>

      {/* Credit Score Summary Widget */}
      <CreditScoreWidget
        title="Platform Credit Score Summary"
        averageScore={creditScoreStats.average}
        distribution={creditScoreStats.distribution}
        totalCount={creditScoreStats.totalStores}
        variant="platform"
      />

      {/* Sales Chart */}
      {salesTrend.length > 0 && (
        <div className="chart-section">
          <div className="section-header">
            <h2 className="section-title">Sales Trend (Last 30 Days)</h2>
            <span className="read-only-indicator">View Only</span>
          </div>
          <SalesChart data={salesTrend} type="area" variant="platform" />
        </div>
      )}

      {/* Recent Activity */}
      <div className="activity-section">
        <div className="section-header">
          <h2 className="section-title">Recent Activity</h2>
          <span className="activity-count">{recentActivity.length} events</span>
        </div>
        <div className="activity-list">
          {recentActivity.length > 0 ? (
            recentActivity.map((activity, index) => (
              <div key={index} className="activity-item">
                <div className="activity-icon">
                  {activity.type === 'transaction' ? '💳' : 
                   activity.type === 'cooperative' ? '👥' : 
                   activity.type === 'store' ? '🏪' : '📋'}
                </div>
                <div className="activity-content">
                  <p className="activity-text">{activity.message}</p>
                  <span className="activity-time">
                    {new Date(activity.timestamp).toLocaleString()}
                  </span>
                </div>
              </div>
            ))
          ) : (
            <div className="empty-state">
              <span className="empty-icon">📭</span>
              <p>No recent activity</p>
            </div>
          )}
        </div>
      </div>

      {/* Platform Health Indicators */}
      <div className="health-section">
        <div className="section-header">
          <h2 className="section-title">Platform Health</h2>
        </div>
        <div className="health-grid">
          <div className="health-card">
            <div className="health-indicator healthy"></div>
            <span className="health-label">API Services</span>
            <span className="health-status">Operational</span>
          </div>
          <div className="health-card">
            <div className="health-indicator healthy"></div>
            <span className="health-label">Blockchain Node</span>
            <span className="health-status">Connected</span>
          </div>
          <div className="health-card">
            <div className="health-indicator healthy"></div>
            <span className="health-label">Database</span>
            <span className="health-status">Healthy</span>
          </div>
          <div className="health-card">
            <div className="health-indicator healthy"></div>
            <span className="health-label">ML Services</span>
            <span className="health-status">Running</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Overview;

