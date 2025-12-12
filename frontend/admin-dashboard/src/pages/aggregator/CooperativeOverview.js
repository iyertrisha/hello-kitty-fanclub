import React, { useState, useEffect } from 'react';
import apiService from '../../services/api';
import StatsCard from '../../components/StatsCard';
import CreditScoreWidget from '../../components/CreditScoreWidget';
import './CooperativeOverview.css';

const CooperativeOverview = () => {
  const [coopData, setCoopData] = useState({
    name: 'Delhi Kirana Network',
    memberCount: 0,
    revenue: { today: 0, week: 0, month: 0 },
    activeOrders: 0,
    recentActivity: [],
  });
  const [memberScoreStats, setMemberScoreStats] = useState({
    average: 0,
    distribution: { high: 0, medium: 0, low: 0 },
    totalMembers: 0,
    topPerformers: [],
    needsAttention: []
  });
  const [metrics, setMetrics] = useState({
    salesGrowth: 0,
    orderVolume: 0,
    avgOrderValue: 0,
  });
  const [loading, setLoading] = useState(true);

  // Mock cooperative ID - in real app, this would come from auth context
  const cooperativeId = 'coop-001';

  useEffect(() => {
    loadCooperativeData();
  }, []);

  const loadCooperativeData = async () => {
    try {
      setLoading(true);
      
      // Load cooperative overview
      const overview = await apiService.getCooperativeOverview(cooperativeId);
      
      setCoopData({
        name: overview.name || 'Delhi Kirana Network',
        memberCount: overview.member_count || 42,
        revenue: {
          today: overview.revenue?.today || 0,
          week: overview.revenue?.week || 0,
          month: overview.revenue?.month || 0,
        },
        activeOrders: overview.active_orders || 0,
        recentActivity: overview.recent_activity || [],
      });

      // Load member credit scores
      const memberScores = await apiService.getCooperativeMemberScores(cooperativeId);
      const scores = memberScores.scores || memberScores.members || [];
      
      const scoreValues = scores.map(m => m.credit_score || m.score || 0).filter(s => s > 0);
      const avgScore = scoreValues.length > 0 
        ? Math.round(scoreValues.reduce((a, b) => a + b, 0) / scoreValues.length)
        : 0;

      setMemberScoreStats({
        average: avgScore,
        distribution: {
          high: scores.filter(m => (m.credit_score || m.score || 0) >= 700).length,
          medium: scores.filter(m => (m.credit_score || m.score || 0) >= 500 && (m.credit_score || m.score || 0) < 700).length,
          low: scores.filter(m => (m.credit_score || m.score || 0) < 500).length
        },
        totalMembers: scores.length,
        topPerformers: scores
          .filter(m => (m.credit_score || m.score || 0) >= 700)
          .slice(0, 5),
        needsAttention: scores
          .filter(m => (m.credit_score || m.score || 0) < 500)
          .slice(0, 5)
      });

      // Set metrics
      setMetrics({
        salesGrowth: overview.sales_growth || 23,
        orderVolume: overview.order_volume || 156,
        avgOrderValue: overview.avg_order_value || 450,
      });

    } catch (error) {
      console.error('Error loading cooperative data:', error);
      // Set mock data for demonstration
      setCoopData({
        name: 'Delhi Kirana Network',
        memberCount: 42,
        revenue: { today: 45000, week: 312000, month: 1250000 },
        activeOrders: 23,
        recentActivity: [
          { type: 'order', message: 'New order #1234 received', timestamp: new Date().toISOString() },
          { type: 'member', message: 'Sharma Store joined cooperative', timestamp: new Date().toISOString() },
        ],
      });
      setMemberScoreStats({
        average: 685,
        distribution: { high: 18, medium: 16, low: 8 },
        totalMembers: 42,
        topPerformers: [
          { name: 'Krishna Store', credit_score: 845 },
          { name: 'Gupta Provisions', credit_score: 820 },
        ],
        needsAttention: [
          { name: 'New Mart', credit_score: 420 },
        ]
      });
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 700) return '#34d399';
    if (score >= 500) return '#fbbf24';
    return '#f87171';
  };

  if (loading) {
    return (
      <div className="cooperative-overview">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading cooperative data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="cooperative-overview">
      <div className="page-header">
        <div className="header-content">
          <h1 className="page-title">Cooperative Overview</h1>
          <p className="page-subtitle">{coopData.name}</p>
        </div>
        <div className="header-badge">
          <span className="coop-badge">
            <span className="badge-icon">🤝</span>
            {coopData.memberCount} Members
          </span>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <StatsCard
          title="Member Stores"
          value={coopData.memberCount}
          icon="🏪"
          variant="aggregator"
        />
        <StatsCard
          title="Today's Revenue"
          value={coopData.revenue.today}
          icon="💰"
          variant="aggregator"
          isCurrency={true}
        />
        <StatsCard
          title="Active Orders"
          value={coopData.activeOrders}
          icon="📦"
          variant="aggregator"
        />
        <StatsCard
          title="Monthly Revenue"
          value={coopData.revenue.month}
          icon="📈"
          variant="aggregator"
          isCurrency={true}
        />
      </div>

      {/* Member Credit Score Summary Widget */}
      <CreditScoreWidget
        title="Member Vishwas Score Summary"
        averageScore={memberScoreStats.average}
        distribution={memberScoreStats.distribution}
        totalCount={memberScoreStats.totalMembers}
        variant="aggregator"
      />

      {/* Performance Metrics */}
      <div className="metrics-section">
        <h2 className="section-title">Performance Metrics</h2>
        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-icon">📈</div>
            <div className="metric-content">
              <span className="metric-value positive">+{metrics.salesGrowth}%</span>
              <span className="metric-label">Sales Growth (30d)</span>
            </div>
          </div>
          <div className="metric-card">
            <div className="metric-icon">📦</div>
            <div className="metric-content">
              <span className="metric-value">{metrics.orderVolume}</span>
              <span className="metric-label">Orders This Week</span>
            </div>
          </div>
          <div className="metric-card">
            <div className="metric-icon">💵</div>
            <div className="metric-content">
              <span className="metric-value">₹{metrics.avgOrderValue}</span>
              <span className="metric-label">Avg Order Value</span>
            </div>
          </div>
        </div>
      </div>

      <div className="two-column-section">
        {/* Top Performers */}
        <div className="performers-section">
          <h2 className="section-title">🏆 Top Performers (700+ Score)</h2>
          <div className="performers-list">
            {memberScoreStats.topPerformers.length > 0 ? (
              memberScoreStats.topPerformers.map((member, index) => (
                <div key={index} className="performer-item">
                  <div className="performer-rank">{index + 1}</div>
                  <div className="performer-info">
                    <span className="performer-name">{member.name}</span>
                  </div>
                  <span 
                    className="performer-score"
                    style={{ color: getScoreColor(member.credit_score || member.score) }}
                  >
                    {member.credit_score || member.score}
                  </span>
                </div>
              ))
            ) : (
              <div className="empty-performers">
                <p>No top performers yet</p>
              </div>
            )}
          </div>
        </div>

        {/* Needs Attention */}
        <div className="attention-section">
          <h2 className="section-title">⚠️ Needs Attention (Below 500)</h2>
          <div className="attention-list">
            {memberScoreStats.needsAttention.length > 0 ? (
              memberScoreStats.needsAttention.map((member, index) => (
                <div key={index} className="attention-item">
                  <div className="attention-icon">⚠️</div>
                  <div className="attention-info">
                    <span className="attention-name">{member.name}</span>
                  </div>
                  <span 
                    className="attention-score"
                    style={{ color: getScoreColor(member.credit_score || member.score) }}
                  >
                    {member.credit_score || member.score}
                  </span>
                </div>
              ))
            ) : (
              <div className="empty-attention">
                <span className="success-icon">✅</span>
                <p>All members in good standing!</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="activity-section">
        <h2 className="section-title">Recent Activity</h2>
        <div className="activity-list">
          {coopData.recentActivity.length > 0 ? (
            coopData.recentActivity.map((activity, index) => (
              <div key={index} className="activity-item">
                <div className="activity-icon">
                  {activity.type === 'order' ? '📦' : 
                   activity.type === 'member' ? '👤' : 
                   activity.type === 'transaction' ? '💳' : '📋'}
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

      {/* Quick Actions */}
      <div className="quick-actions">
        <h2 className="section-title">Quick Actions</h2>
        <div className="actions-grid">
          <button className="action-card" onClick={() => window.location.href = '/orders'}>
            <span className="action-icon">📦</span>
            <span className="action-text">View Orders</span>
          </button>
          <button className="action-card" onClick={() => window.location.href = '/map'}>
            <span className="action-icon">🗺️</span>
            <span className="action-text">Geographic Map</span>
          </button>
          <button className="action-card" onClick={() => window.location.href = '/blockchain'}>
            <span className="action-icon">⛓️</span>
            <span className="action-text">Blockchain Logs</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default CooperativeOverview;

