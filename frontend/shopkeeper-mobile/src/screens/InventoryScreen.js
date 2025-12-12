import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  Alert,
  Modal,
  ActivityIndicator,
} from 'react-native';
import ProductCard from '../components/ProductCard';
import apiService from '../services/api';
import AsyncStorage from '@react-native-async-storage/async-storage';

const InventoryScreen = () => {
  const [inventory, setInventory] = useState([]);
  const [filteredInventory, setFilteredInventory] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    price: '',
    stock_quantity: '',
    category: '',
  });
  const [shopkeeperId, setShopkeeperId] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadShopkeeperId();
  }, []);

  useEffect(() => {
    if (shopkeeperId) {
      loadInventory();
    }
  }, [shopkeeperId]);

  useEffect(() => {
    filterInventory();
  }, [searchQuery, selectedCategory, inventory]);

  const loadShopkeeperId = async () => {
    try {
      const id = await AsyncStorage.getItem('shopkeeper_id');
      setShopkeeperId(id || '1');
    } catch (error) {
      console.error('Error loading shopkeeper ID:', error);
      setShopkeeperId('1');
    }
  };

  const loadInventory = async () => {
    try {
      setLoading(true);
      const data = await apiService.getInventory(shopkeeperId);
      const products = data.data || data || [];
      setInventory(products);
      setFilteredInventory(products);
    } catch (error) {
      console.error('Error loading inventory:', error);
      Alert.alert('Error', 'Failed to load inventory');
    } finally {
      setLoading(false);
    }
  };

  const filterInventory = () => {
    let filtered = [...inventory];

    // Filter by search query
    if (searchQuery) {
      filtered = filtered.filter(
        (product) =>
          product.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          product.category?.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Filter by category
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(
        (product) => product.category === selectedCategory
      );
    }

    setFilteredInventory(filtered);
  };

  const getCategories = () => {
    const categories = new Set(
      inventory.map((product) => product.category).filter(Boolean)
    );
    return Array.from(categories);
  };

  const openAddModal = () => {
    setEditingProduct(null);
    setFormData({
      name: '',
      price: '',
      stock_quantity: '',
      category: '',
    });
    setIsModalVisible(true);
  };

  const openEditModal = (product) => {
    setEditingProduct(product);
    setFormData({
      name: product.name || '',
      price: product.price?.toString() || '',
      stock_quantity: product.stock_quantity?.toString() || '',
      category: product.category || '',
    });
    setIsModalVisible(true);
  };

  const handleSave = async () => {
    if (!formData.name || !formData.price || !formData.stock_quantity) {
      Alert.alert('Error', 'Please fill in all required fields');
      return;
    }

    try {
      setLoading(true);
      const productData = {
        name: formData.name,
        price: parseFloat(formData.price),
        stock_quantity: parseInt(formData.stock_quantity),
        category: formData.category || 'General',
      };

      if (editingProduct) {
        await apiService.updateInventory(
          shopkeeperId,
          editingProduct.id,
          productData
        );
        Alert.alert('Success', 'Product updated successfully');
      } else {
        await apiService.addProduct(shopkeeperId, productData);
        Alert.alert('Success', 'Product added successfully');
      }

      setIsModalVisible(false);
      loadInventory();
    } catch (error) {
      console.error('Error saving product:', error);
      Alert.alert('Error', 'Failed to save product');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = (productId) => {
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
              setLoading(true);
              await apiService.deleteProduct(shopkeeperId, productId);
              Alert.alert('Success', 'Product deleted successfully');
              loadInventory();
            } catch (error) {
              console.error('Error deleting product:', error);
              Alert.alert('Error', 'Failed to delete product');
            } finally {
              setLoading(false);
            }
          },
        },
      ]
    );
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Inventory</Text>
        <TouchableOpacity style={styles.addButton} onPress={openAddModal}>
          <Text style={styles.addButtonText}>+ Add Product</Text>
        </TouchableOpacity>
      </View>

      {/* Search and Filter */}
      <View style={styles.filterContainer}>
        <TextInput
          style={styles.searchInput}
          placeholder="Search products..."
          value={searchQuery}
          onChangeText={setSearchQuery}
        />
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          style={styles.categoryContainer}
        >
          <TouchableOpacity
            style={[
              styles.categoryButton,
              selectedCategory === 'all' && styles.categoryButtonActive,
            ]}
            onPress={() => setSelectedCategory('all')}
          >
            <Text
              style={[
                styles.categoryButtonText,
                selectedCategory === 'all' && styles.categoryButtonTextActive,
              ]}
            >
              All
            </Text>
          </TouchableOpacity>
          {getCategories().map((category) => (
            <TouchableOpacity
              key={category}
              style={[
                styles.categoryButton,
                selectedCategory === category && styles.categoryButtonActive,
              ]}
              onPress={() => setSelectedCategory(category)}
            >
              <Text
                style={[
                  styles.categoryButtonText,
                  selectedCategory === category && styles.categoryButtonTextActive,
                ]}
              >
                {category}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      {/* Product List */}
      {loading && !inventory.length ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#007AFF" />
        </View>
      ) : (
        <ScrollView style={styles.content}>
          {filteredInventory.length > 0 ? (
            filteredInventory.map((product) => (
              <ProductCard
                key={product.id}
                product={product}
                onEdit={openEditModal}
                onDelete={handleDelete}
              />
            ))
          ) : (
            <View style={styles.emptyContainer}>
              <Text style={styles.emptyText}>No products found</Text>
            </View>
          )}
        </ScrollView>
      )}

      {/* Add/Edit Modal */}
      <Modal
        visible={isModalVisible}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setIsModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>
              {editingProduct ? 'Edit Product' : 'Add Product'}
            </Text>

            <TextInput
              style={styles.modalInput}
              placeholder="Product Name *"
              value={formData.name}
              onChangeText={(text) => setFormData({ ...formData, name: text })}
            />

            <TextInput
              style={styles.modalInput}
              placeholder="Price (₹) *"
              value={formData.price}
              onChangeText={(text) =>
                setFormData({ ...formData, price: text })
              }
              keyboardType="decimal-pad"
            />

            <TextInput
              style={styles.modalInput}
              placeholder="Stock Quantity *"
              value={formData.stock_quantity}
              onChangeText={(text) =>
                setFormData({ ...formData, stock_quantity: text })
              }
              keyboardType="numeric"
            />

            <TextInput
              style={styles.modalInput}
              placeholder="Category"
              value={formData.category}
              onChangeText={(text) =>
                setFormData({ ...formData, category: text })
              }
            />

            <View style={styles.modalActions}>
              <TouchableOpacity
                style={styles.modalCancelButton}
                onPress={() => setIsModalVisible(false)}
              >
                <Text style={styles.modalCancelButtonText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.modalSaveButton}
                onPress={handleSave}
                disabled={loading}
              >
                {loading ? (
                  <ActivityIndicator color="#FFFFFF" />
                ) : (
                  <Text style={styles.modalSaveButtonText}>Save</Text>
                )}
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </View>
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
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: '#333',
  },
  addButton: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
  },
  addButtonText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
  filterContainer: {
    backgroundColor: '#FFFFFF',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  searchInput: {
    backgroundColor: '#F5F5F5',
    borderRadius: 8,
    padding: 12,
    fontSize: 14,
    marginBottom: 12,
  },
  categoryContainer: {
    flexDirection: 'row',
  },
  categoryButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#F0F0F0',
    marginRight: 8,
  },
  categoryButtonActive: {
    backgroundColor: '#007AFF',
  },
  categoryButtonText: {
    fontSize: 13,
    color: '#666',
    fontWeight: '600',
  },
  categoryButtonTextActive: {
    color: '#FFFFFF',
  },
  content: {
    flex: 1,
    padding: 16,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyContainer: {
    padding: 40,
    alignItems: 'center',
  },
  emptyText: {
    color: '#999',
    fontSize: 14,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: '#FFFFFF',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    padding: 24,
    maxHeight: '80%',
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#333',
    marginBottom: 20,
  },
  modalInput: {
    backgroundColor: '#F5F5F5',
    borderRadius: 8,
    padding: 12,
    fontSize: 14,
    marginBottom: 16,
  },
  modalActions: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    gap: 12,
    marginTop: 8,
  },
  modalCancelButton: {
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 8,
  },
  modalCancelButtonText: {
    color: '#666',
    fontSize: 14,
    fontWeight: '600',
  },
  modalSaveButton: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 8,
    minWidth: 80,
    alignItems: 'center',
  },
  modalSaveButtonText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
});

export default InventoryScreen;

