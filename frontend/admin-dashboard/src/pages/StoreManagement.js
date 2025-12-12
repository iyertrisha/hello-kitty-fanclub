import React, { useState, useEffect } from 'react';
import apiService from '../services/api';
import StoreTable from '../components/StoreTable';
import './StoreManagement.css';

const StoreManagement = () => {
  const [stores, setStores] = useState([]);
  const [filteredStores, setFilteredStores] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [selectedStore, setSelectedStore] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    address: '',
    phone: '',
    email: '',
    wallet_address: '',
  });

  useEffect(() => {
    loadStores();
  }, []);

  const loadStores = async () => {
    try {
      setLoading(true);
      const data = await apiService.getStores();
      // Backend returns {stores: [...], pagination: {...}}
      const storesList = data.stores || data.data || data || [];
      // Map backend fields to frontend expected format
      const mappedStores = storesList.map(store => ({
        ...store,
        status: store.is_active ? 'active' : 'inactive',
        total_sales: store.total_sales_30d || 0,
      }));
      setStores(mappedStores);
      setFilteredStores(mappedStores);
    } catch (error) {
      console.error('Error loading stores:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (query) => {
    const filtered = stores.filter(
      (store) =>
        store.name.toLowerCase().includes(query.toLowerCase()) ||
        store.address?.toLowerCase().includes(query.toLowerCase())
    );
    setFilteredStores(filtered);
  };

  const handleFilter = (filters) => {
    let filtered = [...stores];

    if (filters.status && filters.status !== 'all') {
      filtered = filtered.filter((store) => store.status === filters.status);
    }

    if (filters.scoreRange && filters.scoreRange !== 'all') {
      filtered = filtered.filter((store) => {
        const score = store.credit_score || 0;
        if (filters.scoreRange === 'high') return score >= 700;
        if (filters.scoreRange === 'medium') return score >= 500 && score < 700;
        if (filters.scoreRange === 'low') return score < 500;
        return true;
      });
    }

    setFilteredStores(filtered);
  };

  const handleView = async (storeId) => {
    try {
      const store = stores.find(s => s.id === storeId);
      if (store) {
        setSelectedStore(store);
        setShowViewModal(true);
      }
    } catch (error) {
      console.error('Error viewing store:', error);
      alert('Failed to load store details');
    }
  };

  const handleEdit = (storeId) => {
    const store = stores.find(s => s.id === storeId);
    if (store) {
      setSelectedStore(store);
      setFormData({
        name: store.name || '',
        address: store.address || '',
        phone: store.phone || '',
        email: store.email || '',
        wallet_address: store.wallet_address || '',
      });
      setShowEditModal(true);
    }
  };

  const handleDelete = async (storeId) => {
    if (window.confirm('Are you sure you want to delete this store? This action cannot be undone.')) {
      try {
        await apiService.deleteStore(storeId);
        alert('Store deleted successfully');
        loadStores();
      } catch (error) {
        console.error('Error deleting store:', error);
        alert('Failed to delete store: ' + (error.response?.data?.message || error.message));
      }
    }
  };

  const handleToggleStatus = async (storeId) => {
    try {
      const result = await apiService.toggleStoreStatus(storeId);
      alert(result.message || 'Status updated successfully');
      loadStores();
    } catch (error) {
      console.error('Error toggling store status:', error);
      alert('Failed to toggle store status: ' + (error.response?.data?.message || error.message));
    }
  };

  const handleAddStore = async () => {
    if (!formData.name || !formData.address || !formData.phone || !formData.wallet_address) {
      alert('Please fill in all required fields (Name, Address, Phone, Wallet Address)');
      return;
    }

    try {
      await apiService.createStore(formData);
      alert('Store added successfully');
      setShowAddModal(false);
      setFormData({ name: '', address: '', phone: '', email: '', wallet_address: '' });
      loadStores();
    } catch (error) {
      console.error('Error adding store:', error);
      alert('Failed to add store: ' + (error.response?.data?.message || error.message));
    }
  };

  const handleUpdateStore = async () => {
    if (!formData.name || !formData.address || !formData.phone) {
      alert('Please fill in all required fields (Name, Address, Phone)');
      return;
    }

    try {
      await apiService.updateStore(selectedStore.id, {
        name: formData.name,
        address: formData.address,
        phone: formData.phone,
        email: formData.email,
      });
      alert('Store updated successfully');
      setShowEditModal(false);
      setSelectedStore(null);
      setFormData({ name: '', address: '', phone: '', email: '', wallet_address: '' });
      loadStores();
    } catch (error) {
      console.error('Error updating store:', error);
      alert('Failed to update store: ' + (error.response?.data?.message || error.message));
    }
  };

  const generateWalletAddress = () => {
    // Generate a random wallet address for testing
    const chars = '0123456789abcdef';
    let address = '0x';
    for (let i = 0; i < 40; i++) {
      address += chars[Math.floor(Math.random() * chars.length)];
    }
    setFormData({ ...formData, wallet_address: address });
  };

  if (loading) {
    return (
      <div className="store-management-container">
        <div className="loading-message">Loading stores...</div>
      </div>
    );
  }

  return (
    <div className="store-management-container">
      <div className="page-header">
        <h1 className="page-title">Store Management</h1>
        <button 
          className="add-store-button"
          onClick={() => setShowAddModal(true)}
        >
          + Add Store
        </button>
      </div>

      <StoreTable
        stores={filteredStores}
        onView={handleView}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onToggleStatus={handleToggleStatus}
        onSearch={handleSearch}
        onFilter={handleFilter}
      />

      {/* Add Store Modal */}
      {showAddModal && (
        <div className="modal-overlay" onClick={() => setShowAddModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2 className="modal-title">Add New Store</h2>
            <div className="modal-form">
              <label className="modal-label">
                Name *
                <input
                  type="text"
                  className="modal-input"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="Store name"
                />
              </label>
              <label className="modal-label">
                Address *
                <input
                  type="text"
                  className="modal-input"
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                  placeholder="Store address"
                />
              </label>
              <label className="modal-label">
                Phone *
                <input
                  type="text"
                  className="modal-input"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  placeholder="Phone number"
                />
              </label>
              <label className="modal-label">
                Email
                <input
                  type="email"
                  className="modal-input"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  placeholder="Email address"
                />
              </label>
              <label className="modal-label">
                Wallet Address *
                <div className="wallet-input-group">
                  <input
                    type="text"
                    className="modal-input"
                    value={formData.wallet_address}
                    onChange={(e) => setFormData({ ...formData, wallet_address: e.target.value })}
                    placeholder="0x..."
                  />
                  <button 
                    type="button" 
                    className="generate-wallet-btn"
                    onClick={generateWalletAddress}
                  >
                    Generate
                  </button>
                </div>
              </label>
              <div className="modal-actions">
                <button
                  className="modal-button cancel"
                  onClick={() => {
                    setShowAddModal(false);
                    setFormData({ name: '', address: '', phone: '', email: '', wallet_address: '' });
                  }}
                >
                  Cancel
                </button>
                <button
                  className="modal-button primary"
                  onClick={handleAddStore}
                >
                  Add Store
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Edit Store Modal */}
      {showEditModal && selectedStore && (
        <div className="modal-overlay" onClick={() => setShowEditModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2 className="modal-title">Edit Store</h2>
            <div className="modal-form">
              <label className="modal-label">
                Name *
                <input
                  type="text"
                  className="modal-input"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="Store name"
                />
              </label>
              <label className="modal-label">
                Address *
                <input
                  type="text"
                  className="modal-input"
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                  placeholder="Store address"
                />
              </label>
              <label className="modal-label">
                Phone *
                <input
                  type="text"
                  className="modal-input"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  placeholder="Phone number"
                />
              </label>
              <label className="modal-label">
                Email
                <input
                  type="email"
                  className="modal-input"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  placeholder="Email address"
                />
              </label>
              <label className="modal-label">
                Wallet Address (Read-only)
                <input
                  type="text"
                  className="modal-input"
                  value={formData.wallet_address}
                  disabled
                />
              </label>
              <div className="modal-actions">
                <button
                  className="modal-button cancel"
                  onClick={() => {
                    setShowEditModal(false);
                    setSelectedStore(null);
                    setFormData({ name: '', address: '', phone: '', email: '', wallet_address: '' });
                  }}
                >
                  Cancel
                </button>
                <button
                  className="modal-button primary"
                  onClick={handleUpdateStore}
                >
                  Update Store
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* View Store Modal */}
      {showViewModal && selectedStore && (
        <div className="modal-overlay" onClick={() => setShowViewModal(false)}>
          <div className="modal-content view-modal" onClick={(e) => e.stopPropagation()}>
            <h2 className="modal-title">Store Details</h2>
            <div className="store-details">
              <div className="detail-row">
                <span className="detail-label">Name:</span>
                <span className="detail-value">{selectedStore.name}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Address:</span>
                <span className="detail-value">{selectedStore.address}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Phone:</span>
                <span className="detail-value">{selectedStore.phone}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Email:</span>
                <span className="detail-value">{selectedStore.email || 'N/A'}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Wallet Address:</span>
                <span className="detail-value wallet">{selectedStore.wallet_address}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Credit Score:</span>
                <span className="detail-value">{selectedStore.credit_score || 0}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Status:</span>
                <span className={`detail-value status-badge ${selectedStore.status}`}>
                  {selectedStore.status === 'active' ? 'Active' : 'Inactive'}
                </span>
              </div>
              <div className="detail-row">
                <span className="detail-label">30-Day Sales:</span>
                <span className="detail-value">Rs. {(selectedStore.total_sales || 0).toFixed(2)}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Registered:</span>
                <span className="detail-value">
                  {selectedStore.registered_at 
                    ? new Date(selectedStore.registered_at).toLocaleDateString() 
                    : 'N/A'}
                </span>
              </div>
            </div>
            <div className="modal-actions">
              <button
                className="modal-button cancel"
                onClick={() => {
                  setShowViewModal(false);
                  setSelectedStore(null);
                }}
              >
                Close
              </button>
              <button
                className="modal-button primary"
                onClick={() => {
                  setShowViewModal(false);
                  handleEdit(selectedStore.id);
                }}
              >
                Edit
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StoreManagement;
