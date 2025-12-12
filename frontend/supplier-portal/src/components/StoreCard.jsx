import React from 'react';
import './StoreCard.css';

const StoreCard = ({ store, onOrderClick }) => {
  const getScoreColor = (score) => {
    if (score >= 700) return '#34d399';
    if (score >= 500) return '#fbbf24';
    return '#f87171';
  };

  const getScoreLabel = (score) => {
    if (score >= 700) return 'Excellent';
    if (score >= 500) return 'Good';
    return 'Fair';
  };

  return (
    <div className="store-card">
      <div className="store-header">
        <h3>{store.name}</h3>
        <div className="credit-score" style={{ color: getScoreColor(store.credit_score) }}>
          <span className="score-value">{store.credit_score}</span>
          <span className="score-label">{getScoreLabel(store.credit_score)}</span>
        </div>
      </div>

      <div className="store-info">
        <div className="info-item">
          <span className="info-label">📍</span>
          <span>{store.address}</span>
        </div>
        <div className="info-item">
          <span className="info-label">📞</span>
          <span>{store.phone}</span>
        </div>
        {store.distance_km && (
          <div className="info-item">
            <span className="info-label">📏</span>
            <span>{store.distance_km} km away</span>
          </div>
        )}
      </div>

      <div className="performance-metrics">
        <div className="metric">
          <span className="metric-label">30-Day Sales</span>
          <span className="metric-value">₹{store.performance?.total_sales_30d?.toLocaleString() || 0}</span>
        </div>
        <div className="metric">
          <span className="metric-label">Transactions</span>
          <span className="metric-value">{store.performance?.transaction_count_30d || 0}</span>
        </div>
        <div className="metric">
          <span className="metric-label">Low Stock Items</span>
          <span className={`metric-value ${store.performance?.low_stock_count > 0 ? 'warning' : ''}`}>
            {store.performance?.low_stock_count || 0}
          </span>
        </div>
      </div>

      {store.performance?.low_stock_products && store.performance.low_stock_products.length > 0 && (
        <div className="low-stock-alert">
          <strong>Low Stock Products:</strong>
          <ul>
            {store.performance.low_stock_products.slice(0, 3).map(product => (
              <li key={product.id}>
                {product.name} ({product.current_stock} left)
              </li>
            ))}
          </ul>
        </div>
      )}

      <button onClick={onOrderClick} className="order-btn">
        Create Bulk Order
      </button>
    </div>
  );
};

export default StoreCard;

