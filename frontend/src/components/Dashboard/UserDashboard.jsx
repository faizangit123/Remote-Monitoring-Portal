import { useState, useEffect } from 'react'
import { agentsAPI } from '../../services/api'
import { useAuth } from '../../context/AuthContext'
import Navbar from '../Common/Navbar'
import Sidebar from '../Common/Sidebar'
import AgentList from './AgentList'
import { FiMonitor, FiWifi, FiEye, FiRefreshCw } from 'react-icons/fi'
import './UserDashboard.css'

function UserDashboard() {
  const { user } = useAuth()

  const [agents, setAgents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError]   = useState(null)

  const fetchAgents = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await agentsAPI.getAll()
      setAgents(data)
    } catch (err) {
      console.log(err)
      setError('Failed to load your assigned agents.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAgents()
  }, [])

  const onlineCount = agents.filter(a => a.is_online).length

  return (
    <div className="page-layout">
      <Sidebar />

      <div className="page-content">
        <Navbar agentCount={agents.length} onlineCount={onlineCount} />

        <div className="page-inner">

          {/* Header */}
          <div className="user-dash-header">
            <div>
              <h1 className="user-dash-title">
                <FiEye size={22} />
                My Dashboard
              </h1>
              <p className="user-dash-sub">
                Welcome back, <strong>{user?.username}</strong> · Viewing assigned agents
              </p>
            </div>
            <button className="btn btn-ghost btn-sm" onClick={fetchAgents} disabled={loading}>
              <FiRefreshCw size={13} className={loading ? 'spin-anim' : ''} />
              Refresh
            </button>
          </div>

          {/* Mini stats */}
          <div className="grid-2 user-stats-row">
            <div className="stat-card">
              <span className="stat-card-label">Assigned Agents</span>
              <span className="stat-card-value">{agents.length}</span>
              <span className="stat-card-sub">Accessible to you</span>
              <FiMonitor size={32} className="stat-card-bg-icon" />
            </div>

            <div className="stat-card">
              <span className="stat-card-label">Currently Online</span>
              <span className="stat-card-value" style={{ color: 'var(--success)' }}>
                {onlineCount}
              </span>
              <span className="stat-card-sub">Active right now</span>
              <FiWifi size={32} className="stat-card-bg-icon" />
            </div>
          </div>

          {/* Agent list */}
          <div className="card">
            <div className="section-header">
              <div className="section-title">
                <FiMonitor size={16} />
                Assigned Agents
              </div>
              <span className="text-xs text-muted font-mono">Read-only access</span>
            </div>

            {!loading && !error && agents.length === 0 ? (
              <div className="user-no-agents">
                <FiMonitor size={40} />
                <h3>No Agents Assigned</h3>
                <p>Ask your administrator to assign agents to your account.</p>
              </div>
            ) : (
              <AgentList agents={agents} loading={loading} error={error} />
            )}
          </div>

        </div>
      </div>
    </div>
  )
}

export default UserDashboard