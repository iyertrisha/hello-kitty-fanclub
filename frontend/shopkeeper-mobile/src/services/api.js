import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
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
    // const response = await api.get('/transactions', { params });
    // return response.data;
  },

  createTransaction: async (data) => {
    // Mock data for testing
    return await mockApiService.createTransaction(data);
    
    // Real API call:
    // const response = await api.post('/transactions', data);
    // return response.data;
  },

  getTransactionById: async (id) => {
    // Mock implementation
    const transactions = await mockApiService.getTransactions();
    const transaction = transactions.data.find(t => t.id === parseInt(id));
    return transaction || null;
    
    // Real API call:
    // const response = await api.get(`/transactions/${id}`);
    // return response.data;
  },

  updateTransactionStatus: async (id, status) => {
    // Mock implementation
    return { success: true, id, status, message: 'Status updated successfully' };
    
    // Real API call:
    // const response = await api.put(`/transactions/${id}/status`, { status });
    // return response.data;
  },

  uploadAudio: async (audioFile) => {
    // Mock data for testing
    return await mockApiService.uploadAudio(audioFile);
    
    // Real API call:
    // const formData = new FormData();
    // formData.append('audio', {
    //   uri: audioFile.uri,
    //   type: 'audio/m4a',
    //   name: 'recording.m4a',
    // });
    // const response = await api.post('/transactions/transcribe', formData, {
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
    // const response = await api.get(`/shopkeeper/${id}`);
    // return response.data;
  },

  updateShopkeeperProfile: async (id, data) => {
    // Mock implementation
    return { success: true, id, ...data, message: 'Profile updated successfully' };
    
    // Real API call:
    // const response = await api.put(`/shopkeeper/${id}`, data);
    // return response.data;
  },

  getCreditScore: async (shopkeeperId) => {
    // Mock data for testing
    return await mockApiService.getCreditScore(shopkeeperId);
    
    // Real API call:
    // const response = await api.get(`/shopkeeper/${shopkeeperId}/credit-score`);
    // return response.data;
  },

  getInventory: async (shopkeeperId) => {
    // Mock data for testing
    return await mockApiService.getInventory(shopkeeperId);
    
    // Real API call:
    // const response = await api.get(`/shopkeeper/${shopkeeperId}/inventory`);
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
    //   `/shopkeeper/${shopkeeperId}/inventory/${productId}`,
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
    //   `/shopkeeper/${shopkeeperId}/inventory`,
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
    //   `/shopkeeper/${shopkeeperId}/inventory/${productId}`
    // );
    // return response.data;
  },

  // Cooperative endpoints
  getCooperatives: async () => {
    // Mock data for testing
    return await mockApiService.getCooperatives();
    
    // Real API call:
    // const response = await api.get('/cooperative');
    // return response.data;
  },

  getCooperativeById: async (id) => {
    // Mock implementation
    const cooperatives = await mockApiService.getCooperatives();
    const cooperative = cooperatives.data.find(c => c.id === parseInt(id));
    return cooperative || null;
    
    // Real API call:
    // const response = await api.get(`/cooperative/${id}`);
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
    // const response = await api.post(`/cooperative/${coopId}/join`);
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
    // const response = await api.post(`/cooperative/${coopId}/leave`);
    // return response.data;
  },

  getCooperativeMembers: async (coopId) => {
    // Mock implementation
    const cooperatives = await mockApiService.getCooperatives();
    const cooperative = cooperatives.data.find(c => c.id === parseInt(coopId));
    return cooperative ? { data: cooperative.members } : { data: [] };
    
    // Real API call:
    // const response = await api.get(`/cooperative/${coopId}/members`);
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
    // const response = await api.get(`/cooperative/${coopId}/orders`);
    // return response.data;
  },
};

export default apiService;

