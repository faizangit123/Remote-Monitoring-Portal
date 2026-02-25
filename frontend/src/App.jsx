import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { WebSocketProvider } from './context/WebSocketContext'
import ProtectedRoute from './components/Auth/ProtectedRoute'
import Login from './components/Auth/Login'
import AdminDashboard from './components/Dashboard/AdminDashboard'
import UserDashboard from './components/Dashboard/UserDashboard'
import AgentDetails from './components/Agent/AgentDetails'
import UserList from './components/UserManagement/UserList'
import './App.css'

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <WebSocketProvider>
          <Routes>

            {/* Public route — no login needed */}
            <Route path="/login" element={<Login />} />

            {/* Default redirect */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />

            {/* Protected: any logged-in user */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <UserDashboard />
                </ProtectedRoute>
              }
            />

            {/* Protected: admin only */}
            <Route
              path="/admin"
              element={
                <ProtectedRoute requireAdmin>
                  <AdminDashboard />
                </ProtectedRoute>
              }
            />

            {/* Protected: agent detail (any logged-in user) */}
            <Route
              path="/agents/:agentId"
              element={
                <ProtectedRoute>
                  <AgentDetails />
                </ProtectedRoute>
              }
            />

            {/* Protected: user management (admin only) */}
            <Route
              path="/users"
              element={
                <ProtectedRoute requireAdmin>
                  <UserList />
                </ProtectedRoute>
              }
            />

            {/* Catch-all — redirect unknown URLs to dashboard */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />

          </Routes>
        </WebSocketProvider>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App