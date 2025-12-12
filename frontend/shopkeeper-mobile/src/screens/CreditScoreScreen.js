import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
} from 'react-native';
import CreditScoreCard from '../components/CreditScoreCard';
import apiService from '../services/api';
import AsyncStorage from '@react-native-async-storage/async-storage';

const CreditScoreScreen = () => {
  const [creditScore, setCreditScore] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const [shopkeeperId, setShopkeeperId] = useState(null);
  const [scoreHistory, setScoreHistory] = useState([]);

  useEffect(() => {
    loadShopkeeperId();
  }, []);

  useEffect(() => {
    if (shopkeeperId) {
      loadCreditScore();
      loadScoreHistory();
    }
  }, [shopkeeperId]);

  const loadShopkeeperId = async () => {
    try {
      const id = await AsyncStorage.getItem('shopkeeper_id');
      setShopkeeperId(id || '1');
    } catch (error) {
      console.error('Error loading shopkeeper ID:', error);
      setShopkeeperId('1');
    }
  };

  const loadCreditScore = async () => {
    try {
      const score = await apiService.getCreditScore(shopkeeperId);
      setCreditScore(score);
    } catch (error) {
      console.error('Error loading credit score:', error);
    }
  };

  const loadScoreHistory = async () => {
    try {
      // This would typically come from an API endpoint
      // For now, we'll simulate it
      const transactions = await apiService.getTransactions({
        shopkeeper_id: shopkeeperId,
        limit: 100,
      });
      
      // Calculate historical scores (simplified)
      // In production, this would come from the API
      const history = [];
      if (transactions.data || transactions.length > 0) {
        const txList = transactions.data || transactions;
        // Group by month and calculate approximate scores
        // This is a placeholder - actual implementation would use ML service
      }
      setScoreHistory(history);
    } catch (error) {
      console.error('Error loading score history:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadCreditScore();
    await loadScoreHistory();
    setRefreshing(false);
  };

  const calculateTrend = () => {
    if (!scoreHistory || scoreHistory.length < 2) return null;
    const current = creditScore?.score || 0;
    const previous = scoreHistory[scoreHistory.length - 2]?.score || current;
    return current - previous;
  };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <View style={styles.header}>
        <Text style={styles.title}>Credit Score</Text>
      </View>

      <View style={styles.content}>
        {creditScore ? (
          <>
            <CreditScoreCard
              creditScore={creditScore}
              trend={calculateTrend()}
            />

            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Score Explanation</Text>
              <View style={styles.explanationCard}>
                <Text style={styles.explanationText}>
                  Your Vishwas Score is calculated based on several factors:
                </Text>
                <View style={styles.factorList}>
                  <Text style={styles.factorItem}>
                    • Transaction History: Regular and verified transactions
                  </Text>
                  <Text style={styles.factorItem}>
                    • Credit Repayment: Timely repayment of credits
                  </Text>
                  <Text style={styles.factorItem}>
                    • Blockchain Verification: Verified transactions on blockchain
                  </Text>
                  <Text style={styles.factorItem}>
                    • Cooperative Participation: Active membership in cooperatives
                  </Text>
                </View>
                <Text style={styles.explanationText}>
                  Scores range from 300-900, with higher scores indicating better
                  creditworthiness.
                </Text>
              </View>
            </View>

            {creditScore.blockchain_verified && (
              <View style={styles.section}>
                <View style={styles.blockchainInfo}>
                  <Text style={styles.blockchainTitle}>
                    ✓ Blockchain Verified
                  </Text>
                  <Text style={styles.blockchainText}>
                    Your credit score is verified on the Polygon blockchain,
                    ensuring transparency and trust.
                  </Text>
                </View>
              </View>
            )}
          </>
        ) : (
          <View style={styles.loadingContainer}>
            <Text style={styles.loadingText}>Loading credit score...</Text>
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
  content: {
    padding: 16,
  },
  section: {
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#333',
    marginBottom: 12,
  },
  explanationCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  explanationText: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
    marginBottom: 12,
  },
  factorList: {
    marginLeft: 8,
    marginBottom: 12,
  },
  factorItem: {
    fontSize: 14,
    color: '#666',
    lineHeight: 24,
  },
  blockchainInfo: {
    backgroundColor: '#E8F5E9',
    borderRadius: 12,
    padding: 16,
    borderLeftWidth: 4,
    borderLeftColor: '#2E7D32',
  },
  blockchainTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#2E7D32',
    marginBottom: 8,
  },
  blockchainText: {
    fontSize: 14,
    color: '#1B5E20',
    lineHeight: 20,
  },
  loadingContainer: {
    padding: 40,
    alignItems: 'center',
  },
  loadingText: {
    color: '#999',
    fontSize: 14,
  },
});

export default CreditScoreScreen;

