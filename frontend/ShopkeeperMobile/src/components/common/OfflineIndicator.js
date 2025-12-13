import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { COLORS, SIZES } from '../../utils/constants';
import useOfflineSync from '../../hooks/useOfflineSync';

const OfflineIndicator = () => {
  const { isOnline, isSyncing, pendingCount, triggerSync } = useOfflineSync();

  if (isOnline && pendingCount === 0) {
    return null; // Don't show indicator when online and no pending syncs
  }

  return (
    <TouchableOpacity
      style={[
        styles.container,
        !isOnline && styles.offlineContainer,
        isSyncing && styles.syncingContainer,
      ]}
      onPress={isOnline && pendingCount > 0 ? triggerSync : undefined}
      activeOpacity={0.7}
    >
      <Icon
        name={isSyncing ? 'sync' : !isOnline ? 'cloud-off' : 'cloud-sync'}
        size={16}
        color={COLORS.onPrimary}
      />
      <Text style={styles.text}>
        {isSyncing
          ? 'Syncing...'
          : !isOnline
          ? 'Offline'
          : `${pendingCount} pending sync${pendingCount !== 1 ? 's' : ''}`}
      </Text>
      {isOnline && pendingCount > 0 && !isSyncing && (
        <Icon name="refresh" size={16} color={COLORS.onPrimary} style={styles.refreshIcon} />
      )}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: COLORS.warning,
    paddingVertical: 8,
    paddingHorizontal: SIZES.padding,
  },
  offlineContainer: {
    backgroundColor: COLORS.error,
  },
  syncingContainer: {
    backgroundColor: COLORS.info,
  },
  text: {
    color: COLORS.onPrimary,
    fontSize: 12,
    fontWeight: '600',
    marginLeft: 6,
  },
  refreshIcon: {
    marginLeft: 6,
  },
});

export default OfflineIndicator;



