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

const CooperativeDetailScreen = () => {
  const route = useRoute();
  const navigation = useNavigation();
  const { cooperativeId } = route.params;
  const [cooperative, setCooperative] = useState(null);
  const [members, setMembers] = useState([]);
  const [isMember, setIsMember] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCooperativeDetails();
  }, [cooperativeId]);

  const loadCooperativeDetails = async () => {
    try {
      setLoading(true);
      const [coopData, membersData] = await Promise.all([
        apiService.getCooperativeById(cooperativeId),
        apiService.getCooperativeMembers(cooperativeId),
      ]);

      setCooperative(coopData);
      setMembers(membersData.data || []);
      // In real app, check membership from API
      setIsMember(cooperativeId === 1); // Mock: user is member of cooperative 1
    } catch (error) {
      console.error('Error loading cooperative details:', error);
      Alert.alert('Error', 'Failed to load cooperative details');
    } finally {
      setLoading(false);
    }
  };

  const handleJoin = () => {
    Alert.alert(
      'Join Cooperative',
      'Are you sure you want to join this cooperative?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Join',
          onPress: async () => {
            try {
              await apiService.joinCooperative(cooperativeId);
              setIsMember(true);
              Alert.alert('Success', 'Successfully joined cooperative');
              loadCooperativeDetails();
            } catch (error) {
              Alert.alert('Error', 'Failed to join cooperative');
            }
          },
        },
      ]
    );
  };

  const handleLeave = () => {
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
              await apiService.leaveCooperative(cooperativeId);
              setIsMember(false);
              Alert.alert('Success', 'Successfully left cooperative');
              loadCooperativeDetails();
            } catch (error) {
              Alert.alert('Error', 'Failed to leave cooperative');
            }
          },
        },
      ]
    );
  };

  if (loading) {
    return <LoadingSpinner text="Loading cooperative details..." />;
  }

  if (!cooperative) {
    return (
      <View style={styles.container}>
        <Text style={styles.errorText}>Cooperative not found</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.card}>
        <Text style={styles.name}>{cooperative.name}</Text>
        <Text style={styles.description}>{cooperative.description}</Text>
      </Card>

      <Card style={styles.card}>
        <Text style={styles.sectionTitle}>Cooperative Information</Text>
        <View style={styles.infoRow}>
          <Text style={styles.label}>Established:</Text>
          <Text style={styles.value}>{formatDate(cooperative.established)}</Text>
        </View>
        <View style={styles.infoRow}>
          <Text style={styles.label}>Total Members:</Text>
          <Text style={styles.value}>{cooperative.total_members}</Text>
        </View>
        <View style={styles.infoRow}>
          <Text style={styles.label}>Revenue Split:</Text>
          <Text style={styles.value}>{cooperative.revenue_split}%</Text>
        </View>
        <View style={styles.infoRow}>
          <Text style={styles.label}>Total Orders:</Text>
          <Text style={styles.value}>{cooperative.total_orders}</Text>
        </View>
        <View style={styles.infoRow}>
          <Text style={styles.label}>Total Revenue:</Text>
          <Text style={styles.value}>{formatCurrency(cooperative.total_revenue)}</Text>
        </View>
      </Card>

      <Card style={styles.card}>
        <Text style={styles.sectionTitle}>Members ({members.length})</Text>
        {members.length === 0 ? (
          <Text style={styles.emptyText}>No members found</Text>
        ) : (
          members.slice(0, 10).map((member) => (
            <View key={member.id} style={styles.memberRow}>
              <View style={styles.memberInfo}>
                <Text style={styles.memberName}>{member.name}</Text>
                <Text style={styles.memberAddress}>{member.address}</Text>
                <Text style={styles.memberPhone}>{member.phone}</Text>
              </View>
              <View style={styles.memberStats}>
                <Text style={styles.memberContribution}>
                  {formatCurrency(member.total_contribution)}
                </Text>
                <Text style={styles.memberDate}>
                  Joined: {formatDate(member.joined_date)}
                </Text>
              </View>
            </View>
          ))
        )}
        {members.length > 10 && (
          <Text style={styles.moreText}>+ {members.length - 10} more members</Text>
        )}
      </Card>

      <Card style={styles.card}>
        {isMember ? (
          <Button
            title="Leave Cooperative"
            variant="danger"
            onPress={handleLeave}
          />
        ) : (
          <Button
            title="Join Cooperative"
            onPress={handleJoin}
          />
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
    marginTop: 0,
  },
  name: {
    fontSize: 24,
    fontWeight: 'bold',
    color: COLORS.text,
    marginBottom: 8,
  },
  description: {
    fontSize: 14,
    color: COLORS.textSecondary,
    lineHeight: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: COLORS.text,
    marginBottom: SIZES.padding,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  label: {
    fontSize: 14,
    color: COLORS.textSecondary,
  },
  value: {
    fontSize: 14,
    color: COLORS.text,
    fontWeight: '500',
  },
  memberRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.border,
  },
  memberInfo: {
    flex: 1,
  },
  memberName: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.text,
    marginBottom: 4,
  },
  memberAddress: {
    fontSize: 12,
    color: COLORS.textSecondary,
    marginBottom: 2,
  },
  memberPhone: {
    fontSize: 12,
    color: COLORS.textSecondary,
  },
  memberStats: {
    alignItems: 'flex-end',
  },
  memberContribution: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.primary,
    marginBottom: 4,
  },
  memberDate: {
    fontSize: 12,
    color: COLORS.textSecondary,
  },
  emptyText: {
    textAlign: 'center',
    color: COLORS.textSecondary,
    fontSize: 14,
    padding: SIZES.padding,
  },
  moreText: {
    textAlign: 'center',
    color: COLORS.primary,
    fontSize: 14,
    marginTop: 8,
    fontWeight: '600',
  },
  errorText: {
    textAlign: 'center',
    color: COLORS.error,
    fontSize: 16,
    marginTop: 20,
  },
});

export default CooperativeDetailScreen;
