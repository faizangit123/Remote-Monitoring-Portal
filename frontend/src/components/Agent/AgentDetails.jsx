import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  FiCpu, FiHardDrive, FiActivity, FiWifi, FiUsers,
  FiRefreshCw, FiAlertCircle, FiCheckCircle
} from 'react-icons/fi'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer
} from 'recharts'

import { agentsAPI, commandsAPI } from '../../services/api'
import { useWebSocket } from '../../context/WebSocketContext'
import {
  formatPercent, formatGB, formatUptime, formatDateTime,
  getErrorMessage
} from '../../utils/helpers'

import ProcessList from './ProcessList'
import StorageInfo from './StorageInfo'
import NetworkInfo from './NetworkInfo'
import SystemUsers from './SystemUsers'
import './AgentDetails.css'

function AgentDetails() {
  const { agentId } = useParams()
  const navigate = useNavigate()

  const { subscribeToAgent, unsubscribeFromAgent, agentStates } = useWebSocket()

  const [agent, setAgent] = useState(null)
  const [systemData, setSystemData] = useState(null)
  const [processes, setProcesses] = useState([])
  const [chartData, setChartData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('overview')
  const [refreshing, setRefreshing] = useState(false)

  const wsData = agentStates[agentId] || {}
  const isConnected = wsData.connected || false
  const agentStatus = wsData.agentStatus || agent?.status || 'offline'

  useEffect(() => {
    const loadInitialData = async () => {
      try {
        setLoading(true)
        const agentData = await agentsAPI.getById(agentId)
        setAgent(agentData)

        const sysData = await agentsAPI.getSystemData(agentId)
        if (sysData) setSystemData(sysData)

        const history = await agentsAPI.getHistory(agentId, 50)
        setChartData(history || [])

        const procs = await agentsAPI.getProcesses(agentId)
        setProcesses(procs || [])
      } catch (err) {
        setError(getErrorMessage(err))
      } finally {
        setLoading(false)
      }
    }

    if (agentId) {
      loadInitialData()
      subscribeToAgent(agentId)
    }

    return () => {
      if (agentId) unsubscribeFromAgent(agentId)
    }
  }, [agentId, subscribeToAgent, unsubscribeFromAgent])

  useEffect(() => {
    if (wsData.systemData) {
      setSystemData(wsData.systemData)
      setChartData(prev => [...prev, wsData.systemData].slice(-50))
    }
  }, [wsData.systemData])

  useEffect(() => {
    if (wsData.processes) setProcesses(wsData.processes)
  }, [wsData.processes])

  const handleRefresh = async () => {
    try {
      setRefreshing(true)
      await commandsAPI.send(agentId, 'refresh_data')
      setTimeout(() => setRefreshing(false), 2000)
    } catch (err) {
      console.error('Failed to send refresh command:', err)
      setRefreshing(false)
    }
  }

  if (loading) {
    return (
      <div className="agent-details-loading">
        <div className="spinner" />
        <p>Loading agent details...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="agent-details-error">
        <FiAlertCircle size={48} />
        <h2>Failed to Load Agent</h2>
        <p>{error}</p>
        <button onClick={() => navigate('/dashboard')} className="btn btn-primary">
          Back to Dashboard
        </button>
      </div>
    )
  }

  return (
    <div className="agent-details">

      {/* Header */}
      <div className="agent-details-header">
        <div className="agent-header-info">
          <h1>{agent?.hostname || 'Unknown Agent'}</h1>
          <div className="agent-header-meta">
            <span className={`badge badge-${agentStatus}`}>
              <span className={`status-dot ${agentStatus}`} />
              {agentStatus}
            </span>
            {isConnected && (
              <span className="badge badge-online">
                <FiCheckCircle size={12} />
                WebSocket Connected
              </span>
            )}
            <span className="agent-ip">
              {agent?.ip_address || 'No IP'}
            </span>
          </div>
        </div>

        <button
          onClick={handleRefresh}
          disabled={refreshing || agentStatus === 'offline'}
          className="btn btn-primary"
        >
          <FiRefreshCw className={refreshing ? 'spinning' : ''} />
          {refreshing ? 'Refreshing...' : 'Refresh Data'}
        </button>
      </div>

      {/* Tabs */}
      <div className="agent-tabs">
        {[
          { key: 'overview',  icon: <FiActivity />,  label: 'Overview'  },
          { key: 'processes', icon: <FiCpu />,        label: 'Processes' },
          { key: 'storage',   icon: <FiHardDrive />,  label: 'Storage'   },
          { key: 'network',   icon: <FiWifi />,       label: 'Network'   },
          { key: 'users',     icon: <FiUsers />,      label: 'Users'     },
        ].map(({ key, icon, label }) => (
          <button
            key={key}
            className={`tab ${activeTab === key ? 'active' : ''}`}
            onClick={() => setActiveTab(key)}
          >
            {icon}
            {label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="agent-tab-content">
        {activeTab === 'overview' && (
          <OverviewTab systemData={systemData} chartData={chartData} agent={agent} />
        )}
        {activeTab === 'processes' && (
          <ProcessList processes={processes} agentId={agentId} />
        )}
        {activeTab === 'storage' && (
          <StorageInfo diskPartitions={wsData.diskPartitions || []} />
        )}
        {activeTab === 'network' && (
          <NetworkInfo networkInfo={wsData.networkInfo || {}} />
        )}
        {activeTab === 'users' && (
          <SystemUsers users={wsData.users || []} />
        )}
      </div>

    </div>
  )
}

// ─────────────────────────────────────────────
// Overview Tab
// ─────────────────────────────────────────────
function OverviewTab({ systemData, chartData, agent }) {
  if (!systemData) {
    return (
      <div className="empty-state">
        <FiActivity size={48} />
        <p>No system data available yet</p>
        <small>Waiting for agent to send data...</small>
      </div>
    )
  }

  return (
    <div className="overview-tab">

      {/* 4 Stat Cards */}
      <div className="stat-cards-grid">
        <StatCard
          label="CPU Usage"
          value={formatPercent(systemData.cpu_usage_percent)}
          color="var(--accent)"
          icon={<FiCpu />}
          detail={`${systemData.cpu_cores || 0} cores`}
          percent={systemData.cpu_usage_percent}
        />
        <StatCard
          label="RAM Usage"
          value={formatPercent(systemData.ram_usage_percent)}
          color="var(--success)"
          icon={<FiActivity />}
          detail={`${formatGB(systemData.ram_used_gb)} / ${formatGB(systemData.ram_total_gb)}`}
          percent={systemData.ram_usage_percent}
        />
        <StatCard
          label="Disk Usage"
          value={formatPercent(systemData.disk_usage_percent)}
          color="var(--warning)"
          icon={<FiHardDrive />}
          detail={`${formatGB(systemData.disk_used_gb)} / ${formatGB(systemData.disk_total_gb)}`}
          percent={systemData.disk_usage_percent}
        />
        <StatCard
          label="Uptime"
          value={formatUptime(systemData.uptime_hours)}
          color="#7c83f5"
          icon={<FiCheckCircle />}
          detail={systemData.os_name || 'Unknown OS'}
          percent={null}
        />
      </div>

      {/* Charts — side by side */}
      <div className="charts-row">
        <div className="chart-card">
          <h3>CPU Usage History</h3>
          <ResponsiveContainer width="100%" height={180}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
              <XAxis
                dataKey="collected_at"
                tickFormatter={(val) =>
                  new Date(val).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                }
                stroke="var(--text-muted)"
                tick={{ fontSize: 11 }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                stroke="var(--text-muted)"
                tick={{ fontSize: 11 }}
                domain={[0, 100]}
                axisLine={false}
                tickLine={false}
                width={32}
              />
              <Tooltip
                contentStyle={{
                  background: 'var(--bg-surface)',
                  border: '1px solid var(--border)',
                  borderRadius: '8px',
                  fontSize: '12px',
                }}
                labelFormatter={(val) => new Date(val).toLocaleTimeString()}
              />
              <Line
                type="monotone"
                dataKey="cpu_usage_percent"
                stroke="var(--accent)"
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4, fill: 'var(--accent)' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h3>RAM Usage History</h3>
          <ResponsiveContainer width="100%" height={180}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
              <XAxis
                dataKey="collected_at"
                tickFormatter={(val) =>
                  new Date(val).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                }
                stroke="var(--text-muted)"
                tick={{ fontSize: 11 }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                stroke="var(--text-muted)"
                tick={{ fontSize: 11 }}
                domain={[0, 100]}
                axisLine={false}
                tickLine={false}
                width={32}
              />
              <Tooltip
                contentStyle={{
                  background: 'var(--bg-surface)',
                  border: '1px solid var(--border)',
                  borderRadius: '8px',
                  fontSize: '12px',
                }}
                labelFormatter={(val) => new Date(val).toLocaleTimeString()}
              />
              <Line
                type="monotone"
                dataKey="ram_usage_percent"
                stroke="var(--success)"
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4, fill: 'var(--success)' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* System Info */}
      <div className="system-details-card">
        <h3>System Information</h3>
        <div className="details-grid">
          <DetailRow label="Operating System" value={systemData.os_name    || 'Unknown'} />
          <DetailRow label="OS Version"        value={systemData.os_version || 'Unknown'} />
          <DetailRow label="CPU Model"         value={systemData.cpu_model  || 'Unknown'} />
          <DetailRow label="CPU Cores"         value={systemData.cpu_cores  || '0'}       />
          <DetailRow label="Hostname"          value={agent?.hostname       || 'Unknown'} />
          <DetailRow label="IP Address"        value={agent?.ip_address     || 'Unknown'} />
          <DetailRow label="Last Seen"         value={formatDateTime(agent?.last_seen)}   />
        </div>
      </div>

    </div>
  )
}

// ─────────────────────────────────────────────
// Stat Card
// ─────────────────────────────────────────────
function StatCard({ label, value, color, icon, detail, percent }) {
  return (
    <div className="stat-card">
      <div className="stat-card-icon" style={{ color }}>{icon}</div>
      <div className="stat-card-label">{label}</div>
      <div className="stat-card-value" style={{ color }}>{value}</div>
      <div className="stat-card-detail">{detail}</div>
      {percent !== null && percent !== undefined && (
        <div className="stat-progress">
          <div
            className="stat-progress-fill"
            style={{ width: `${Math.min(percent, 100)}%`, background: color }}
          />
        </div>
      )}
    </div>
  )
}

// ─────────────────────────────────────────────
// Detail Row
// ─────────────────────────────────────────────
function DetailRow({ label, value }) {
  return (
    <div className="detail-row">
      <span className="detail-label">{label}</span>
      <span className="detail-value font-mono">{value}</span>
    </div>
  )
}

export default AgentDetails