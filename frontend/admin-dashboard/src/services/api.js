import axios from 'axios';

// Base API URL - Update this to match your Flask API
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('admin_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized - clear token and redirect to login
      localStorage.removeItem('admin_token');
      // Don't redirect for now as we don't have login page
      // window.location.href = '/login';
    }
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// API Methods - Connected to real Flask backend
export const apiService = {
  // Admin Overview
  getOverviewStats: async () => {
    try {
      const response = await api.get('/admin/overview');
      return response.data;
    } catch (error) {
      console.error('Error fetching overview stats:', error);
      throw error;
    }
  },

  // Store Management
  getStores: async (filters = {}) => {
    try {
      const response = await api.get('/admin/stores', { params: filters });
      return response.data;
    } catch (error) {
      console.error('Error fetching stores:', error);
      throw error;
    }
  },

  getStore: async (storeId) => {
    try {
      const response = await api.get(`/shopkeeper/${storeId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching store:', error);
      throw error;
    }
  },

  createStore: async (data) => {
    try {
      const response = await api.post('/shopkeeper/register', data);
      return response.data;
    } catch (error) {
      console.error('Error creating store:', error);
      throw error;
    }
  },

  updateStore: async (storeId, data) => {
    try {
      const response = await api.put(`/shopkeeper/${storeId}`, data);
      return response.data;
    } catch (error) {
      console.error('Error updating store:', error);
      throw error;
    }
  },

  deleteStore: async (storeId) => {
    try {
      const response = await api.delete(`/shopkeeper/${storeId}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting store:', error);
      throw error;
    }
  },

  toggleStoreStatus: async (storeId) => {
    try {
      const response = await api.post(`/shopkeeper/${storeId}/toggle-status`);
      return response.data;
    } catch (error) {
      console.error('Error toggling store status:', error);
      throw error;
    }
  },

  // Cooperative Management
  getCooperatives: async () => {
    try {
      const response = await api.get('/admin/cooperatives');
      return response.data;
    } catch (error) {
      console.error('Error fetching cooperatives:', error);
      throw error;
    }
  },

  createCooperative: async (data) => {
    try {
      const response = await api.post('/admin/cooperatives', data);
      return response.data;
    } catch (error) {
      console.error('Error creating cooperative:', error);
      throw error;
    }
  },

  updateCooperative: async (coopId, data) => {
    try {
      const response = await api.put(`/cooperative/${coopId}`, data);
      return response.data;
    } catch (error) {
      console.error('Error updating cooperative:', error);
      throw error;
    }
  },

  deleteCooperative: async (coopId) => {
    try {
      const response = await api.delete(`/cooperative/${coopId}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting cooperative:', error);
      throw error;
    }
  },

  getCooperativeMembers: async (coopId) => {
    try {
      const response = await api.get(`/cooperative/${coopId}/members`);
      return response.data;
    } catch (error) {
      console.error('Error fetching cooperative members:', error);
      throw error;
    }
  },

  addCooperativeMember: async (coopId, shopkeeperId) => {
    try {
      const response = await api.post(`/cooperative/${coopId}/join`, {
        shopkeeper_id: shopkeeperId
      });
      return response.data;
    } catch (error) {
      console.error('Error adding cooperative member:', error);
      throw error;
    }
  },

  removeCooperativeMember: async (coopId, shopkeeperId) => {
    try {
      const response = await api.delete(`/cooperative/${coopId}/members/${shopkeeperId}`);
      return response.data;
    } catch (error) {
      console.error('Error removing cooperative member:', error);
      throw error;
    }
  },

  // Analytics
  getAnalytics: async (dateRange = {}) => {
    try {
      const response = await api.get('/admin/analytics', { params: dateRange });
      return response.data;
    } catch (error) {
      console.error('Error fetching analytics:', error);
      throw error;
    }
  },

  // Blockchain Logs
  getBlockchainLogs: async (filters = {}) => {
    try {
      const response = await api.get('/admin/blockchain-logs', { params: filters });
      return response.data;
    } catch (error) {
      console.error('Error fetching blockchain logs:', error);
      throw error;
    }
  },

  // Blockchain Status
  getBlockchainStatus: async () => {
    try {
      const response = await api.get('/blockchain/status');
      return response.data;
    } catch (error) {
      console.error('Error fetching blockchain status:', error);
      throw error;
    }
  },

  // Transactions
  getTransactions: async (filters = {}) => {
    try {
      const response = await api.get('/transactions', { params: filters });
      return response.data;
    } catch (error) {
      console.error('Error fetching transactions:', error);
      throw error;
    }
  },

  // Shopkeeper Credit Score
  getShopkeeperCreditScore: async (shopkeeperId) => {
    try {
      const response = await api.get(`/shopkeeper/${shopkeeperId}/credit-score`);
      return response.data;
    } catch (error) {
      console.error('Error fetching credit score:', error);
      throw error;
    }
  },
};

export default apiService;
