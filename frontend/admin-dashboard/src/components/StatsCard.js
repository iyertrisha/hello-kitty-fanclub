import React from 'react';
import './StatsCard.css';

const StatsCard = ({ title, value, icon, trend, onClick }) => {
  const getTrendColor = () => {
    if (!trend) return '#8E8E93';
    return trend > 0 ? '#34C759' : trend < 0 ? '#FF3B30' : '#8E8E93';
  };

  const formatValue = (val) => {
    if (typeof val === 'number') {
      if (val >= 1000000) {
        return `₹${(val / 1000000).toFixed(2)}M`;
      }
      if (val >= 1000) {
        return `₹${(val / 1000).toFixed(2)}K`;
      }
      return `₹${val.toFixed(2)}`;
    }
    return val;
  };

  return (
    <div className="stats-card" onClick={onClick}>
      <div className="stats-card-header">
        <div className="stats-card-icon">{icon}</div>
        {trend !== undefined && (
          <div className="stats-card-trend" style={{ color: getTrendColor() }}>
            {trend > 0 ? '↑' : trend < 0 ? '↓' : '→'} {Math.abs(trend)}%
          </div>
        )}
      </div>
      <div className="stats-card-content">
        <div className="stats-card-value">{formatValue(value)}</div>
        <div className="stats-card-title">{title}</div>
      </div>
    </div>
  );
};

export default StatsCard;

