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
      localStorage.removeItem('admin_token');
    }
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// API Methods
export const apiService = {
  // ==========================================
  // PLATFORM ADMIN ENDPOINTS (Read-Only)
  // ==========================================

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

  // Store Management (Read-Only + Flagging)
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

  // Flag store for review (Platform Admin only action)
  flagStore: async (storeId, reason) => {
    try {
      const response = await api.post(`/admin/stores/${storeId}/flag`, { reason });
      return response.data;
    } catch (error) {
      console.error('Error flagging store:', error);
      throw error;
    }
  },

  // Remove flag from store
  unflagStore: async (storeId) => {
    try {
      const response = await api.delete(`/admin/stores/${storeId}/flag`);
      return response.data;
    } catch (error) {
      console.error('Error unflagging store:', error);
      throw error;
    }
  },

  // Analytics (Read-Only)
  getAnalytics: async (params = {}) => {
    try {
      const response = await api.get('/admin/analytics', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching analytics:', error);
      throw error;
    }
  },

  // Blockchain Logs (Read-Only - All transactions)
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

  // All Credit Scores (Platform Admin)
  getAllCreditScores: async () => {
    try {
      const response = await api.get('/admin/credit-scores');
      return response.data;
    } catch (error) {
      console.error('Error fetching credit scores:', error);
      throw error;
    }
  },

  // ==========================================
  // AGGREGATOR/COOPERATIVE ENDPOINTS
  // ==========================================

  // Cooperative Overview
  getCooperativeOverview: async (cooperativeId) => {
    try {
      const response = await api.get(`/cooperative/${cooperativeId}/overview`);
      return response.data;
    } catch (error) {
      console.error('Error fetching cooperative overview:', error);
      // Return mock data for now
      return {
        name: 'Delhi Kirana Network',
        member_count: 42,
        revenue: { today: 45000, week: 312000, month: 1250000 },
        active_orders: 23,
        sales_growth: 23,
        order_volume: 156,
        avg_order_value: 450,
        recent_activity: []
      };
    }
  },

  // Cooperative Members (Read-Only)
  getCooperativeMembers: async (cooperativeId) => {
    try {
      const response = await api.get(`/cooperative/${cooperativeId}/members`);
      return response.data;
    } catch (error) {
      console.error('Error fetching cooperative members:', error);
      throw error;
    }
  },

  // Cooperative Member Credit Scores
  getCooperativeMemberScores: async (cooperativeId) => {
    try {
      const response = await api.get(`/cooperative/${cooperativeId}/member-scores`);
      return response.data;
    } catch (error) {
      console.error('Error fetching member scores:', error);
      // Return mock data
      return {
        scores: [
          { name: 'Krishna Store', credit_score: 845 },
          { name: 'Gupta Provisions', credit_score: 720 },
          { name: 'Sharma Kirana', credit_score: 680 },
          { name: 'Verma Mart', credit_score: 590 },
          { name: 'Singh Store', credit_score: 420 },
        ]
      };
    }
  },

  // Geographic Map Data
  getCooperativeMapData: async (cooperativeId) => {
    try {
      const response = await api.get(`/cooperative/${cooperativeId}/map-data`);
      return response.data;
    } catch (error) {
      console.error('Error fetching map data:', error);
      throw error;
    }
  },

  // Cooperative Orders
  getCooperativeOrders: async (cooperativeId, filters = {}) => {
    try {
      const response = await api.get(`/cooperative/${cooperativeId}/orders`, { params: filters });
      return response.data;
    } catch (error) {
      console.error('Error fetching cooperative orders:', error);
      throw error;
    }
  },

  // Update Order Status
  updateOrderStatus: async (cooperativeId, orderId, status) => {
    try {
      const response = await api.put(`/cooperative/${cooperativeId}/orders/${orderId}/status`, { status });
      return response.data;
    } catch (error) {
      console.error('Error updating order status:', error);
      throw error;
    }
  },

  // Cooperative Blockchain Logs
  getCooperativeBlockchainLogs: async (cooperativeId, filters = {}) => {
    try {
      const response = await api.get(`/cooperative/${cooperativeId}/blockchain-logs`, { params: filters });
      return response.data;
    } catch (error) {
      console.error('Error fetching cooperative blockchain logs:', error);
      throw error;
    }
  },


  // ==========================================
  // SHARED/UTILITY ENDPOINTS
  // ==========================================

  // Cooperatives List
  getCooperatives: async () => {
    try {
      const response = await api.get('/admin/cooperatives');
      return response.data;
    } catch (error) {
      console.error('Error fetching cooperatives:', error);
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

  // ==========================================
  // LEGACY ENDPOINTS (for backward compatibility)
  // ==========================================

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
};

export default apiService;
