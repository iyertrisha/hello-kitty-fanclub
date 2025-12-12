import React, { useState, useEffect } from 'react';
import apiService from '../services/api';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import './Analytics.css';

const COLORS = ['#3b82f6', '#34d399', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];
const SCORE_COLORS = {
  high: '#34d399',
  medium: '#fbbf24',
  low: '#f87171'
};

const Analytics = () => {
  const [analyticsData, setAnalyticsData] = useState({
    salesTrend: [],
    creditScores: [],
    revenueByCoop: [],
    transactionVolume: [],
  });
  const [dateRange, setDateRange] = useState('month');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, [dateRange]);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      const data = await apiService.getAnalytics({ date_range: dateRange });
      
      const creditScoreRanges = processCreditScores(data.credit_scores || []);
      
      const revenueByCoop = (data.revenue_by_coop || []).map(coop => ({
        ...coop,
        name: coop.coop_name || coop.name || `Coop ${coop.coop_id}`,
      }));
      
      setAnalyticsData({
        salesTrend: data.sales_trend || [],
        creditScores: creditScoreRanges,
        revenueByCoop: revenueByCoop,
        transactionVolume: data.transaction_volume || [],
      });
    } catch (error) {
      console.error('Error loading analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const processCreditScores = (scores) => {
    if (!scores || scores.length === 0) return [];
    
    if (scores[0] && scores[0].range) return scores;
    
    const ranges = {
      '700-900 (Excellent)': 0,
      '500-700 (Good)': 0,
      '300-500 (Needs Attention)': 0,
    };
    
    scores.forEach(item => {
      const score = item.score || 0;
      if (score >= 700) ranges['700-900 (Excellent)']++;
      else if (score >= 500) ranges['500-700 (Good)']++;
      else ranges['300-500 (Needs Attention)']++;
    });
    
    return Object.entries(ranges).map(([range, count]) => ({ range, count }));
  };

  const getScoreBarColor = (range) => {
    if (range.includes('700')) return SCORE_COLORS.high;
    if (range.includes('500')) return SCORE_COLORS.medium;
    return SCORE_COLORS.low;
  };

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-tooltip">
          <p className="tooltip-label">{label}</p>
          {payload.map((entry, index) => (
            <p key={index} className="tooltip-value" style={{ color: entry.color }}>
              {entry.name}: {entry.value.toLocaleString()}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  if (loading) {
    return (
      <div className="analytics-page">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="analytics-page">
      <div className="page-header">
        <div className="header-content">
          <h1 className="page-title">Analytics</h1>
          <p className="page-subtitle">Data-driven insights and platform metrics</p>
        </div>
        <div className="header-controls">
          <select
            className="date-range-selector"
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
          >
            <option value="week">Last Week</option>
            <option value="month">Last Month</option>
            <option value="quarter">Last Quarter</option>
            <option value="year">Last Year</option>
          </select>
          <span className="read-only-badge">
            <span className="badge-icon">🔒</span>
            Read-Only
          </span>
        </div>
      </div>

      <div className="charts-grid">
        {/* Sales Trends Chart */}
        <div className="chart-card full-width">
          <div className="chart-header">
            <h2 className="chart-title">📈 Sales Trends</h2>
            <span className="chart-subtitle">Revenue over time</span>
          </div>
          {analyticsData.salesTrend.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={analyticsData.salesTrend}>
                <defs>
                  <linearGradient id="salesGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis
                  dataKey="date"
                  tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 12 }}
                  tickLine={{ stroke: 'rgba(255,255,255,0.1)' }}
                  axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
                  tickFormatter={(value) => {
                    const date = new Date(value);
                    return `${date.getMonth() + 1}/${date.getDate()}`;
                  }}
                />
                <YAxis
                  tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 12 }}
                  tickLine={{ stroke: 'rgba(255,255,255,0.1)' }}
                  axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
                  tickFormatter={(value) => `₹${value / 1000}K`}
                />
                <Tooltip content={<CustomTooltip />} />
                <Area
                  type="monotone"
                  dataKey="amount"
                  name="Sales"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  fill="url(#salesGradient)"
                />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="no-data">
              <span className="no-data-icon">📊</span>
              <p>No sales data available</p>
            </div>
          )}
        </div>

        {/* Credit Score Distribution */}
        <div className="chart-card">
          <div className="chart-header">
            <h2 className="chart-title">✨ Vishwas Score Distribution</h2>
            <span className="chart-subtitle">Store creditworthiness breakdown</span>
          </div>
          {analyticsData.creditScores.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={analyticsData.creditScores} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis 
                  type="number"
                  tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 12 }}
                  tickLine={{ stroke: 'rgba(255,255,255,0.1)' }}
                  axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
                />
                <YAxis 
                  dataKey="range" 
                  type="category"
                  tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 12 }}
                  tickLine={{ stroke: 'rgba(255,255,255,0.1)' }}
                  axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
                  width={150}
                />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="count" name="Stores" radius={[0, 4, 4, 0]}>
                  {analyticsData.creditScores.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={getScoreBarColor(entry.range)} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="no-data">
              <span className="no-data-icon">✨</span>
              <p>No credit score data available</p>
            </div>
          )}
        </div>

        {/* Revenue by Cooperative */}
        <div className="chart-card">
          <div className="chart-header">
            <h2 className="chart-title">🥧 Revenue by Cooperative</h2>
            <span className="chart-subtitle">Distribution across cooperatives</span>
          </div>
          {analyticsData.revenueByCoop.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={analyticsData.revenueByCoop}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) =>
                    percent > 0.05 ? `${(percent * 100).toFixed(0)}%` : ''
                  }
                  outerRadius={100}
                  innerRadius={60}
                  fill="#8884d8"
                  dataKey="revenue"
                  paddingAngle={2}
                >
                  {analyticsData.revenueByCoop.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip 
                  formatter={(value) => `₹${value.toLocaleString()}`}
                  contentStyle={{
                    background: '#1a1f3c',
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: '8px'
                  }}
                />
                <Legend 
                  formatter={(value) => <span style={{ color: 'rgba(255,255,255,0.7)' }}>{value}</span>}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="no-data">
              <span className="no-data-icon">🥧</span>
              <p>No cooperative revenue data available</p>
            </div>
          )}
        </div>

        {/* Transaction Volume */}
        <div className="chart-card full-width">
          <div className="chart-header">
            <h2 className="chart-title">📊 Transaction Volume</h2>
            <span className="chart-subtitle">Number of transactions over time</span>
          </div>
          {analyticsData.transactionVolume.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={analyticsData.transactionVolume}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis
                  dataKey="date"
                  tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 12 }}
                  tickLine={{ stroke: 'rgba(255,255,255,0.1)' }}
                  axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
                  tickFormatter={(value) => {
                    const date = new Date(value);
                    return `${date.getMonth() + 1}/${date.getDate()}`;
                  }}
                />
                <YAxis
                  tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 12 }}
                  tickLine={{ stroke: 'rgba(255,255,255,0.1)' }}
                  axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
                />
                <Tooltip content={<CustomTooltip />} />
                <Line
                  type="monotone"
                  dataKey="count"
                  name="Transactions"
                  stroke="#34d399"
                  strokeWidth={2}
                  dot={{ fill: '#34d399', strokeWidth: 0 }}
                  activeDot={{ r: 6, fill: '#34d399' }}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="no-data">
              <span className="no-data-icon">📊</span>
              <p>No transaction volume data available</p>
            </div>
          )}
        </div>
      </div>

      {/* Score Legend */}
      <div className="score-legend">
        <h3>Vishwas Score Guide</h3>
        <div className="legend-items">
          <div className="legend-item">
            <span className="legend-color" style={{ background: SCORE_COLORS.high }}></span>
            <span className="legend-label">700-900: Excellent</span>
            <span className="legend-desc">High creditworthiness, reliable partner</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{ background: SCORE_COLORS.medium }}></span>
            <span className="legend-label">500-700: Good</span>
            <span className="legend-desc">Moderate creditworthiness, growing trust</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{ background: SCORE_COLORS.low }}></span>
            <span className="legend-label">300-500: Needs Attention</span>
            <span className="legend-desc">Lower creditworthiness, requires monitoring</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;

