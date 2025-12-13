import React from 'react';
import './StatsCard.css';

const StatsCard = ({ title, value, subtitle, icon, trend, onClick }) => {
  return (
    <div className={`stats-card ${onClick ? 'clickable' : ''}`} onClick={onClick}>
      <div className="stats-card-content">
        <div className="stats-card-header">
          <h3 className="stats-card-title">{title}</h3>
          {icon && <div className="stats-card-icon">{icon}</div>}
        </div>
        <div className="stats-card-value">{value}</div>
        {subtitle && <div className="stats-card-subtitle">{subtitle}</div>}
        {trend && (
          <div className={`stats-card-trend ${trend.direction}`}>
            {trend.direction === 'up' ? '↑' : '↓'} {trend.value}
          </div>
        )}
      </div>
    </div>
  );
};

export default StatsCard;

