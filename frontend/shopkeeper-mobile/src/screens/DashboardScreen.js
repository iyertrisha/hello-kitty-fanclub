import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  TouchableOpacity,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import apiService from '../services/api';
import TransactionCard from '../components/TransactionCard';
import CreditScoreCard from '../components/CreditScoreCard';
import AsyncStorage from '@react-native-async-storage/async-storage';

const DashboardScreen = () => {
  const navigation = useNavigation();
  const [refreshing, setRefreshing] = useState(false);
  const [stats, setStats] = useState({
    todaySales: 0,
    pendingCredits: 0,
    inventoryAlerts: 0,
  });
  const [recentTransactions, setRecentTransactions] = useState([]);
  const [creditScore, setCreditScore] = useState(null);
  const [shopkeeperId, setShopkeeperId] = useState(null);

  useEffect(() => {
    loadShopkeeperId();
  }, []);

  useEffect(() => {
    if (shopkeeperId) {
      loadDashboardData();
    }
  }, [shopkeeperId]);

  const loadShopkeeperId = async () => {
    try {
      const id = await AsyncStorage.getItem('shopkeeper_id');
      setShopkeeperId(id || '1'); // Default to '1' for testing
    } catch (error) {
      console.error('Error loading shopkeeper ID:', error);
      setShopkeeperId('1');
    }
  };

  const loadDashboardData = async () => {
    try {
      // Load transactions
      const transactions = await apiService.getTransactions({
        shopkeeper_id: shopkeeperId,
        limit: 5,
      });
      setRecentTransactions(transactions.data || transactions || []);

      // Calculate stats
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const todayTransactions = (transactions.data || transactions).filter(
        (t) => new Date(t.timestamp) >= today
      );
      const todaySales = todayTransactions
        .filter((t) => t.type === 'sale')
        .reduce((sum, t) => sum + (t.amount || 0), 0);
      const pendingCredits = (transactions.data || transactions)
        .filter((t) => t.type === 'credit' && t.status === 'pending')
        .reduce((sum, t) => sum + (t.amount || 0), 0);

      // Load inventory alerts
      const inventory = await apiService.getInventory(shopkeeperId);
      const lowStockItems = (inventory.data || inventory || []).filter(
        (item) => item.stock_quantity < 10
      ).length;

      setStats({
        todaySales,
        pendingCredits,
        inventoryAlerts: lowStockItems,
      });

      // Load credit score
      const score = await apiService.getCreditScore(shopkeeperId);
      setCreditScore(score);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
  };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <View style={styles.header}>
        <Text style={styles.title}>Dashboard</Text>
      </View>

      {/* Stats Cards */}
      <View style={styles.statsContainer}>
        <View style={styles.statCard}>
          <Text style={styles.statValue}>₹{stats.todaySales.toFixed(2)}</Text>
          <Text style={styles.statLabel}>Today's Sales</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statValue}>₹{stats.pendingCredits.toFixed(2)}</Text>
          <Text style={styles.statLabel}>Pending Credits</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statValue}>{stats.inventoryAlerts}</Text>
          <Text style={styles.statLabel}>Low Stock Items</Text>
        </View>
      </View>

      {/* Credit Score Card */}
      {creditScore && (
        <View style={styles.section}>
          <CreditScoreCard creditScore={creditScore} />
        </View>
      )}

      {/* Quick Actions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        <View style={styles.actionsContainer}>
          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => navigation.navigate('RecordTransaction')}
          >
            <Text style={styles.actionButtonText}>Record Transaction</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => navigation.navigate('CreditScore')}
          >
            <Text style={styles.actionButtonText}>View Credit Score</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => navigation.navigate('Inventory')}
          >
            <Text style={styles.actionButtonText}>Manage Inventory</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Recent Transactions */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Recent Transactions</Text>
          <TouchableOpacity
            onPress={() => navigation.navigate('Transactions')}
          >
            <Text style={styles.viewAllText}>View All</Text>
          </TouchableOpacity>
        </View>
        {recentTransactions.length > 0 ? (
          recentTransactions.map((transaction) => (
            <TransactionCard
              key={transaction.id}
              transaction={transaction}
              onPress={() =>
                navigation.navigate('TransactionDetails', { id: transaction.id })
              }
            />
          ))
        ) : (
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>No transactions yet</Text>
          </View>
        )}
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  header: {
    padding: 20,
    paddingTop: 60,
    backgroundColor: '#FFFFFF',
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: '#333',
  },
  statsContainer: {
    flexDirection: 'row',
    padding: 16,
    gap: 12,
  },
  statCard: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statValue: {
    fontSize: 20,
    fontWeight: '700',
    color: '#007AFF',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
  },
  section: {
    padding: 16,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#333',
    marginBottom: 12,
  },
  actionsContainer: {
    gap: 12,
  },
  actionButton: {
    backgroundColor: '#007AFF',
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderRadius: 12,
    alignItems: 'center',
  },
  actionButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  viewAllText: {
    color: '#007AFF',
    fontSize: 14,
    fontWeight: '600',
  },
  emptyContainer: {
    padding: 40,
    alignItems: 'center',
  },
  emptyText: {
    color: '#999',
    fontSize: 14,
  },
});

export default DashboardScreen;

