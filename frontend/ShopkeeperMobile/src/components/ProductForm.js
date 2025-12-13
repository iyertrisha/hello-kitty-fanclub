import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, Picker } from 'react-native';
import { COLORS, SIZES } from '../utils/constants';
import Input from './common/Input';
import Button from './common/Button';
import { validateProduct } from '../utils/validation';

const CATEGORIES = [
  'Groceries',
  'Electronics',
  'Clothing',
  'Personal Care',
  'Snacks',
  'Beverages',
  'Other',
];

const ProductForm = ({ onSubmit, initialData = {}, loading = false, onCancel }) => {
  const [formData, setFormData] = useState({
    name: initialData.name || '',
    price: initialData.price?.toString() || '',
    stock_quantity: initialData.stock_quantity?.toString() || '0',
    category: initialData.category || CATEGORIES[0],
    description: initialData.description || '',
  });
  const [errors, setErrors] = useState({});

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: null }));
    }
  };

  const handleSubmit = () => {
    const validation = validateProduct({
      name: formData.name,
      price: formData.price,
      stock_quantity: formData.stock_quantity,
    });

    if (!validation.isValid) {
      setErrors(validation.errors);
      return;
    }

    onSubmit({
      ...formData,
      price: parseFloat(formData.price),
      stock_quantity: parseInt(formData.stock_quantity),
    });
  };

  return (
    <ScrollView style={styles.container}>
      <Input
        label="Product Name *"
        value={formData.name}
        onChangeText={(value) => handleChange('name', value)}
        placeholder="Enter product name"
        error={errors.name}
      />

      <Input
        label="Price (₹) *"
        value={formData.price}
        onChangeText={(value) => handleChange('price', value)}
        placeholder="Enter price"
        keyboardType="numeric"
        error={errors.price}
      />

      <Input
        label="Stock Quantity *"
        value={formData.stock_quantity}
        onChangeText={(value) => handleChange('stock_quantity', value)}
        placeholder="Enter stock quantity"
        keyboardType="numeric"
        error={errors.stock_quantity}
      />

      <View style={styles.pickerContainer}>
        <Text style={styles.pickerLabel}>Category</Text>
        <View style={styles.pickerWrapper}>
          {CATEGORIES.map((category) => (
            <Button
              key={category}
              title={category}
              variant={formData.category === category ? 'primary' : 'secondary'}
              onPress={() => handleChange('category', category)}
              style={styles.categoryButton}
            />
          ))}
        </View>
      </View>

      <Input
        label="Description (Optional)"
        value={formData.description}
        onChangeText={(value) => handleChange('description', value)}
        placeholder="Enter product description"
        multiline
        numberOfLines={4}
      />

      <View style={styles.buttonRow}>
        {onCancel && (
          <Button
            title="Cancel"
            variant="secondary"
            onPress={onCancel}
            style={styles.cancelButton}
          />
        )}
        <Button
          title="Save Product"
          onPress={handleSubmit}
          loading={loading}
          style={styles.submitButton}
        />
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: SIZES.padding,
  },
  pickerContainer: {
    marginBottom: SIZES.margin,
  },
  pickerLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.text,
    marginBottom: 8,
  },
  pickerWrapper: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  categoryButton: {
    marginRight: 8,
    marginBottom: 8,
    minWidth: 100,
  },
  buttonRow: {
    flexDirection: 'row',
    marginTop: SIZES.margin * 2,
  },
  cancelButton: {
    flex: 1,
    marginRight: 8,
  },
  submitButton: {
    flex: 1,
  },
});

export default ProductForm;



