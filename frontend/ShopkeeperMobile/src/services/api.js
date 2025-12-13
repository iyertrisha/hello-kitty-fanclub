import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { mockApiService } from './mockApi';
import { API_ENDPOINTS } from '../utils/constants';

// Base API URL - Update this to match your Flask API
// For device testing, use your computer's IP address instead of localhost
const API_BASE_URL = API_ENDPOINTS.BASE_URL;

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
  async (config) => {
    const token = await AsyncStorage.getItem('auth_token');
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
  async (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized - clear token and redirect to login
      await AsyncStorage.removeItem('auth_token');
    }
    return Promise.reject(error);
  }
);

// API Methods - Using Mock Data for Testing
// When backend is ready, uncomment the real API calls and comment out mock calls
export const apiService = {
  // Transaction endpoints
  getTransactions: async (params = {}) => {
    // Mock data for testing
    return await mockApiService.getTransactions(params);
    
    // Real API call (uncomment when backend is ready):
    // const response = await api.get(API_ENDPOINTS.TRANSACTIONS, { params });
    // return response.data;
  },

  createTransaction: async (data) => {
    // Mock data for testing
    return await mockApiService.createTransaction(data);
    
    // Real API call:
    // const response = await api.post(API_ENDPOINTS.TRANSACTIONS, data);
    // return response.data;
  },

  getTransactionById: async (id) => {
    // Mock implementation
    const transactions = await mockApiService.getTransactions();
    const transaction = transactions.data.find(t => t.id === parseInt(id));
    return transaction || null;
    
    // Real API call:
    // const response = await api.get(`${API_ENDPOINTS.TRANSACTIONS}/${id}`);
    // return response.data;
  },

  updateTransactionStatus: async (id, status) => {
    // Mock implementation
    return { success: true, id, status, message: 'Status updated successfully' };
    
    // Real API call:
    // const response = await api.put(`${API_ENDPOINTS.TRANSACTIONS}/${id}/status`, { status });
    // return response.data;
  },

  uploadAudio: async (audioFile) => {
    // Mock data for testing
    return await mockApiService.uploadAudio(audioFile);
    
    // Real API call (React Native CLI compatible):
    // Option 1: Send as base64
    // const response = await api.post(API_ENDPOINTS.TRANSACTIONS_TRANSCRIBE, {
    //   audio: audioFile.base64,
    //   mimeType: audioFile.type,
    //   filename: audioFile.name,
    // });
    // return response.data;
    
    // Option 2: Send as FormData (if backend supports it)
    // const FormData = require('form-data');
    // const formData = new FormData();
    // formData.append('audio', {
    //   uri: audioFile.uri,
    //   type: audioFile.type || 'audio/m4a',
    //   name: audioFile.name || 'recording.m4a',
    // });
    // const response = await api.post(API_ENDPOINTS.TRANSACTIONS_TRANSCRIBE, formData, {
    //   headers: {
    //     'Content-Type': 'multipart/form-data',
    //   },
    // });
    // return response.data;
  },

  // Shopkeeper endpoints
  getShopkeeperProfile: async (id) => {
    // Mock implementation
    return {
      id: id || '1',
      name: `Shopkeeper ${id || '1'}`,
      address: `123 Main Street, City ${id || '1'}`,
      phone: `+91 98765${String(id || '1').padStart(5, '0')}`,
      email: `shopkeeper${id || '1'}@example.com`,
      wallet_address: `0x${Math.random().toString(16).substr(2, 40)}`,
      registered_at: new Date().toISOString(),
    };
    
    // Real API call:
    // const response = await api.get(`${API_ENDPOINTS.SHOPKEEPER}/${id}`);
    // return response.data;
  },

  updateShopkeeperProfile: async (id, data) => {
    // Mock implementation
    return { success: true, id, ...data, message: 'Profile updated successfully' };
    
    // Real API call:
    // const response = await api.put(`${API_ENDPOINTS.SHOPKEEPER}/${id}`, data);
    // return response.data;
  },

  getCreditScore: async (shopkeeperId) => {
    // Mock data for testing
    return await mockApiService.getCreditScore(shopkeeperId);
    
    // Real API call:
    // const response = await api.get(API_ENDPOINTS.SHOPKEEPER_CREDIT_SCORE(shopkeeperId));
    // return response.data;
  },

  getInventory: async (shopkeeperId) => {
    // Mock data for testing
    return await mockApiService.getInventory(shopkeeperId);
    
    // Real API call:
    // const response = await api.get(API_ENDPOINTS.SHOPKEEPER_INVENTORY(shopkeeperId));
    // return response.data;
  },

  updateInventory: async (shopkeeperId, productId, data) => {
    // Mock implementation
    return { 
      success: true, 
      id: productId, 
      shopkeeper_id: shopkeeperId,
      ...data,
      message: 'Product updated successfully' 
    };
    
    // Real API call:
    // const response = await api.put(
    //   `${API_ENDPOINTS.SHOPKEEPER_INVENTORY(shopkeeperId)}/${productId}`,
    //   data
    // );
    // return response.data;
  },

  addProduct: async (shopkeeperId, data) => {
    // Mock implementation
    return { 
      success: true, 
      id: Math.floor(Math.random() * 1000), 
      shopkeeper_id: shopkeeperId,
      ...data,
      message: 'Product added successfully' 
    };
    
    // Real API call:
    // const response = await api.post(
    //   API_ENDPOINTS.SHOPKEEPER_INVENTORY(shopkeeperId),
    //   data
    // );
    // return response.data;
  },

  deleteProduct: async (shopkeeperId, productId) => {
    // Mock implementation
    return { 
      success: true, 
      id: productId,
      message: 'Product deleted successfully' 
    };
    
    // Real API call:
    // const response = await api.delete(
    //   `${API_ENDPOINTS.SHOPKEEPER_INVENTORY(shopkeeperId)}/${productId}`
    // );
    // return response.data;
  },

  // Cooperative endpoints
  getCooperatives: async () => {
    // Mock data for testing
    return await mockApiService.getCooperatives();
    
    // Real API call:
    // const response = await api.get(API_ENDPOINTS.COOPERATIVE);
    // return response.data;
  },

  getCooperativeById: async (id) => {
    // Mock implementation
    const cooperatives = await mockApiService.getCooperatives();
    const cooperative = cooperatives.data.find(c => c.id === parseInt(id));
    return cooperative || null;
    
    // Real API call:
    // const response = await api.get(`${API_ENDPOINTS.COOPERATIVE}/${id}`);
    // return response.data;
  },

  joinCooperative: async (coopId) => {
    // Mock implementation
    return { 
      success: true, 
      cooperative_id: coopId,
      message: 'Successfully joined cooperative' 
    };
    
    // Real API call:
    // const response = await api.post(API_ENDPOINTS.COOPERATIVE_JOIN(coopId));
    // return response.data;
  },

  leaveCooperative: async (coopId) => {
    // Mock implementation
    return { 
      success: true, 
      cooperative_id: coopId,
      message: 'Successfully left cooperative' 
    };
    
    // Real API call:
    // const response = await api.post(API_ENDPOINTS.COOPERATIVE_LEAVE(coopId));
    // return response.data;
  },

  getCooperativeMembers: async (coopId) => {
    // Mock implementation
    const cooperatives = await mockApiService.getCooperatives();
    const cooperative = cooperatives.data.find(c => c.id === parseInt(coopId));
    return cooperative ? { data: cooperative.members } : { data: [] };
    
    // Real API call:
    // const response = await api.get(API_ENDPOINTS.COOPERATIVE_MEMBERS(coopId));
    // return response.data;
  },

  getCooperativeOrders: async (coopId) => {
    // Mock implementation
    return {
      data: Array.from({ length: 5 }, (_, i) => ({
        id: i + 1,
        cooperative_id: parseInt(coopId),
        total_amount: Math.floor(Math.random() * 10000) + 1000,
        status: ['pending', 'completed', 'cancelled'][i % 3],
        created_at: new Date(Date.now() - i * 7 * 24 * 60 * 60 * 1000).toISOString(),
        items: Array.from({ length: Math.floor(Math.random() * 5) + 1 }, (_, j) => ({
          id: j + 1,
          name: `Item ${j + 1}`,
          quantity: Math.floor(Math.random() * 10) + 1,
          price: Math.floor(Math.random() * 500) + 50,
        })),
      })),
    };
    
    // Real API call:
    // const response = await api.get(`${API_ENDPOINTS.COOPERATIVE}/${coopId}/orders`);
    // return response.data;
  },
};

export default apiService;



