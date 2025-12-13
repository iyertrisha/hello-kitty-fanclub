import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { StatusBar, View } from 'react-native';
import AppNavigator from './src/navigation/AppNavigator';
import OfflineIndicator from './src/components/common/OfflineIndicator';

const App = () => {
  return (
    <View style={{ flex: 1 }}>
      <NavigationContainer>
        <StatusBar barStyle="dark-content" />
        <AppNavigator />
        <OfflineIndicator />
      </NavigationContainer>
    </View>
  );
};

export default App;

