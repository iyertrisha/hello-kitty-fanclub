import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { COLORS, SIZES } from '../utils/constants';
import { formatCurrency } from '../utils/helpers';
import Card from './common/Card';

const CooperativeCard = ({ cooperative, isMember = false, onPress, onJoin, onLeave }) => {
  return (
    <Card onPress={onPress} style={styles.card}>
      <View style={styles.header}>
        <View style={styles.info}>
          <Text style={styles.name}>{cooperative.name}</Text>
          <Text style={styles.description} numberOfLines={2}>
            {cooperative.description}
          </Text>
          
          <View style={styles.statsRow}>
            <View style={styles.stat}>
              <Icon name="group" size={16} color={COLORS.textSecondary} />
              <Text style={styles.statText}>{cooperative.total_members} members</Text>
            </View>
            <View style={styles.stat}>
              <Icon name="percent" size={16} color={COLORS.textSecondary} />
              <Text style={styles.statText}>{cooperative.revenue_split}% split</Text>
            </View>
          </View>
        </View>
      </View>
      
      <View style={styles.footer}>
        {isMember ? (
          <TouchableOpacity
            style={[styles.actionButton, styles.leaveButton]}
            onPress={onLeave}
            activeOpacity={0.7}
          >
            <Icon name="exit-to-app" size={18} color={COLORS.error} />
            <Text style={styles.leaveButtonText}>Leave</Text>
          </TouchableOpacity>
        ) : (
          <TouchableOpacity
            style={[styles.actionButton, styles.joinButton]}
            onPress={onJoin}
            activeOpacity={0.7}
          >
            <Icon name="group-add" size={18} color={COLORS.success} />
            <Text style={styles.joinButtonText}>Join</Text>
          </TouchableOpacity>
        )}
      </View>
    </Card>
  );
};

const styles = StyleSheet.create({
  card: {
    marginBottom: SIZES.margin,
  },
  header: {
    marginBottom: SIZES.padding,
  },
  info: {
    flex: 1,
  },
  name: {
    fontSize: 18,
    fontWeight: '600',
    color: COLORS.text,
    marginBottom: 8,
  },
  description: {
    fontSize: 14,
    color: COLORS.textSecondary,
    marginBottom: 12,
    lineHeight: 20,
  },
  statsRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  stat: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 16,
  },
  statText: {
    fontSize: 12,
    color: COLORS.textSecondary,
    marginLeft: 4,
  },
  footer: {
    borderTopWidth: 1,
    borderTopColor: COLORS.border,
    paddingTop: SIZES.padding,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 10,
    borderRadius: SIZES.borderRadius,
  },
  joinButton: {
    backgroundColor: COLORS.success + '20',
  },
  leaveButton: {
    backgroundColor: COLORS.error + '20',
  },
  joinButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.success,
    marginLeft: 6,
  },
  leaveButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.error,
    marginLeft: 6,
  },
});

export default CooperativeCard;



