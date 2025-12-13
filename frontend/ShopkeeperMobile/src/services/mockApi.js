// Mock API service for development and testing

export const mockApiService = {
  getTransactions: async (params = {}) => ({
    data: Array.from({ length: 5 }, (_, i) => ({
      id: i + 1,
      type: ['sale', 'credit', 'repay'][i % 3],
      amount: Math.floor(Math.random() * 5000) + 100,
      customer: { id: i + 1, name: `Customer ${i + 1}` },
      timestamp: new Date(Date.now() - i * 24 * 60 * 60 * 1000).toISOString(),
      status: ['verified', 'pending'][i % 2],
      blockchain_hash: i % 2 === 0 ? `0x${Math.random().toString(16).substr(2, 64)}` : null,
    })),
  }),

  getCreditScore: async () => ({
    score: 725,
    blockchain_verified: true,
    factors: {
      transaction_history: 85,
      credit_repayment: 90,
      blockchain_verification: 95,
      cooperative_participation: 75,
      payment_timeliness: 88,
      transaction_volume: 82,
    },
    explanation: 'Your score is based on transaction history, credit repayment, blockchain verification, and cooperative participation. Your score has improved by 15 points this month due to timely repayments.',
    last_updated: new Date().toISOString(),
    previous_score: 710,
    score_trend: [
      { month: 'Jan', score: 680 },
      { month: 'Feb', score: 695 },
      { month: 'Mar', score: 710 },
      { month: 'Apr', score: 725 },
    ],
  }),

  getInventory: async () => ({
    data: [
      { id: 1, name: 'Rice (1kg)', price: 85, stock_quantity: 45, category: 'Groceries', last_restocked: '2024-01-15' },
      { id: 2, name: 'Wheat Flour (5kg)', price: 220, stock_quantity: 32, category: 'Groceries', last_restocked: '2024-01-14' },
      { id: 3, name: 'Cooking Oil (1L)', price: 150, stock_quantity: 28, category: 'Groceries', last_restocked: '2024-01-13' },
      { id: 4, name: 'Sugar (1kg)', price: 45, stock_quantity: 67, category: 'Groceries', last_restocked: '2024-01-12' },
      { id: 5, name: 'Mobile Charger', price: 299, stock_quantity: 8, category: 'Electronics', last_restocked: '2024-01-10' },
      { id: 6, name: 'USB Cable', price: 149, stock_quantity: 5, category: 'Electronics', last_restocked: '2024-01-09' },
      { id: 7, name: 'T-Shirt', price: 399, stock_quantity: 12, category: 'Clothing', last_restocked: '2024-01-08' },
      { id: 8, name: 'Jeans', price: 899, stock_quantity: 6, category: 'Clothing', last_restocked: '2024-01-07' },
      { id: 9, name: 'Soap', price: 35, stock_quantity: 89, category: 'Personal Care', last_restocked: '2024-01-16' },
      { id: 10, name: 'Shampoo (200ml)', price: 125, stock_quantity: 24, category: 'Personal Care', last_restocked: '2024-01-15' },
      { id: 11, name: 'Toothpaste', price: 75, stock_quantity: 42, category: 'Personal Care', last_restocked: '2024-01-14' },
      { id: 12, name: 'Biscuits (500g)', price: 55, stock_quantity: 38, category: 'Snacks', last_restocked: '2024-01-13' },
    ],
  }),

  getCooperatives: async () => ({
    data: [
      {
        id: 1,
        name: 'City Central Cooperative',
        description: 'A cooperative focused on bulk purchasing and shared resources for shopkeepers in the city center. We negotiate better prices through collective buying power.',
        revenue_split: 15,
        total_members: 12,
        established: '2023-01-15',
        total_orders: 45,
        total_revenue: 1250000,
        members: Array.from({ length: 12 }, (_, j) => ({
          id: j + 1,
          name: `Shopkeeper ${j + 1}`,
          address: `${j + 1} Main Street, City Center`,
          phone: `+91 98765${String(j + 1).padStart(5, '0')}`,
          joined_date: '2023-01-15',
          total_contribution: Math.floor(Math.random() * 100000) + 50000,
        })),
      },
      {
        id: 2,
        name: 'North Market Alliance',
        description: 'Cooperative serving shopkeepers in the northern market area. Special focus on fresh produce and daily essentials.',
        revenue_split: 20,
        total_members: 8,
        established: '2023-03-20',
        total_orders: 32,
        total_revenue: 890000,
        members: Array.from({ length: 8 }, (_, j) => ({
          id: j + 1,
          name: `Shopkeeper ${j + 1}`,
          address: `${j + 1} North Market Road`,
          phone: `+91 98765${String(j + 1).padStart(5, '0')}`,
          joined_date: '2023-03-20',
          total_contribution: Math.floor(Math.random() * 80000) + 40000,
        })),
      },
      {
        id: 3,
        name: 'South Zone Merchants',
        description: 'A community-driven cooperative for merchants in the southern zone. We focus on sustainable practices and fair trade.',
        revenue_split: 12,
        total_members: 15,
        established: '2022-11-10',
        total_orders: 78,
        total_revenue: 2100000,
        members: Array.from({ length: 15 }, (_, j) => ({
          id: j + 1,
          name: `Shopkeeper ${j + 1}`,
          address: `${j + 1} South Zone Avenue`,
          phone: `+91 98765${String(j + 1).padStart(5, '0')}`,
          joined_date: '2022-11-10',
          total_contribution: Math.floor(Math.random() * 120000) + 60000,
        })),
      },
    ],
  }),

  createTransaction: async (data) => ({
    id: Math.floor(Math.random() * 1000),
    status: 'pending',
    ...data,
  }),

  uploadAudio: async () => ({
    transcript: 'Customer purchased items worth 500 rupees',
  }),
};



