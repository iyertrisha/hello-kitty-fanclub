import React from 'react';
import './CreditScoreWidget.css';

const CreditScoreWidget = ({ 
  title = 'Credit Score Summary',
  averageScore = 0, 
  distribution = { high: 0, medium: 0, low: 0 },
  totalCount = 0,
  variant = 'platform' // 'platform' or 'aggregator'
}) => {
  const getScoreColor = (score) => {
    if (score >= 700) return '#34d399';
    if (score >= 500) return '#fbbf24';
    return '#f87171';
  };

  const getScoreLabel = (score) => {
    if (score >= 700) return 'Excellent';
    if (score >= 500) return 'Good';
    return 'Needs Attention';
  };

  const total = distribution.high + distribution.medium + distribution.low;
  const highPercent = total > 0 ? (distribution.high / total) * 100 : 0;
  const mediumPercent = total > 0 ? (distribution.medium / total) * 100 : 0;
  const lowPercent = total > 0 ? (distribution.low / total) * 100 : 0;

  return (
    <div className={`credit-score-widget ${variant}`}>
      <div className="widget-header">
        <h2 className="widget-title">✨ {title}</h2>
        <span className="widget-badge">Vishwas Score</span>
      </div>

      <div className="widget-content">
        {/* Average Score Circle */}
        <div className="score-circle-section">
          <div 
            className="score-circle"
            style={{ 
              borderColor: getScoreColor(averageScore),
              boxShadow: `0 0 30px ${getScoreColor(averageScore)}30`
            }}
          >
            <span 
              className="score-value"
              style={{ color: getScoreColor(averageScore) }}
            >
              {averageScore}
            </span>
            <span className="score-max">/900</span>
          </div>
          <div className="score-info">
            <span 
              className="score-status"
              style={{ color: getScoreColor(averageScore) }}
            >
              {getScoreLabel(averageScore)}
            </span>
            <span className="score-desc">Platform Average</span>
          </div>
        </div>

        {/* Distribution Bar */}
        <div className="distribution-section">
          <div className="distribution-header">
            <span className="distribution-title">Score Distribution</span>
            <span className="distribution-total">{totalCount} stores</span>
          </div>
          
          <div className="distribution-bar">
            <div 
              className="bar-segment high"
              style={{ width: `${highPercent}%` }}
              title={`Excellent: ${distribution.high}`}
            />
            <div 
              className="bar-segment medium"
              style={{ width: `${mediumPercent}%` }}
              title={`Good: ${distribution.medium}`}
            />
            <div 
              className="bar-segment low"
              style={{ width: `${lowPercent}%` }}
              title={`Needs Attention: ${distribution.low}`}
            />
          </div>

          <div className="distribution-legend">
            <div className="legend-item">
              <span className="legend-dot high"></span>
              <span className="legend-label">700-900</span>
              <span className="legend-value">{distribution.high}</span>
              <span className="legend-percent">({highPercent.toFixed(0)}%)</span>
            </div>
            <div className="legend-item">
              <span className="legend-dot medium"></span>
              <span className="legend-label">500-700</span>
              <span className="legend-value">{distribution.medium}</span>
              <span className="legend-percent">({mediumPercent.toFixed(0)}%)</span>
            </div>
            <div className="legend-item">
              <span className="legend-dot low"></span>
              <span className="legend-label">300-500</span>
              <span className="legend-value">{distribution.low}</span>
              <span className="legend-percent">({lowPercent.toFixed(0)}%)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="quick-stats">
        <div className="quick-stat">
          <span className="quick-stat-value high">{distribution.high}</span>
          <span className="quick-stat-label">High Performers</span>
        </div>
        <div className="quick-stat">
          <span className="quick-stat-value medium">{distribution.medium}</span>
          <span className="quick-stat-label">Good Standing</span>
        </div>
        <div className="quick-stat">
          <span className="quick-stat-value low">{distribution.low}</span>
          <span className="quick-stat-label">Needs Attention</span>
        </div>
      </div>
    </div>
  );
};

export default CreditScoreWidget;

