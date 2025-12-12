import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const CreditScoreCard = ({ creditScore, trend }) => {
  const getScoreColor = (score) => {
    if (score >= 700) return '#34C759'; // Green
    if (score >= 500) return '#FF9500'; // Yellow
    return '#FF3B30'; // Red
  };

  const getScoreLabel = (score) => {
    if (score >= 700) return 'Excellent';
    if (score >= 500) return 'Good';
    return 'Needs Improvement';
  };

  const score = creditScore?.score || 0;
  const color = getScoreColor(score);
  const label = getScoreLabel(score);

  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <Text style={styles.title}>Vishwas Score</Text>
        {creditScore?.blockchain_verified && (
          <View style={styles.blockchainBadge}>
            <Text style={styles.blockchainText}>✓ Verified</Text>
          </View>
        )}
      </View>

      <View style={styles.scoreContainer}>
        <Text style={[styles.score, { color }]}>{score}</Text>
        <Text style={styles.scoreRange}>/ 900</Text>
      </View>

      <View style={styles.labelContainer}>
        <Text style={[styles.label, { color }]}>{label}</Text>
        {trend && (
          <View style={styles.trendContainer}>
            {trend > 0 ? (
              <Text style={styles.trendUp}>↑ {trend}</Text>
            ) : trend < 0 ? (
              <Text style={styles.trendDown}>↓ {Math.abs(trend)}</Text>
            ) : null}
          </View>
        )}
      </View>

      {creditScore?.factors && (
        <View style={styles.factorsContainer}>
          <Text style={styles.factorsTitle}>Score Breakdown:</Text>
          {Object.entries(creditScore.factors).map(([key, value]) => (
            <View key={key} style={styles.factorRow}>
              <Text style={styles.factorLabel}>
                {key.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}:
              </Text>
              <Text style={styles.factorValue}>{value}</Text>
            </View>
          ))}
        </View>
      )}

      {creditScore?.explanation && (
        <View style={styles.explanationContainer}>
          <Text style={styles.explanationText}>{creditScore.explanation}</Text>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 5,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  title: {
    fontSize: 18,
    fontWeight: '700',
    color: '#333',
  },
  blockchainBadge: {
    backgroundColor: '#E8F5E9',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  blockchainText: {
    color: '#2E7D32',
    fontSize: 11,
    fontWeight: '600',
  },
  scoreContainer: {
    flexDirection: 'row',
    alignItems: 'baseline',
    marginBottom: 8,
  },
  score: {
    fontSize: 48,
    fontWeight: '700',
  },
  scoreRange: {
    fontSize: 20,
    color: '#999',
    marginLeft: 8,
  },
  labelContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    marginRight: 12,
  },
  trendContainer: {
    marginLeft: 8,
  },
  trendUp: {
    color: '#34C759',
    fontSize: 14,
    fontWeight: '600',
  },
  trendDown: {
    color: '#FF3B30',
    fontSize: 14,
    fontWeight: '600',
  },
  factorsContainer: {
    marginTop: 16,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#E5E5E5',
  },
  factorsTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  factorRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  factorLabel: {
    fontSize: 13,
    color: '#666',
    flex: 1,
  },
  factorValue: {
    fontSize: 13,
    fontWeight: '600',
    color: '#333',
  },
  explanationContainer: {
    marginTop: 16,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#E5E5E5',
  },
  explanationText: {
    fontSize: 13,
    color: '#666',
    lineHeight: 20,
  },
});

export default CreditScoreCard;

