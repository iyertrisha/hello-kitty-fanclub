import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
} from 'react-native';
import { COLORS, SIZES } from '../utils/constants';
import { apiService } from '../services/api';
import CreditScoreCard from '../components/CreditScoreCard';
import BlockchainBadge from '../components/BlockchainBadge';
import Card from '../components/common/Card';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { getCreditScoreCategory } from '../utils/helpers';

const CreditScoreScreen = () => {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [creditScore, setCreditScore] = useState(null);
  const [blockchainData, setBlockchainData] = useState(null);

  useEffect(() => {
    loadCreditScore();
  }, []);

  const loadCreditScore = async () => {
    try {
      setLoading(true);
      const [scoreData, blockchainResponse] = await Promise.all([
        apiService.getCreditScore('1'),
        apiService.getCreditScore('1'), // This would be blockchain endpoint in real app
      ]);

      setCreditScore(scoreData);
      // Mock blockchain data - in real app, this would come from blockchain endpoint
      setBlockchainData({
        verified: scoreData.blockchain_verified || false,
        txHash: scoreData.blockchain_hash || null,
      });
    } catch (error) {
      console.error('Error loading credit score:', error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadCreditScore();
    setRefreshing(false);
  };

  if (loading) {
    return <LoadingSpinner text="Loading credit score..." />;
  }

  if (!creditScore) {
    return (
      <View style={styles.container}>
        <Text style={styles.errorText}>Failed to load credit score</Text>
      </View>
    );
  }

  const category = getCreditScoreCategory(creditScore.score);

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <View style={styles.scoreSection}>
        <CreditScoreCard
          score={creditScore.score}
          blockchainVerified={blockchainData?.verified}
          blockchainHash={blockchainData?.txHash}
        />
      </View>

      <Card style={styles.card}>
        <Text style={styles.sectionTitle}>Score Breakdown</Text>
        {creditScore.factors && Object.entries(creditScore.factors).map(([factor, value]) => (
          <View key={factor} style={styles.factorRow}>
            <View style={styles.factorInfo}>
              <Text style={styles.factorName}>
                {factor.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </Text>
              <View style={styles.progressBar}>
                <View
                  style={[
                    styles.progressFill,
                    { width: `${value}%`, backgroundColor: category.color },
                  ]}
                />
              </View>
            </View>
            <Text style={styles.factorValue}>{value}%</Text>
          </View>
        ))}
      </Card>

      {creditScore.explanation && (
        <Card style={styles.card}>
          <Text style={styles.sectionTitle}>Explanation</Text>
          <Text style={styles.explanation}>{creditScore.explanation}</Text>
        </Card>
      )}

      {creditScore.score_trend && creditScore.score_trend.length > 0 && (
        <Card style={styles.card}>
          <Text style={styles.sectionTitle}>Score History</Text>
          <View style={styles.trendContainer}>
            {creditScore.score_trend.map((point, index) => (
              <View key={index} style={styles.trendPoint}>
                <View
                  style={[
                    styles.trendBar,
                    {
                      height: (point.score / 900) * 100,
                      backgroundColor: category.color,
                    },
                  ]}
                />
                <Text style={styles.trendMonth}>{point.month}</Text>
                <Text style={styles.trendScore}>{point.score}</Text>
              </View>
            ))}
          </View>
        </Card>
      )}

      {creditScore.previous_score && (
        <Card style={styles.card}>
          <View style={styles.comparisonRow}>
            <View>
              <Text style={styles.comparisonLabel}>Previous Score</Text>
              <Text style={styles.comparisonValue}>{creditScore.previous_score}</Text>
            </View>
            <View>
              <Text style={styles.comparisonLabel}>Change</Text>
              <Text
                style={[
                  styles.comparisonValue,
                  {
                    color:
                      creditScore.score > creditScore.previous_score
                        ? COLORS.success
                        : COLORS.error,
                  },
                ]}
              >
                {creditScore.score > creditScore.previous_score ? '+' : ''}
                {creditScore.score - creditScore.previous_score}
              </Text>
            </View>
          </View>
        </Card>
      )}

      {creditScore.last_updated && (
        <Card style={styles.card}>
          <Text style={styles.lastUpdated}>
            Last updated: {new Date(creditScore.last_updated).toLocaleDateString()}
          </Text>
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
  scoreSection: {
    padding: SIZES.padding,
  },
  card: {
    margin: SIZES.padding,
    marginTop: 0,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: COLORS.text,
    marginBottom: SIZES.padding,
  },
  factorRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: SIZES.padding,
  },
  factorInfo: {
    flex: 1,
    marginRight: SIZES.padding,
  },
  factorName: {
    fontSize: 14,
    color: COLORS.text,
    marginBottom: 4,
  },
  progressBar: {
    height: 8,
    backgroundColor: COLORS.border,
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    borderRadius: 4,
  },
  factorValue: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.text,
    minWidth: 40,
    textAlign: 'right',
  },
  explanation: {
    fontSize: 14,
    color: COLORS.text,
    lineHeight: 20,
  },
  trendContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'flex-end',
    height: 150,
    marginTop: SIZES.padding,
  },
  trendPoint: {
    alignItems: 'center',
    flex: 1,
  },
  trendBar: {
    width: 30,
    borderRadius: 4,
    marginBottom: 8,
  },
  trendMonth: {
    fontSize: 12,
    color: COLORS.textSecondary,
    marginBottom: 4,
  },
  trendScore: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.text,
  },
  comparisonRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  comparisonLabel: {
    fontSize: 14,
    color: COLORS.textSecondary,
    marginBottom: 4,
  },
  comparisonValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: COLORS.text,
  },
  lastUpdated: {
    fontSize: 12,
    color: COLORS.textSecondary,
    textAlign: 'center',
  },
  errorText: {
    textAlign: 'center',
    color: COLORS.error,
    fontSize: 16,
    marginTop: 20,
  },
});

export default CreditScoreScreen;
