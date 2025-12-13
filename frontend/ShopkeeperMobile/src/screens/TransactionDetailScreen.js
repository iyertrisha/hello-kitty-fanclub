import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Alert,
} from 'react-native';
import { useRoute } from '@react-navigation/native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { COLORS, SIZES, TRANSACTION_STATUS } from '../utils/constants';
import { formatCurrency, formatDateTime } from '../utils/helpers';
import { apiService } from '../services/api';
import Card from '../components/common/Card';
import LoadingSpinner from '../components/common/LoadingSpinner';
import AudioPlayer from '../components/AudioPlayer';
import Button from '../components/common/Button';

const TransactionDetailScreen = () => {
  const route = useRoute();
  const { transactionId } = route.params;
  const [transaction, setTransaction] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTransaction();
  }, [transactionId]);

  const loadTransaction = async () => {
    try {
      setLoading(true);
      const data = await apiService.getTransactionById(transactionId);
      setTransaction(data);
    } catch (error) {
      console.error('Error loading transaction:', error);
      Alert.alert('Error', 'Failed to load transaction details');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = () => {
    // Navigate to edit screen or show edit modal
    Alert.alert('Edit', 'Edit functionality coming soon');
  };

  const handleUpdateStatus = async (newStatus) => {
    try {
      await apiService.updateTransactionStatus(transactionId, newStatus);
      Alert.alert('Success', 'Transaction status updated');
      loadTransaction();
    } catch (error) {
      Alert.alert('Error', 'Failed to update transaction status');
    }
  };

  if (loading) {
    return <LoadingSpinner text="Loading transaction..." />;
  }

  if (!transaction) {
    return (
      <View style={styles.container}>
        <Text style={styles.errorText}>Transaction not found</Text>
      </View>
    );
  }

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
    <ScrollView style={styles.container}>
      <Card style={styles.card}>
        <View style={styles.header}>
          <View>
            <Text style={styles.type}>
              {transaction.type.charAt(0).toUpperCase() + transaction.type.slice(1)}
            </Text>
            <Text style={styles.amount}>{formatCurrency(transaction.amount)}</Text>
          </View>
          <View
            style={[
              styles.statusBadge,
              { backgroundColor: getStatusColor(transaction.status) + '20' },
            ]}
          >
            <Text style={[styles.statusText, { color: getStatusColor(transaction.status) }]}>
              {transaction.status}
            </Text>
          </View>
        </View>
      </Card>

      <Card style={styles.card}>
        <Text style={styles.sectionTitle}>Customer Information</Text>
        <View style={styles.infoRow}>
          <Text style={styles.label}>Name:</Text>
          <Text style={styles.value}>{transaction.customer?.name || 'Unknown'}</Text>
        </View>
        <View style={styles.infoRow}>
          <Text style={styles.label}>Customer ID:</Text>
          <Text style={styles.value}>{transaction.customer?.id || 'N/A'}</Text>
        </View>
      </Card>

      <Card style={styles.card}>
        <Text style={styles.sectionTitle}>Transaction Details</Text>
        <View style={styles.infoRow}>
          <Text style={styles.label}>Date:</Text>
          <Text style={styles.value}>{formatDateTime(transaction.timestamp)}</Text>
        </View>
        <View style={styles.infoRow}>
          <Text style={styles.label}>Type:</Text>
          <Text style={styles.value}>
            {transaction.type.charAt(0).toUpperCase() + transaction.type.slice(1)}
          </Text>
        </View>
        <View style={styles.infoRow}>
          <Text style={styles.label}>Amount:</Text>
          <Text style={styles.value}>{formatCurrency(transaction.amount)}</Text>
        </View>
        {transaction.blockchain_hash && (
          <View style={styles.infoRow}>
            <Text style={styles.label}>Blockchain Hash:</Text>
            <View style={styles.hashContainer}>
              <Icon name="verified" size={16} color={COLORS.info} />
              <Text style={styles.hashText}>{transaction.blockchain_hash.substring(0, 20)}...</Text>
            </View>
          </View>
        )}
      </Card>

      {transaction.transcript && (
        <Card style={styles.card}>
          <Text style={styles.sectionTitle}>Transcript</Text>
          <Text style={styles.transcript}>{transaction.transcript}</Text>
        </Card>
      )}

      {transaction.audio_uri && (
        <Card style={styles.card}>
          <Text style={styles.sectionTitle}>Audio Recording</Text>
          <AudioPlayer audioUri={transaction.audio_uri} />
        </Card>
      )}

      {transaction.status === TRANSACTION_STATUS.PENDING && (
        <Card style={styles.card}>
          <Text style={styles.sectionTitle}>Actions</Text>
          <Button
            title="Edit Transaction"
            variant="secondary"
            onPress={handleEdit}
            style={styles.actionButton}
          />
          <Button
            title="Mark as Verified"
            onPress={() => handleUpdateStatus(TRANSACTION_STATUS.VERIFIED)}
            style={styles.actionButton}
          />
        </Card>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  card: {
    margin: SIZES.padding,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  type: {
    fontSize: 18,
    fontWeight: '600',
    color: COLORS.text,
    marginBottom: 4,
  },
  amount: {
    fontSize: 24,
    fontWeight: 'bold',
    color: COLORS.primary,
  },
  statusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 4,
  },
  statusText: {
    fontSize: 14,
    fontWeight: '600',
    textTransform: 'capitalize',
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.text,
    marginBottom: SIZES.padding,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  label: {
    fontSize: 14,
    color: COLORS.textSecondary,
  },
  value: {
    fontSize: 14,
    color: COLORS.text,
    fontWeight: '500',
  },
  hashContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  hashText: {
    fontSize: 12,
    color: COLORS.info,
    marginLeft: 4,
    fontFamily: 'monospace',
  },
  transcript: {
    fontSize: 16,
    color: COLORS.text,
    lineHeight: 24,
  },
  actionButton: {
    marginTop: 8,
  },
  errorText: {
    textAlign: 'center',
    color: COLORS.error,
    fontSize: 16,
    marginTop: 20,
  },
});

export default TransactionDetailScreen;



