import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

// Platform Admin Dashboard
import PlatformAdminLayout from './layouts/PlatformAdminLayout';
import PlatformOverview from './pages/Overview';
import PlatformStoreManagement from './pages/StoreManagement';
import PlatformBlockchainLogs from './pages/BlockchainLogs';
import PlatformAnalytics from './pages/Analytics';

import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        {/* Platform Admin Dashboard Routes */}
        <Route path="/" element={<PlatformAdminLayout />}>
          <Route index element={<PlatformOverview />} />
          <Route path="stores" element={<PlatformStoreManagement />} />
          <Route path="blockchain" element={<PlatformBlockchainLogs />} />
          <Route path="analytics" element={<PlatformAnalytics />} />
        </Route>

        {/* Fallback redirect */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;

