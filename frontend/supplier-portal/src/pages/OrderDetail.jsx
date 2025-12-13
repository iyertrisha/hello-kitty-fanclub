import React, { useState, useEffect, useContext } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { supplierApi } from '../services/api';
import OrderStatusBadge from '../components/OrderStatusBadge';
import './OrderDetail.css';

const OrderDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { supplier, logout } = useContext(AuthContext);
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    if (supplier && id) {
      loadOrder();
    }
  }, [supplier, id]);

  const loadOrder = async () => {
    try {
      setLoading(true);
      const response = await supplierApi.getOrder(id);
      setOrder(response.order);
    } catch (error) {
      console.error('Error loading order:', error);
      alert('Failed to load order details');
      navigate('/orders');
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (newStatus) => {
    if (!window.confirm(`Are you sure you want to update order status to "${newStatus}"?`)) {
      return;
    }

    try {
      setUpdating(true);
      await supplierApi.updateOrderStatus(id, newStatus);
      await loadOrder();
      alert('Order status updated successfully!');
    } catch (error) {
      console.error('Error updating order status:', error);
      alert('Failed to update order status');
    } finally {
      setUpdating(false);
    }
  };

  const handleCancel = async () => {
    if (!window.confirm('Are you sure you want to cancel this order?')) {
      return;
    }

    try {
      setUpdating(true);
      await supplierApi.cancelOrder(id);
      await loadOrder();
      alert('Order cancelled successfully!');
    } catch (error) {
      console.error('Error cancelling order:', error);
      alert('Failed to cancel order');
    } finally {
      setUpdating(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'long',
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

  const getNextStatus = (currentStatus) => {
    const statusFlow = {
      pending: 'confirmed',
      confirmed: 'dispatched',
      dispatched: 'delivered'
    };
    return statusFlow[currentStatus?.toLowerCase()];
  };

  const canUpdateStatus = (currentStatus) => {
    return ['pending', 'confirmed', 'dispatched'].includes(currentStatus?.toLowerCase());
  };

  const canCancel = (currentStatus) => {
    return ['pending', 'confirmed'].includes(currentStatus?.toLowerCase());
  };

  if (loading) {
    return (
      <div className="order-detail-page">
        <div className="loading">Loading order details...</div>
      </div>
    );
  }

  if (!order) {
    return (
      <div className="order-detail-page">
        <div className="empty-state">
          <h2>Order not found</h2>
          <button onClick={() => navigate('/orders')} className="btn-primary">
            Back to Orders
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="order-detail-page">
      <header className="order-detail-header">
        <div className="header-content">
          <button onClick={() => navigate('/orders')} className="btn-back">
            ← Back to Orders
          </button>
          <div className="header-right">
            <span className="supplier-name">{supplier?.name}</span>
            <button onClick={logout} className="btn-logout">
              Logout
            </button>
          </div>
        </div>
      </header>

      <div className="order-detail-content">
        <div className="order-detail-main">
          <div className="order-header">
            <div>
              <h1>Order #{order.id.slice(-8)}</h1>
              <p className="order-date">Created: {formatDate(order.created_at)}</p>
            </div>
            <OrderStatusBadge status={order.status} />
          </div>

          <div className="order-info-section">
            <h2>Shopkeeper Information</h2>
            <div className="info-grid">
              <div className="info-item">
                <span className="label">Name:</span>
                <span className="value">{order.shopkeeper_name || 'N/A'}</span>
              </div>
              <div className="info-item">
                <span className="label">Address:</span>
                <span className="value">{order.shopkeeper_address || 'N/A'}</span>
              </div>
              <div className="info-item">
                <span className="label">Phone:</span>
                <span className="value">{order.shopkeeper_phone || 'N/A'}</span>
              </div>
              <div className="info-item">
                <span className="label">Email:</span>
                <span className="value">{order.shopkeeper_email || 'N/A'}</span>
              </div>
            </div>
          </div>

          <div className="order-products-section">
            <h2>Products</h2>
            <div className="products-table">
              <table>
                <thead>
                  <tr>
                    <th>Product Name</th>
                    <th>Quantity</th>
                    <th>Unit Price</th>
                    <th>Total</th>
                  </tr>
                </thead>
                <tbody>
                  {order.products?.map((product, index) => (
                    <tr key={index}>
                      <td>{product.name}</td>
                      <td>{product.quantity}</td>
                      <td>{formatCurrency(product.unit_price)}</td>
                      <td>{formatCurrency(product.quantity * product.unit_price)}</td>
                    </tr>
                  ))}
                </tbody>
                <tfoot>
                  <tr>
                    <td colSpan="3" className="total-label">
                      <strong>Total Amount:</strong>
                    </td>
                    <td className="total-amount">
                      <strong>{formatCurrency(order.total_amount)}</strong>
                    </td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>

          {order.notes && (
            <div className="order-notes-section">
              <h2>Notes</h2>
              <p>{order.notes}</p>
            </div>
          )}

          <div className="order-actions">
            {canUpdateStatus(order.status) && (
              <button
                onClick={() => handleStatusUpdate(getNextStatus(order.status))}
                disabled={updating}
                className="btn-primary"
              >
                {updating ? 'Updating...' : `Mark as ${getNextStatus(order.status)}`}
              </button>
            )}
            {canCancel(order.status) && (
              <button
                onClick={handleCancel}
                disabled={updating}
                className="btn-danger"
              >
                {updating ? 'Cancelling...' : 'Cancel Order'}
              </button>
            )}
            <button onClick={() => navigate('/orders')} className="btn-secondary">
              Back to Orders
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OrderDetail;

