import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Important for session cookies
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Session expired or invalid
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const supplierApi = {
  // Authentication - OTP based
  requestOTP: async (email) => {
    const response = await api.post('/supplier/login/request-otp', { email });
    return response.data;
  },

  verifyOTP: async (email, otpCode) => {
    const response = await api.post('/supplier/login/verify-otp', { email, otp_code: otpCode });
    return response.data;
  },

  checkSession: async () => {
    const response = await api.get('/supplier/session');
    return response.data;
  },

  logout: async () => {
    const response = await api.post('/supplier/logout');
    return response.data;
  },

  // Registration (optional)
  register: async (data) => {
    const response = await api.post('/supplier/register', data);
    return response.data;
  },

  getSupplier: async (supplierId) => {
    const response = await api.get(`/supplier/${supplierId}`);
    return response.data;
  },

  // Service Area (uses session)
  updateServiceArea: async (serviceAreaData) => {
    const response = await api.put('/supplier/service-area', serviceAreaData);
    return response.data;
  },

  // Stores (uses session)
  getStores: async () => {
    const response = await api.get('/supplier/stores');
    return response.data;
  },

  // Orders (uses session)
  createOrder: async (orderData) => {
    const response = await api.post('/supplier/orders', orderData);
    return response.data;
  },

  getOrders: async () => {
    const response = await api.get('/supplier/orders');
    return response.data;
  },

  getOrder: async (orderId) => {
    const response = await api.get(`/supplier/orders/${orderId}`);
    return response.data;
  },

  updateOrderStatus: async (orderId, status) => {
    const response = await api.put(`/supplier/orders/${orderId}/status`, { status });
    return response.data;
  },

  cancelOrder: async (orderId) => {
    const response = await api.delete(`/supplier/orders/${orderId}`);
    return response.data;
  },

  // Analytics
  getAnalyticsOverview: async () => {
    const response = await api.get('/supplier/analytics/overview');
    return response.data;
  },

  getAnalyticsOrders: async (dateRange) => {
    const response = await api.get('/supplier/analytics/orders', { params: dateRange });
    return response.data;
  },

  getAnalyticsStores: async () => {
    const response = await api.get('/supplier/analytics/stores');
    return response.data;
  },

  getAnalyticsRevenue: async (dateRange) => {
    const response = await api.get('/supplier/analytics/revenue', { params: dateRange });
    return response.data;
  },
};

export default api;

