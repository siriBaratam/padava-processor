import React from 'react';
import { Routes, Route } from 'react-router-dom';

import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import ScoutPage from './pages/ScoutPage';
import AccountantPage from './pages/AccountantPage';
import StrategistPage from './pages/StrategistPage';
import AllocatorPage from './pages/AllocatorPage';
import DealmakerPage from './pages/DealmakerPage';
import NavigatorPage from './pages/NavigatorPage';
import AlertsPage from './pages/AlertsPage';
import ReportsPage from './pages/ReportsPage';
import SettingsPage from './pages/SettingsPage';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/dashboard" element={<DashboardPage />} />
      <Route path="/scout" element={<ScoutPage />} />
      <Route path="/accountant" element={<AccountantPage />} />
      <Route path="/strategist" element={<StrategistPage />} />
      <Route path="/allocator" element={<AllocatorPage />} />
      <Route path="/dealmaker" element={<DealmakerPage />} />
      <Route path="/navigator" element={<NavigatorPage />} />
      <Route path="/alerts" element={<AlertsPage />} />
      <Route path="/reports" element={<ReportsPage />} />
      <Route path="/settings" element={<SettingsPage />} />
    </Routes>
  );
}
