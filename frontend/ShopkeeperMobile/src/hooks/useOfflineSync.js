import { useState, useEffect } from 'react';
import syncManager from '../services/syncManager';
import useNetworkStatus from './useNetworkStatus';

/**
 * Hook to manage offline sync functionality
 * Auto-syncs when online, provides manual sync trigger
 */
const useOfflineSync = () => {
  const { isConnected, isInternetReachable } = useNetworkStatus();
  const [syncStatus, setSyncStatus] = useState({
    isSyncing: false,
    pendingCount: 0,
    lastSync: null,
    error: null,
  });

  useEffect(() => {
    // Load initial sync status
    loadSyncStatus();

    // Subscribe to sync manager updates
    const unsubscribe = syncManager.addListener((status) => {
      setSyncStatus(prev => ({ ...prev, ...status }));
    });

    return unsubscribe;
  }, []);

  useEffect(() => {
    // Auto-sync when connection is restored
    if (isConnected && isInternetReachable && syncStatus.pendingCount > 0 && !syncStatus.isSyncing) {
      triggerSync();
    }
  }, [isConnected, isInternetReachable]);

  const loadSyncStatus = async () => {
    const status = await syncManager.getQueueStatus();
    setSyncStatus(prev => ({ ...prev, ...status }));
  };

  const triggerSync = async () => {
    if (!isConnected || !isInternetReachable) {
      return { success: false, error: 'No internet connection' };
    }

    try {
      const result = await syncManager.processSyncQueue();
      await loadSyncStatus();
      return { success: true, ...result };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  return {
    ...syncStatus,
    isOnline: isConnected && isInternetReachable,
    triggerSync,
    refreshStatus: loadSyncStatus,
  };
};

export default useOfflineSync;



