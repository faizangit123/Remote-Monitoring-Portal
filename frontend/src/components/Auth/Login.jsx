import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { getErrorMessage } from '../../utils/helpers'
import { FiMonitor, FiUser, FiLock, FiLogIn, FiAlertCircle } from 'react-icons/fi'
import './Login.css'

function Login() {
  const { login, isAuthenticated } = useAuth()
  const navigate = useNavigate()

  const [form, setForm]     = useState({ username: '', password: '' })
  const [loading, setLoading] = useState(false)
  const [error, setError]   = useState(null)

 useEffect(() => {
  if (isAuthenticated) {
    navigate('/dashboard', { replace: true })
  }
}, [isAuthenticated, navigate])

  const handleChange = (e) => {
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }))
    if (error) setError(null)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!form.username.trim() || !form.password.trim()) {
      setError('Please enter both username and password.')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const user = await login(form.username.trim(), form.password)
      navigate(user.role === 'admin' ? '/admin' : '/dashboard', { replace: true })
    } catch (err) {
      setError(getErrorMessage(err) || 'Invalid username or password.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      {/* Animated grid background */}
      <div className="login-bg">
        <div className="login-grid" />
        <div className="login-glow login-glow-1" />
        <div className="login-glow login-glow-2" />
      </div>

      {/* Floating particles */}
      {[...Array(6)].map((_, i) => (
        <div key={i} className={`login-particle p${i + 1}`} />
      ))}

      <div className="login-container">

        {/* Header */}
        <div className="login-header">
          <div className="login-logo">
            <FiMonitor size={28} />
          </div>
          <h1 className="login-title">Remote Monitor</h1>
          <p className="login-subtitle">Secure Admin Portal Access</p>
        </div>

        {/* Card */}
        <div className="login-card">
          <div className="login-card-header">
            <span className="login-card-label">Authentication Required</span>
            <div className="login-card-dots">
              <span className="dot green" />
              <span className="dot yellow" />
              <span className="dot red" />
            </div>
          </div>

          <form className="login-form" onSubmit={handleSubmit}>

            {/* Error */}
            {error && (
              <div className="login-error">
                <FiAlertCircle size={14} />
                <span>{error}</span>
              </div>
            )}

            {/* Username */}
            <div className="form-group">
              <label className="form-label" htmlFor="username">
                Username
              </label>
              <div className="login-input-wrap">
                <FiUser size={15} className="login-input-icon" />
                <input
                  id="username"
                  name="username"
                  type="text"
                  className="form-input login-input"
                  placeholder="Enter username"
                  value={form.username}
                  onChange={handleChange}
                  autoComplete="username"
                  autoFocus
                  disabled={loading}
                />
              </div>
            </div>

            {/* Password */}
            <div className="form-group">
              <label className="form-label" htmlFor="password">
                Password
              </label>
              <div className="login-input-wrap">
                <FiLock size={15} className="login-input-icon" />
                <input
                  id="password"
                  name="password"
                  type="password"
                  className="form-input login-input"
                  placeholder="Enter password"
                  value={form.password}
                  onChange={handleChange}
                  autoComplete="current-password"
                  disabled={loading}
                />
              </div>
            </div>

            {/* Submit */}
            <button
              type="submit"
              className="login-btn"
              disabled={loading}
            >
              {loading ? (
                <>
                  <div className="spinner-sm" />
                  <span>Authenticating...</span>
                </>
              ) : (
                <>
                  <FiLogIn size={16} />
                  <span>Sign In</span>
                </>
              )}
            </button>
          </form>

          {/* Demo credentials hint */}
          <div className="login-hint">
            <span className="login-hint-label">Demo Credentials</span>
            <div className="login-hint-row">
              <code>admin</code><span>/</span><code>admin123</code>
              <span className="login-hint-role admin">ADMIN</span>
            </div>
            <div className="login-hint-row">
              <code>testuser</code><span>/</span><code>testuser@example.com</code>
              <span className="login-hint-role user">USER</span>
            </div>
          </div>
        </div>

        <p className="login-footer">
          Remote Monitoring Portal · Secure Connection
        </p>
      </div>
    </div>
  )
}

export default Login