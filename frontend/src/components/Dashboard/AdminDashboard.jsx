import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { agentsAPI, wsAPI } from '../../services/api'
import { useAuth } from '../../context/AuthContext'
import Navbar from '../Common/Navbar'
import Sidebar from '../Common/Sidebar'
import AgentList from './AgentList'
import { FiMonitor, FiWifi, FiWifiOff, FiUsers, FiRefreshCw, FiActivity } from 'react-icons/fi'
import { formatRelativeTime } from '../../utils/helpers'
import './AdminDashboard.css'

function AdminDashboard() {
  const { user } = useAuth()
  const navigate = useNavigate()

  const [agents, setAgents]   = useState([])
  const [wsStats, setWsStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState(null)
  const [lastRefresh, setLastRefresh] = useState(new Date())

  const fetchData = async () => {
    try {
      setLoading(true)
      setError(null)
      const [agentList, stats] = await Promise.all([
        agentsAPI.getAll(),
        wsAPI.getStats().catch(() => null),
      ])
      setAgents(agentList)
      setWsStats(stats)
      setLastRefresh(new Date())
    } catch (err) {
      setError('Failed to load agents. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 30000) // auto-refresh every 30s
    return () => clearInterval(interval)
  }, [])

  const onlineCount  = agents.filter(a => a.is_online).length
  const offlineCount = agents.length - onlineCount

  return (
    <div className="page-layout">
      <Sidebar />

      <div className="page-content">
        <Navbar agentCount={agents.length} onlineCount={onlineCount} />

        <div className="page-inner">

          {/* Page Header */}
          <div className="admin-page-header">
            <div>
              <h1 className="admin-page-title">
                <FiActivity size={22} />
                Admin Dashboard
              </h1>
              <p className="admin-page-sub">
                Full system overview · Last updated {formatRelativeTime(lastRefresh.toISOString())}
              </p>
            </div>
            <button className="btn btn-ghost btn-sm" onClick={fetchData} disabled={loading}>
              <FiRefreshCw size={13} className={loading ? 'spin-anim' : ''} />
              Refresh
            </button>
          </div>

          {/* Stat Cards */}
          <div className="grid-4 mb-6">
            <div className="stat-card">
              <span className="stat-card-label">Total Agents</span>
              <span className="stat-card-value">{agents.length}</span>
              <span className="stat-card-sub">Registered devices</span>
              <FiMonitor size={32} className="stat-card-bg-icon" />
            </div>

            <div className="stat-card stat-card--online">
              <span className="stat-card-label">Online</span>
              <span className="stat-card-value" style={{ color: 'var(--success)' }}>
                {onlineCount}
              </span>
              <span className="stat-card-sub">Active connections</span>
              <FiWifi size={32} className="stat-card-bg-icon" />
            </div>

            <div className="stat-card">
              <span className="stat-card-label">Offline</span>
              <span className="stat-card-value" style={{ color: offlineCount > 0 ? 'var(--danger)' : 'var(--text-muted)' }}>
                {offlineCount}
              </span>
              <span className="stat-card-sub">Disconnected</span>
              <FiWifiOff size={32} className="stat-card-bg-icon" />
            </div>

            <div className="stat-card">
              <span className="stat-card-label">Watching</span>
              <span className="stat-card-value">{wsStats?.watching_clients ?? '—'}</span>
              <span className="stat-card-sub">Browser clients</span>
              <FiUsers size={32} className="stat-card-bg-icon" />
            </div>
          </div>

          {/* Agent List */}
          <div className="card">
            <div className="section-header">
              <div className="section-title">
                <FiMonitor size={16} />
                All Agents
              </div>
              <button
                className="btn btn-primary btn-sm"
                onClick={() => navigate('/users')}
              >
                <FiUsers size={13} />
                Manage Users
              </button>
            </div>

            <AgentList agents={agents} loading={loading} error={error} />
          </div>

        </div>
      </div>
    </div>
  )
}

export default AdminDashboard