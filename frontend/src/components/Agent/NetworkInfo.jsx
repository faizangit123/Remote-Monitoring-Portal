import { FiWifi } from 'react-icons/fi'
import './NetworkInfo.css'

function NetworkInfo({ networkInfo }) {
  const interfaces = networkInfo?.interfaces || []
  const stats = networkInfo?.stats || {}

  if (interfaces.length === 0) {
    return (
      <div className="empty-state">
        <FiWifi size={48} />
        <p>No network information available</p>
      </div>
    )
  }

  return (
    <div className="network-info">
      <div className="network-stats-card">
        <h3>Network Statistics</h3>
        <div className="stats-grid">
          <div className="stat-item">
            <span className="stat-label">Sent</span>
            <span className="stat-value">{stats.bytes_sent_mb?.toFixed(2) || '0'} MB</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Received</span>
            <span className="stat-value">{stats.bytes_recv_mb?.toFixed(2) || '0'} MB</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Packets Sent</span>
            <span className="stat-value">{stats.packets_sent?.toLocaleString() || '0'}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Packets Received</span>
            <span className="stat-value">{stats.packets_recv?.toLocaleString() || '0'}</span>
          </div>
        </div>
      </div>

      <div className="interfaces-list">
        <h3>Network Interfaces</h3>
        {interfaces.map((iface, idx) => (
          <div key={idx} className="interface-card">
            <h4>{iface.name}</h4>
            <div className="interface-details">
              {iface.addresses?.map((addr, addrIdx) => (
                <div key={addrIdx} className="address-row font-mono text-sm">
                  <span className="text-muted">{addr.family}:</span>
                  <span>{addr.address}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default NetworkInfo