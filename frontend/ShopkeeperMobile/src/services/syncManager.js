import { getSyncQueue, removeFromSyncQueue, addToSyncQueue } from './offlineStorage';
import { apiService } from './api';

/**
 * Sync Manager Service
 * Handles syncing offline data when connection is restored
 */

class SyncManager {
  constructor() {
    this.isSyncing = false;
    this.syncListeners = [];
  }

  /**
   * Add operation to sync queue
   */
  async addToQueue(action, data) {
    return await addToSyncQueue(action, data);
  }

  /**
   * Process sync queue
   */
  async processSyncQueue() {
    if (this.isSyncing) {
      console.log('Sync already in progress');
      return;
    }

    this.isSyncing = true;
    this.notifyListeners({ isSyncing: true });

    try {
      const queue = await getSyncQueue();
      let successCount = 0;
      let failureCount = 0;

      for (let i = queue.length - 1; i >= 0; i--) {
        const item = queue[i];
        try {
          await this.syncItem(item);
          await removeFromSyncQueue(i);
          successCount++;
        } catch (error) {
          console.error(`Failed to sync item ${i}:`, error);
          // Increment retry count
          item.retries = (item.retries || 0) + 1;
          
          // Remove from queue if retries exceeded
          if (item.retries >= 3) {
            await removeFromSyncQueue(i);
            failureCount++;
          } else {
            // Update queue item with new retry count
            const updatedQueue = await getSyncQueue();
            updatedQueue[i] = item;
            // Note: This is simplified - in production, you'd want to update the queue properly
          }
        }
      }

      this.notifyListeners({
        isSyncing: false,
        lastSync: new Date(),
        successCount,
        failureCount,
      });

      return { successCount, failureCount };
    } catch (error) {
      console.error('Error processing sync queue:', error);
      this.isSyncing = false;
      this.notifyListeners({ isSyncing: false, error });
      throw error;
    } finally {
      this.isSyncing = false;
    }
  }

  /**
   * Sync a single item
   */
  async syncItem(item) {
    const { action, data } = item;

    switch (action) {
      case 'createTransaction':
        await apiService.createTransaction(data);
        break;
      case 'addProduct':
        await apiService.addProduct(data.shopkeeperId, data);
        break;
      case 'updateProduct':
        await apiService.updateInventory(data.shopkeeperId, data.productId, data);
        break;
      case 'deleteProduct':
        await apiService.deleteProduct(data.shopkeeperId, data.productId);
        break;
      case 'joinCooperative':
        await apiService.joinCooperative(data.coopId);
        break;
      case 'leaveCooperative':
        await apiService.leaveCooperative(data.coopId);
        break;
      default:
        throw new Error(`Unknown sync action: ${action}`);
    }
  }

  /**
   * Get sync queue status
   */
  async getQueueStatus() {
    const queue = await getSyncQueue();
    return {
      pendingCount: queue.length,
      isSyncing: this.isSyncing,
    };
  }

  /**
   * Add sync status listener
   */
  addListener(callback) {
    this.syncListeners.push(callback);
    return () => {
      this.syncListeners = this.syncListeners.filter(cb => cb !== callback);
    };
  }

  /**
   * Notify all listeners
   */
  notifyListeners(status) {
    this.syncListeners.forEach(callback => callback(status));
  }

  /**
   * Handle sync conflicts
   * Simple last-write-wins strategy
   */
  handleSyncConflict(localData, remoteData) {
    // Simple strategy: use the most recent data
    const localTime = new Date(localData.updated_at || localData.created_at);
    const remoteTime = new Date(remoteData.updated_at || remoteData.created_at);
    
    return localTime > remoteTime ? localData : remoteData;
  }
}

// Export singleton instance
export const syncManager = new SyncManager();
export default syncManager;



