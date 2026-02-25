/**
 * Helper Functions
 * =================
 */

// ============================================================
// FORMATTING
// ============================================================

export function formatBytes(bytes, decimals = 2) {
  if (!bytes || bytes === 0) return '0 B'
  const k = 1024
  const dm = decimals < 0 ? 0 : decimals
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i]
}

export function formatGB(gb, decimals = 1) {
  if (gb === null || gb === undefined) return 'N/A'
  return `${parseFloat(gb).toFixed(decimals)} GB`
}

export function formatPercent(value, decimals = 1) {
  if (value === null || value === undefined) return 'N/A'
  return `${parseFloat(value).toFixed(decimals)}%`
}

export function formatUptime(hours) {
  if (!hours && hours !== 0) return 'N/A'

  const totalMinutes = Math.floor(hours * 60)
  const days = Math.floor(totalMinutes / 1440)     // 1440 min = 1 day
  const remainingAfterDays = totalMinutes % 1440
  const hrs = Math.floor(remainingAfterDays / 60)
  const mins = remainingAfterDays % 60

  if (days > 0) return `${days}d ${hrs}h`
  if (hrs > 0) return `${hrs}h ${mins}m`
  return `${mins}m`
}

export function formatDateTime(dateString) {
  if (!dateString) return 'Never'
  try {
    const date = new Date(dateString)
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return dateString
  }
}

export function formatRelativeTime(dateString) {
  if (!dateString) return 'Never'
  try {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now - date            // Difference in milliseconds
    const diffSecs = Math.floor(diffMs / 1000)
    const diffMins = Math.floor(diffSecs / 60)
    const diffHours = Math.floor(diffMins / 60)
    const diffDays = Math.floor(diffHours / 24)

    if (diffSecs < 10) return 'just now'
    if (diffSecs < 60) return `${diffSecs}s ago`
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    return `${diffDays}d ago`
  } catch {
    return dateString
  }
}

// ============================================================
// USAGE COLOR HELPERS
// (Returns CSS class based on how high a percentage is)
// ============================================================

export function getUsageColor(percent) {
  if (!percent && percent !== 0) return 'low'
  if (percent >= 85) return 'high'
  if (percent >= 60) return 'medium'
  return 'low'
}

export function getUsageTextColor(percent) {
  if (!percent && percent !== 0) return 'var(--success)'
  if (percent >= 85) return 'var(--danger)'
  if (percent >= 60) return 'var(--warning)'
  return 'var(--success)'
}

// ============================================================
// AUTH HELPERS
// ============================================================

export function getStoredToken() {
  /** Get JWT token from localStorage. */
  return localStorage.getItem('access_token')
}

export function getStoredUser() {

  try {
    const data = localStorage.getItem('user_data')
    return data ? JSON.parse(data) : null
  } catch {
    return null
  }
}

export function storeAuthData(token, user) {
  localStorage.setItem('access_token', token)
  localStorage.setItem('user_data', JSON.stringify(user))
}

export function clearAuthData() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('user_data')
}

export function isAdmin(user) {
  /** Check if a user object has admin role. */
  return user?.role === 'admin'
}

// ============================================================
// MISC HELPERS
// ============================================================

export function truncate(str, maxLength = 30) {
  if (!str) return ''
  if (str.length <= maxLength) return str
  return str.slice(0, maxLength) + '...'
}

export function getErrorMessage(error) {
  if (error?.response?.data?.detail) {
    return error.response.data.detail
  }
  if (error?.message) {
    return error.message
  }
  return 'An unexpected error occurred'
}

export function generateRandomId(prefix = 'id') {
  const rand = Math.random().toString(36).slice(2, 10)
  return `${prefix}-${rand}`
}