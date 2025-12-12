import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';

const TransactionCard = ({ transaction, onPress, onDispute }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'verified':
        return '#34C759';
      case 'pending':
        return '#FF9500';
      case 'disputed':
        return '#FF3B30';
      default:
        return '#8E8E93';
    }
  };

  const getTypeLabel = (type) => {
    switch (type) {
      case 'sale':
        return 'Sale';
      case 'credit':
        return 'Credit';
      case 'repay':
        return 'Repayment';
      default:
        return type;
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <TouchableOpacity style={styles.card} onPress={onPress}>
      <View style={styles.header}>
        <View style={styles.typeContainer}>
          <Text style={styles.typeLabel}>{getTypeLabel(transaction.type)}</Text>
        </View>
        <View
          style={[
            styles.statusBadge,
            { backgroundColor: getStatusColor(transaction.status) },
          ]}
        >
          <Text style={styles.statusText}>{transaction.status}</Text>
        </View>
      </View>

      <View style={styles.content}>
        <Text style={styles.amount}>₹{transaction.amount?.toFixed(2)}</Text>
        {transaction.customer && (
          <Text style={styles.customer}>
            Customer: {transaction.customer.name || transaction.customer_id}
          </Text>
        )}
        <Text style={styles.date}>{formatDate(transaction.timestamp)}</Text>
      </View>

      {transaction.blockchain_hash && (
        <View style={styles.blockchainBadge}>
          <Text style={styles.blockchainText}>✓ Blockchain Verified</Text>
        </View>
      )}

      {transaction.status === 'pending' && onDispute && (
        <TouchableOpacity
          style={styles.disputeButton}
          onPress={() => onDispute(transaction.id)}
        >
          <Text style={styles.disputeButtonText}>Dispute</Text>
        </TouchableOpacity>
      )}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  typeContainer: {
    backgroundColor: '#F0F0F0',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
  },
  typeLabel: {
    fontSize: 12,
    fontWeight: '600',
    color: '#333',
    textTransform: 'uppercase',
  },
  statusBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusText: {
    color: '#FFFFFF',
    fontSize: 11,
    fontWeight: '600',
    textTransform: 'capitalize',
  },
  content: {
    marginBottom: 12,
  },
  amount: {
    fontSize: 24,
    fontWeight: '700',
    color: '#333',
    marginBottom: 4,
  },
  customer: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  date: {
    fontSize: 12,
    color: '#999',
  },
  blockchainBadge: {
    backgroundColor: '#E8F5E9',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 8,
    alignSelf: 'flex-start',
    marginTop: 8,
  },
  blockchainText: {
    color: '#2E7D32',
    fontSize: 11,
    fontWeight: '600',
  },
  disputeButton: {
    marginTop: 12,
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 8,
    backgroundColor: '#FFEBEE',
    alignSelf: 'flex-start',
  },
  disputeButtonText: {
    color: '#C62828',
    fontSize: 12,
    fontWeight: '600',
  },
});

export default TransactionCard;

