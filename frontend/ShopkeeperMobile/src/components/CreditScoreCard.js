import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { COLORS, SIZES } from '../utils/constants';
import { getCreditScoreCategory } from '../utils/helpers';
import Card from './common/Card';
import BlockchainBadge from './BlockchainBadge';

const CreditScoreCard = ({ score, blockchainVerified, blockchainHash, style }) => {
  const category = getCreditScoreCategory(score);

  return (
    <Card style={[styles.card, style]}>
      <View style={styles.header}>
        <View>
          <Text style={styles.label}>Credit Score</Text>
          <Text style={[styles.score, { color: category.color }]}>{score}</Text>
          <Text style={[styles.category, { color: category.color }]}>
            {category.label}
          </Text>
        </View>
        <BlockchainBadge verified={blockchainVerified} txHash={blockchainHash} />
      </View>
    </Card>
  );
};

const styles = StyleSheet.create({
  card: {
    marginBottom: SIZES.margin,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  label: {
    fontSize: 14,
    color: COLORS.textSecondary,
    marginBottom: 4,
  },
  score: {
    fontSize: 36,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  category: {
    fontSize: 16,
    fontWeight: '600',
  },
});

export default CreditScoreCard;



