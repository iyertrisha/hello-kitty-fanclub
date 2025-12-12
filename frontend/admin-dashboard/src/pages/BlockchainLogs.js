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

  useEffect(() => {
    loadBlockchainLogs();
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

  const applyFilters = () => {
    let filtered = [...logs];

    if (filters.shopkeeper_id) {
      filtered = filtered.filter(
        (log) => log.shopkeeper_id === filters.shopkeeper_id
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
    const url = `https://amoy.polygonscan.com/tx/${txHash}`;
    window.open(url, '_blank');
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'verified':
        return '#34C759';
      case 'pending':
        return '#FF9500';
      case 'failed':
        return '#FF3B30';
      default:
        return '#8E8E93';
    }
  };

  if (loading) {
    return (
      <div className="blockchain-logs-container">
        <div className="loading-message">Loading blockchain logs...</div>
      </div>
    );
  }

  return (
    <div className="blockchain-logs-container">
      <h1 className="page-title">Blockchain Logs</h1>

      {/* Filters */}
      <div className="filters-section">
        <input
          type="text"
          placeholder="Shopkeeper ID"
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
          <option value="transaction">Transaction</option>
          <option value="credit_score">Credit Score</option>
          <option value="registration">Registration</option>
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

      {/* Logs Table */}
      <div className="logs-table-container">
        <table className="logs-table">
          <thead>
            <tr>
              <th>Transaction Hash</th>
              <th>Shopkeeper ID</th>
              <th>Type</th>
              <th>Block Number</th>
              <th>Timestamp</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredLogs.length > 0 ? (
              filteredLogs.map((log) => (
                <tr key={log.id}>
                  <td className="hash-cell">
                    {log.transaction_hash
                      ? `${log.transaction_hash.substring(0, 10)}...`
                      : 'N/A'}
                  </td>
                  <td>{log.shopkeeper_id || 'N/A'}</td>
                  <td>
                    <span className="type-badge">{log.type || 'N/A'}</span>
                  </td>
                  <td>{log.block_number || 'N/A'}</td>
                  <td>
                    {log.timestamp
                      ? new Date(log.timestamp).toLocaleString()
                      : 'N/A'}
                  </td>
                  <td>
                    <span
                      className="status-badge"
                      style={{ color: getStatusColor(log.status) }}
                    >
                      {log.status || 'unknown'}
                    </span>
                  </td>
                  <td>
                    {log.transaction_hash && (
                      <button
                        className="view-button"
                        onClick={() => openPolygonScan(log.transaction_hash)}
                      >
                        View on PolygonScan
                      </button>
                    )}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="7" className="empty-message">
                  No blockchain logs found
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

