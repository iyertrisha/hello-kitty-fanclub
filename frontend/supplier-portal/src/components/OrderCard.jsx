import React from 'react';
import { useNavigate } from 'react-router-dom';
import OrderStatusBadge from './OrderStatusBadge';
import './OrderCard.css';

const OrderCard = ({ order }) => {
  const navigate = useNavigate();

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount);
  };

  const handleClick = () => {
    navigate(`/orders/${order.id}`);
  };

  return (
    <div className="order-card" onClick={handleClick}>
      <div className="order-card-header">
        <div className="order-id">
          <span className="label">Order ID:</span>
          <span className="value">#{order.id.slice(-8)}</span>
        </div>
        <OrderStatusBadge status={order.status} />
      </div>
      
      <div className="order-card-body">
        <div className="order-shopkeeper">
          <span className="label">Shopkeeper:</span>
          <span className="value">{order.shopkeeper_name || 'N/A'}</span>
        </div>
        
        <div className="order-products">
          <span className="label">Products:</span>
          <span className="value">{order.products?.length || 0} items</span>
        </div>
        
        <div className="order-total">
          <span className="label">Total Amount:</span>
          <span className="value amount">{formatCurrency(order.total_amount)}</span>
        </div>
        
        <div className="order-date">
          <span className="label">Order Date:</span>
          <span className="value">{formatDate(order.created_at)}</span>
        </div>
      </div>
    </div>
  );
};

export default OrderCard;

