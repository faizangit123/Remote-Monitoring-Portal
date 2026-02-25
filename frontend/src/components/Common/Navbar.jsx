import { useAuth } from '../../context/AuthContext'
import { FiMonitor, FiBell, FiLogOut, FiUser, FiWifi } from 'react-icons/fi'
import './Navbar.css'

function Navbar({ agentCount = 0, onlineCount = 0 }) {
  const { user, logout } = useAuth()

  return (
    <nav className="navbar">
      {/* Left: Brand */}
      <div className="navbar-brand">
        <div className="navbar-logo">
          <FiMonitor size={18} />
        </div>
        <div className="navbar-title">
          <span className="navbar-title-main">RemoteMonitor</span>
          <span className="navbar-title-sub">Portal v1.0</span>
        </div>
      </div>

      {/* Center: Live stats */}
      <div className="navbar-stats">
        <div className="navbar-stat">
          <FiWifi size={13} className="navbar-stat-icon online" />
          <span className="navbar-stat-value">{onlineCount}</span>
          <span className="navbar-stat-label">Online</span>
        </div>
        <div className="navbar-stat-divider" />
        <div className="navbar-stat">
          <FiMonitor size={13} className="navbar-stat-icon" />
          <span className="navbar-stat-value">{agentCount}</span>
          <span className="navbar-stat-label">Agents</span>
        </div>
      </div>

      {/* Right: User + actions */}
      <div className="navbar-right">
        <button className="navbar-icon-btn" title="Notifications">
          <FiBell size={16} />
          <span className="navbar-notif-dot" />
        </button>

        <div className="navbar-user">
          <div className="navbar-user-avatar">
            <FiUser size={14} />
          </div>
          <div className="navbar-user-info">
            <span className="navbar-user-name">{user?.username}</span>
            <span className={`navbar-user-role ${user?.role}`}>{user?.role}</span>
          </div>
        </div>

        <button className="navbar-logout-btn" onClick={logout} title="Logout">
          <FiLogOut size={15} />
          <span>Logout</span>
        </button>
      </div>
    </nav>
  )
}

export default Navbar