import { useNavigate } from 'react-router-dom'
import { FiMonitor, FiWifi, FiWifiOff, FiChevronRight, FiCpu, FiHardDrive } from 'react-icons/fi'
import { formatPercent, formatRelativeTime } from '../../utils/helpers'
import './AgentList.css'

function AgentList({ agents = [], loading = false, error = null }) {
  const navigate = useNavigate()

  if (loading) {
    return (
      <div className="agent-list-skeleton">
        {[1, 2, 3].map(i => (
          <div key={i} className="agent-card-skeleton">
            <div className="skeleton-pulse" style={{ width: '40px', height: '40px', borderRadius: '8px' }} />
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div className="skeleton-pulse" style={{ width: '60%', height: '14px', borderRadius: '4px' }} />
              <div className="skeleton-pulse" style={{ width: '40%', height: '11px', borderRadius: '4px' }} />
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="error-state">
        <FiMonitor size={28} />
        <span>{error}</span>
      </div>
    )
  }

  if (!agents.length) {
    return (
      <div className="empty-state">
        <FiMonitor size={36} />
        <span>No agents found</span>
        <p className="text-sm">Agents will appear here once registered and connected.</p>
      </div>
    )
  }

  return (
    <div className="agent-list">
      {agents.map(agent => (
        <AgentCard
          key={agent.id || agent.agent_id}
          agent={agent}
          onClick={() => navigate(`/agents/${agent.agent_id || agent.id}`)}
        />
      ))}
    </div>
  )
}

function AgentCard({ agent, onClick }) {
  const online = agent.is_online
  const cpu = agent.latest_cpu ?? agent.cpu_percent ?? null
  const ram = agent.latest_ram ?? agent.ram_percent ?? null

  return (
    <div className={`agent-card ${online ? 'online' : 'offline'}`} onClick={onClick}>
      {/* Status indicator stripe */}
      <div className={`agent-card-stripe ${online ? 'online' : 'offline'}`} />

      {/* Icon */}
      <div className={`agent-card-icon ${online ? 'online' : 'offline'}`}>
        <FiMonitor size={18} />
      </div>

      {/* Info */}
      <div className="agent-card-info">
        <div className="agent-card-row">
          <span className="agent-card-hostname">{agent.hostname || agent.agent_id}</span>
          <div className={`badge ${online ? 'badge-online' : 'badge-offline'}`}>
            <span className={`status-dot ${online ? 'online' : 'offline'}`} />
            {online ? 'Online' : 'Offline'}
          </div>
        </div>

        <div className="agent-card-meta">
          <span className="font-mono text-xs text-muted">{agent.ip_address || '—'}</span>
          {agent.os_info && (
            <span className="agent-card-os">{agent.os_info}</span>
          )}
        </div>

        {/* Mini stats */}
        {online && (cpu !== null || ram !== null) && (
          <div className="agent-card-stats">
            {cpu !== null && (
              <div className="agent-mini-stat">
                <FiCpu size={10} />
                <span>CPU</span>
                <span className="agent-mini-value">{formatPercent(cpu)}</span>
              </div>
            )}
            {ram !== null && (
              <div className="agent-mini-stat">
                <FiHardDrive size={10} />
                <span>RAM</span>
                <span className="agent-mini-value">{formatPercent(ram)}</span>
              </div>
            )}
          </div>
        )}

        {!online && agent.last_seen && (
          <span className="agent-card-lastseen">
            Last seen {formatRelativeTime(agent.last_seen)}
          </span>
        )}
      </div>

      {/* Arrow */}
      <FiChevronRight size={16} className="agent-card-arrow" />
    </div>
  )
}

export default AgentList