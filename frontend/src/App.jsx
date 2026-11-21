/**
 * App.jsx — routing with auth protection and new analytics/history pages.
 */

import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'

import ProtectedRoute from './components/auth/ProtectedRoute'
import DashboardLayout from './components/layout/DashboardLayout'
import { AuthProvider } from './context/AuthContext'
import { SimulationProvider } from './context/SimulationContext'
import AnalyticsPage from './pages/AnalyticsPage'
import DashboardPage from './pages/DashboardPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import SessionDetailPage from './pages/SessionDetailPage'
import SessionHistoryPage from './pages/SessionHistoryPage'
import SimulationPage from './pages/SimulationPage'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <SimulationProvider>
          <BrowserRouter>
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />

              <Route
                element={
                  <ProtectedRoute>
                    <DashboardLayout />
                  </ProtectedRoute>
                }
              >
                <Route index element={<DashboardPage />} />
                <Route path="simulation" element={<SimulationPage />} />
                <Route path="history" element={<SessionHistoryPage />} />
                <Route path="history/:sessionId" element={<SessionDetailPage />} />
                <Route path="analytics" element={<AnalyticsPage />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Route>
            </Routes>
          </BrowserRouter>
          <Toaster
            position="bottom-right"
            toastOptions={{
              style: {
                background: '#111827',
                color: '#e2e8f0',
                border: '1px solid #1e293b',
              },
            }}
          />
        </SimulationProvider>
      </AuthProvider>
    </QueryClientProvider>
  )
}
