import React, { useState, useEffect } from 'react';
import apiService from '../services/api';
import StoreTable from '../components/StoreTable';
import './StoreManagement.css';

const StoreManagement = () => {
  const [stores, setStores] = useState([]);
  const [filteredStores, setFilteredStores] = useState([]);
  const [loading, setLoading] = useState(true);

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

  const handleView = (storeId) => {
    // Navigate to store details page
    console.log('View store:', storeId);
    alert(`View store details for ID: ${storeId}`);
  };

  const handleEdit = (storeId) => {
    // Open edit modal or navigate to edit page
    console.log('Edit store:', storeId);
    alert(`Edit store ID: ${storeId}`);
  };

  const handleDelete = (storeId) => {
    if (window.confirm('Are you sure you want to delete this store?')) {
      apiService
        .deleteStore(storeId)
        .then(() => {
          alert('Store deleted successfully');
          loadStores();
        })
        .catch((error) => {
          console.error('Error deleting store:', error);
          alert('Failed to delete store');
        });
    }
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
        <button className="add-store-button">+ Add Store</button>
      </div>

      <StoreTable
        stores={filteredStores}
        onView={handleView}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onSearch={handleSearch}
        onFilter={handleFilter}
      />
    </div>
  );
};

export default StoreManagement;

