/**
 * components/auth/ProtectedRoute.jsx — redirects unauthenticated users to login.
 */

import { Navigate, useLocation } from 'react-router-dom'

import LoadingSpinner from '../ui/LoadingSpinner'
import { useAuth } from '../../context/AuthContext'

export default function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth()
  const location = useLocation()

  if (loading) {
    return <LoadingSpinner fullScreen label="Checking authentication…" />
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />
  }

  return children
}
