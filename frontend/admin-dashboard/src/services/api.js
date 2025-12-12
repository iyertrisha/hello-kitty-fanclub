import axios from 'axios';
import { mockApiService } from './mockApi';
// Base API URL - Update this to match your Flask API
const API_BASE_URL = 'http://localhost:5000/api';

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
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API Methods
export const apiService = {
  // Admin Overview
  getOverviewStats: async () => {
    return await mockApiService.getOverviewStats();
    //const response = await api.get('/admin/overview');
    //return response.data;
  },

  // Store Management
  getStores: async (filters = {}) => {
    //const response = await api.get('/admin/stores', { params: filters });
    //return response.data;
    return await mockApiService.getStores(filters);
  },

  updateStore: async (storeId, data) => {
    //const response = await api.put(`/admin/stores/${storeId}`, data);
    //return response.data;
    return await mockApiService.updateStore(storeId, data);
  },

  deleteStore: async (storeId) => {
    //const response = await api.delete(`/admin/stores/${storeId}`);
    //return response.data;
    return await mockApiService.deleteStore(storeId);
  },

  // Cooperative Management
  getCooperatives: async () => {
    //const response = await api.get('/admin/cooperatives');
    //return response.data;
    return await mockApiService.getCooperatives();
  },

  createCooperative: async (data) => {
    //const response = await api.post('/admin/cooperatives', data);
    //return response.data;
    return await mockApiService.createCooperative(data);
  },

  updateCooperative: async (coopId, data) => {
    //const response = await api.put(`/admin/cooperatives/${coopId}`, data);
    //return response.data;
    return await mockApiService.updateCooperative(coopId, data);
  },

  deleteCooperative: async (coopId) => {
    //const response = await api.delete(`/admin/cooperatives/${coopId}`);
    //return response.data;
    return await mockApiService.deleteCooperative(coopId);
  },

  getCooperativeMembers: async (coopId) => {
    //const response = await api.get(`/admin/cooperatives/${coopId}/members`);
    //return response.data;
    return await mockApiService.getCooperativeMembers(coopId);
  },

  addCooperativeMember: async (coopId, shopkeeperId) => {
    //const response = await api.post(
      //`/admin/cooperatives/${coopId}/members`,
      //{ shopkeeper_id: shopkeeperId }
    //);
    //return response.data;
    return await mockApiService.addCooperativeMember(coopId, shopkeeperId);
  },

  removeCooperativeMember: async (coopId, shopkeeperId) => {
    //const response = await api.delete(
      //`/admin/cooperatives/${coopId}/members/${shopkeeperId}`
    //);
    //return response.data;
    return await mockApiService.removeCooperativeMember(coopId, shopkeeperId);
  },

  // Analytics
  getAnalytics: async (dateRange = {}) => {
    //const response = await api.get('/admin/analytics', { params: dateRange });
    //return response.data;
    return await mockApiService.getAnalytics(dateRange);
    
  },

  // Blockchain Logs
  getBlockchainLogs: async (filters = {}) => {
    //const response = await api.get('/admin/blockchain-logs', {
      //params: filters,
    //);
    //return response.data;
    return await mockApiService.getBlockchainLogs(filters);
  },
};

export default apiService;

