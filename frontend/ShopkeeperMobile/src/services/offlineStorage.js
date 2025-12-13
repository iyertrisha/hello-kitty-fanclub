import AsyncStorage from '@react-native-async-storage/async-storage';

const STORAGE_KEYS = {
  TRANSACTIONS: '@offline_transactions',
  PRODUCTS: '@offline_products',
  SYNC_QUEUE: '@sync_queue',
};

/**
 * Save transaction locally
 */
export const saveTransactionOffline = async (transaction) => {
  try {
    const existing = await AsyncStorage.getItem(STORAGE_KEYS.TRANSACTIONS);
    const transactions = existing ? JSON.parse(existing) : [];
    transactions.push({
      ...transaction,
      id: transaction.id || Date.now(),
      offline: true,
      created_at: new Date().toISOString(),
    });
    await AsyncStorage.setItem(STORAGE_KEYS.TRANSACTIONS, JSON.stringify(transactions));
    return true;
  } catch (error) {
    console.error('Error saving transaction offline:', error);
    return false;
  }
};

/**
 * Get all offline transactions
 */
export const getOfflineTransactions = async () => {
  try {
    const data = await AsyncStorage.getItem(STORAGE_KEYS.TRANSACTIONS);
    return data ? JSON.parse(data) : [];
  } catch (error) {
    console.error('Error getting offline transactions:', error);
    return [];
  }
};

/**
 * Save product locally
 */
export const saveProductOffline = async (product) => {
  try {
    const existing = await AsyncStorage.getItem(STORAGE_KEYS.PRODUCTS);
    const products = existing ? JSON.parse(existing) : [];
    products.push({
      ...product,
      id: product.id || Date.now(),
      offline: true,
      created_at: new Date().toISOString(),
    });
    await AsyncStorage.setItem(STORAGE_KEYS.PRODUCTS, JSON.stringify(products));
    return true;
  } catch (error) {
    console.error('Error saving product offline:', error);
    return false;
  }
};

/**
 * Get all offline products
 */
export const getOfflineProducts = async () => {
  try {
    const data = await AsyncStorage.getItem(STORAGE_KEYS.PRODUCTS);
    return data ? JSON.parse(data) : [];
  } catch (error) {
    console.error('Error getting offline products:', error);
    return [];
  }
};

/**
 * Add operation to sync queue
 */
export const addToSyncQueue = async (action, data) => {
  try {
    const existing = await AsyncStorage.getItem(STORAGE_KEYS.SYNC_QUEUE);
    const queue = existing ? JSON.parse(existing) : [];
    queue.push({
      action,
      data,
      timestamp: new Date().toISOString(),
      retries: 0,
    });
    await AsyncStorage.setItem(STORAGE_KEYS.SYNC_QUEUE, JSON.stringify(queue));
    return true;
  } catch (error) {
    console.error('Error adding to sync queue:', error);
    return false;
  }
};

/**
 * Get sync queue
 */
export const getSyncQueue = async () => {
  try {
    const data = await AsyncStorage.getItem(STORAGE_KEYS.SYNC_QUEUE);
    return data ? JSON.parse(data) : [];
  } catch (error) {
    console.error('Error getting sync queue:', error);
    return [];
  }
};

/**
 * Remove item from sync queue
 */
export const removeFromSyncQueue = async (index) => {
  try {
    const queue = await getSyncQueue();
    queue.splice(index, 1);
    await AsyncStorage.setItem(STORAGE_KEYS.SYNC_QUEUE, JSON.stringify(queue));
    return true;
  } catch (error) {
    console.error('Error removing from sync queue:', error);
    return false;
  }
};

/**
 * Clear all offline data
 */
export const clearOfflineData = async () => {
  try {
    await AsyncStorage.multiRemove([
      STORAGE_KEYS.TRANSACTIONS,
      STORAGE_KEYS.PRODUCTS,
      STORAGE_KEYS.SYNC_QUEUE,
    ]);
    return true;
  } catch (error) {
    console.error('Error clearing offline data:', error);
    return false;
  }
};



