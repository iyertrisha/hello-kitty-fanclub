import React, { useState, useEffect } from 'react';
import apiService from '../../services/api';
import './StoreManagement.css';

const StoreManagement = () => {
  const [stores, setStores] = useState([]);
  const [filteredStores, setFilteredStores] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showViewModal, setShowViewModal] = useState(false);
  const [showFlagModal, setShowFlagModal] = useState(false);
  const [selectedStore, setSelectedStore] = useState(null);
  const [flagReason, setFlagReason] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [scoreFilter, setScoreFilter] = useState('all');
  const [flagFilter, setFlagFilter] = useState('all');
  const [sortField, setSortField] = useState('name');
  const [sortDirection, setSortDirection] = useState('asc');

  useEffect(() => {
    loadStores();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [stores, searchQuery, statusFilter, scoreFilter, flagFilter, sortField, sortDirection]);

  const loadStores = async () => {
    try {
      setLoading(true);
      const data = await apiService.getStores();
      const storesList = data.stores || data.data || data || [];
      const mappedStores = storesList.map(store => ({
        ...store,
        status: store.is_active ? 'active' : 'inactive',
        total_sales: store.total_sales_30d || 0,
        is_flagged: store.is_flagged || false,
        flag_reason: store.flag_reason || '',
      }));
      setStores(mappedStores);
      setFilteredStores(mappedStores);
    } catch (error) {
      console.error('Error loading stores:', error);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...stores];

    // Search filter
    if (searchQuery) {
      filtered = filtered.filter(
        (store) =>
          store.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
          store.address?.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter((store) => store.status === statusFilter);
    }

    // Score filter
    if (scoreFilter !== 'all') {
      filtered = filtered.filter((store) => {
        const score = store.credit_score || 0;
        if (scoreFilter === 'high') return score >= 700;
        if (scoreFilter === 'medium') return score >= 500 && score < 700;
        if (scoreFilter === 'low') return score < 500;
        return true;
      });
    }

    // Flag filter
    if (flagFilter !== 'all') {
      filtered = filtered.filter((store) => 
        flagFilter === 'flagged' ? store.is_flagged : !store.is_flagged
      );
    }

    // Sorting
    filtered.sort((a, b) => {
      let aVal = a[sortField];
      let bVal = b[sortField];
      if (typeof aVal === 'string') aVal = aVal.toLowerCase();
      if (typeof bVal === 'string') bVal = bVal.toLowerCase();
      if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });

    setFilteredStores(filtered);
  };

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const handleView = (store) => {
    setSelectedStore(store);
    setShowViewModal(true);
  };

  const handleFlagClick = (store) => {
    setSelectedStore(store);
    setFlagReason(store.flag_reason || '');
    setShowFlagModal(true);
  };

  const handleFlagSubmit = async () => {
    if (!flagReason.trim()) {
      alert('Please provide a reason for flagging');
      return;
    }

    try {
      await apiService.flagStore(selectedStore.id, flagReason);
      alert('Store flagged successfully');
      setShowFlagModal(false);
      setFlagReason('');
      setSelectedStore(null);
      loadStores();
    } catch (error) {
      console.error('Error flagging store:', error);
      alert('Failed to flag store: ' + (error.response?.data?.message || error.message));
    }
  };

  const handleUnflag = async (storeId) => {
    if (window.confirm('Are you sure you want to remove the flag from this store?')) {
      try {
        await apiService.unflagStore(storeId);
        alert('Flag removed successfully');
        loadStores();
      } catch (error) {
        console.error('Error removing flag:', error);
        alert('Failed to remove flag: ' + (error.response?.data?.message || error.message));
      }
    }
  };

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

  if (loading) {
    return (
      <div className="store-management">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading stores...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="store-management">
      <div className="page-header">
        <div className="header-content">
          <h1 className="page-title">Store Management</h1>
          <p className="page-subtitle">Monitor stores and flag issues for review</p>
        </div>
        <div className="header-badges">
          <span className="read-only-badge">
            <span className="badge-icon">🔒</span>
            Read-Only
          </span>
          <span className="flag-badge">
            <span className="badge-icon">🚩</span>
            {stores.filter(s => s.is_flagged).length} Flagged
          </span>
        </div>
      </div>

      {/* Filters */}
      <div className="filters-section">
        <div className="search-box">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            placeholder="Search by name or address..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="filter-select"
        >
          <option value="all">All Status</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
        <select
          value={scoreFilter}
          onChange={(e) => setScoreFilter(e.target.value)}
          className="filter-select"
        >
          <option value="all">All Scores</option>
          <option value="high">700+ (Excellent)</option>
          <option value="medium">500-699 (Good)</option>
          <option value="low">Below 500 (Needs Attention)</option>
        </select>
        <select
          value={flagFilter}
          onChange={(e) => setFlagFilter(e.target.value)}
          className="filter-select"
        >
          <option value="all">All Stores</option>
          <option value="flagged">Flagged Only</option>
          <option value="unflagged">Not Flagged</option>
        </select>
      </div>

      {/* Summary */}
      <div className="summary-bar">
        <span className="summary-item">
          <strong>{filteredStores.length}</strong> stores found
        </span>
        <span className="summary-divider">|</span>
        <span className="summary-item score-high">
          <span className="dot"></span>
          {filteredStores.filter(s => (s.credit_score || 0) >= 700).length} Excellent
        </span>
        <span className="summary-item score-medium">
          <span className="dot"></span>
          {filteredStores.filter(s => (s.credit_score || 0) >= 500 && (s.credit_score || 0) < 700).length} Good
        </span>
        <span className="summary-item score-low">
          <span className="dot"></span>
          {filteredStores.filter(s => (s.credit_score || 0) < 500).length} Needs Attention
        </span>
      </div>

      {/* Store Table */}
      <div className="table-container">
        <table className="store-table">
          <thead>
            <tr>
              <th onClick={() => handleSort('name')} className="sortable">
                Store Name
                {sortField === 'name' && <span className="sort-icon">{sortDirection === 'asc' ? '↑' : '↓'}</span>}
              </th>
              <th onClick={() => handleSort('address')} className="sortable">
                Address
                {sortField === 'address' && <span className="sort-icon">{sortDirection === 'asc' ? '↑' : '↓'}</span>}
              </th>
              <th onClick={() => handleSort('credit_score')} className="sortable">
                Vishwas Score
                {sortField === 'credit_score' && <span className="sort-icon">{sortDirection === 'asc' ? '↑' : '↓'}</span>}
              </th>
              <th onClick={() => handleSort('status')} className="sortable">
                Status
                {sortField === 'status' && <span className="sort-icon">{sortDirection === 'asc' ? '↑' : '↓'}</span>}
              </th>
              <th>Flag Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredStores.length > 0 ? (
              filteredStores.map((store) => (
                <tr key={store.id} className={store.is_flagged ? 'flagged-row' : ''}>
                  <td>
                    <div className="store-name-cell">
                      <span className="store-name">{store.name}</span>
                      {store.is_flagged && <span className="flag-indicator">🚩</span>}
                    </div>
                  </td>
                  <td className="address-cell">{store.address}</td>
                  <td>
                    <div className="score-cell">
                      <span 
                        className="score-value"
                        style={{ color: getScoreColor(store.credit_score || 0) }}
                      >
                        {store.credit_score || 'N/A'}
                      </span>
                      <span 
                        className="score-label"
                        style={{ color: getScoreColor(store.credit_score || 0) }}
                      >
                        {store.credit_score ? getScoreLabel(store.credit_score) : ''}
                      </span>
                    </div>
                  </td>
                  <td>
                    <span className={`status-badge status-${store.status}`}>
                      {store.status === 'active' ? '● Active' : '○ Inactive'}
                    </span>
                  </td>
                  <td>
                    {store.is_flagged ? (
                      <span className="flag-badge-cell">
                        🚩 Flagged
                      </span>
                    ) : (
                      <span className="no-flag">—</span>
                    )}
                  </td>
                  <td>
                    <div className="action-buttons">
                      <button
                        className="action-btn view-btn"
                        onClick={() => handleView(store)}
                      >
                        View
                      </button>
                      {store.is_flagged ? (
                        <button
                          className="action-btn unflag-btn"
                          onClick={() => handleUnflag(store.id)}
                        >
                          Unflag
                        </button>
                      ) : (
                        <button
                          className="action-btn flag-btn"
                          onClick={() => handleFlagClick(store)}
                        >
                          Flag
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="6" className="empty-cell">
                  <div className="empty-state">
                    <span className="empty-icon">🏪</span>
                    <p>No stores found matching your criteria</p>
                  </div>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* View Store Modal */}
      {showViewModal && selectedStore && (
        <div className="modal-overlay" onClick={() => setShowViewModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">Store Details</h2>
              <span className="read-only-modal-badge">🔒 Read-Only</span>
            </div>
            
            <div className="store-details">
              {selectedStore.is_flagged && (
                <div className="flag-alert">
                  <span className="flag-alert-icon">🚩</span>
                  <div className="flag-alert-content">
                    <strong>This store is flagged</strong>
                    <p>{selectedStore.flag_reason}</p>
                  </div>
                </div>
              )}
              
              <div className="detail-grid">
                <div className="detail-item">
                  <span className="detail-label">Store Name</span>
                  <span className="detail-value">{selectedStore.name}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Address</span>
                  <span className="detail-value">{selectedStore.address}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Phone</span>
                  <span className="detail-value">{selectedStore.phone || 'N/A'}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Email</span>
                  <span className="detail-value">{selectedStore.email || 'N/A'}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Status</span>
                  <span className={`detail-value status-${selectedStore.status}`}>
                    {selectedStore.status === 'active' ? '● Active' : '○ Inactive'}
                  </span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Registered</span>
                  <span className="detail-value">
                    {selectedStore.registered_at 
                      ? new Date(selectedStore.registered_at).toLocaleDateString() 
                      : 'N/A'}
                  </span>
                </div>
              </div>

              <div className="score-detail-section">
                <h3>Vishwas Score</h3>
                <div className="score-detail">
                  <div 
                    className="score-circle"
                    style={{ 
                      borderColor: getScoreColor(selectedStore.credit_score || 0),
                      color: getScoreColor(selectedStore.credit_score || 0)
                    }}
                  >
                    <span className="score-number">{selectedStore.credit_score || 'N/A'}</span>
                    <span className="score-max">/900</span>
                  </div>
                  <div className="score-info">
                    <span 
                      className="score-status"
                      style={{ color: getScoreColor(selectedStore.credit_score || 0) }}
                    >
                      {selectedStore.credit_score ? getScoreLabel(selectedStore.credit_score) : 'No Score'}
                    </span>
                    <p className="score-desc">
                      {selectedStore.credit_score >= 700 
                        ? 'This store has excellent creditworthiness'
                        : selectedStore.credit_score >= 500
                        ? 'This store has good creditworthiness'
                        : 'This store needs attention'}
                    </p>
                  </div>
                </div>
              </div>

              <div className="wallet-detail">
                <span className="detail-label">Wallet Address</span>
                <span className="wallet-value">{selectedStore.wallet_address}</span>
              </div>
            </div>

            <div className="modal-actions">
              <button
                className="modal-btn close-btn"
                onClick={() => setShowViewModal(false)}
              >
                Close
              </button>
              {!selectedStore.is_flagged && (
                <button
                  className="modal-btn flag-modal-btn"
                  onClick={() => {
                    setShowViewModal(false);
                    handleFlagClick(selectedStore);
                  }}
                >
                  🚩 Flag Store
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Flag Store Modal */}
      {showFlagModal && selectedStore && (
        <div className="modal-overlay" onClick={() => setShowFlagModal(false)}>
          <div className="modal-content flag-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">🚩 Flag Store for Review</h2>
            </div>
            
            <div className="flag-form">
              <p className="flag-store-name">
                Flagging: <strong>{selectedStore.name}</strong>
              </p>
              
              <div className="flag-input-group">
                <label className="flag-label">Reason for Flagging *</label>
                <textarea
                  className="flag-textarea"
                  value={flagReason}
                  onChange={(e) => setFlagReason(e.target.value)}
                  placeholder="Describe the issue or concern..."
                  rows="4"
                />
              </div>

              <div className="flag-note">
                <span className="note-icon">ℹ️</span>
                <p>
                  Flagging a store does not delete or modify any data. 
                  It marks the store for review by the team.
                </p>
              </div>
            </div>

            <div className="modal-actions">
              <button
                className="modal-btn cancel-btn"
                onClick={() => {
                  setShowFlagModal(false);
                  setFlagReason('');
                }}
              >
                Cancel
              </button>
              <button
                className="modal-btn submit-flag-btn"
                onClick={handleFlagSubmit}
              >
                Submit Flag
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StoreManagement;

