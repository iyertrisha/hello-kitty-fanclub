import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import { Text } from 'react-native';

// Screens
import DashboardScreen from '../screens/DashboardScreen';
import RecordTransactionScreen from '../screens/RecordTransactionScreen';
import CreditScoreScreen from '../screens/CreditScoreScreen';
import InventoryScreen from '../screens/InventoryScreen';
import CooperativeScreen from '../screens/CooperativeScreen';

const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

const DashboardStack = () => {
  return (
    <Stack.Navigator>
      <Stack.Screen
        name="DashboardMain"
        component={DashboardScreen}
        options={{ headerShown: false }}
      />
    </Stack.Navigator>
  );
};

const TransactionStack = () => {
  return (
    <Stack.Navigator>
      <Stack.Screen
        name="RecordTransactionMain"
        component={RecordTransactionScreen}
        options={{ headerShown: false }}
      />
    </Stack.Navigator>
  );
};

const CreditScoreStack = () => {
  return (
    <Stack.Navigator>
      <Stack.Screen
        name="CreditScoreMain"
        component={CreditScoreScreen}
        options={{ headerShown: false }}
      />
    </Stack.Navigator>
  );
};

const InventoryStack = () => {
  return (
    <Stack.Navigator>
      <Stack.Screen
        name="InventoryMain"
        component={InventoryScreen}
        options={{ headerShown: false }}
      />
    </Stack.Navigator>
  );
};

const CooperativeStack = () => {
  return (
    <Stack.Navigator>
      <Stack.Screen
        name="CooperativeMain"
        component={CooperativeScreen}
        options={{ headerShown: false }}
      />
    </Stack.Navigator>
  );
};

const AppNavigator = () => {
  return (
    <NavigationContainer>
      <Tab.Navigator
        screenOptions={{
          tabBarActiveTintColor: '#007AFF',
          tabBarInactiveTintColor: '#8E8E93',
          tabBarStyle: {
            height: 60,
            paddingBottom: 8,
            paddingTop: 8,
          },
          headerShown: false,
        }}
      >
        <Tab.Screen
          name="Dashboard"
          component={DashboardStack}
          options={{
            tabBarLabel: 'Dashboard',
            tabBarIcon: ({ color, size }) => (
              <Text style={{ color, fontSize: size }}>🏠</Text>
            ),
          }}
        />
        <Tab.Screen
          name="RecordTransaction"
          component={TransactionStack}
          options={{
            tabBarLabel: 'Record',
            tabBarIcon: ({ color, size }) => (
              <Text style={{ color, fontSize: size }}>🎤</Text>
            ),
          }}
        />
        <Tab.Screen
          name="CreditScore"
          component={CreditScoreStack}
          options={{
            tabBarLabel: 'Credit',
            tabBarIcon: ({ color, size }) => (
              <Text style={{ color, fontSize: size }}>⭐</Text>
            ),
          }}
        />
        <Tab.Screen
          name="Inventory"
          component={InventoryStack}
          options={{
            tabBarLabel: 'Inventory',
            tabBarIcon: ({ color, size }) => (
              <Text style={{ color, fontSize: size }}>📦</Text>
            ),
          }}
        />
        <Tab.Screen
          name="Cooperative"
          component={CooperativeStack}
          options={{
            tabBarLabel: 'Cooperative',
            tabBarIcon: ({ color, size }) => (
              <Text style={{ color, fontSize: size }}>👥</Text>
            ),
          }}
        />
      </Tab.Navigator>
    </NavigationContainer>
  );
};

export default AppNavigator;

