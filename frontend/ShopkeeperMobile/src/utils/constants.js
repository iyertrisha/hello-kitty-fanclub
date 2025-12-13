// Colors
export const COLORS = {
  primary: '#6200ee',
  primaryDark: '#3700b3',
  primaryLight: '#bb86fc',
  secondary: '#03dac6',
  background: '#f5f5f5',
  surface: '#ffffff',
  error: '#b00020',
  onPrimary: '#ffffff',
  onSecondary: '#000000',
  onBackground: '#000000',
  onSurface: '#000000',
  onError: '#ffffff',
  text: '#212121',
  textSecondary: '#757575',
  border: '#e0e0e0',
  success: '#4caf50',
  warning: '#ff9800',
  info: '#2196f3',
};

// API Endpoints
export const API_ENDPOINTS = {
  BASE_URL: 'http://localhost:5000/api',
  TRANSACTIONS: '/transactions',
  TRANSACTIONS_TRANSCRIBE: '/transactions/transcribe',
  SHOPKEEPER: '/shopkeeper',
  SHOPKEEPER_CREDIT_SCORE: (id) => `/shopkeeper/${id}/credit-score`,
  SHOPKEEPER_INVENTORY: (id) => `/shopkeeper/${id}/inventory`,
  COOPERATIVE: '/cooperative',
  COOPERATIVE_MEMBERS: (id) => `/cooperative/${id}/members`,
  COOPERATIVE_JOIN: (id) => `/cooperative/${id}/join`,
  COOPERATIVE_LEAVE: (id) => `/cooperative/${id}/leave`,
  BLOCKCHAIN_CREDIT_SCORE: (id) => `/blockchain/credit-score/${id}`,
};

// Sizes
export const SIZES = {
  padding: 16,
  margin: 16,
  borderRadius: 8,
  iconSize: 24,
  buttonHeight: 48,
  inputHeight: 48,
};

// Transaction Types
export const TRANSACTION_TYPES = {
  SALE: 'sale',
  CREDIT: 'credit',
  REPAY: 'repay',
};

// Transaction Status
export const TRANSACTION_STATUS = {
  PENDING: 'pending',
  VERIFIED: 'verified',
  DISPUTED: 'disputed',
};

// Credit Score Ranges
export const CREDIT_SCORE_RANGES = {
  POOR: { min: 300, max: 499, label: 'Poor', color: COLORS.error },
  FAIR: { min: 500, max: 649, label: 'Fair', color: COLORS.warning },
  GOOD: { min: 650, max: 799, label: 'Good', color: COLORS.info },
  EXCELLENT: { min: 800, max: 900, label: 'Excellent', color: COLORS.success },
};



