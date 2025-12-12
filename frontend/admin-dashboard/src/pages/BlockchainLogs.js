import React, { useState, useEffect } from 'react';
import apiService from '../services/api';
import './BlockchainLogs.css';

const BlockchainLogs = () => {
  const [logs, setLogs] = useState([]);
  const [filteredLogs, setFilteredLogs] = useState([]);
  const [filters, setFilters] = useState({
    shopkeeper_id: '',
    date_from: '',
    date_to: '',
    type: 'all',
  });
  const [loading, setLoading] = useState(true);
  const [blockchainStatus, setBlockchainStatus] = useState(null);

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
      const data = await apiService.getBlockchainLogs();
      // Backend returns {logs: [...], pagination: {...}}
      const logsList = data.logs || data.data || data || [];
      setLogs(logsList);
      setFilteredLogs(logsList);
    } catch (error) {
      console.error('Error loading blockchain logs:', error);
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

    setFilteredLogs(filtered);
  };

  const handleFilterChange = (key, value) => {
    setFilters({ ...filters, [key]: value });
  };

  const openPolygonScan = (txHash) => {
    if (txHash && !txHash.startsWith('pending-')) {
      const url = `https://amoy.polygonscan.com/tx/${txHash}`;
      window.open(url, '_blank');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'verified':
        return '#34C759';
      case 'completed':
        return '#34C759';
      case 'pending':
      case 'pending_blockchain':
        return '#FF9500';
      case 'failed':
        return '#FF3B30';
      default:
        return '#8E8E93';
    }
  };

  const getStatusText = (log) => {
    if (log.has_blockchain_record) {
      return 'On Blockchain';
    }
    return log.db_status || log.status || 'Pending';
  };

  if (loading) {
    return (
      <div className="blockchain-logs-container">
        <div className="loading-message">Loading transaction logs...</div>
      </div>
    );
  }

  return (
    <div className="blockchain-logs-container">
      <h1 className="page-title">Transaction & Blockchain Logs</h1>

      {/* Blockchain Status Banner */}
      {blockchainStatus && (
        <div className={`blockchain-status-banner ${blockchainStatus.available ? 'available' : 'unavailable'}`}>
          <span className="status-icon">{blockchainStatus.available ? '🟢' : '🔴'}</span>
          <span>
            Blockchain Service: {blockchainStatus.available ? 'Connected' : 'Not Available'}
            {blockchainStatus.configured && ` | Network: ${blockchainStatus.network || 'Local'}`}
          </span>
        </div>
      )}

      {/* Filters */}
      <div className="filters-section">
        <input
          type="text"
          placeholder="Search by Shopkeeper..."
          className="filter-input"
          value={filters.shopkeeper_id}
          onChange={(e) => handleFilterChange('shopkeeper_id', e.target.value)}
        />
        <input
          type="date"
          className="filter-input"
          value={filters.date_from}
          onChange={(e) => handleFilterChange('date_from', e.target.value)}
        />
        <input
          type="date"
          className="filter-input"
          value={filters.date_to}
          onChange={(e) => handleFilterChange('date_to', e.target.value)}
        />
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
        <button
          className="filter-reset-button"
          onClick={() =>
            setFilters({
              shopkeeper_id: '',
              date_from: '',
              date_to: '',
              type: 'all',
            })
          }
        >
          Reset Filters
        </button>
      </div>

      {/* Summary */}
      <div className="logs-summary">
        <span>Total: {filteredLogs.length} transactions</span>
        <span>On Blockchain: {filteredLogs.filter(l => l.has_blockchain_record).length}</span>
        <span>Pending: {filteredLogs.filter(l => !l.has_blockchain_record).length}</span>
      </div>

      {/* Logs Table */}
      <div className="logs-table-container">
        <table className="logs-table">
          <thead>
            <tr>
              <th>Transaction Hash / ID</th>
              <th>Shopkeeper</th>
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
                <tr key={log.id} className={log.has_blockchain_record ? 'blockchain-verified' : ''}>
                  <td className="hash-cell">
                    {log.has_blockchain_record ? (
                      <span className="hash-text" title={log.transaction_hash}>
                        {log.transaction_hash?.substring(0, 10)}...
                      </span>
                    ) : (
                      <span className="pending-hash" title="Not yet on blockchain">
                        {log.id?.substring(0, 12)}...
                      </span>
                    )}
                  </td>
                  <td>
                    <div className="shopkeeper-cell">
                      <span className="shopkeeper-name">{log.shopkeeper_name || 'Unknown'}</span>
                      <span className="shopkeeper-id">{log.shopkeeper_id?.substring(0, 8)}...</span>
                    </div>
                  </td>
                  <td>
                    <span className={`type-badge type-${log.type}`}>{log.type || 'N/A'}</span>
                  </td>
                  <td className="amount-cell">Rs. {log.amount?.toFixed(2) || '0.00'}</td>
                  <td>
                    {log.timestamp
                      ? new Date(log.timestamp).toLocaleString()
                      : 'N/A'}
                  </td>
                  <td>
                    <span
                      className={`status-badge ${log.has_blockchain_record ? 'on-chain' : 'off-chain'}`}
                      style={{ color: getStatusColor(log.status) }}
                    >
                      {getStatusText(log)}
                    </span>
                  </td>
                  <td>
                    {log.has_blockchain_record && log.transaction_hash && !log.transaction_hash.startsWith('pending-') ? (
                      <button
                        className="view-button"
                        onClick={() => openPolygonScan(log.transaction_hash)}
                      >
                        View on PolygonScan
                      </button>
                    ) : (
                      <span className="no-action">-</span>
                    )}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="7" className="empty-message">
                  No transaction logs found. Transactions will appear here once created.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default BlockchainLogs;
