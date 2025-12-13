import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { COLORS, SIZES, TRANSACTION_TYPES, TRANSACTION_STATUS } from '../utils/constants';
import { formatCurrency, formatDate } from '../utils/helpers';
import Card from './common/Card';

const TransactionCard = ({ transaction, onPress }) => {
  const getTypeIcon = (type) => {
    switch (type) {
      case TRANSACTION_TYPES.SALE:
        return 'shopping-cart';
      case TRANSACTION_TYPES.CREDIT:
        return 'credit-card';
      case TRANSACTION_TYPES.REPAY:
        return 'payment';
      default:
        return 'receipt';
    }
  };

  const getTypeColor = (type) => {
    switch (type) {
      case TRANSACTION_TYPES.SALE:
        return COLORS.success;
      case TRANSACTION_TYPES.CREDIT:
        return COLORS.warning;
      case TRANSACTION_TYPES.REPAY:
        return COLORS.info;
      default:
        return COLORS.textSecondary;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case TRANSACTION_STATUS.VERIFIED:
        return COLORS.success;
      case TRANSACTION_STATUS.PENDING:
        return COLORS.warning;
      case TRANSACTION_STATUS.DISPUTED:
        return COLORS.error;
      default:
        return COLORS.textSecondary;
    }
  };

  return (
    <Card onPress={onPress} style={styles.card}>
      <View style={styles.row}>
        <View style={[styles.iconContainer, { backgroundColor: getTypeColor(transaction.type) + '20' }]}>
          <Icon
            name={getTypeIcon(transaction.type)}
            size={24}
            color={getTypeColor(transaction.type)}
          />
        </View>
        
        <View style={styles.info}>
          <View style={styles.headerRow}>
            <Text style={styles.type}>
              {transaction.type.charAt(0).toUpperCase() + transaction.type.slice(1)}
            </Text>
            <View style={[styles.statusBadge, { backgroundColor: getStatusColor(transaction.status) + '20' }]}>
              <Text style={[styles.statusText, { color: getStatusColor(transaction.status) }]}>
                {transaction.status}
              </Text>
            </View>
          </View>
          
          <Text style={styles.customer}>
            {transaction.customer?.name || 'Unknown Customer'}
          </Text>
          
          <Text style={styles.date}>
            {formatDate(transaction.timestamp)}
          </Text>
          
          {transaction.blockchain_hash && (
            <View style={styles.blockchainBadge}>
              <Icon name="verified" size={14} color={COLORS.info} />
              <Text style={styles.blockchainText}>Blockchain Verified</Text>
            </View>
          )}
        </View>
        
        <View style={styles.amountContainer}>
          <Text style={[styles.amount, { color: getTypeColor(transaction.type) }]}>
            {formatCurrency(transaction.amount)}
          </Text>
        </View>
      </View>
    </Card>
  );
};

const styles = StyleSheet.create({
  card: {
    marginBottom: SIZES.margin / 2,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  iconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: SIZES.padding,
  },
  info: {
    flex: 1,
  },
  headerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  type: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.text,
    marginRight: 8,
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 4,
  },
  statusText: {
    fontSize: 12,
    fontWeight: '600',
    textTransform: 'capitalize',
  },
  customer: {
    fontSize: 14,
    color: COLORS.text,
    marginBottom: 2,
  },
  date: {
    fontSize: 12,
    color: COLORS.textSecondary,
    marginBottom: 4,
  },
  blockchainBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 4,
  },
  blockchainText: {
    fontSize: 12,
    color: COLORS.info,
    marginLeft: 4,
  },
  amountContainer: {
    alignItems: 'flex-end',
  },
  amount: {
    fontSize: 18,
    fontWeight: 'bold',
  },
});

export default TransactionCard;



