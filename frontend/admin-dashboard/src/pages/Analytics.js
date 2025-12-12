import React, { useState, useEffect } from 'react';
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
import apiService from '../services/api';
import './Analytics.css';

const COLORS = ['#007AFF', '#34C759', '#FF9500', '#FF3B30', '#AF52DE', '#FF2D55'];

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
      
      setAnalyticsData({
        salesTrend: data.sales_trend || [],
        creditScores: data.credit_scores || [],
        revenueByCoop: data.revenue_by_coop || [],
        transactionVolume: data.transaction_volume || [],
      });
    } catch (error) {
      console.error('Error loading analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="analytics-container">
        <div className="loading-message">Loading analytics...</div>
      </div>
    );
  }

  return (
    <div className="analytics-container">
      <div className="page-header">
        <h1 className="page-title">Analytics</h1>
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
      </div>

      {/* Sales Trends Chart */}
      {analyticsData.salesTrend.length > 0 && (
        <div className="chart-section">
          <h2 className="chart-section-title">Sales Trends</h2>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={analyticsData.salesTrend}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 12 }}
                tickFormatter={(value) => {
                  const date = new Date(value);
                  return `${date.getMonth() + 1}/${date.getDate()}`;
                }}
              />
              <YAxis
                tick={{ fontSize: 12 }}
                tickFormatter={(value) => `₹${value / 1000}K`}
              />
              <Tooltip
                formatter={(value) => [`₹${value.toFixed(2)}`, 'Sales']}
                labelFormatter={(label) => {
                  const date = new Date(label);
                  return date.toLocaleDateString();
                }}
              />
              <Legend />
              <Area
                type="monotone"
                dataKey="amount"
                stroke="#007AFF"
                fill="#007AFF"
                fillOpacity={0.3}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Credit Score Distribution */}
      {analyticsData.creditScores.length > 0 && (
        <div className="chart-section">
          <h2 className="chart-section-title">Credit Score Distribution</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={analyticsData.creditScores}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="range" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" fill="#007AFF" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Revenue by Cooperative */}
      {analyticsData.revenueByCoop.length > 0 && (
        <div className="chart-section">
          <h2 className="chart-section-title">Revenue by Cooperative</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={analyticsData.revenueByCoop}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) =>
                  `${name}: ${(percent * 100).toFixed(0)}%`
                }
                outerRadius={80}
                fill="#8884d8"
                dataKey="revenue"
              >
                {analyticsData.revenueByCoop.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={COLORS[index % COLORS.length]}
                  />
                ))}
              </Pie>
              <Tooltip formatter={(value) => `₹${value.toFixed(2)}`} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Transaction Volume */}
      {analyticsData.transactionVolume.length > 0 && (
        <div className="chart-section">
          <h2 className="chart-section-title">Transaction Volume Over Time</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={analyticsData.transactionVolume}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 12 }}
                tickFormatter={(value) => {
                  const date = new Date(value);
                  return `${date.getMonth() + 1}/${date.getDate()}`;
                }}
              />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip
                formatter={(value) => [value, 'Transactions']}
                labelFormatter={(label) => {
                  const date = new Date(label);
                  return date.toLocaleDateString();
                }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="count"
                stroke="#34C759"
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};

export default Analytics;

