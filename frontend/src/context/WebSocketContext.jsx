/**
 * WebSocket Context — Real-time data updates
 * ==========================================
 * Manages WebSocket connections for agent monitoring.
 * Components subscribe to specific agents to receive live updates.
 */

import { createContext, useContext, useState, useCallback, useRef, useEffect } from 'react'
import { createAgentWebSocket } from '../services/websocket'
import { getStoredToken } from '../utils/helpers'

const WebSocketContext = createContext(null)

export function WebSocketProvider({ children }) {
  const connectionsRef = useRef({})
  const [agentStates, setAgentStates] = useState({})
  
  useEffect(() => {
    return () => {
      Object.values(connectionsRef.current).forEach(ws => {
        if (ws && typeof ws.close === 'function') {
          ws.close()
        }
      })
    }
  }, [])

  const subscribeToAgent = useCallback((agentId) => {
    if (connectionsRef.current[agentId]) {
      console.log(`Already subscribed to agent: ${agentId}`)
      return
    }

    const token = getStoredToken()
    if (!token) {
      console.error('No token available for WebSocket connection')
      return
    }

    console.log(`📡 Subscribing to agent: ${agentId}`)

    const ws = createAgentWebSocket(agentId, token, {
      onConnect: () => {
        console.log(`✅ WebSocket connected: ${agentId}`)
        updateAgentState(agentId, { connected: true })
      },

      onDisconnect: () => {
        console.log(`🔌 WebSocket disconnected: ${agentId}`)
        updateAgentState(agentId, { connected: false })
      },

      onSystemData: (data) => {
        console.log(`📊 System data update for ${agentId}:`, data)
        updateAgentState(agentId, { systemData: data })
      },

      onProcesses: (data) => {
        console.log(`⚙️ Processes update for ${agentId}: ${data?.length || 0} processes`)
        updateAgentState(agentId, { processes: data })
      },

      onDiskPartitions: (data) => {
        console.log(`💾 Disk partitions update for ${agentId}`)
        updateAgentState(agentId, { diskPartitions: data })
      },

      onNetworkInfo: (data) => {
        console.log(`🌐 Network info update for ${agentId}`)
        updateAgentState(agentId, { networkInfo: data })
      },

      onUsers: (data) => {
        console.log(`👤 Users update for ${agentId}`)
        updateAgentState(agentId, { users: data })
      },

      onStatusChange: (status) => {
        console.log(`📡 Agent ${agentId} status changed to: ${status}`)
        updateAgentState(agentId, { agentStatus: status })
      },

      onCommandResult: (result) => {
        console.log(`📨 Command result for ${agentId}:`, result)
        updateAgentState(agentId, { lastCommandResult: result })
      },

      onError: (error) => {
        console.error(`❌ WebSocket error for ${agentId}:`, error)
      }
    })

    connectionsRef.current[agentId] = ws
  }, [])

  const unsubscribeFromAgent = useCallback((agentId) => {
    console.log(`🔌 Unsubscribing from agent: ${agentId}`)
    const ws = connectionsRef.current[agentId]
    if (ws && typeof ws.close === 'function') {
      ws.close()
      delete connectionsRef.current[agentId]
    }
  }, [])

  const updateAgentState = useCallback((agentId, updates) => {
    setAgentStates(prev => ({
      ...prev,
      [agentId]: {
        ...prev[agentId],
        ...updates,
        lastUpdate: new Date().toISOString()
      }
    }))
  }, [])

  const value = {
    subscribeToAgent,
    unsubscribeFromAgent,
    agentStates,
  }

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  )
}

export function useWebSocket() {
  const context = useContext(WebSocketContext)
  if (!context) {
    throw new Error('useWebSocket must be used inside <WebSocketProvider>')
  }
  return context
}

export default WebSocketContext