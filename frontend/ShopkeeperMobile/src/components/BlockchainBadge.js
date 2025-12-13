import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { COLORS, SIZES } from '../utils/constants';

const BlockchainBadge = ({ verified, onPress, txHash }) => {
  if (!verified) {
    return (
      <View style={styles.container}>
        <View style={[styles.badge, styles.notVerified]}>
          <Icon name="cancel" size={16} color={COLORS.textSecondary} />
          <Text style={styles.notVerifiedText}>Not Verified</Text>
        </View>
      </View>
    );
  }

  return (
    <TouchableOpacity
      style={styles.container}
      onPress={onPress}
      activeOpacity={0.7}
    >
      <View style={[styles.badge, styles.verified]}>
        <Icon name="verified" size={16} color={COLORS.info} />
        <Text style={styles.verifiedText}>Blockchain Verified</Text>
      </View>
      {txHash && (
        <Text style={styles.hashText} numberOfLines={1}>
          {txHash.substring(0, 20)}...
        </Text>
      )}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  container: {
    alignItems: 'flex-start',
  },
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: SIZES.borderRadius,
  },
  verified: {
    backgroundColor: COLORS.info + '20',
  },
  notVerified: {
    backgroundColor: COLORS.border,
  },
  verifiedText: {
    fontSize: 12,
    fontWeight: '600',
    color: COLORS.info,
    marginLeft: 4,
  },
  notVerifiedText: {
    fontSize: 12,
    fontWeight: '600',
    color: COLORS.textSecondary,
    marginLeft: 4,
  },
  hashText: {
    fontSize: 10,
    color: COLORS.textSecondary,
    marginTop: 4,
    fontFamily: 'monospace',
  },
});

export default BlockchainBadge;



