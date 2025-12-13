import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  RefreshControl,
  Alert,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { COLORS, SIZES } from '../utils/constants';
import { apiService } from '../services/api';
import CooperativeCard from '../components/CooperativeCard';
import LoadingSpinner from '../components/common/LoadingSpinner';
import Card from '../components/common/Card';

const CooperativesScreen = () => {
  const navigation = useNavigation();
  const [cooperatives, setCooperatives] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [memberIds, setMemberIds] = useState(new Set()); // Track which cooperatives user is member of

  useEffect(() => {
    loadCooperatives();
  }, []);

  const loadCooperatives = async () => {
    try {
      setLoading(true);
      const response = await apiService.getCooperatives();
      setCooperatives(response.data || []);
      // In real app, check membership status from API
      // For now, mock some memberships
      setMemberIds(new Set([1])); // Mock: user is member of cooperative 1
    } catch (error) {
      console.error('Error loading cooperatives:', error);
      Alert.alert('Error', 'Failed to load cooperatives');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadCooperatives();
    setRefreshing(false);
  };

  const handleCooperativePress = (cooperative) => {
    navigation.navigate('CooperativeDetail', { cooperativeId: cooperative.id });
  };

  const handleJoin = async (coopId) => {
    Alert.alert(
      'Join Cooperative',
      'Are you sure you want to join this cooperative?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Join',
          onPress: async () => {
            try {
              await apiService.joinCooperative(coopId);
              setMemberIds(prev => new Set([...prev, coopId]));
              Alert.alert('Success', 'Successfully joined cooperative');
              loadCooperatives();
            } catch (error) {
              Alert.alert('Error', 'Failed to join cooperative');
            }
          },
        },
      ]
    );
  };

  const handleLeave = async (coopId) => {
    Alert.alert(
      'Leave Cooperative',
      'Are you sure you want to leave this cooperative?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Leave',
          style: 'destructive',
          onPress: async () => {
            try {
              await apiService.leaveCooperative(coopId);
              setMemberIds(prev => {
                const newSet = new Set(prev);
                newSet.delete(coopId);
                return newSet;
              });
              Alert.alert('Success', 'Successfully left cooperative');
              loadCooperatives();
            } catch (error) {
              Alert.alert('Error', 'Failed to leave cooperative');
            }
          },
        },
      ]
    );
  };

  if (loading) {
    return <LoadingSpinner text="Loading cooperatives..." />;
  }

  return (
    <View style={styles.container}>
      {cooperatives.length === 0 ? (
        <Card style={styles.emptyCard}>
          <Text style={styles.emptyText}>No cooperatives available</Text>
        </Card>
      ) : (
        <FlatList
          data={cooperatives}
          keyExtractor={(item) => item.id.toString()}
          renderItem={({ item }) => (
            <CooperativeCard
              cooperative={item}
              isMember={memberIds.has(item.id)}
              onPress={() => handleCooperativePress(item)}
              onJoin={() => handleJoin(item.id)}
              onLeave={() => handleLeave(item.id)}
            />
          )}
          contentContainerStyle={styles.listContent}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  listContent: {
    padding: SIZES.padding,
  },
  emptyCard: {
    alignItems: 'center',
    padding: SIZES.padding * 2,
    margin: SIZES.padding,
  },
  emptyText: {
    fontSize: 16,
    color: COLORS.textSecondary,
  },
});

export default CooperativesScreen;
