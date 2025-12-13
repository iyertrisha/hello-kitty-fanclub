import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import TabNavigator from './TabNavigator';
import RecordTransactionScreen from '../screens/RecordTransactionScreen';
import CreditScoreScreen from '../screens/CreditScoreScreen';
import InventoryScreen from '../screens/InventoryScreen';
import InventoryDetailScreen from '../screens/InventoryDetailScreen';
import AddProductScreen from '../screens/AddProductScreen';
import CooperativesScreen from '../screens/CooperativesScreen';
import CooperativeDetailScreen from '../screens/CooperativeDetailScreen';
import TransactionListScreen from '../screens/TransactionListScreen';
import TransactionDetailScreen from '../screens/TransactionDetailScreen';

const Stack = createStackNavigator();

const AppNavigator = () => {
  return (
    <Stack.Navigator
      screenOptions={{
        headerStyle: {
          backgroundColor: '#6200ee',
        },
        headerTintColor: '#fff',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      }}
    >
      <Stack.Screen 
        name="MainTabs" 
        component={TabNavigator} 
        options={{ headerShown: false }}
      />
      <Stack.Screen 
        name="RecordTransaction" 
        component={RecordTransactionScreen}
        options={{ title: 'Record Transaction' }}
      />
      <Stack.Screen 
        name="CreditScore" 
        component={CreditScoreScreen}
        options={{ title: 'Credit Score' }}
      />
      <Stack.Screen 
        name="Inventory" 
        component={InventoryScreen}
        options={{ title: 'Inventory' }}
      />
      <Stack.Screen 
        name="InventoryDetail" 
        component={InventoryDetailScreen}
        options={{ title: 'Product Details' }}
      />
      <Stack.Screen 
        name="AddProduct" 
        component={AddProductScreen}
        options={{ title: 'Add Product' }}
      />
      <Stack.Screen 
        name="Cooperatives" 
        component={CooperativesScreen}
        options={{ title: 'Cooperatives' }}
      />
      <Stack.Screen 
        name="CooperativeDetail" 
        component={CooperativeDetailScreen}
        options={{ title: 'Cooperative Details' }}
      />
      <Stack.Screen 
        name="TransactionList" 
        component={TransactionListScreen}
        options={{ title: 'Transactions' }}
      />
      <Stack.Screen 
        name="TransactionDetail" 
        component={TransactionDetailScreen}
        options={{ title: 'Transaction Details' }}
      />
    </Stack.Navigator>
  );
};

export default AppNavigator;

