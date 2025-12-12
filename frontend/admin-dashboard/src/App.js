import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

// Cooperative Dashboard
import CooperativeLayout from './layouts/AggregatorLayout';
import CooperativeOverview from './pages/aggregator/CooperativeOverview';
import GeographicMap from './pages/aggregator/GeographicMap';
import CooperativeOrders from './pages/aggregator/CooperativeOrders';
import CooperativeBlockchainLogs from './pages/aggregator/BlockchainLogs';

import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        {/* Cooperative Dashboard Routes */}
        <Route path="/" element={<CooperativeLayout />}>
          <Route index element={<CooperativeOverview />} />
          <Route path="map" element={<GeographicMap />} />
          <Route path="orders" element={<CooperativeOrders />} />
          <Route path="blockchain" element={<CooperativeBlockchainLogs />} />
        </Route>

        {/* Fallback redirect */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
