import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { useNavigation } from '@react-navigation/native';
import { COLORS, SIZES } from '../utils/constants';
import { formatCurrency, formatDate } from '../utils/helpers';
import { apiService } from '../services/api';
import Card from '../components/common/Card';
import LoadingSpinner from '../components/common/LoadingSpinner';

const DashboardScreen = () => {
  const navigation = useNavigation();
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    todaySales: 0,
    pendingCredits: 0,
    lowStockItems: 0,
    creditScore: 0,
  });
  const [recentTransactions, setRecentTransactions] = useState([]);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [transactionsResponse, creditScoreResponse, inventoryResponse] = await Promise.all([
        apiService.getTransactions({ shopkeeper_id: '1' }),
        apiService.getCreditScore('1'),
        apiService.getInventory('1'),
      ]);

      // Calculate today's sales
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const todaySales = transactionsResponse.data
        .filter(t => {
          const txDate = new Date(t.timestamp);
          txDate.setHours(0, 0, 0, 0);
          return txDate.getTime() === today.getTime() && t.type === 'sale';
        })
        .reduce((sum, t) => sum + t.amount, 0);

      // Calculate pending credits
      const pendingCredits = transactionsResponse.data
        .filter(t => t.type === 'credit' && t.status === 'pending')
        .reduce((sum, t) => sum + t.amount, 0);

      // Count low stock items
      const lowStockItems = inventoryResponse.data.filter(p => p.stock_quantity < 10).length;

      setStats({
        todaySales,
        pendingCredits,
        lowStockItems,
        creditScore: creditScoreResponse.score || 0,
      });

      // Get recent transactions (last 5)
      setRecentTransactions(transactionsResponse.data.slice(0, 5));
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
  };

  const StatCard = ({ title, value, icon, color, onPress }) => (
    <TouchableOpacity style={styles.statCard} onPress={onPress} activeOpacity={0.7}>
      <View style={[styles.iconContainer, { backgroundColor: color }]}>
        <Icon name={icon} size={30} color="#fff" />
      </View>
      <Text style={styles.statValue}>{value}</Text>
      <Text style={styles.statTitle}>{title}</Text>
    </TouchableOpacity>
  );

  if (loading) {
    return <LoadingSpinner text="Loading dashboard..." />;
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Dashboard</Text>
        <Text style={styles.headerSubtitle}>Welcome back!</Text>
      </View>

      <View style={styles.statsGrid}>
        <StatCard
          title="Today's Sales"
          value={formatCurrency(stats.todaySales)}
          icon="attach-money"
          color={COLORS.success}
          onPress={() => navigation.navigate('TransactionList')}
        />
        <StatCard
          title="Pending Credits"
          value={formatCurrency(stats.pendingCredits)}
          icon="credit-card"
          color={COLORS.warning}
          onPress={() => navigation.navigate('TransactionList')}
        />
        <StatCard
          title="Low Stock"
          value={stats.lowStockItems}
          icon="warning"
          color={COLORS.error}
          onPress={() => navigation.navigate('Inventory')}
        />
        <StatCard
          title="Credit Score"
          value={stats.creditScore}
          icon="star"
          color={COLORS.info}
          onPress={() => navigation.navigate('CreditScore')}
        />
      </View>

      <View style={styles.quickActions}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => navigation.navigate('RecordTransaction')}
          activeOpacity={0.7}
        >
          <Icon name="mic" size={24} color={COLORS.primary} />
          <Text style={styles.actionButtonText}>Record Transaction</Text>
          <Icon name="chevron-right" size={24} color={COLORS.primary} />
        </TouchableOpacity>
        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => navigation.navigate('CreditScore')}
          activeOpacity={0.7}
        >
          <Icon name="verified" size={24} color={COLORS.primary} />
          <Text style={styles.actionButtonText}>View Credit Score</Text>
          <Icon name="chevron-right" size={24} color={COLORS.primary} />
        </TouchableOpacity>
      </View>

      <View style={styles.recentTransactions}>
        <Text style={styles.sectionTitle}>Recent Transactions</Text>
        {recentTransactions.length === 0 ? (
          <Card>
            <Text style={styles.emptyText}>No recent transactions</Text>
          </Card>
        ) : (
          recentTransactions.map((transaction) => (
            <Card
              key={transaction.id}
              onPress={() => navigation.navigate('TransactionList')}
            >
              <View style={styles.transactionRow}>
                <View style={styles.transactionInfo}>
                  <Text style={styles.transactionType}>
                    {transaction.type.charAt(0).toUpperCase() + transaction.type.slice(1)}
                  </Text>
                  <Text style={styles.transactionCustomer}>
                    {transaction.customer?.name || 'Unknown Customer'}
                  </Text>
                  <Text style={styles.transactionDate}>
                    {formatDate(transaction.timestamp)}
                  </Text>
                </View>
                <View style={styles.transactionAmount}>
                  <Text style={styles.amountText}>
                    {formatCurrency(transaction.amount)}
                  </Text>
                  <View
                    style={[
                      styles.statusBadge,
                      transaction.status === 'verified'
                        ? styles.statusVerified
                        : styles.statusPending,
                    ]}
                  >
                    <Text style={styles.statusText}>{transaction.status}</Text>
                  </View>
                </View>
              </View>
            </Card>
          ))
        )}
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  header: {
    padding: SIZES.padding,
    backgroundColor: COLORS.surface,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.border,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: COLORS.text,
  },
  headerSubtitle: {
    fontSize: 16,
    color: COLORS.textSecondary,
    marginTop: 4,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 10,
    justifyContent: 'space-between',
  },
  statCard: {
    width: '48%',
    backgroundColor: COLORS.surface,
    borderRadius: SIZES.borderRadius,
    padding: SIZES.padding,
    marginBottom: 10,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  iconContainer: {
    width: 60,
    height: 60,
    borderRadius: 30,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: COLORS.text,
    marginBottom: 4,
  },
  statTitle: {
    fontSize: 14,
    color: COLORS.textSecondary,
    textAlign: 'center',
  },
  quickActions: {
    padding: SIZES.padding,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: COLORS.text,
    marginBottom: 12,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.surface,
    padding: SIZES.padding,
    borderRadius: SIZES.borderRadius,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  actionButtonText: {
    flex: 1,
    fontSize: 16,
    color: COLORS.text,
    marginLeft: 12,
  },
  recentTransactions: {
    padding: SIZES.padding,
    paddingTop: 0,
  },
  transactionRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  transactionInfo: {
    flex: 1,
  },
  transactionType: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.text,
    marginBottom: 4,
  },
  transactionCustomer: {
    fontSize: 14,
    color: COLORS.textSecondary,
    marginBottom: 2,
  },
  transactionDate: {
    fontSize: 12,
    color: COLORS.textSecondary,
  },
  transactionAmount: {
    alignItems: 'flex-end',
  },
  amountText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: COLORS.text,
    marginBottom: 4,
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  statusVerified: {
    backgroundColor: COLORS.success + '20',
  },
  statusPending: {
    backgroundColor: COLORS.warning + '20',
  },
  statusText: {
    fontSize: 12,
    fontWeight: '600',
    color: COLORS.text,
    textTransform: 'capitalize',
  },
  emptyText: {
    textAlign: 'center',
    color: COLORS.textSecondary,
    fontSize: 14,
  },
});

export default DashboardScreen;
