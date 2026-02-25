import { NavLink, useLocation } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import {
  FiGrid,
  FiMonitor,
  FiUsers,
  FiShield,
  FiActivity,
  FiChevronRight
} from 'react-icons/fi'
import './Sidebar.css'

const adminNavItems = [
  { to: '/admin',   icon: FiShield,   label: 'Admin View',      badge: 'ADMIN' },
  { to: '/dashboard', icon: FiGrid,    label: 'Dashboard',       badge: null },
  { to: '/users',   icon: FiUsers,    label: 'User Management', badge: null },
]

const userNavItems = [
  { to: '/dashboard', icon: FiGrid,    label: 'Dashboard', badge: null },
]

function Sidebar() {
  const { user, isAdmin } = useAuth()
  const location = useLocation()
  const navItems = isAdmin ? adminNavItems : userNavItems

  return (
    <aside className="sidebar">
      {/* Top: System indicator */}
      <div className="sidebar-top">
        <div className="sidebar-system-badge">
          <FiActivity size={11} />
          <span>SYSTEM ONLINE</span>
        </div>
      </div>

      {/* Nav */}
      <nav className="sidebar-nav">
        <div className="sidebar-section-label">Navigation</div>

        {navItems.map(({ to, icon: Icon, label, badge }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `sidebar-link ${isActive ? 'active' : ''}`
            }
          >
            <Icon size={16} className="sidebar-link-icon" />
            <span className="sidebar-link-label">{label}</span>
            {badge && <span className="sidebar-link-badge">{badge}</span>}
            <FiChevronRight size={12} className="sidebar-link-arrow" />
          </NavLink>
        ))}
      </nav>

      {/* Bottom: User info */}
      <div className="sidebar-bottom">
        <div className="sidebar-divider" />
        <div className="sidebar-user-card">
          <div className="sidebar-user-icon">
            {user?.username?.[0]?.toUpperCase() || 'U'}
          </div>
          <div className="sidebar-user-meta">
            <span className="sidebar-user-name">{user?.username}</span>
            <span className={`sidebar-user-role ${user?.role}`}>
              {user?.role === 'admin' ? '● Admin' : '● User'}
            </span>
          </div>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar