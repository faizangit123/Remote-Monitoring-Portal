/**
 * Authentication Context
 * ======================
 */

import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { authAPI } from '../services/api'
import { storeAuthData, clearAuthData, getStoredToken, getStoredUser } from '../utils/helpers'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {

  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  // ============================================================
  // On app load: Check if there's a stored token
  // ============================================================

  useEffect(() => {
    const initAuth = async () => {
      const token = getStoredToken()
      
      if (!token) {
        setLoading(false)
        return
      }

      try {
        const userData = await authAPI.getMe()
        setUser(userData)
      } catch (err) {
        console.log(err)
        clearAuthData()
        setUser(null)
      } finally {
        setLoading(false)
      }
    }

    initAuth()
  }, [])

  // ============================================================
  // LOGIN
  // ============================================================

  const login = useCallback(async (username, password) => {
    /**
     * @returns {object} user data on success
     * @throws {Error} on failure
     */
    const tokenData = await authAPI.login(username, password)
    const token = tokenData.access_token

    localStorage.setItem('access_token', token)

    const userData = await authAPI.getMe()

    storeAuthData(token, userData)
    setUser(userData)

    return userData
  }, [])

  // ============================================================
  // LOGOUT
  // ============================================================

  const logout = useCallback(() => {

    clearAuthData()
    setUser(null)
    window.location.href = '/login'
  }, [])

  // ============================================================
  // COMPUTED VALUES
  // ============================================================

  const isAuthenticated = !!user

  const isAdminUser = user?.role === 'admin'

  // ============================================================
  // CONTEXT VALUE
  // Everything inside this object is available via useAuth()
  // ============================================================

  const value = {
    user,          // The user object (or null)
    loading,       // True while checking token on page load
    isAuthenticated,  // Boolean: is user logged in?
    isAdmin: isAdminUser,  // Boolean: is user an admin?
    login,         // Function to log in
    logout,        // Function to log out
  }

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        background: 'var(--bg-base)',
        color: 'var(--accent)',
        fontFamily: 'var(--font-data)',
        fontSize: '0.875rem',
        gap: '12px'
      }}>
        <div className="spinner" />
        Initializing...
      </div>
    )
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  
  if (!context) {
    throw new Error('useAuth must be used inside <AuthProvider>')
  }
  
  return context
}

export default AuthContext