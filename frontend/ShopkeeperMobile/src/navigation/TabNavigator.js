import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import Icon from 'react-native-vector-icons/MaterialIcons';
import DashboardScreen from '../screens/DashboardScreen';
import RecordTransactionScreen from '../screens/RecordTransactionScreen';
import InventoryScreen from '../screens/InventoryScreen';
import CooperativesScreen from '../screens/CooperativesScreen';

const Tab = createBottomTabNavigator();

const TabNavigator = () => {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;

          if (route.name === 'Dashboard') {
            iconName = 'dashboard';
          } else if (route.name === 'Record') {
            iconName = 'mic';
          } else if (route.name === 'Inventory') {
            iconName = 'inventory';
          } else if (route.name === 'Cooperatives') {
            iconName = 'group';
          }

          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#6200ee',
        tabBarInactiveTintColor: 'gray',
        headerShown: false,
      })}
    >
      <Tab.Screen name="Dashboard" component={DashboardScreen} />
      <Tab.Screen name="Record" component={RecordTransactionScreen} />
      <Tab.Screen name="Inventory" component={InventoryScreen} />
      <Tab.Screen name="Cooperatives" component={CooperativesScreen} />
    </Tab.Navigator>
  );
};

export default TabNavigator;



