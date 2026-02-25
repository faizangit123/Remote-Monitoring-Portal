/**
 * WebSocket Service
 * ==================
 * Manages real-time WebSocket connections between browser and backend.
 */

const WS_BASE = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'

// ============================================================
// AGENT DETAIL WEBSOCKET
// Creates a WebSocket connection to watch a specific agent
// ============================================================

export function createAgentWebSocket(agentId, token, callbacks = {}) {
  /**
   * Connect to the backend to receive real-time updates for one agent.
   * 
   * @param {string} agentId - The agent's string ID (e.g. "agent-001")
   * @param {string} token   - User's JWT access token for authentication
   * @param {object} callbacks - Event handlers:
   *   onSystemData(data)   - Called when agent sends CPU/RAM/Disk update
   *   onProcesses(data)    - Called when agent sends process list update
   *   onDiskPartitions(data) - Called when agent sends disk info
   *   onNetworkInfo(data)  - Called when agent sends network info
   *   onUsers(data)        - Called when agent sends user list
   *   onStatusChange(status) - Called when agent goes online/offline
   *   onCommandResult(data)  - Called when agent executes a command
   *   onConnect()          - Called when WebSocket connects
   *   onDisconnect()       - Called when WebSocket disconnects
   *   onError(error)       - Called on WebSocket error
   * 
   * @returns {object} - { close: function } — call close() to disconnect
   */

  const url = `${WS_BASE}/ws/client/${agentId}?token=${token}`

  let ws = null
  let reconnectTimer = null
  let isIntentionallyClosed = false
  let reconnectDelay = 3000  // Start with 3 second delay
  const maxReconnectDelay = 30000  // Max 30 seconds between retries

  function connect() {
    try {
      ws = new WebSocket(url)

      ws.onopen = () => {
        console.log(` WebSocket connected: ${agentId}`)
        reconnectDelay = 3000
        callbacks.onConnect?.()
      }

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          handleMessage(message)
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err)
        }
      }

      ws.onerror = (error) => {
        console.error(`WebSocket error (${agentId}):`, error)
        callbacks.onError?.(error)
      }

      ws.onclose = (event) => {
        console.log(`🔌 WebSocket closed: ${agentId} (code: ${event.code})`)
        callbacks.onDisconnect?.()

        if (!isIntentionallyClosed) {
          console.log(`Reconnecting in ${reconnectDelay / 1000}s...`)
          reconnectTimer = setTimeout(() => {
            reconnectDelay = Math.min(reconnectDelay * 2, maxReconnectDelay)
            connect()
          }, reconnectDelay)
        }
      }

    } catch (err) {
      console.error('Failed to create WebSocket:', err)
      callbacks.onError?.(err)
    }
  }

  function handleMessage(message) {
    const { type } = message

    switch (type) {

      case 'connected':
        console.log(`📡 Watching agent: ${agentId}, status: ${message.agent_status}`)
        break

      case 'system_data_update':
        callbacks.onSystemData?.(message.data)
        break

      case 'processes_update':
        callbacks.onProcesses?.(message.data)
        break

      case 'disk_partitions':
        callbacks.onDiskPartitions?.(message.data)
        break

      case 'network_info':
        callbacks.onNetworkInfo?.(message.data)
        break

      case 'users':
        callbacks.onUsers?.(message.data)
        break

      case 'agent_status':
        callbacks.onStatusChange?.(message.status)
        break

      case 'command_result':
        callbacks.onCommandResult?.(message)
        break

      case 'pong':
        break

      default:
        console.log(`Unknown message type: ${type}`, message)
    }
  }

  const pingInterval = setInterval(() => {
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'ping' }))
    }
  }, 30000)

  // Connect immediately
  connect()

  return {
    close: () => {
      isIntentionallyClosed = true
      clearTimeout(reconnectTimer)
      clearInterval(pingInterval)
      if (ws) {
        ws.close(1000, 'Component unmounted')
        ws = null
      }
    },

    isConnected: () => ws?.readyState === WebSocket.OPEN,
  }
}

// ============================================================
// DASHBOARD WEBSOCKET
// Watches ALL agents for the dashboard overview page
// ============================================================

export function createDashboardWebSocket(agentIds, token, callbacks = {}) {
  /**
   * Create WebSocket connections for multiple agents at once.
   * @param {string[]} agentIds - Array of agent ID strings
   * @param {string}   token    - JWT token
   * @param {object}   callbacks
   *   onStatusChange(agentId, status) - When any agent changes status
   * @returns {object} - { close: function }
   */

  const connections = {}

  for (const agentId of agentIds) {
    connections[agentId] = createAgentWebSocket(agentId, token, {
      onStatusChange: (status) => {
        callbacks.onStatusChange?.(agentId, status)
      },
    })
  }

  return {
    close: () => {
      // Close all connections at once
      Object.values(connections).forEach((conn) => conn.close())
    },
  }
}