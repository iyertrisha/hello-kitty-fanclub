import React, { useState } from 'react';
import './StoreTable.css';

const StoreTable = ({
  stores,
  onView,
  onEdit,
  onDelete,
  onSearch,
  onFilter,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [scoreFilter, setScoreFilter] = useState('all');
  const [sortField, setSortField] = useState(null);
  const [sortDirection, setSortDirection] = useState('asc');

  const handleSearch = (e) => {
    const query = e.target.value;
    setSearchQuery(query);
    if (onSearch) {
      onSearch(query);
    }
  };

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const getScoreColor = (score) => {
    if (score >= 700) return '#34C759';
    if (score >= 500) return '#FF9500';
    return '#FF3B30';
  };

  const sortedStores = [...stores].sort((a, b) => {
    if (!sortField) return 0;
    const aVal = a[sortField];
    const bVal = b[sortField];
    if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
    if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
    return 0;
  });

  return (
    <div className="store-table-container">
      <div className="store-table-filters">
        <input
          type="text"
          placeholder="Search stores..."
          className="store-table-search"
          value={searchQuery}
          onChange={handleSearch}
        />
        <select
          className="store-table-filter"
          value={statusFilter}
          onChange={(e) => {
            setStatusFilter(e.target.value);
            if (onFilter) {
              onFilter({ status: e.target.value });
            }
          }}
        >
          <option value="all">All Status</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
        <select
          className="store-table-filter"
          value={scoreFilter}
          onChange={(e) => {
            setScoreFilter(e.target.value);
            if (onFilter) {
              onFilter({ scoreRange: e.target.value });
            }
          }}
        >
          <option value="all">All Scores</option>
          <option value="high">700+</option>
          <option value="medium">500-699</option>
          <option value="low">Below 500</option>
        </select>
      </div>

      <div className="store-table-wrapper">
        <table className="store-table">
          <thead>
            <tr>
              <th onClick={() => handleSort('name')}>
                Name {sortField === 'name' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('address')}>
                Address {sortField === 'address' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('credit_score')}>
                Credit Score {sortField === 'credit_score' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('total_sales')}>
                Total Sales {sortField === 'total_sales' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('status')}>
                Status {sortField === 'status' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {sortedStores.length > 0 ? (
              sortedStores.map((store) => (
                <tr key={store.id}>
                  <td>{store.name}</td>
                  <td>{store.address}</td>
                  <td>
                    <span
                      className="credit-score-badge"
                      style={{ color: getScoreColor(store.credit_score || 0) }}
                    >
                      {store.credit_score || 'N/A'}
                    </span>
                  </td>
                  <td>₹{store.total_sales?.toFixed(2) || '0.00'}</td>
                  <td>
                    <span
                      className={`status-badge ${
                        store.status === 'active' ? 'status-active' : 'status-inactive'
                      }`}
                    >
                      {store.status || 'active'}
                    </span>
                  </td>
                  <td>
                    <div className="action-buttons">
                      {onView && (
                        <button
                          className="action-button view-button"
                          onClick={() => onView(store.id)}
                        >
                          View
                        </button>
                      )}
                      {onEdit && (
                        <button
                          className="action-button edit-button"
                          onClick={() => onEdit(store.id)}
                        >
                          Edit
                        </button>
                      )}
                      {onDelete && (
                        <button
                          className="action-button delete-button"
                          onClick={() => onDelete(store.id)}
                        >
                          Delete
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="6" className="empty-message">
                  No stores found
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default StoreTable;

