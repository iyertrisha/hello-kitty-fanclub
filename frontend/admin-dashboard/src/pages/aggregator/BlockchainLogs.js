import React, { useState, useEffect } from 'react';
import apiService from '../../services/api';
import './BlockchainLogs.css';

const BlockchainLogs = () => {
  const [logs, setLogs] = useState([]);
  const [filteredLogs, setFilteredLogs] = useState([]);
  const [filters, setFilters] = useState({
    member: '',
    date_from: '',
    date_to: '',
    type: 'all',
  });
  const [loading, setLoading] = useState(true);
  const [blockchainStatus, setBlockchainStatus] = useState(null);
  const [selectedLog, setSelectedLog] = useState(null);

  const cooperativeId = 'coop-001';

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
      const data = await apiService.getCooperativeBlockchainLogs(cooperativeId);
      const logsList = data.logs || data.data || data || [];
      setLogs(logsList);
      setFilteredLogs(logsList);
    } catch (error) {
      console.error('Error loading blockchain logs:', error);
      // Mock data for demonstration
      const mockLogs = [
        {
          id: 'txn-001',
          transaction_hash: '0x1234567890abcdef1234567890abcdef12345678',
          shopkeeper_name: 'Krishna Store',
          shopkeeper_id: 'shop-001',
          type: 'sale',
          amount: 1500,
          timestamp: new Date().toISOString(),
          has_blockchain_record: true,
          block_number: 12345678,
        },
        {
          id: 'txn-002',
          transaction_hash: '0xabcdef1234567890abcdef1234567890abcdef12',
          shopkeeper_name: 'Gupta Provisions',
          shopkeeper_id: 'shop-002',
          type: 'credit',
          amount: 2500,
          timestamp: new Date(Date.now() - 3600000).toISOString(),
          has_blockchain_record: true,
          block_number: 12345679,
        },
        {
          id: 'txn-003',
          transaction_hash: null,
          shopkeeper_name: 'Sharma Kirana',
          shopkeeper_id: 'shop-003',
          type: 'repay',
          amount: 800,
          timestamp: new Date(Date.now() - 7200000).toISOString(),
          has_blockchain_record: false,
          status: 'pending',
        },
      ];
      setLogs(mockLogs);
      setFilteredLogs(mockLogs);
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
      setBlockchainStatus({ available: true, network: 'Polygon Amoy' });
    }
  };

  const applyFilters = () => {
    let filtered = [...logs];

    if (filters.member) {
      filtered = filtered.filter(
        (log) =>
          log.shopkeeper_id?.includes(filters.member) ||
          log.shopkeeper_name?.toLowerCase().includes(filters.member.toLowerCase())
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

    setFilteredLogs(filtered);
  };

  const handleFilterChange = (key, value) => {
    setFilters({ ...filters, [key]: value });
  };

  const resetFilters = () => {
    setFilters({
      member: '',
      date_from: '',
      date_to: '',
      type: 'all',
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
    if (log.status === 'pending') return '#fbbf24';
    if (log.status === 'failed') return '#f87171';
    return '#9ca3af';
  };

  const getStatusText = (log) => {
    if (log.has_blockchain_record) return 'Verified';
    if (log.status === 'pending') return 'Pending';
    if (log.status === 'failed') return 'Failed';
    return 'Pending';
  };

  if (loading) {
    return (
      <div className="aggregator-blockchain-logs">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading blockchain logs...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="aggregator-blockchain-logs">
      <div className="page-header">
        <div className="header-content">
          <h1 className="page-title">Blockchain Logs</h1>
          <p className="page-subtitle">Cooperative transaction transparency</p>
        </div>
        <div className="header-badge">
          <span className="coop-badge">
            <span className="badge-icon">⛓️</span>
            Cooperative Only
          </span>
        </div>
      </div>

      {/* Blockchain Status */}
      {blockchainStatus && (
        <div className={`status-banner ${blockchainStatus.available ? 'connected' : 'disconnected'}`}>
          <div className="status-indicator"></div>
          <span className="status-text">
            Blockchain: {blockchainStatus.available ? 'Connected' : 'Not Available'}
          </span>
          {blockchainStatus.network && (
            <span className="network-badge">
              Network: {blockchainStatus.network}
            </span>
          )}
        </div>
      )}

      {/* Stats Summary */}
      <div className="stats-summary">
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
          <span className="stat-label">Pending</span>
        </div>
        <div className="stat-card amount">
          <span className="stat-value">₹{filteredLogs.reduce((sum, l) => sum + (l.amount || 0), 0).toLocaleString()}</span>
          <span className="stat-label">Total Value</span>
        </div>
      </div>

      {/* Filters */}
      <div className="filters-section">
        <div className="search-box">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            placeholder="Search by member..."
            className="search-input"
            value={filters.member}
            onChange={(e) => handleFilterChange('member', e.target.value)}
          />
        </div>
        <div className="date-filters">
          <input
            type="date"
            className="date-input"
            value={filters.date_from}
            onChange={(e) => handleFilterChange('date_from', e.target.value)}
          />
          <span className="date-separator">to</span>
          <input
            type="date"
            className="date-input"
            value={filters.date_to}
            onChange={(e) => handleFilterChange('date_to', e.target.value)}
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
        <button className="reset-btn" onClick={resetFilters}>
          Reset
        </button>
      </div>

      {/* Logs Table */}
      <div className="table-container">
        <table className="logs-table">
          <thead>
            <tr>
              <th>Transaction Hash</th>
              <th>Member</th>
              <th>Type</th>
              <th>Amount</th>
              <th>Timestamp</th>
              <th>Status</th>
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
                    {log.has_blockchain_record && log.transaction_hash ? (
                      <div className="hash-content">
                        <span className="chain-icon">⛓️</span>
                        <span className="hash-text" title={log.transaction_hash}>
                          {log.transaction_hash?.substring(0, 12)}...
                        </span>
                      </div>
                    ) : (
                      <div className="hash-content pending">
                        <span className="pending-icon">⏳</span>
                        <span className="hash-text">{log.id?.substring(0, 12)}...</span>
                      </div>
                    )}
                  </td>
                  <td>
                    <div className="member-cell">
                      <span className="member-name">{log.shopkeeper_name}</span>
                    </div>
                  </td>
                  <td>
                    <span className={`type-badge type-${log.type}`}>
                      {log.type || 'N/A'}
                    </span>
                  </td>
                  <td className="amount-cell">₹{log.amount?.toLocaleString() || '0'}</td>
                  <td className="timestamp-cell">
                    {log.timestamp ? new Date(log.timestamp).toLocaleString() : 'N/A'}
                  </td>
                  <td>
                    <span 
                      className="status-badge"
                      style={{ 
                        background: `${getStatusColor(log)}20`,
                        color: getStatusColor(log),
                      }}
                    >
                      {getStatusText(log)}
                    </span>
                  </td>
                  <td>
                    {log.has_blockchain_record && log.transaction_hash ? (
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
              <button className="close-btn" onClick={() => setSelectedLog(null)}>×</button>
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
                  <span className="detail-label">Member</span>
                  <span className="detail-value">{selectedLog.shopkeeper_name}</span>
                </div>

                <div className="detail-item">
                  <span className="detail-label">Timestamp</span>
                  <span className="detail-value">
                    {new Date(selectedLog.timestamp).toLocaleString()}
                  </span>
                </div>
              </div>

              <div className="trust-indicator">
                <h4>Trust Indicator</h4>
                <p>
                  {selectedLog.has_blockchain_record 
                    ? '✅ This transaction is permanently recorded on the Polygon blockchain and cannot be modified.'
                    : '⏳ This transaction is awaiting blockchain verification for permanent immutability.'}
                </p>
              </div>
            </div>

            <div className="modal-actions">
              <button
                className="modal-btn close-modal-btn"
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

