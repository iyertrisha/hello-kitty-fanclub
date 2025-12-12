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
      // Get score history from credit score data
      const score = await apiService.getCreditScore(shopkeeperId);
      if (score.score_trend) {
        setScoreHistory(score.score_trend);
      } else {
        // Generate mock history if not available
        const history = [
          { month: 'Jan', score: 680 },
          { month: 'Feb', score: 695 },
          { month: 'Mar', score: 710 },
          { month: 'Apr', score: 725 },
        ];
        setScoreHistory(history);
      }
    } catch (error) {
      console.error('Error loading score history:', error);
      // Set default history
      setScoreHistory([
        { month: 'Jan', score: 680 },
        { month: 'Feb', score: 695 },
        { month: 'Mar', score: 710 },
        { month: 'Apr', score: 725 },
      ]);
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

            {/* Score History Chart */}
            {scoreHistory.length > 0 && (
              <View style={styles.section}>
                <Text style={styles.sectionTitle}>Score Trend</Text>
                <View style={styles.historyCard}>
                  <View style={styles.historyContainer}>
                    {scoreHistory.map((item, index) => (
                      <View key={index} style={styles.historyItem}>
                        <View style={styles.historyBarContainer}>
                          <View
                            style={[
                              styles.historyBar,
                              {
                                height: `${((item.score - 300) / 600) * 100}%`,
                                backgroundColor:
                                  item.score >= 700
                                    ? '#34C759'
                                    : item.score >= 500
                                    ? '#FF9500'
                                    : '#FF3B30',
                              },
                            ]}
                          />
                        </View>
                        <Text style={styles.historyMonth}>{item.month}</Text>
                        <Text style={styles.historyScore}>{item.score}</Text>
                      </View>
                    ))}
                  </View>
                </View>
              </View>
            )}

            {/* Additional Stats */}
            {creditScore && (
              <View style={styles.section}>
                <Text style={styles.sectionTitle}>Score Details</Text>
                <View style={styles.statsCard}>
                  <View style={styles.statRow}>
                    <Text style={styles.statLabel}>Current Score</Text>
                    <Text style={styles.statValue}>{creditScore.score}</Text>
                  </View>
                  {creditScore.previous_score && (
                    <View style={styles.statRow}>
                      <Text style={styles.statLabel}>Previous Score</Text>
                      <Text style={styles.statValue}>
                        {creditScore.previous_score}
                      </Text>
                    </View>
                  )}
                  {creditScore.last_updated && (
                    <View style={styles.statRow}>
                      <Text style={styles.statLabel}>Last Updated</Text>
                      <Text style={styles.statValue}>
                        {new Date(creditScore.last_updated).toLocaleDateString()}
                      </Text>
                    </View>
                  )}
                </View>
              </View>
            )}

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
  historyCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  historyContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'flex-end',
    height: 150,
    marginBottom: 8,
  },
  historyItem: {
    flex: 1,
    alignItems: 'center',
    marginHorizontal: 4,
  },
  historyBarContainer: {
    width: 30,
    height: 100,
    justifyContent: 'flex-end',
    marginBottom: 8,
  },
  historyBar: {
    width: '100%',
    borderRadius: 4,
    minHeight: 4,
  },
  historyMonth: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  historyScore: {
    fontSize: 11,
    fontWeight: '600',
    color: '#333',
  },
  statsCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0',
  },
  statLabel: {
    fontSize: 14,
    color: '#666',
  },
  statValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
});

export default CreditScoreScreen;

