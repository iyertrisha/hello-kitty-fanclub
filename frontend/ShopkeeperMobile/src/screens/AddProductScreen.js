import React, { useState } from 'react';
import {
  View,
  StyleSheet,
  Alert,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { COLORS, SIZES } from '../utils/constants';
import { apiService } from '../services/api';
import ProductForm from '../components/ProductForm';
import { saveProductOffline, addToSyncQueue } from '../services/offlineStorage';

const AddProductScreen = () => {
  const navigation = useNavigation();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (data) => {
    setLoading(true);
    try {
      // Try to submit online first
      try {
        await apiService.addProduct('1', data);
        Alert.alert('Success', 'Product added successfully', [
          { text: 'OK', onPress: () => navigation.goBack() },
        ]);
      } catch (error) {
        // If offline, save locally
        console.log('Offline mode - saving product locally');
        await saveProductOffline(data);
        await addToSyncQueue('addProduct', { shopkeeperId: '1', ...data });
        Alert.alert(
          'Saved Offline',
          'Product saved locally and will sync when online',
          [{ text: 'OK', onPress: () => navigation.goBack() }]
        );
      }
    } catch (error) {
      console.error('Error adding product:', error);
      Alert.alert('Error', 'Failed to add product');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <ProductForm
        onSubmit={handleSubmit}
        loading={loading}
        onCancel={() => navigation.goBack()}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
});

export default AddProductScreen;



