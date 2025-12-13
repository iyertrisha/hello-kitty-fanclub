import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Alert,
  ActivityIndicator,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useNavigation } from '@react-navigation/native';
import { COLORS, SIZES } from '../utils/constants';
import VoiceRecorder from '../components/VoiceRecorder';
import TransactionForm from '../components/TransactionForm';
import { apiService } from '../services/api';
import { saveTransactionOffline, addToSyncQueue } from '../services/offlineStorage';

const RecordTransactionScreen = () => {
  const navigation = useNavigation();
  const [transcript, setTranscript] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [shopkeeperId, setShopkeeperId] = useState(null);
  const [formData, setFormData] = useState({
    type: 'sale',
    amount: '',
    customer_id: '',
    transcript: '',
  });

  useEffect(() => {
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
    setFormData(prev => ({ ...prev, transcript: text }));
    
    // Try to extract amount from transcript
    const amountMatch = text.match(/₹?(\d+(?:\.\d{2})?)/);
    if (amountMatch) {
      setFormData(prev => ({ ...prev, amount: amountMatch[1] }));
    }
  };

  const handleSubmit = async (data) => {
    setIsSubmitting(true);
    try {
      const transactionData = {
        ...data,
        shopkeeper_id: shopkeeperId,
        transcript: transcript || data.transcript,
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
    setFormData({
      type: 'sale',
      amount: '',
      customer_id: '',
      transcript: '',
    });
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Voice Recording</Text>
        <VoiceRecorder
          onTranscriptReceived={handleTranscriptReceived}
          onError={(error) => Alert.alert('Error', error)}
        />
      </View>

      <View style={styles.section}>
        <TransactionForm
          initialData={{
            ...formData,
            transcript: transcript,
          }}
          onSubmit={handleSubmit}
          loading={isSubmitting}
        />
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  section: {
    padding: SIZES.padding,
    backgroundColor: COLORS.surface,
    marginBottom: SIZES.margin,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: COLORS.text,
    marginBottom: SIZES.margin,
  },
});

export default RecordTransactionScreen;
