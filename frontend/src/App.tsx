import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { LoadingSpinner } from './components/common/LoadingSpinner';

// Auth pages
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';

// Patient pages
import PatientDashboard from './pages/patient/Dashboard';
import UploadPage from './pages/patient/UploadPage';
import AnalysisPage from './pages/patient/AnalysisPage';
import AppointmentsPage from './pages/appointments/AppointmentsPage';
import ChatPage from './pages/chat/ChatPage';
import HistoryPage from './pages/history/HistoryPage';
import SettingsPage from './pages/settings/SettingsPage';
import PatientChatPage from './pages/patient/PatientChatPage';

// Doctor pages
import DoctorDashboard from './pages/doctor/Dashboard';
import PatientsPage from './pages/doctor/PatientsPage';
import AnalyticsPage from './pages/doctor/AnalyticsPage';

// Agent page
import AgentPage from './pages/agent/AgentPage';

import './index.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: 'patient' | 'doctor';
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, requiredRole }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return <LoadingSpinner />;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (requiredRole && user.role !== requiredRole) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <>{children}</>;
};

const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return <LoadingSpinner />;
  }

  if (user) {
    return <Navigate to={user.role === 'patient' ? '/dashboard' : '/doctor-dashboard'} replace />;
  }

  return <>{children}</>;
};

function AppRoutes() {
  const { user } = useAuth();

  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={
        <PublicRoute>
          <LoginPage />
        </PublicRoute>
      } />
      <Route path="/register" element={
        <PublicRoute>
          <RegisterPage />
        </PublicRoute>
      } />

      {/* Patient routes */}
      <Route path="/dashboard" element={
        <ProtectedRoute requiredRole="patient">
          <PatientDashboard />
        </ProtectedRoute>
      } />
      <Route path="/upload" element={
        <ProtectedRoute requiredRole="patient">
          <UploadPage />
        </ProtectedRoute>
      } />
      <Route path="/analysis/:filename" element={
        <ProtectedRoute requiredRole="patient">
          <AnalysisPage />
        </ProtectedRoute>
      } />

      {/* Doctor routes */}
      <Route path="/doctor-dashboard" element={
        <ProtectedRoute requiredRole="doctor">
          <DoctorDashboard />
        </ProtectedRoute>
      } />
      <Route path="/patients" element={
        <ProtectedRoute requiredRole="doctor">
          <PatientsPage />
        </ProtectedRoute>
      } />
      <Route path="/analytics" element={
        <ProtectedRoute requiredRole="doctor">
          <AnalyticsPage />
        </ProtectedRoute>
      } />

      {/* Agent route */}
      <Route path="/agent" element={
        <ProtectedRoute requiredRole="doctor">
          <AgentPage />
        </ProtectedRoute>
      } />

      {/* Shared routes */}
      <Route path="/appointments" element={
        <ProtectedRoute>
          <AppointmentsPage />
        </ProtectedRoute>
      } />
      <Route path="/chat" element={
        <ProtectedRoute>
          <ChatPage />
        </ProtectedRoute>
      } />
      <Route path="/patient-chat" element={
        <ProtectedRoute requiredRole="patient">
          <PatientChatPage />
        </ProtectedRoute>
      } />
      <Route path="/history" element={
        <ProtectedRoute>
          <HistoryPage />
        </ProtectedRoute>
      } />
      <Route path="/settings" element={
        <ProtectedRoute>
          <SettingsPage />
        </ProtectedRoute>
      } />

      {/* Default redirect */}
      <Route path="/" element={
        user ? (
          <Navigate to={user.role === 'patient' ? '/dashboard' : '/doctor-dashboard'} replace />
        ) : (
          <Navigate to="/login" replace />
        )
      } />

      {/* 404 and unauthorized */}
      <Route path="/unauthorized" element={
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-900 mb-4">Unauthorized</h1>
            <p className="text-gray-600">You don't have permission to access this page.</p>
          </div>
        </div>
      } />
      <Route path="*" element={
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-900 mb-4">Page Not Found</h1>
            <p className="text-gray-600">The page you're looking for doesn't exist.</p>
          </div>
        </div>
      } />
    </Routes>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Router>
          <div className="App">
            <AppRoutes />
          </div>
        </Router>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
