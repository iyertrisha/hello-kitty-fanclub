// Mock API for mobile app testing
export const mockApiService = {
    getTransactions: async () => ({
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
      score: Math.floor(Math.random() * 600) + 300,
      blockchain_verified: true,
      factors: {
        transaction_history: 85,
        credit_repayment: 90,
        blockchain_verification: 95,
        cooperative_participation: 75,
      },
      explanation: 'Your score is based on transaction history, credit repayment, and blockchain verification.',
    }),
  
    getInventory: async () => ({
      data: Array.from({ length: 8 }, (_, i) => ({
        id: i + 1,
        name: `Product ${i + 1}`,
        price: Math.floor(Math.random() * 500) + 50,
        stock_quantity: Math.floor(Math.random() * 100) + 5,
        category: ['Groceries', 'Electronics', 'Clothing'][i % 3],
      })),
    }),
  
    getCooperatives: async () => ({
      data: Array.from({ length: 3 }, (_, i) => ({
        id: i + 1,
        name: `Cooperative ${i + 1}`,
        description: `Description ${i + 1}`,
        revenue_split: (i + 1) * 10,
        members: Array.from({ length: i + 2 }, (_, j) => ({
          id: j + 1,
          name: `Member ${j + 1}`,
          address: `Address ${j + 1}`,
        })),
      })),
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