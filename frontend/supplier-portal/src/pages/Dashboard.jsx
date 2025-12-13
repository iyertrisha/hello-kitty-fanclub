import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { supplierApi } from '../services/api';
import StoreCard from '../components/StoreCard';
import StoreMap from '../components/StoreMap';
import ServiceAreaModal from '../components/ServiceAreaModal';
import BulkOrderModal from '../components/BulkOrderModal';
import './Dashboard.css';

const Dashboard = () => {
  const { supplier, logout } = useContext(AuthContext);
  const navigate = useNavigate();
  const [stores, setStores] = useState([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState('list'); // 'list' or 'map'
  const [selectedStore, setSelectedStore] = useState(null);
  const [showServiceAreaModal, setShowServiceAreaModal] = useState(false);
  const [showBulkOrderModal, setShowBulkOrderModal] = useState(false);
  const [filter, setFilter] = useState('all'); // 'all', 'high-score', 'low-stock'
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    if (supplier) {
      loadStores();
    }
  }, [supplier]);

  const loadStores = async () => {
    if (!supplier) return;
    
    try {
      setLoading(true);
      const response = await supplierApi.getStores();
      setStores(response.stores || []);
    } catch (error) {
      console.error('Error loading stores:', error);
      alert('Failed to load stores. Please set your service area first.');
    } finally {
      setLoading(false);
    }
  };

  const handleServiceAreaUpdate = async (serviceAreaData) => {
    try {
      await supplierApi.updateServiceArea(serviceAreaData);
      setShowServiceAreaModal(false);
      loadStores();
      alert('Service area updated successfully!');
    } catch (error) {
      console.error('Error updating service area:', error);
      alert('Failed to update service area');
    }
  };

  const handleCreateOrder = async (orderData) => {
    try {
      await supplierApi.createOrder(orderData);
      setShowBulkOrderModal(false);
      setSelectedStore(null);
      alert('Order created successfully!');
    } catch (error) {
      console.error('Error creating order:', error);
      alert('Failed to create order');
    }
  };

  const filteredStores = stores.filter(store => {
    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      if (!store.name.toLowerCase().includes(query) && 
          !store.address?.toLowerCase().includes(query)) {
        return false;
      }
    }

    // Performance filter
    if (filter === 'high-score') {
      return store.credit_score >= 700;
    }
    if (filter === 'low-stock') {
      return store.performance?.low_stock_count > 0;
    }
    return true;
  });

  if (!supplier) {
    return <div>Loading...</div>;
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <h1>Supplier Portal</h1>
          <div className="header-actions">
            <button onClick={() => navigate('/orders')} className="btn-secondary">
              Orders
            </button>
            <span className="supplier-name">{supplier.name}</span>
            <button onClick={() => setShowServiceAreaModal(true)} className="btn-secondary">
              Set Service Area
            </button>
            <button onClick={logout} className="btn-logout">
              Logout
            </button>
          </div>
        </div>
      </header>

      <div className="dashboard-content">
        <div className="dashboard-toolbar">
          <div className="search-bar">
            <input
              type="text"
              placeholder="Search stores..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <div className="filters">
            <select value={filter} onChange={(e) => setFilter(e.target.value)}>
              <option value="all">All Stores</option>
              <option value="high-score">High Credit Score (700+)</option>
              <option value="low-stock">Low Stock Stores</option>
            </select>
          </div>
          <div className="view-toggle">
            <button
              className={viewMode === 'list' ? 'active' : ''}
              onClick={() => setViewMode('list')}
            >
              List
            </button>
            <button
              className={viewMode === 'map' ? 'active' : ''}
              onClick={() => setViewMode('map')}
            >
              Map
            </button>
          </div>
        </div>

        {loading ? (
          <div className="loading">Loading stores...</div>
        ) : stores.length === 0 ? (
          <div className="empty-state">
            <h2>No stores found in your service area</h2>
            <p>Set your service area to see kirana stores nearby</p>
            <button onClick={() => setShowServiceAreaModal(true)} className="btn-primary">
              Set Service Area
            </button>
          </div>
        ) : (
          <>
            <div className="stats-bar">
              <div className="stat">
                <span className="stat-label">Total Stores</span>
                <span className="stat-value">{stores.length}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Low Stock Stores</span>
                <span className="stat-value">
                  {stores.filter(s => s.performance?.low_stock_count > 0).length}
                </span>
              </div>
              <div className="stat">
                <span className="stat-label">Avg Credit Score</span>
                <span className="stat-value">
                  {stores.length > 0
                    ? Math.round(stores.reduce((sum, s) => sum + s.credit_score, 0) / stores.length)
                    : 0}
                </span>
              </div>
            </div>

            {viewMode === 'list' ? (
              <div className="stores-list">
                {filteredStores.map(store => (
                  <StoreCard
                    key={store.id}
                    store={store}
                    onOrderClick={() => {
                      setSelectedStore(store);
                      setShowBulkOrderModal(true);
                    }}
                  />
                ))}
              </div>
            ) : (
              <StoreMap
                stores={filteredStores}
                serviceAreaCenter={supplier.service_area_center}
                serviceAreaRadius={supplier.service_area_radius_km}
                onStoreClick={(store) => {
                  setSelectedStore(store);
                  setShowBulkOrderModal(true);
                }}
              />
            )}
          </>
        )}
      </div>

      {showServiceAreaModal && (
        <ServiceAreaModal
          currentServiceArea={supplier.service_area_center}
          currentRadius={supplier.service_area_radius_km}
          onClose={() => setShowServiceAreaModal(false)}
          onSave={handleServiceAreaUpdate}
        />
      )}

      {showBulkOrderModal && selectedStore && (
        <BulkOrderModal
          store={selectedStore}
          onClose={() => {
            setShowBulkOrderModal(false);
            setSelectedStore(null);
          }}
          onOrder={handleCreateOrder}
        />
      )}
    </div>
  );
};

export default Dashboard;

