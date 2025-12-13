import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Alert,
} from 'react-native';
import { useRoute, useNavigation } from '@react-navigation/native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { COLORS, SIZES } from '../utils/constants';
import { formatCurrency, formatDate } from '../utils/helpers';
import { apiService } from '../services/api';
import Card from '../components/common/Card';
import LoadingSpinner from '../components/common/LoadingSpinner';
import Button from '../components/common/Button';
import Input from '../components/common/Input';

const InventoryDetailScreen = () => {
  const route = useRoute();
  const navigation = useNavigation();
  const { productId } = route.params;
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    price: '',
    stock_quantity: '',
    category: '',
    description: '',
  });
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    loadProduct();
  }, [productId]);

  const loadProduct = async () => {
    try {
      setLoading(true);
      const inventory = await apiService.getInventory('1');
      const foundProduct = inventory.data.find(p => p.id === parseInt(productId));
      setProduct(foundProduct);
      if (foundProduct) {
        setFormData({
          name: foundProduct.name,
          price: foundProduct.price.toString(),
          stock_quantity: foundProduct.stock_quantity.toString(),
          category: foundProduct.category || '',
          description: foundProduct.description || '',
        });
      }
    } catch (error) {
      console.error('Error loading product:', error);
      Alert.alert('Error', 'Failed to load product details');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = async () => {
    try {
      setUpdating(true);
      await apiService.updateInventory('1', productId, {
        ...formData,
        price: parseFloat(formData.price),
        stock_quantity: parseInt(formData.stock_quantity),
      });
      Alert.alert('Success', 'Product updated successfully');
      setEditing(false);
      loadProduct();
    } catch (error) {
      Alert.alert('Error', 'Failed to update product');
    } finally {
      setUpdating(false);
    }
  };

  const handleDelete = () => {
    Alert.alert(
      'Delete Product',
      'Are you sure you want to delete this product?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              await apiService.deleteProduct('1', productId);
              Alert.alert('Success', 'Product deleted successfully', [
                { text: 'OK', onPress: () => navigation.goBack() },
              ]);
            } catch (error) {
              Alert.alert('Error', 'Failed to delete product');
            }
          },
        },
      ]
    );
  };

  const handleStockUpdate = async (delta) => {
    const newStock = Math.max(0, parseInt(formData.stock_quantity) + delta);
    setFormData(prev => ({ ...prev, stock_quantity: newStock.toString() }));
    if (!editing) {
      try {
        await apiService.updateInventory('1', productId, {
          stock_quantity: newStock,
        });
        loadProduct();
      } catch (error) {
        Alert.alert('Error', 'Failed to update stock');
      }
    }
  };

  if (loading) {
    return <LoadingSpinner text="Loading product..." />;
  }

  if (!product) {
    return (
      <View style={styles.container}>
        <Text style={styles.errorText}>Product not found</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.card}>
        {editing ? (
          <>
            <Input
              label="Product Name"
              value={formData.name}
              onChangeText={(value) => setFormData(prev => ({ ...prev, name: value }))}
            />
            <Input
              label="Price (₹)"
              value={formData.price}
              onChangeText={(value) => setFormData(prev => ({ ...prev, price: value }))}
              keyboardType="numeric"
            />
            <Input
              label="Category"
              value={formData.category}
              onChangeText={(value) => setFormData(prev => ({ ...prev, category: value }))}
            />
            <Input
              label="Description"
              value={formData.description}
              onChangeText={(value) => setFormData(prev => ({ ...prev, description: value }))}
              multiline
              numberOfLines={4}
            />
            <View style={styles.buttonRow}>
              <Button
                title="Cancel"
                variant="secondary"
                onPress={() => {
                  setEditing(false);
                  loadProduct();
                }}
                style={styles.button}
              />
              <Button
                title="Save"
                onPress={handleUpdate}
                loading={updating}
                style={styles.button}
              />
            </View>
          </>
        ) : (
          <>
            <View style={styles.header}>
              <Text style={styles.name}>{product.name}</Text>
              <TouchableOpacity onPress={() => setEditing(true)}>
                <Icon name="edit" size={24} color={COLORS.primary} />
              </TouchableOpacity>
            </View>
            
            <View style={styles.infoRow}>
              <Text style={styles.label}>Price:</Text>
              <Text style={styles.value}>{formatCurrency(product.price)}</Text>
            </View>
            
            <View style={styles.infoRow}>
              <Text style={styles.label}>Stock Quantity:</Text>
              <View style={styles.stockContainer}>
                <TouchableOpacity
                  style={styles.stockButton}
                  onPress={() => handleStockUpdate(-1)}
                >
                  <Icon name="remove" size={20} color={COLORS.primary} />
                </TouchableOpacity>
                <Text style={styles.stockValue}>{product.stock_quantity}</Text>
                <TouchableOpacity
                  style={styles.stockButton}
                  onPress={() => handleStockUpdate(1)}
                >
                  <Icon name="add" size={20} color={COLORS.primary} />
                </TouchableOpacity>
              </View>
            </View>
            
            {product.category && (
              <View style={styles.infoRow}>
                <Text style={styles.label}>Category:</Text>
                <Text style={styles.value}>{product.category}</Text>
              </View>
            )}
            
            {product.description && (
              <View style={styles.infoRow}>
                <Text style={styles.label}>Description:</Text>
                <Text style={styles.value}>{product.description}</Text>
              </View>
            )}
            
            {product.last_restocked && (
              <View style={styles.infoRow}>
                <Text style={styles.label}>Last Restocked:</Text>
                <Text style={styles.value}>{formatDate(product.last_restocked)}</Text>
              </View>
            )}
            
            <Button
              title="Delete Product"
              variant="danger"
              onPress={handleDelete}
              style={styles.deleteButton}
            />
          </>
        )}
      </Card>
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
    marginBottom: SIZES.padding,
  },
  name: {
    fontSize: 24,
    fontWeight: 'bold',
    color: COLORS.text,
    flex: 1,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
    alignItems: 'center',
  },
  label: {
    fontSize: 14,
    color: COLORS.textSecondary,
  },
  value: {
    fontSize: 14,
    color: COLORS.text,
    fontWeight: '500',
    flex: 1,
    textAlign: 'right',
  },
  stockContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  stockButton: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: COLORS.primary + '20',
    justifyContent: 'center',
    alignItems: 'center',
  },
  stockValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: COLORS.text,
    marginHorizontal: 16,
    minWidth: 40,
    textAlign: 'center',
  },
  buttonRow: {
    flexDirection: 'row',
    marginTop: SIZES.margin,
  },
  button: {
    flex: 1,
    marginHorizontal: 4,
  },
  deleteButton: {
    marginTop: SIZES.margin,
  },
  errorText: {
    textAlign: 'center',
    color: COLORS.error,
    fontSize: 16,
    marginTop: 20,
  },
});

export default InventoryDetailScreen;
