import React from 'react';
import {
  AreaChart,
  Area,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import './SalesChart.css';

const SalesChart = ({ data, type = 'area', title, variant = 'platform' }) => {
  const accentColor = variant === 'aggregator' ? '#10b981' : '#3b82f6';
  const gradientId = `salesGradient-${variant}`;

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="sales-chart-tooltip">
          <p className="tooltip-date">
            {new Date(label).toLocaleDateString('en-IN', {
              day: 'numeric',
              month: 'short',
              year: 'numeric'
            })}
          </p>
          <p className="tooltip-value" style={{ color: accentColor }}>
            ₹{payload[0].value.toLocaleString()}
          </p>
        </div>
      );
    }
    return null;
  };

  const formatYAxis = (value) => {
    if (value >= 100000) {
      return `₹${(value / 100000).toFixed(1)}L`;
    }
    if (value >= 1000) {
      return `₹${(value / 1000).toFixed(0)}K`;
    }
    return `₹${value}`;
  };

  const formatXAxis = (value) => {
    const date = new Date(value);
    return `${date.getDate()}/${date.getMonth() + 1}`;
  };

  if (!data || data.length === 0) {
    return (
      <div className={`sales-chart-container ${variant}`}>
        {title && <h3 className="chart-title">{title}</h3>}
        <div className="no-data">
          <span className="no-data-icon">📊</span>
          <p>No data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`sales-chart-container ${variant}`}>
      {title && <h3 className="chart-title">{title}</h3>}
      <ResponsiveContainer width="100%" height={280}>
        {type === 'area' ? (
          <AreaChart data={data}>
            <defs>
              <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={accentColor} stopOpacity={0.3} />
                <stop offset="95%" stopColor={accentColor} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid 
              strokeDasharray="3 3" 
              stroke="rgba(255,255,255,0.06)" 
              vertical={false}
            />
            <XAxis
              dataKey="date"
              tick={{ fill: 'rgba(255,255,255,0.4)', fontSize: 11 }}
              tickLine={{ stroke: 'rgba(255,255,255,0.1)' }}
              axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
              tickFormatter={formatXAxis}
            />
            <YAxis
              tick={{ fill: 'rgba(255,255,255,0.4)', fontSize: 11 }}
              tickLine={{ stroke: 'rgba(255,255,255,0.1)' }}
              axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
              tickFormatter={formatYAxis}
              width={65}
            />
            <Tooltip content={<CustomTooltip />} />
            <Area
              type="monotone"
              dataKey="amount"
              stroke={accentColor}
              strokeWidth={2}
              fill={`url(#${gradientId})`}
            />
          </AreaChart>
        ) : (
          <LineChart data={data}>
            <CartesianGrid 
              strokeDasharray="3 3" 
              stroke="rgba(255,255,255,0.06)" 
              vertical={false}
            />
            <XAxis
              dataKey="date"
              tick={{ fill: 'rgba(255,255,255,0.4)', fontSize: 11 }}
              tickLine={{ stroke: 'rgba(255,255,255,0.1)' }}
              axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
              tickFormatter={formatXAxis}
            />
            <YAxis
              tick={{ fill: 'rgba(255,255,255,0.4)', fontSize: 11 }}
              tickLine={{ stroke: 'rgba(255,255,255,0.1)' }}
              axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
              tickFormatter={formatYAxis}
              width={65}
            />
            <Tooltip content={<CustomTooltip />} />
            <Line
              type="monotone"
              dataKey="amount"
              stroke={accentColor}
              strokeWidth={2}
              dot={{ fill: accentColor, strokeWidth: 0, r: 3 }}
              activeDot={{ r: 5, fill: accentColor }}
            />
          </LineChart>
        )}
      </ResponsiveContainer>
    </div>
  );
};

export default SalesChart;
