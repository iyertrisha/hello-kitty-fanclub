import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
} from 'react-native';
import VoiceRecorder from '../components/VoiceRecorder';
import apiService from '../services/api';
import { saveTransactionOffline, addToSyncQueue } from '../utils/offlineStorage';
import AsyncStorage from '@react-native-async-storage/async-storage';

const RecordTransactionScreen = () => {
  const [transcript, setTranscript] = useState('');
  const [transactionType, setTransactionType] = useState('sale');
  const [amount, setAmount] = useState('');
  const [customerId, setCustomerId] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [shopkeeperId, setShopkeeperId] = useState(null);

  React.useEffect(() => {
    loadShopkeeperId();
  }, []);

  const loadShopkeeperId = async () => {
    try {
      const id = await AsyncStorage.getItem('shopkeeper_id');
      setShopkeeperId(id || '1');
    } catch (error) {
      console.error('Error loading shopkeeper ID:', error);
      setShopkeeperId('1');
    }
  };

  const handleTranscriptReceived = (text) => {
    setTranscript(text);
    // Try to extract amount and customer info from transcript
    // This is a simple implementation - you might want to use NLP here
    const amountMatch = text.match(/₹?(\d+(?:\.\d{2})?)/);
    if (amountMatch) {
      setAmount(amountMatch[1]);
    }
  };

  const handleSubmit = async () => {
    if (!amount || !customerId) {
      Alert.alert('Error', 'Please fill in all required fields');
      return;
    }

    setIsSubmitting(true);
    try {
      const transactionData = {
        type: transactionType,
        amount: parseFloat(amount),
        customer_id: customerId,
        shopkeeper_id: shopkeeperId,
        transcript: transcript,
      };

      // Try to submit online first
      try {
        const result = await apiService.createTransaction(transactionData);
        Alert.alert('Success', 'Transaction recorded successfully', [
          { text: 'OK', onPress: () => resetForm() },
        ]);
      } catch (error) {
        // If offline, save locally
        console.log('Offline mode - saving transaction locally');
        await saveTransactionOffline(transactionData);
        await addToSyncQueue('createTransaction', transactionData);
        Alert.alert(
          'Saved Offline',
          'Transaction saved locally and will sync when online',
          [{ text: 'OK', onPress: () => resetForm() }]
        );
      }
    } catch (error) {
      console.error('Error submitting transaction:', error);
      Alert.alert('Error', 'Failed to record transaction');
    } finally {
      setIsSubmitting(false);
    }
  };

  const resetForm = () => {
    setTranscript('');
    setAmount('');
    setCustomerId('');
    setTransactionType('sale');
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Record Transaction</Text>
      </View>

      <View style={styles.content}>
        {/* Voice Recorder */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Voice Recording</Text>
          <VoiceRecorder
            onTranscriptReceived={handleTranscriptReceived}
            onError={(error) => Alert.alert('Error', error)}
          />
        </View>

        {/* Transcript Display */}
        {transcript ? (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Transcript</Text>
            <View style={styles.transcriptBox}>
              <Text style={styles.transcriptText}>{transcript}</Text>
            </View>
          </View>
        ) : null}

        {/* Transaction Type */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Transaction Type</Text>
          <View style={styles.typeContainer}>
            {['sale', 'credit', 'repay'].map((type) => (
              <TouchableOpacity
                key={type}
                style={[
                  styles.typeButton,
                  transactionType === type && styles.typeButtonActive,
                ]}
                onPress={() => setTransactionType(type)}
              >
                <Text
                  style={[
                    styles.typeButtonText,
                    transactionType === type && styles.typeButtonTextActive,
                  ]}
                >
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Amount Input */}
        <View style={styles.section}>
          <Text style={styles.label}>Amount (₹) *</Text>
          <TextInput
            style={styles.input}
            value={amount}
            onChangeText={setAmount}
            placeholder="Enter amount"
            keyboardType="decimal-pad"
          />
        </View>

        {/* Customer ID Input */}
        <View style={styles.section}>
          <Text style={styles.label}>Customer ID *</Text>
          <TextInput
            style={styles.input}
            value={customerId}
            onChangeText={setCustomerId}
            placeholder="Enter customer ID"
          />
        </View>

        {/* Submit Button */}
        <TouchableOpacity
          style={[styles.submitButton, isSubmitting && styles.submitButtonDisabled]}
          onPress={handleSubmit}
          disabled={isSubmitting}
        >
          {isSubmitting ? (
            <ActivityIndicator color="#FFFFFF" />
          ) : (
            <Text style={styles.submitButtonText}>Submit Transaction</Text>
          )}
        </TouchableOpacity>
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
    padding: 20,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  transcriptBox: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    minHeight: 100,
  },
  transcriptText: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  typeContainer: {
    flexDirection: 'row',
    gap: 12,
  },
  typeButton: {
    flex: 1,
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    backgroundColor: '#F0F0F0',
    alignItems: 'center',
  },
  typeButtonActive: {
    backgroundColor: '#007AFF',
  },
  typeButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
  },
  typeButtonTextActive: {
    color: '#FFFFFF',
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#FFFFFF',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#E0E0E0',
  },
  submitButton: {
    backgroundColor: '#007AFF',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 8,
  },
  submitButtonDisabled: {
    opacity: 0.6,
  },
  submitButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default RecordTransactionScreen;

