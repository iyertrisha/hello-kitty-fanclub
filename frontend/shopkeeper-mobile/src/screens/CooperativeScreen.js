import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  Alert,
  ActivityIndicator,
} from 'react-native';
import apiService from '../services/api';
import AsyncStorage from '@react-native-async-storage/async-storage';

const CooperativeScreen = () => {
  const [cooperatives, setCooperatives] = useState([]);
  const [myCooperatives, setMyCooperatives] = useState([]);
  const [selectedCoop, setSelectedCoop] = useState(null);
  const [members, setMembers] = useState([]);
  const [orders, setOrders] = useState([]);
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [shopkeeperId, setShopkeeperId] = useState(null);

  useEffect(() => {
    loadShopkeeperId();
  }, []);

  useEffect(() => {
    if (shopkeeperId) {
      loadCooperatives();
    }
  }, [shopkeeperId]);

  const loadShopkeeperId = async () => {
    try {
      const id = await AsyncStorage.getItem('shopkeeper_id');
      setShopkeeperId(id || '1');
    } catch (error) {
      console.error('Error loading shopkeeper ID:', error);
      setShopkeeperId('1');
    }
  };

  const loadCooperatives = async () => {
    try {
      setLoading(true);
      const data = await apiService.getCooperatives();
      const coopList = data.data || data || [];
      setCooperatives(coopList);
      
      // Filter cooperatives where current shopkeeper is a member
      // This would typically come from the API
      setMyCooperatives(coopList.filter((coop) => coop.members?.includes(shopkeeperId)));
    } catch (error) {
      console.error('Error loading cooperatives:', error);
      Alert.alert('Error', 'Failed to load cooperatives');
    } finally {
      setLoading(false);
    }
  };

  const loadCooperativeDetails = async (coopId) => {
    try {
      const [coopData, membersData, ordersData] = await Promise.all([
        apiService.getCooperativeById(coopId),
        apiService.getCooperativeMembers(coopId),
        apiService.getCooperativeOrders(coopId),
      ]);
      
      setSelectedCoop(coopData);
      setMembers(membersData.data || membersData || []);
      setOrders(ordersData.data || ordersData || []);
    } catch (error) {
      console.error('Error loading cooperative details:', error);
      Alert.alert('Error', 'Failed to load cooperative details');
    }
  };

  const handleJoinCooperative = async (coopId) => {
    Alert.alert(
      'Join Cooperative',
      'Are you sure you want to join this cooperative?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Join',
          onPress: async () => {
            try {
              setLoading(true);
              await apiService.joinCooperative(coopId);
              Alert.alert('Success', 'Successfully joined cooperative');
              loadCooperatives();
            } catch (error) {
              console.error('Error joining cooperative:', error);
              Alert.alert('Error', 'Failed to join cooperative');
            } finally {
              setLoading(false);
            }
          },
        },
      ]
    );
  };

  const handleLeaveCooperative = async (coopId) => {
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
              setLoading(true);
              await apiService.leaveCooperative(coopId);
              Alert.alert('Success', 'Successfully left cooperative');
              loadCooperatives();
              setSelectedCoop(null);
            } catch (error) {
              console.error('Error leaving cooperative:', error);
              Alert.alert('Error', 'Failed to leave cooperative');
            } finally {
              setLoading(false);
            }
          },
        },
      ]
    );
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadCooperatives();
    if (selectedCoop) {
      await loadCooperativeDetails(selectedCoop.id);
    }
    setRefreshing(false);
  };

  const isMember = (coopId) => {
    return myCooperatives.some((coop) => coop.id === coopId);
  };

  if (selectedCoop) {
    return (
      <ScrollView
        style={styles.container}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        <View style={styles.header}>
          <TouchableOpacity
            onPress={() => setSelectedCoop(null)}
            style={styles.backButton}
          >
            <Text style={styles.backButtonText}>← Back</Text>
          </TouchableOpacity>
          <Text style={styles.title}>{selectedCoop.name}</Text>
        </View>

        <View style={styles.content}>
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Cooperative Details</Text>
            <View style={styles.detailCard}>
              <Text style={styles.detailText}>
                <Text style={styles.detailLabel}>Description: </Text>
                {selectedCoop.description || 'No description available'}
              </Text>
              <Text style={styles.detailText}>
                <Text style={styles.detailLabel}>Members: </Text>
                {members.length}
              </Text>
              {selectedCoop.revenue_split && (
                <Text style={styles.detailText}>
                  <Text style={styles.detailLabel}>Revenue Split: </Text>
                  {selectedCoop.revenue_split}%
                </Text>
              )}
            </View>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Members</Text>
            {members.length > 0 ? (
              members.map((member) => (
                <View key={member.id} style={styles.memberCard}>
                  <Text style={styles.memberName}>
                    {member.name || `Shopkeeper ${member.id}`}
                  </Text>
                  <Text style={styles.memberInfo}>
                    {member.address || 'No address'}
                  </Text>
                </View>
              ))
            ) : (
              <Text style={styles.emptyText}>No members found</Text>
            )}
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Bulk Orders</Text>
            {orders.length > 0 ? (
              orders.map((order) => (
                <View key={order.id} style={styles.orderCard}>
                  <Text style={styles.orderTitle}>Order #{order.id}</Text>
                  <Text style={styles.orderInfo}>
                    Amount: ₹{order.total_amount?.toFixed(2)}
                  </Text>
                  <Text style={styles.orderInfo}>
                    Date: {new Date(order.created_at).toLocaleDateString()}
                  </Text>
                  <Text style={styles.orderInfo}>
                    Status: {order.status}
                  </Text>
                </View>
              ))
            ) : (
              <Text style={styles.emptyText}>No orders found</Text>
            )}
          </View>

          {isMember(selectedCoop.id) && (
            <TouchableOpacity
              style={styles.leaveButton}
              onPress={() => handleLeaveCooperative(selectedCoop.id)}
            >
              <Text style={styles.leaveButtonText}>Leave Cooperative</Text>
            </TouchableOpacity>
          )}
        </View>
      </ScrollView>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <View style={styles.header}>
        <Text style={styles.title}>Cooperatives</Text>
      </View>

      <View style={styles.content}>
        {loading && !cooperatives.length ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#007AFF" />
          </View>
        ) : (
          <>
            {myCooperatives.length > 0 && (
              <View style={styles.section}>
                <Text style={styles.sectionTitle}>My Cooperatives</Text>
                {myCooperatives.map((coop) => (
                  <TouchableOpacity
                    key={coop.id}
                    style={styles.coopCard}
                    onPress={() => loadCooperativeDetails(coop.id)}
                  >
                    <Text style={styles.coopName}>{coop.name}</Text>
                    <Text style={styles.coopInfo}>
                      {coop.members?.length || 0} members
                    </Text>
                    <Text style={styles.coopBadge}>Member</Text>
                  </TouchableOpacity>
                ))}
              </View>
            )}

            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Available Cooperatives</Text>
              {cooperatives
                .filter((coop) => !isMember(coop.id))
                .map((coop) => (
                  <View key={coop.id} style={styles.coopCard}>
                    <Text style={styles.coopName}>{coop.name}</Text>
                    <Text style={styles.coopInfo}>
                      {coop.members?.length || 0} members
                    </Text>
                    <TouchableOpacity
                      style={styles.joinButton}
                      onPress={() => handleJoinCooperative(coop.id)}
                    >
                      <Text style={styles.joinButtonText}>Join</Text>
                    </TouchableOpacity>
                  </View>
                ))}
              {cooperatives.filter((coop) => !isMember(coop.id)).length ===
                0 && (
                <Text style={styles.emptyText}>
                  No available cooperatives
                </Text>
              )}
            </View>
          </>
        )}
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
  backButton: {
    marginBottom: 8,
  },
  backButtonText: {
    color: '#007AFF',
    fontSize: 16,
    fontWeight: '600',
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: '#333',
  },
  content: {
    padding: 16,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#333',
    marginBottom: 12,
  },
  coopCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  coopName: {
    fontSize: 18,
    fontWeight: '700',
    color: '#333',
    marginBottom: 4,
  },
  coopInfo: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  coopBadge: {
    alignSelf: 'flex-start',
    backgroundColor: '#E8F5E9',
    color: '#2E7D32',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
    fontSize: 12,
    fontWeight: '600',
  },
  joinButton: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 20,
    paddingVertical: 8,
    borderRadius: 8,
    alignSelf: 'flex-start',
    marginTop: 8,
  },
  joinButtonText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
  detailCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  detailText: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
    lineHeight: 20,
  },
  detailLabel: {
    fontWeight: '600',
    color: '#333',
  },
  memberCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  memberName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  memberInfo: {
    fontSize: 13,
    color: '#666',
  },
  orderCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  orderTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#333',
    marginBottom: 8,
  },
  orderInfo: {
    fontSize: 13,
    color: '#666',
    marginBottom: 4,
  },
  leaveButton: {
    backgroundColor: '#FF3B30',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 16,
  },
  leaveButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  loadingContainer: {
    padding: 40,
    alignItems: 'center',
  },
  emptyText: {
    color: '#999',
    fontSize: 14,
    textAlign: 'center',
    padding: 20,
  },
});

export default CooperativeScreen;

