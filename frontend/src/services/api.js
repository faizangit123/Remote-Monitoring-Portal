/**
 * API Service
 * ===========
 * All HTTP requests to the backend in one place.
 */

import axios from 'axios'

// ============================================================
// AXIOS INSTANCE SETUP
// ============================================================

const API_BASE = ''

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
})

// ============================================================
// REQUEST INTERCEPTOR — Attach JWT token to every request
// ============================================================

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// ============================================================
// RESPONSE INTERCEPTOR — Handle 401 errors globally
// ============================================================

api.interceptors.response.use(
  (response) => response,

  (error) => {

    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user_data')
      // Only redirect if we're not already on the login page
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

// ============================================================
// AUTH ENDPOINTS
// ============================================================

export const authAPI = {

  login: async (username, password) => {
    const formData = new URLSearchParams()
    formData.append('username', username)
    formData.append('password', password)

    const response = await api.post('/api/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
    return response.data
    // Returns: { access_token: "eyJ...", token_type: "bearer" }
  },

  getMe: async () => {
    const response = await api.get('/api/auth/me')
    return response.data
    // Returns: { id, username, email, role, is_active, created_at }
  },

  register: async (userData) => {
    const response = await api.post('/api/auth/register', userData)
    return response.data
  },

  refreshToken: async () => {
    const response = await api.post('/api/auth/refresh')
    return response.data
  },
}

// ============================================================
// USERS ENDPOINTS (Admin only)
// ============================================================

export const usersAPI = {

  getAll: async (skip = 0, limit = 100) => {
    const response = await api.get('/api/users/', { params: { skip, limit } })
    return response.data
    // Returns: array of user objects
  },

  getById: async (userId) => {
    const response = await api.get(`/api/users/${userId}`)
    return response.data
  },

  create: async (userData) => {
    const response = await api.post('/api/users/', userData)
    return response.data
  },

  update: async (userId, updateData) => {
    const response = await api.put(`/api/users/${userId}`, updateData)
    return response.data
  },

  delete: async (userId) => {
    const response = await api.delete(`/api/users/${userId}`)
    return response.data
  },

  assignAgent: async (userId, agentId) => {
    const response = await api.post(`/api/users/${userId}/assign-agent`, {
      user_id: userId,
      agent_id: agentId,
    })
    return response.data
  },

  unassignAgent: async (userId, agentId) => {
    const response = await api.delete(
      `/api/users/${userId}/unassign-agent/${agentId}`
    )
    return response.data
  },

  getMyProfile: async () => {
    const response = await api.get('/api/users/me/profile')
    return response.data
  },
}

// ============================================================
// AGENTS ENDPOINTS
// ============================================================

export const agentsAPI = {

  getAll: async (skip = 0, limit = 100) => {
    const response = await api.get('/api/agents/', { params: { skip, limit } })
    return response.data
    // Returns: array of agent objects with status (online/offline)
  },

  getById: async (agentId) => {
    const response = await api.get(`/api/agents/${agentId}`)
    return response.data
  },

  register: async (agentData) => {
    const response = await api.post('/api/agents/register', agentData)
    return response.data
  },

  generateToken: async () => {
    const response = await api.get('/api/agents/generate-token')
    return response.data
    // Returns: { token: "abc123..." }
  },

  update: async (agentId, updateData) => {
    const response = await api.put(`/api/agents/${agentId}`, updateData)
    return response.data
  },

  delete: async (agentId) => {
    const response = await api.delete(`/api/agents/${agentId}`)
    return response.data
  },

  getSystemData: async (agentId) => {
    const response = await api.get(`/api/agents/${agentId}/system-data`)
    return response.data
  },

  getHistory: async (agentId, limit = 50) => {
    const response = await api.get(`/api/agents/${agentId}/history`, {
      params: { limit }
    })
    return response.data
    // Returns: array of system data snapshots, newest first
  },

  getProcesses: async (agentId) => {
    const response = await api.get(`/api/agents/${agentId}/processes`)
    return response.data
  },
}

// ============================================================
// COMMANDS ENDPOINTS
// ============================================================

export const commandsAPI = {

  send: async (agentId, commandType, commandData = null) => {
    const response = await api.post('/api/commands/', {
      agent_id: agentId,
      command_type: commandType,
      command_data: commandData,
    })
    return response.data
    // Returns: command object with status: "pending"
  },

  getAll: async (skip = 0, limit = 100) => {
    const response = await api.get('/api/commands/', { params: { skip, limit } })
    return response.data
  },

  getForAgent: async (agentId, statusFilter = null, limit = 50) => {
    const params = { limit }
    if (statusFilter) params.status_filter = statusFilter

    const response = await api.get(`/api/commands/agent/${agentId}`, { params })
    return response.data
  },

  getById: async (commandId) => {
    const response = await api.get(`/api/commands/${commandId}`)
    return response.data
  },
}

// ============================================================
// WEBSOCKET STATS
// ============================================================

export const wsAPI = {
  getStats: async () => {
    const response = await api.get('/ws/stats')
    return response.data
    // Returns: { connected_agents: 2, agent_ids: [...], watching_clients: 5 }
  },
}

export default api