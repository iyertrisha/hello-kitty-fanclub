import React, { useState, useEffect } from 'react';
import apiService from '../services/api';
import CooperativeCard from '../components/CooperativeCard';
import './Cooperatives.css';

const Cooperatives = () => {
  const [cooperatives, setCooperatives] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    revenue_split: '',
  });

  useEffect(() => {
    loadCooperatives();
  }, []);

  const loadCooperatives = async () => {
    try {
      setLoading(true);
      const data = await apiService.getCooperatives();
      const coopList = data.data || data || [];
      setCooperatives(coopList);
    } catch (error) {
      console.error('Error loading cooperatives:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCooperative = async () => {
    if (!formData.name) {
      alert('Please enter a cooperative name');
      return;
    }

    try {
      await apiService.createCooperative({
        name: formData.name,
        description: formData.description,
        revenue_split: parseFloat(formData.revenue_split) || 0,
      });
      alert('Cooperative created successfully');
      setShowCreateModal(false);
      setFormData({ name: '', description: '', revenue_split: '' });
      loadCooperatives();
    } catch (error) {
      console.error('Error creating cooperative:', error);
      alert('Failed to create cooperative');
    }
  };

  const handleEdit = (coopId) => {
    console.log('Edit cooperative:', coopId);
    alert(`Edit cooperative ID: ${coopId}`);
  };

  const handleViewDetails = (coopId) => {
    console.log('View cooperative details:', coopId);
    alert(`View details for cooperative ID: ${coopId}`);
  };

  const handleAddMembers = (coopId) => {
    console.log('Add members to cooperative:', coopId);
    alert(`Add members to cooperative ID: ${coopId}`);
  };

  const handleDelete = (coopId) => {
    if (window.confirm('Are you sure you want to delete this cooperative?')) {
      apiService
        .deleteCooperative(coopId)
        .then(() => {
          alert('Cooperative deleted successfully');
          loadCooperatives();
        })
        .catch((error) => {
          console.error('Error deleting cooperative:', error);
          alert('Failed to delete cooperative');
        });
    }
  };

  if (loading) {
    return (
      <div className="cooperatives-container">
        <div className="loading-message">Loading cooperatives...</div>
      </div>
    );
  }

  return (
    <div className="cooperatives-container">
      <div className="page-header">
        <h1 className="page-title">Cooperatives</h1>
        <button
          className="create-cooperative-button"
          onClick={() => setShowCreateModal(true)}
        >
          + Create Cooperative
        </button>
      </div>

      <div className="cooperatives-list">
        {cooperatives.length > 0 ? (
          cooperatives.map((coop) => (
            <CooperativeCard
              key={coop.id}
              cooperative={coop}
              onEdit={handleEdit}
              onViewDetails={handleViewDetails}
              onAddMembers={handleAddMembers}
              onDelete={handleDelete}
            />
          ))
        ) : (
          <div className="empty-message">No cooperatives found</div>
        )}
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2 className="modal-title">Create Cooperative</h2>
            <div className="modal-form">
              <label className="modal-label">
                Name *
                <input
                  type="text"
                  className="modal-input"
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                  placeholder="Enter cooperative name"
                />
              </label>
              <label className="modal-label">
                Description
                <textarea
                  className="modal-textarea"
                  value={formData.description}
                  onChange={(e) =>
                    setFormData({ ...formData, description: e.target.value })
                  }
                  placeholder="Enter description"
                  rows="4"
                />
              </label>
              <label className="modal-label">
                Revenue Split (%)
                <input
                  type="number"
                  className="modal-input"
                  value={formData.revenue_split}
                  onChange={(e) =>
                    setFormData({ ...formData, revenue_split: e.target.value })
                  }
                  placeholder="0"
                  min="0"
                  max="100"
                />
              </label>
              <div className="modal-actions">
                <button
                  className="modal-button cancel"
                  onClick={() => setShowCreateModal(false)}
                >
                  Cancel
                </button>
                <button
                  className="modal-button primary"
                  onClick={handleCreateCooperative}
                >
                  Create
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Cooperatives;

