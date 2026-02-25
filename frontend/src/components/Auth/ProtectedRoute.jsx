import { Navigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import './ProtectedRoute.css'

function ProtectedRoute({ children, requireAdmin = false }) {
  const { isAuthenticated, isAdmin, loading } = useAuth()

  if (loading) {
    return (
      <div className="protected-loading">
        <div className="spinner" />
        <span>Verifying session...</span>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  if (requireAdmin && !isAdmin) {
    return <Navigate to="/dashboard" replace />
  }

  return children
}

export default ProtectedRoute