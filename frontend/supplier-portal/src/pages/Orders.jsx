import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { supplierApi } from '../services/api';
import OrderCard from '../components/OrderCard';
import OrderStatusBadge from '../components/OrderStatusBadge';
import './Orders.css';

const Orders = () => {
  const { supplier, logout } = useContext(AuthContext);
  const navigate = useNavigate();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('date-desc');

  useEffect(() => {
    if (supplier) {
      loadOrders();
    }
  }, [supplier]);

  const loadOrders = async () => {
    try {
      setLoading(true);
      const response = await supplierApi.getOrders();
      setOrders(response.orders || []);
    } catch (error) {
      console.error('Error loading orders:', error);
      alert('Failed to load orders');
    } finally {
      setLoading(false);
    }
  };

  const filteredAndSortedOrders = orders
    .filter(order => {
      // Status filter
      if (filter !== 'all' && order.status !== filter) {
        return false;
      }

      // Search filter
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        const shopkeeperName = (order.shopkeeper_name || '').toLowerCase();
        const orderId = order.id.toLowerCase();
        if (!shopkeeperName.includes(query) && !orderId.includes(query)) {
          return false;
        }
      }

      return true;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'date-desc':
          return new Date(b.created_at) - new Date(a.created_at);
        case 'date-asc':
          return new Date(a.created_at) - new Date(b.created_at);
        case 'amount-desc':
          return b.total_amount - a.total_amount;
        case 'amount-asc':
          return a.total_amount - b.total_amount;
        case 'status':
          return a.status.localeCompare(b.status);
        default:
          return 0;
      }
    });

  const getStatusCounts = () => {
    const counts = {
      all: orders.length,
      pending: 0,
      confirmed: 0,
      dispatched: 0,
      delivered: 0,
      cancelled: 0
    };
    orders.forEach(order => {
      if (counts.hasOwnProperty(order.status)) {
        counts[order.status]++;
      }
    });
    return counts;
  };

  const statusCounts = getStatusCounts();

  if (!supplier) {
    return <div>Loading...</div>;
  }

  return (
    <div className="orders-page">
      <header className="orders-header">
        <div className="header-content">
          <h1>Orders</h1>
          <div className="header-actions">
            <button onClick={() => navigate('/dashboard')} className="btn-secondary">
              Dashboard
            </button>
            <span className="supplier-name">{supplier.name}</span>
            <button onClick={logout} className="btn-logout">
              Logout
            </button>
          </div>
        </div>
      </header>

      <div className="orders-content">
        <div className="orders-toolbar">
          <div className="search-bar">
            <input
              type="text"
              placeholder="Search by shopkeeper name or order ID..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          <div className="filters">
            <select value={filter} onChange={(e) => setFilter(e.target.value)}>
              <option value="all">All Status ({statusCounts.all})</option>
              <option value="pending">Pending ({statusCounts.pending})</option>
              <option value="confirmed">Confirmed ({statusCounts.confirmed})</option>
              <option value="dispatched">Dispatched ({statusCounts.dispatched})</option>
              <option value="delivered">Delivered ({statusCounts.delivered})</option>
              <option value="cancelled">Cancelled ({statusCounts.cancelled})</option>
            </select>
          </div>

          <div className="sort">
            <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
              <option value="date-desc">Newest First</option>
              <option value="date-asc">Oldest First</option>
              <option value="amount-desc">Highest Amount</option>
              <option value="amount-asc">Lowest Amount</option>
              <option value="status">By Status</option>
            </select>
          </div>
        </div>

        {loading ? (
          <div className="loading">Loading orders...</div>
        ) : filteredAndSortedOrders.length === 0 ? (
          <div className="empty-state">
            <h2>No orders found</h2>
            <p>
              {searchQuery || filter !== 'all'
                ? 'Try adjusting your search or filter criteria'
                : 'Create your first bulk order from the dashboard'}
            </p>
            {!searchQuery && filter === 'all' && (
              <button onClick={() => navigate('/dashboard')} className="btn-primary">
                Go to Dashboard
              </button>
            )}
          </div>
        ) : (
          <>
            <div className="orders-stats">
              <div className="stat">
                <span className="stat-label">Total Orders</span>
                <span className="stat-value">{orders.length}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Total Value</span>
                <span className="stat-value">
                  ₹{filteredAndSortedOrders.reduce((sum, o) => sum + (o.total_amount || 0), 0).toLocaleString('en-IN')}
                </span>
              </div>
              <div className="stat">
                <span className="stat-label">Pending</span>
                <span className="stat-value">{statusCounts.pending}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Delivered</span>
                <span className="stat-value">{statusCounts.delivered}</span>
              </div>
            </div>

            <div className="orders-list">
              {filteredAndSortedOrders.map(order => (
                <OrderCard key={order.id} order={order} />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Orders;

