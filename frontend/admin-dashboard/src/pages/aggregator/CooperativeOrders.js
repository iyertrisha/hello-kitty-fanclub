import React, { useState, useEffect } from 'react';
import apiService from '../../services/api';
import './CooperativeOrders.css';

const CooperativeOrders = () => {
  const [orders, setOrders] = useState([]);
  const [filteredOrders, setFilteredOrders] = useState([]);
  const [filters, setFilters] = useState({
    status: 'all',
    search: '',
    dateRange: 'all',
  });
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    total: 0,
    pending: 0,
    inProgress: 0,
    completed: 0,
    totalRevenue: 0,
  });

  const cooperativeId = 'coop-001';

  useEffect(() => {
    loadOrders();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [orders, filters]);

  const loadOrders = async () => {
    try {
      setLoading(true);
      const data = await apiService.getCooperativeOrders(cooperativeId);
      const ordersList = data.orders || data || [];
      setOrders(ordersList);
      
      // Calculate stats
      setStats({
        total: ordersList.length,
        pending: ordersList.filter(o => o.status === 'pending').length,
        inProgress: ordersList.filter(o => o.status === 'in_progress' || o.status === 'processing').length,
        completed: ordersList.filter(o => o.status === 'completed' || o.status === 'delivered').length,
        totalRevenue: ordersList.reduce((sum, o) => sum + (o.total_amount || 0), 0),
      });
    } catch (error) {
      console.error('Error loading orders:', error);
      // Mock data for demonstration
      const mockOrders = [
        {
          id: 'ORD-001',
          customer_name: 'Rajesh Kumar',
          customer_phone: '+91 98765 43210',
          items: [
            { name: 'Rice (5kg)', quantity: 2, price: 350, store: 'Krishna Store' },
            { name: 'Dal (1kg)', quantity: 3, price: 120, store: 'Gupta Provisions' },
          ],
          total_amount: 1060,
          status: 'pending',
          created_at: new Date().toISOString(),
          delivery_address: '45, Green Park, Delhi',
        },
        {
          id: 'ORD-002',
          customer_name: 'Priya Sharma',
          customer_phone: '+91 87654 32109',
          items: [
            { name: 'Atta (10kg)', quantity: 1, price: 450, store: 'Sharma Kirana' },
            { name: 'Sugar (5kg)', quantity: 1, price: 250, store: 'Krishna Store' },
          ],
          total_amount: 700,
          status: 'in_progress',
          created_at: new Date(Date.now() - 3600000).toISOString(),
          delivery_address: '12, Lajpat Nagar, Delhi',
          assigned_store: 'Krishna Store',
        },
        {
          id: 'ORD-003',
          customer_name: 'Amit Singh',
          customer_phone: '+91 76543 21098',
          items: [
            { name: 'Oil (5L)', quantity: 2, price: 650, store: 'Verma Mart' },
          ],
          total_amount: 1300,
          status: 'completed',
          created_at: new Date(Date.now() - 86400000).toISOString(),
          delivery_address: '78, Saket, Delhi',
          completed_at: new Date().toISOString(),
        },
      ];
      setOrders(mockOrders);
      setStats({
        total: mockOrders.length,
        pending: mockOrders.filter(o => o.status === 'pending').length,
        inProgress: mockOrders.filter(o => o.status === 'in_progress').length,
        completed: mockOrders.filter(o => o.status === 'completed').length,
        totalRevenue: mockOrders.reduce((sum, o) => sum + (o.total_amount || 0), 0),
      });
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...orders];

    if (filters.status !== 'all') {
      filtered = filtered.filter(o => o.status === filters.status);
    }

    if (filters.search) {
      const query = filters.search.toLowerCase();
      filtered = filtered.filter(o =>
        o.id?.toLowerCase().includes(query) ||
        o.customer_name?.toLowerCase().includes(query) ||
        o.customer_phone?.includes(query)
      );
    }

    if (filters.dateRange !== 'all') {
      const now = new Date();
      let startDate;
      if (filters.dateRange === 'today') {
        startDate = new Date(now.setHours(0, 0, 0, 0));
      } else if (filters.dateRange === 'week') {
        startDate = new Date(now.setDate(now.getDate() - 7));
      } else if (filters.dateRange === 'month') {
        startDate = new Date(now.setMonth(now.getMonth() - 1));
      }
      if (startDate) {
        filtered = filtered.filter(o => new Date(o.created_at) >= startDate);
      }
    }

    setFilteredOrders(filtered);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending': return '#fbbf24';
      case 'in_progress':
      case 'processing': return '#60a5fa';
      case 'completed':
      case 'delivered': return '#34d399';
      case 'cancelled': return '#f87171';
      default: return '#9ca3af';
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'pending': return 'Pending';
      case 'in_progress': return 'In Progress';
      case 'processing': return 'Processing';
      case 'completed': return 'Completed';
      case 'delivered': return 'Delivered';
      case 'cancelled': return 'Cancelled';
      default: return status;
    }
  };

  const handleUpdateStatus = async (orderId, newStatus) => {
    try {
      await apiService.updateOrderStatus(cooperativeId, orderId, newStatus);
      loadOrders();
      if (selectedOrder?.id === orderId) {
        setSelectedOrder({ ...selectedOrder, status: newStatus });
      }
    } catch (error) {
      console.error('Error updating order status:', error);
      alert('Failed to update order status');
    }
  };

  if (loading) {
    return (
      <div className="cooperative-orders">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading orders...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="cooperative-orders">
      <div className="page-header">
        <div className="header-content">
          <h1 className="page-title">Cooperative Orders</h1>
          <p className="page-subtitle">Order management and fulfillment coordination</p>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="order-stats">
        <div className="stat-card">
          <span className="stat-icon">📦</span>
          <div className="stat-content">
            <span className="stat-value">{stats.total}</span>
            <span className="stat-label">Total Orders</span>
          </div>
        </div>
        <div className="stat-card pending">
          <span className="stat-icon">⏳</span>
          <div className="stat-content">
            <span className="stat-value">{stats.pending}</span>
            <span className="stat-label">Pending</span>
          </div>
        </div>
        <div className="stat-card progress">
          <span className="stat-icon">🚚</span>
          <div className="stat-content">
            <span className="stat-value">{stats.inProgress}</span>
            <span className="stat-label">In Progress</span>
          </div>
        </div>
        <div className="stat-card completed">
          <span className="stat-icon">✅</span>
          <div className="stat-content">
            <span className="stat-value">{stats.completed}</span>
            <span className="stat-label">Completed</span>
          </div>
        </div>
        <div className="stat-card revenue">
          <span className="stat-icon">💰</span>
          <div className="stat-content">
            <span className="stat-value">₹{stats.totalRevenue.toLocaleString()}</span>
            <span className="stat-label">Total Revenue</span>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="filters-section">
        <div className="search-box">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            placeholder="Search orders..."
            value={filters.search}
            onChange={(e) => setFilters({ ...filters, search: e.target.value })}
            className="search-input"
          />
        </div>
        <select
          value={filters.status}
          onChange={(e) => setFilters({ ...filters, status: e.target.value })}
          className="filter-select"
        >
          <option value="all">All Status</option>
          <option value="pending">Pending</option>
          <option value="in_progress">In Progress</option>
          <option value="completed">Completed</option>
          <option value="cancelled">Cancelled</option>
        </select>
        <select
          value={filters.dateRange}
          onChange={(e) => setFilters({ ...filters, dateRange: e.target.value })}
          className="filter-select"
        >
          <option value="all">All Time</option>
          <option value="today">Today</option>
          <option value="week">This Week</option>
          <option value="month">This Month</option>
        </select>
      </div>

      {/* Orders Table */}
      <div className="table-container">
        <table className="orders-table">
          <thead>
            <tr>
              <th>Order ID</th>
              <th>Customer</th>
              <th>Items</th>
              <th>Total</th>
              <th>Status</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredOrders.length > 0 ? (
              filteredOrders.map((order) => (
                <tr key={order.id} onClick={() => setSelectedOrder(order)}>
                  <td className="order-id">{order.id}</td>
                  <td>
                    <div className="customer-cell">
                      <span className="customer-name">{order.customer_name}</span>
                      <span className="customer-phone">{order.customer_phone}</span>
                    </div>
                  </td>
                  <td className="items-count">{order.items?.length || 0} items</td>
                  <td className="order-total">₹{order.total_amount?.toLocaleString()}</td>
                  <td>
                    <span
                      className="status-badge"
                      style={{
                        background: `${getStatusColor(order.status)}20`,
                        color: getStatusColor(order.status),
                        borderColor: `${getStatusColor(order.status)}40`,
                      }}
                    >
                      {getStatusLabel(order.status)}
                    </span>
                  </td>
                  <td className="order-date">
                    {new Date(order.created_at).toLocaleDateString()}
                  </td>
                  <td>
                    <button
                      className="view-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedOrder(order);
                      }}
                    >
                      View
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="7" className="empty-cell">
                  <div className="empty-state">
                    <span className="empty-icon">📦</span>
                    <p>No orders found</p>
                  </div>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Order Detail Modal */}
      {selectedOrder && (
        <div className="modal-overlay" onClick={() => setSelectedOrder(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div className="modal-title-group">
                <h2 className="modal-title">Order {selectedOrder.id}</h2>
                <span
                  className="modal-status"
                  style={{
                    background: `${getStatusColor(selectedOrder.status)}20`,
                    color: getStatusColor(selectedOrder.status),
                  }}
                >
                  {getStatusLabel(selectedOrder.status)}
                </span>
              </div>
              <button className="close-btn" onClick={() => setSelectedOrder(null)}>×</button>
            </div>

            <div className="order-details">
              {/* Customer Info */}
              <div className="detail-section">
                <h3 className="detail-section-title">👤 Customer Information</h3>
                <div className="detail-grid">
                  <div className="detail-item">
                    <span className="detail-label">Name</span>
                    <span className="detail-value">{selectedOrder.customer_name}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Phone</span>
                    <span className="detail-value">{selectedOrder.customer_phone}</span>
                  </div>
                  <div className="detail-item full-width">
                    <span className="detail-label">Delivery Address</span>
                    <span className="detail-value">{selectedOrder.delivery_address}</span>
                  </div>
                </div>
              </div>

              {/* Order Items */}
              <div className="detail-section">
                <h3 className="detail-section-title">📦 Order Items</h3>
                <div className="items-list">
                  {selectedOrder.items?.map((item, index) => (
                    <div key={index} className="item-row">
                      <div className="item-info">
                        <span className="item-name">{item.name}</span>
                        <span className="item-store">Fulfilled by: {item.store}</span>
                      </div>
                      <div className="item-details">
                        <span className="item-qty">×{item.quantity}</span>
                        <span className="item-price">₹{item.price * item.quantity}</span>
                      </div>
                    </div>
                  ))}
                  <div className="items-total">
                    <span>Total Amount</span>
                    <span className="total-value">₹{selectedOrder.total_amount?.toLocaleString()}</span>
                  </div>
                </div>
              </div>

              {/* Timeline */}
              <div className="detail-section">
                <h3 className="detail-section-title">📅 Order Timeline</h3>
                <div className="timeline">
                  <div className="timeline-item completed">
                    <span className="timeline-dot"></span>
                    <div className="timeline-content">
                      <span className="timeline-title">Order Created</span>
                      <span className="timeline-time">
                        {new Date(selectedOrder.created_at).toLocaleString()}
                      </span>
                    </div>
                  </div>
                  {selectedOrder.status !== 'pending' && (
                    <div className="timeline-item completed">
                      <span className="timeline-dot"></span>
                      <div className="timeline-content">
                        <span className="timeline-title">Order Processing</span>
                        <span className="timeline-time">In progress</span>
                      </div>
                    </div>
                  )}
                  {selectedOrder.completed_at && (
                    <div className="timeline-item completed">
                      <span className="timeline-dot"></span>
                      <div className="timeline-content">
                        <span className="timeline-title">Order Completed</span>
                        <span className="timeline-time">
                          {new Date(selectedOrder.completed_at).toLocaleString()}
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Status Actions */}
              {selectedOrder.status !== 'completed' && selectedOrder.status !== 'cancelled' && (
                <div className="status-actions">
                  <h3 className="detail-section-title">⚡ Update Status</h3>
                  <div className="action-buttons">
                    {selectedOrder.status === 'pending' && (
                      <button
                        className="action-btn progress-btn"
                        onClick={() => handleUpdateStatus(selectedOrder.id, 'in_progress')}
                      >
                        Start Processing
                      </button>
                    )}
                    {selectedOrder.status === 'in_progress' && (
                      <button
                        className="action-btn complete-btn"
                        onClick={() => handleUpdateStatus(selectedOrder.id, 'completed')}
                      >
                        Mark Completed
                      </button>
                    )}
                    <button
                      className="action-btn cancel-btn"
                      onClick={() => handleUpdateStatus(selectedOrder.id, 'cancelled')}
                    >
                      Cancel Order
                    </button>
                  </div>
                </div>
              )}
            </div>

            <div className="modal-footer">
              <button
                className="modal-btn close-modal-btn"
                onClick={() => setSelectedOrder(null)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CooperativeOrders;

