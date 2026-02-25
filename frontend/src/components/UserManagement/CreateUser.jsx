import { useState } from 'react'
import { usersAPI } from '../../services/api'
import { FiX, FiUserPlus, FiUser, FiMail, FiLock, FiShield } from 'react-icons/fi'
import { getErrorMessage } from '../../utils/helpers'
import './CreateUser.css'

function CreateUser({ onClose, onCreated }) {
  const [form, setForm]     = useState({
    username: '',
    email: '',
    password: '',
    role: 'user',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError]   = useState(null)
  const [fieldErrors, setFieldErrors] = useState({})

  const validate = () => {
    const errs = {}
    if (!form.username.trim())    errs.username = 'Username is required'
    else if (form.username.length < 3) errs.username = 'At least 3 characters'
    if (!form.email.trim())       errs.email = 'Email is required'
    else if (!/\S+@\S+\.\S+/.test(form.email)) errs.email = 'Invalid email format'
    if (!form.password.trim())    errs.password = 'Password is required'
    else if (form.password.length < 6) errs.password = 'At least 6 characters'
    return errs
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setForm(prev => ({ ...prev, [name]: value }))
    if (fieldErrors[name]) {
      setFieldErrors(prev => ({ ...prev, [name]: null }))
    }
    if (error) setError(null)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const errs = validate()
    if (Object.keys(errs).length) { setFieldErrors(errs); return }

    setLoading(true)
    setError(null)

    try {
      const newUser = await usersAPI.create(form)
      onCreated(newUser)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box create-user-modal" onClick={e => e.stopPropagation()}>

        {/* Header */}
        <div className="modal-header">
          <h3 className="modal-title">
            <FiUserPlus size={16} />
            Create New User
          </h3>
          <button className="modal-close" onClick={onClose}>
            <FiX size={16} />
          </button>
        </div>

        {/* Form */}
        <form className="create-user-form" onSubmit={handleSubmit}>

          {error && (
            <div className="login-error" style={{ margin: '0 var(--space-6)' }}>
              <span>{error}</span>
            </div>
          )}

          <div className="create-user-body">

            {/* Username */}
            <div className="form-group">
              <label className="form-label" htmlFor="cu-username">Username</label>
              <div className="cu-input-wrap">
                <FiUser size={14} className="cu-input-icon" />
                <input
                  id="cu-username"
                  name="username"
                  type="text"
                  className={`form-input cu-input ${fieldErrors.username ? 'error' : ''}`}
                  placeholder="e.g. testuser_1"
                  value={form.username}
                  onChange={handleChange}
                  autoFocus
                  disabled={loading}
                />
              </div>
              {fieldErrors.username && (
                <span className="field-error">{fieldErrors.username}</span>
              )}
            </div>

            {/* Email */}
            <div className="form-group">
              <label className="form-label" htmlFor="cu-email">Email</label>
              <div className="cu-input-wrap">
                <FiMail size={14} className="cu-input-icon" />
                <input
                  id="cu-email"
                  name="email"
                  type="email"
                  className={`form-input cu-input ${fieldErrors.email ? 'error' : ''}`}
                  placeholder="user@example.com"
                  value={form.email}
                  onChange={handleChange}
                  disabled={loading}
                />
              </div>
              {fieldErrors.email && (
                <span className="field-error">{fieldErrors.email}</span>
              )}
            </div>

            {/* Password */}
            <div className="form-group">
              <label className="form-label" htmlFor="cu-password">Password</label>
              <div className="cu-input-wrap">
                <FiLock size={14} className="cu-input-icon" />
                <input
                  id="cu-password"
                  name="password"
                  type="password"
                  className={`form-input cu-input ${fieldErrors.password ? 'error' : ''}`}
                  placeholder="Min. 6 characters"
                  value={form.password}
                  onChange={handleChange}
                  disabled={loading}
                />
              </div>
              {fieldErrors.password && (
                <span className="field-error">{fieldErrors.password}</span>
              )}
            </div>

            {/* Role */}
            <div className="form-group">
              <label className="form-label" htmlFor="cu-role">Role</label>
              <div className="cu-role-group">
                <label className={`cu-role-option ${form.role === 'user' ? 'selected' : ''}`}>
                  <input
                    type="radio"
                    name="role"
                    value="user"
                    checked={form.role === 'user'}
                    onChange={handleChange}
                    disabled={loading}
                    style={{ display: 'none' }}
                  />
                  <FiUser size={16} />
                  <div>
                    <span className="cu-role-name">User</span>
                    <span className="cu-role-desc">View assigned agents</span>
                  </div>
                </label>

                <label className={`cu-role-option ${form.role === 'admin' ? 'selected' : ''}`}>
                  <input
                    type="radio"
                    name="role"
                    value="admin"
                    checked={form.role === 'admin'}
                    onChange={handleChange}
                    disabled={loading}
                    style={{ display: 'none' }}
                  />
                  <FiShield size={16} />
                  <div>
                    <span className="cu-role-name">Admin</span>
                    <span className="cu-role-desc">Full access + user management</span>
                  </div>
                </label>
              </div>
            </div>

          </div>

          {/* Footer */}
          <div className="create-user-footer">
            <button type="button" className="btn btn-ghost" onClick={onClose} disabled={loading}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? (
                <><div className="spinner-sm" /> Creating...</>
              ) : (
                <><FiUserPlus size={14} /> Create User</>
              )}
            </button>
          </div>

        </form>
      </div>
    </div>
  )
}

export default CreateUser
