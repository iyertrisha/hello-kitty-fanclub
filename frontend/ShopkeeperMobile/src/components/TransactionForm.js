import React, { useState } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { COLORS, SIZES, TRANSACTION_TYPES } from '../utils/constants';
import Input from './common/Input';
import Button from './common/Button';
import { validateTransaction } from '../utils/validation';

const TransactionForm = ({ onSubmit, initialData = {}, loading = false }) => {
  const [formData, setFormData] = useState({
    type: initialData.type || TRANSACTION_TYPES.SALE,
    amount: initialData.amount?.toString() || '',
    customer_id: initialData.customer_id || '',
    transcript: initialData.transcript || '',
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
    const validation = validateTransaction({
      type: formData.type,
      amount: formData.amount,
      customer_id: formData.customer_id,
    });

    if (!validation.isValid) {
      setErrors(validation.errors);
      return;
    }

    onSubmit({
      ...formData,
      amount: parseFloat(formData.amount),
    });
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.typeSelector}>
        {Object.values(TRANSACTION_TYPES).map((type) => (
          <Button
            key={type}
            title={type.charAt(0).toUpperCase() + type.slice(1)}
            variant={formData.type === type ? 'primary' : 'secondary'}
            onPress={() => handleChange('type', type)}
            style={styles.typeButton}
          />
        ))}
      </View>

      <Input
        label="Amount (₹) *"
        value={formData.amount}
        onChangeText={(value) => handleChange('amount', value)}
        placeholder="Enter amount"
        keyboardType="numeric"
        error={errors.amount}
      />

      <Input
        label="Customer ID *"
        value={formData.customer_id}
        onChangeText={(value) => handleChange('customer_id', value)}
        placeholder="Enter customer ID"
        error={errors.customer_id}
      />

      {formData.transcript ? (
        <View style={styles.transcriptContainer}>
          <Input
            label="Transcript"
            value={formData.transcript}
            onChangeText={(value) => handleChange('transcript', value)}
            placeholder="Transaction transcript"
            multiline
            numberOfLines={4}
            editable={false}
          />
        </View>
      ) : null}

      <Button
        title="Submit Transaction"
        onPress={handleSubmit}
        loading={loading}
        style={styles.submitButton}
      />
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: SIZES.padding,
  },
  typeSelector: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: SIZES.margin,
  },
  typeButton: {
    flex: 1,
    marginHorizontal: 4,
  },
  transcriptContainer: {
    marginTop: SIZES.margin,
  },
  submitButton: {
    marginTop: SIZES.margin * 2,
  },
});

export default TransactionForm;



