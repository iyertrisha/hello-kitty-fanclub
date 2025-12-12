import React, { useState, useEffect } from 'react';
import apiService from '../services/api';
import StatsCard from '../components/StatsCard';
import SalesChart from '../components/SalesChart';
import './Overview.css';

const Overview = () => {
  const [stats, setStats] = useState({
    totalStores: 0,
    totalTransactions: { today: 0, week: 0, month: 0 },
    totalRevenue: { today: 0, week: 0, month: 0 },
    activeCooperatives: 0,
  });
  const [recentActivity, setRecentActivity] = useState([]);
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

      setRecentActivity(data.recent_activity || []);
      setSalesTrend(data.sales_trend || []);
    } catch (error) {
      console.error('Error loading overview data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="overview-container">
        <div className="loading-message">Loading overview data...</div>
      </div>
    );
  }

  return (
    <div className="overview-container">
      <h1 className="page-title">Overview</h1>

      {/* Stats Cards */}
      <div className="stats-grid">
        <StatsCard
          title="Total Stores"
          value={stats.totalStores}
          icon="🏪"
        />
        <StatsCard
          title="Today's Transactions"
          value={stats.totalTransactions.today}
          icon="📊"
        />
        <StatsCard
          title="Today's Revenue"
          value={stats.totalRevenue.today}
          icon="💰"
        />
        <StatsCard
          title="Active Cooperatives"
          value={stats.activeCooperatives}
          icon="👥"
        />
      </div>

      {/* Sales Chart */}
      {salesTrend.length > 0 && (
        <SalesChart data={salesTrend} type="area" title="Sales Trend (Last 30 Days)" />
      )}

      {/* Recent Activity */}
      <div className="recent-activity-section">
        <h2 className="section-title">Recent Activity</h2>
        <div className="activity-list">
          {recentActivity.length > 0 ? (
            recentActivity.map((activity, index) => (
              <div key={index} className="activity-item">
                <div className="activity-icon">{activity.type === 'transaction' ? '💳' : activity.type === 'cooperative' ? '👥' : '🏪'}</div>
                <div className="activity-content">
                  <p className="activity-text">{activity.message}</p>
                  <span className="activity-time">
                    {new Date(activity.timestamp).toLocaleString()}
                  </span>
                </div>
              </div>
            ))
          ) : (
            <p className="empty-message">No recent activity</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Overview;

