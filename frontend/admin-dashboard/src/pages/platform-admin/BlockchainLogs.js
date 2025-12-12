import React, { useState, useEffect } from 'react';
import apiService from '../../services/api';
import './BlockchainLogs.css';

const BlockchainLogs = () => {
  const [logs, setLogs] = useState([]);
  const [filteredLogs, setFilteredLogs] = useState([]);
  const [filters, setFilters] = useState({
    shopkeeper_id: '',
    date_from: '',
    date_to: '',
    type: 'all',
    status: 'all',
  });
  const [loading, setLoading] = useState(true);
  const [blockchainStatus, setBlockchainStatus] = useState(null);
  const [selectedLog, setSelectedLog] = useState(null);

  useEffect(() => {
    loadBlockchainLogs();
    loadBlockchainStatus();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [logs, filters]);

  const loadBlockchainLogs = async () => {
    try {
      setLoading(true);
      const data = await apiService.getBlockchainLogs({ page: 1, page_size: 100 });
      // Backend returns { logs: [...], pagination: {...} }
      const logsList = data.logs || data.data || data || [];
      setLogs(logsList);
      setFilteredLogs(logsList);
    } catch (error) {
      console.error('Error loading blockchain logs:', error);
      // Set empty array on error to prevent crashes
      setLogs([]);
      setFilteredLogs([]);
    } finally {
      setLoading(false);
    }
  };

  const loadBlockchainStatus = async () => {
    try {
      const status = await apiService.getBlockchainStatus();
      setBlockchainStatus(status);
    } catch (error) {
      console.error('Error loading blockchain status:', error);
      setBlockchainStatus({ available: false });
    }
  };

  const applyFilters = () => {
    let filtered = [...logs];

    if (filters.shopkeeper_id) {
      filtered = filtered.filter(
        (log) =>
          log.shopkeeper_id?.includes(filters.shopkeeper_id) ||
          log.shopkeeper_name?.toLowerCase().includes(filters.shopkeeper_id.toLowerCase())
      );
    }

    if (filters.date_from) {
      filtered = filtered.filter(
        (log) => new Date(log.timestamp) >= new Date(filters.date_from)
      );
    }

    if (filters.date_to) {
      filtered = filtered.filter(
        (log) => new Date(log.timestamp) <= new Date(filters.date_to)
      );
    }

    if (filters.type !== 'all') {
      filtered = filtered.filter((log) => log.type === filters.type);
    }

    if (filters.status !== 'all') {
      filtered = filtered.filter((log) =>
        filters.status === 'verified' ? log.has_blockchain_record : !log.has_blockchain_record
      );
    }

    setFilteredLogs(filtered);
  };

  const handleFilterChange = (key, value) => {
    setFilters({ ...filters, [key]: value });
  };

  const resetFilters = () => {
    setFilters({
      shopkeeper_id: '',
      date_from: '',
      date_to: '',
      type: 'all',
      status: 'all',
    });
  };

  const openPolygonScan = (txHash) => {
    if (txHash && !txHash.startsWith('pending-')) {
      const url = `https://amoy.polygonscan.com/tx/${txHash}`;
      window.open(url, '_blank');
    }
  };

  const getStatusColor = (log) => {
    if (log.has_blockchain_record) return '#34d399';
    if (log.status === 'pending' || log.status === 'pending_blockchain') return '#fbbf24';
    if (log.status === 'failed') return '#f87171';
    return '#9ca3af';
  };

  const getStatusText = (log) => {
    if (log.has_blockchain_record) return 'On Blockchain';
    if (log.status === 'pending' || log.status === 'pending_blockchain') return 'Pending';
    if (log.status === 'failed') return 'Failed';
    return log.db_status || log.status || 'Pending';
  };

  if (loading) {
    return (
      <div className="blockchain-logs">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading blockchain logs...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="blockchain-logs">
      <div className="page-header">
        <div className="header-content">
          <h1 className="page-title">Blockchain Logs</h1>
          <p className="page-subtitle">Transaction transparency and verification</p>
        </div>
        <div className="header-badge">
          <span className="read-only-badge">
            <span className="badge-icon">🔒</span>
            Read-Only
          </span>
        </div>
      </div>

      {/* Blockchain Status Banner */}
      {blockchainStatus && (
        <div className={`status-banner ${blockchainStatus.available ? 'connected' : 'disconnected'}`}>
          <div className="status-indicator"></div>
          <span className="status-text">
            Blockchain: {blockchainStatus.available ? 'Connected' : 'Not Available'}
          </span>
          {blockchainStatus.configured && (
            <span className="network-badge">
              Network: {blockchainStatus.network || 'Polygon Amoy'}
            </span>
          )}
        </div>
      )}

      {/* Filters */}
      <div className="filters-section">
        <div className="search-box">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            placeholder="Search by shopkeeper..."
            className="search-input"
            value={filters.shopkeeper_id}
            onChange={(e) => handleFilterChange('shopkeeper_id', e.target.value)}
          />
        </div>
        <div className="date-filters">
          <input
            type="date"
            className="date-input"
            value={filters.date_from}
            onChange={(e) => handleFilterChange('date_from', e.target.value)}
            placeholder="From Date"
          />
          <span className="date-separator">to</span>
          <input
            type="date"
            className="date-input"
            value={filters.date_to}
            onChange={(e) => handleFilterChange('date_to', e.target.value)}
            placeholder="To Date"
          />
        </div>
        <select
          className="filter-select"
          value={filters.type}
          onChange={(e) => handleFilterChange('type', e.target.value)}
        >
          <option value="all">All Types</option>
          <option value="sale">Sale</option>
          <option value="credit">Credit</option>
          <option value="repay">Repay</option>
        </select>
        <select
          className="filter-select"
          value={filters.status}
          onChange={(e) => handleFilterChange('status', e.target.value)}
        >
          <option value="all">All Status</option>
          <option value="verified">On Blockchain</option>
          <option value="pending">Pending</option>
        </select>
        <button className="reset-btn" onClick={resetFilters}>
          Reset
        </button>
      </div>

      {/* Summary Stats */}
      <div className="summary-stats">
        <div className="stat-card">
          <span className="stat-value">{filteredLogs.length}</span>
          <span className="stat-label">Total Transactions</span>
        </div>
        <div className="stat-card verified">
          <span className="stat-value">{filteredLogs.filter(l => l.has_blockchain_record).length}</span>
          <span className="stat-label">On Blockchain</span>
        </div>
        <div className="stat-card pending">
          <span className="stat-value">{filteredLogs.filter(l => !l.has_blockchain_record).length}</span>
          <span className="stat-label">Pending Verification</span>
        </div>
        <div className="stat-card amount">
          <span className="stat-value">₹{filteredLogs.reduce((sum, l) => sum + (l.amount || 0), 0).toLocaleString()}</span>
          <span className="stat-label">Total Value</span>
        </div>
      </div>

      {/* Logs Table */}
      <div className="table-container">
        <table className="logs-table">
          <thead>
            <tr>
              <th>Transaction Hash / ID</th>
              <th>Shopkeeper</th>
              <th>Type</th>
              <th>Amount</th>
              <th>Timestamp</th>
              <th>Verification</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredLogs.length > 0 ? (
              filteredLogs.map((log) => (
                <tr 
                  key={log.id} 
                  className={log.has_blockchain_record ? 'verified-row' : ''}
                  onClick={() => setSelectedLog(log)}
                >
                  <td className="hash-cell">
                    {log.has_blockchain_record ? (
                      <div className="hash-content">
                        <span className="chain-icon">⛓️</span>
                        <span className="hash-text" title={log.transaction_hash}>
                          {log.transaction_hash?.substring(0, 12)}...
                        </span>
                      </div>
                    ) : (
                      <div className="hash-content pending">
                        <span className="pending-icon">⏳</span>
                        <span className="hash-text" title={log.id}>
                          {log.id?.substring(0, 12)}...
                        </span>
                      </div>
                    )}
                  </td>
                  <td>
                    <div className="shopkeeper-cell">
                      <span className="shopkeeper-name">{log.shopkeeper_name || 'Unknown'}</span>
                    </div>
                  </td>
                  <td>
                    <span className={`type-badge type-${log.type}`}>
                      {log.type || 'N/A'}
                    </span>
                  </td>
                  <td className="amount-cell">₹{log.amount?.toLocaleString() || '0'}</td>
                  <td className="timestamp-cell">
                    {log.timestamp
                      ? new Date(log.timestamp).toLocaleString()
                      : 'N/A'}
                  </td>
                  <td>
                    <span 
                      className="status-badge"
                      style={{ 
                        background: `${getStatusColor(log)}20`,
                        color: getStatusColor(log),
                        borderColor: `${getStatusColor(log)}40`
                      }}
                    >
                      {getStatusText(log)}
                    </span>
                  </td>
                  <td>
                    {log.has_blockchain_record && log.transaction_hash && !log.transaction_hash.startsWith('pending-') ? (
                      <button
                        className="explorer-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          openPolygonScan(log.transaction_hash);
                        }}
                      >
                        View on PolygonScan
                      </button>
                    ) : (
                      <span className="no-action">—</span>
                    )}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="7" className="empty-cell">
                  <div className="empty-state">
                    <span className="empty-icon">⛓️</span>
                    <p>No transaction logs found</p>
                    <span className="empty-hint">Transactions will appear here once created</span>
                  </div>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Transaction Detail Modal */}
      {selectedLog && (
        <div className="modal-overlay" onClick={() => setSelectedLog(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">Transaction Details</h2>
              <span className="read-only-modal-badge">🔒 Read-Only</span>
            </div>
            
            <div className="transaction-details">
              <div className={`verification-banner ${selectedLog.has_blockchain_record ? 'verified' : 'pending'}`}>
                <span className="verification-icon">
                  {selectedLog.has_blockchain_record ? '✓' : '⏳'}
                </span>
                <span className="verification-text">
                  {selectedLog.has_blockchain_record 
                    ? 'Verified on Blockchain' 
                    : 'Pending Blockchain Verification'}
                </span>
              </div>

              <div className="detail-grid">
                <div className="detail-item full-width">
                  <span className="detail-label">Transaction Hash</span>
                  <span className="detail-value mono">
                    {selectedLog.transaction_hash || selectedLog.id}
                  </span>
                </div>
                
                {selectedLog.block_number && (
                  <div className="detail-item">
                    <span className="detail-label">Block Number</span>
                    <span className="detail-value">{selectedLog.block_number}</span>
                  </div>
                )}

                <div className="detail-item">
                  <span className="detail-label">Type</span>
                  <span className={`detail-value type-badge type-${selectedLog.type}`}>
                    {selectedLog.type}
                  </span>
                </div>

                <div className="detail-item">
                  <span className="detail-label">Amount</span>
                  <span className="detail-value amount">
                    ₹{selectedLog.amount?.toLocaleString()}
                  </span>
                </div>

                <div className="detail-item">
                  <span className="detail-label">Shopkeeper</span>
                  <span className="detail-value">{selectedLog.shopkeeper_name}</span>
                </div>

                <div className="detail-item">
                  <span className="detail-label">Timestamp</span>
                  <span className="detail-value">
                    {new Date(selectedLog.timestamp).toLocaleString()}
                  </span>
                </div>

                {selectedLog.customer_name && (
                  <div className="detail-item">
                    <span className="detail-label">Customer</span>
                    <span className="detail-value">{selectedLog.customer_name}</span>
                  </div>
                )}

                <div className="detail-item">
                  <span className="detail-label">Status</span>
                  <span 
                    className="detail-value"
                    style={{ color: getStatusColor(selectedLog) }}
                  >
                    {getStatusText(selectedLog)}
                  </span>
                </div>
              </div>

              {selectedLog.description && (
                <div className="description-section">
                  <span className="detail-label">Description</span>
                  <p className="description-text">{selectedLog.description}</p>
                </div>
              )}
            </div>

            <div className="modal-actions">
              <button
                className="modal-btn close-btn"
                onClick={() => setSelectedLog(null)}
              >
                Close
              </button>
              {selectedLog.has_blockchain_record && selectedLog.transaction_hash && (
                <button
                  className="modal-btn explorer-modal-btn"
                  onClick={() => openPolygonScan(selectedLog.transaction_hash)}
                >
                  🔗 View on PolygonScan
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BlockchainLogs;

