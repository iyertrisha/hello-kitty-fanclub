import React from 'react';
import './StatsCard.css';

const StatsCard = ({ 
  title, 
  value, 
  icon, 
  trend, 
  onClick, 
  variant = 'default', // 'default', 'platform', 'aggregator'
  isCurrency = false 
}) => {
  const getTrendColor = () => {
    if (!trend) return 'rgba(255,255,255,0.5)';
    return trend > 0 ? '#34d399' : trend < 0 ? '#f87171' : 'rgba(255,255,255,0.5)';
  };

  const formatValue = (val) => {
    if (typeof val === 'number') {
      if (isCurrency) {
        if (val >= 10000000) {
          return `₹${(val / 10000000).toFixed(2)}Cr`;
        }
        if (val >= 100000) {
          return `₹${(val / 100000).toFixed(2)}L`;
        }
        if (val >= 1000) {
          return `₹${(val / 1000).toFixed(1)}K`;
        }
        return `₹${val.toLocaleString()}`;
      }
      if (val >= 1000000) {
        return `${(val / 1000000).toFixed(2)}M`;
      }
      if (val >= 1000) {
        return `${(val / 1000).toFixed(1)}K`;
      }
      return val.toLocaleString();
    }
    return val;
  };

  return (
    <div className={`stats-card ${variant}`} onClick={onClick}>
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
