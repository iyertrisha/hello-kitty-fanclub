import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

// Platform Admin Dashboard
import PlatformAdminLayout from './layouts/PlatformAdminLayout';
import Overview from './pages/platform-admin/Overview';
import StoreManagement from './pages/platform-admin/StoreManagement';
import BlockchainLogs from './pages/platform-admin/BlockchainLogs';
import Analytics from './pages/platform-admin/Analytics';
import GeographicMap from './pages/platform-admin/GeographicMap';

import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        {/* Platform Admin Dashboard Routes */}
        <Route path="/" element={<PlatformAdminLayout />}>
          <Route index element={<Overview />} />
          <Route path="stores" element={<StoreManagement />} />
          <Route path="map" element={<GeographicMap />} />
          <Route path="blockchain" element={<BlockchainLogs />} />
          <Route path="analytics" element={<Analytics />} />
        </Route>

        {/* Fallback redirect */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
