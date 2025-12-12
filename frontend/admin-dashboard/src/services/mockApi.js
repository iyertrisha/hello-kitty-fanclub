// Mock API service for testing without backend
export const mockApiService = {
    getOverviewStats: async () => {
      return {
        total_stores: 25,
        transactions: { today: 45, week: 320, month: 1250 },
        revenue: { today: 12500, week: 87500, month: 350000 },
        active_cooperatives: 8,
        recent_activity: [
          { type: 'transaction', message: 'New transaction recorded', timestamp: new Date() },
          { type: 'cooperative', message: 'New cooperative created', timestamp: new Date() },
        ],
        sales_trend: Array.from({ length: 30 }, (_, i) => ({
          date: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000).toISOString(),
          amount: Math.floor(Math.random() * 50000) + 10000,
        })),
      };
    },
  
    getStores: async () => {
      return {
        data: Array.from({ length: 10 }, (_, i) => ({
          id: i + 1,
          name: `Store ${i + 1}`,
          address: `Address ${i + 1}, City`,
          credit_score: Math.floor(Math.random() * 600) + 300,
          total_sales: Math.floor(Math.random() * 100000) + 10000,
          status: i % 3 === 0 ? 'inactive' : 'active',
        })),
      };
    },
  
    getCooperatives: async () => {
      return {
        data: Array.from({ length: 5 }, (_, i) => ({
          id: i + 1,
          name: `Cooperative ${i + 1}`,
          description: `Description for cooperative ${i + 1}`,
          revenue_split: (i + 1) * 10,
          members: Array.from({ length: i + 2 }, (_, j) => ({
            id: j + 1,
            name: `Member ${j + 1}`,
            address: `Address ${j + 1}`,
          })),
        })),
      };
    },
  
    getAnalytics: async () => {
      return {
        sales_trend: Array.from({ length: 30 }, (_, i) => ({
          date: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000).toISOString(),
          amount: Math.floor(Math.random() * 50000) + 10000,
        })),
        credit_scores: [
          { range: '300-500', count: 5 },
          { range: '500-700', count: 12 },
          { range: '700-900', count: 8 },
        ],
        revenue_by_coop: Array.from({ length: 5 }, (_, i) => ({
          coop_id: i + 1,
          name: `Coop ${i + 1}`,
          revenue: Math.floor(Math.random() * 100000) + 20000,
        })),
        transaction_volume: Array.from({ length: 30 }, (_, i) => ({
          date: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000).toISOString(),
          count: Math.floor(Math.random() * 50) + 10,
        })),
      };
    },
  
    getBlockchainLogs: async () => {
      return {
        data: Array.from({ length: 15 }, (_, i) => ({
          id: i + 1,
          transaction_hash: `0x${Math.random().toString(16).substr(2, 64)}`,
          shopkeeper_id: Math.floor(Math.random() * 10) + 1,
          type: ['transaction', 'credit_score', 'registration'][Math.floor(Math.random() * 3)],
          block_number: 1000000 + i,
          timestamp: new Date(Date.now() - i * 24 * 60 * 60 * 1000).toISOString(),
          status: ['verified', 'pending', 'failed'][Math.floor(Math.random() * 3)],
        })),
      };
    },
  };