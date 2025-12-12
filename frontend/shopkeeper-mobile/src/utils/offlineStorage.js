import AsyncStorage from '@react-native-async-storage/async-storage';

const STORAGE_KEYS = {
  TRANSACTIONS: '@offline_transactions',
  SYNC_QUEUE: '@sync_queue',
  LAST_SYNC: '@last_sync',
};

// Save transaction offline
export const saveTransactionOffline = async (transaction) => {
  try {
    const existing = await AsyncStorage.getItem(STORAGE_KEYS.TRANSACTIONS);
    const transactions = existing ? JSON.parse(existing) : [];
    transactions.push({
      ...transaction,
      id: `offline_${Date.now()}_${Math.random()}`,
      offline: true,
      timestamp: new Date().toISOString(),
    });
    await AsyncStorage.setItem(
      STORAGE_KEYS.TRANSACTIONS,
      JSON.stringify(transactions)
    );
    return true;
  } catch (error) {
    console.error('Error saving transaction offline:', error);
    return false;
  }
};

// Get offline transactions
export const getOfflineTransactions = async () => {
  try {
    const data = await AsyncStorage.getItem(STORAGE_KEYS.TRANSACTIONS);
    return data ? JSON.parse(data) : [];
  } catch (error) {
    console.error('Error getting offline transactions:', error);
    return [];
  }
};

// Add to sync queue
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
  } catch (error) {
    console.error('Error adding to sync queue:', error);
  }
};

// Get sync queue
export const getSyncQueue = async () => {
  try {
    const data = await AsyncStorage.getItem(STORAGE_KEYS.SYNC_QUEUE);
    return data ? JSON.parse(data) : [];
  } catch (error) {
    console.error('Error getting sync queue:', error);
    return [];
  }
};

// Remove from sync queue
export const removeFromSyncQueue = async (index) => {
  try {
    const queue = await getSyncQueue();
    queue.splice(index, 1);
    await AsyncStorage.setItem(STORAGE_KEYS.SYNC_QUEUE, JSON.stringify(queue));
  } catch (error) {
    console.error('Error removing from sync queue:', error);
  }
};

// Update sync queue item retries
export const updateSyncQueueRetries = async (index, retries) => {
  try {
    const queue = await getSyncQueue();
    if (queue[index]) {
      queue[index].retries = retries;
      await AsyncStorage.setItem(
        STORAGE_KEYS.SYNC_QUEUE,
        JSON.stringify(queue)
      );
    }
  } catch (error) {
    console.error('Error updating sync queue retries:', error);
  }
};

// Clear offline transactions
export const clearOfflineTransactions = async () => {
  try {
    await AsyncStorage.removeItem(STORAGE_KEYS.TRANSACTIONS);
  } catch (error) {
    console.error('Error clearing offline transactions:', error);
  }
};

// Save last sync timestamp
export const saveLastSync = async () => {
  try {
    await AsyncStorage.setItem(
      STORAGE_KEYS.LAST_SYNC,
      new Date().toISOString()
    );
  } catch (error) {
    console.error('Error saving last sync:', error);
  }
};

// Get last sync timestamp
export const getLastSync = async () => {
  try {
    return await AsyncStorage.getItem(STORAGE_KEYS.LAST_SYNC);
  } catch (error) {
    console.error('Error getting last sync:', error);
    return null;
  }
};

// Check if online
export const isOnline = () => {
  // This is a simple check - in production, use NetInfo
  return navigator.onLine !== false;
};

