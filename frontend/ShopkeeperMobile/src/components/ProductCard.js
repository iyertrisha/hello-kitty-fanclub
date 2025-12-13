import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { COLORS, SIZES } from '../utils/constants';
import { formatCurrency } from '../utils/helpers';
import Card from './common/Card';

const ProductCard = ({ product, onPress }) => {
  const isLowStock = product.stock_quantity < 10;

  return (
    <Card onPress={onPress} style={styles.card}>
      <View style={styles.row}>
        <View style={styles.info}>
          <View style={styles.headerRow}>
            <Text style={styles.name}>{product.name}</Text>
            {isLowStock && (
              <View style={styles.lowStockBadge}>
                <Icon name="warning" size={16} color={COLORS.error} />
                <Text style={styles.lowStockText}>Low Stock</Text>
              </View>
            )}
          </View>
          
          <View style={styles.detailsRow}>
            <Text style={styles.price}>{formatCurrency(product.price)}</Text>
            <Text style={styles.stock}>Stock: {product.stock_quantity}</Text>
          </View>
          
          {product.category && (
            <View style={styles.categoryBadge}>
              <Text style={styles.categoryText}>{product.category}</Text>
            </View>
          )}
        </View>
        
        <Icon name="chevron-right" size={24} color={COLORS.textSecondary} />
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
    justifyContent: 'space-between',
  },
  info: {
    flex: 1,
  },
  headerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
    flexWrap: 'wrap',
  },
  name: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.text,
    marginRight: 8,
    flex: 1,
  },
  lowStockBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.error + '20',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  lowStockText: {
    fontSize: 12,
    color: COLORS.error,
    marginLeft: 4,
    fontWeight: '600',
  },
  detailsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  price: {
    fontSize: 18,
    fontWeight: 'bold',
    color: COLORS.primary,
    marginRight: 16,
  },
  stock: {
    fontSize: 14,
    color: COLORS.textSecondary,
  },
  categoryBadge: {
    alignSelf: 'flex-start',
    backgroundColor: COLORS.primary + '20',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  categoryText: {
    fontSize: 12,
    color: COLORS.primary,
    fontWeight: '500',
  },
});

export default ProductCard;



