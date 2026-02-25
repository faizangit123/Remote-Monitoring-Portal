import { FiUsers } from 'react-icons/fi'
import { formatDateTime } from '../../utils/helpers'
import './SystemUsers.css'

function SystemUsers({ users }) {
  if (!users || users.length === 0) {
    return (
      <div className="empty-state">
        <FiUsers size={48} />
        <p>No user sessions found</p>
      </div>
    )
  }

  return (
    <div className="system-users">

      {/* Header bar */}
      <div className="system-users-header">
        <h3>Active Sessions ({users.length})</h3>
      </div>

      <table className="data-table">
        <thead>
          <tr>
            <th>Username</th>
            <th>Terminal</th>
            <th>Host</th>
            <th>Login Time</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user, idx) => {
            const name = user.name || user.username || '?'
            const initial = name[0].toUpperCase()

            return (
              <tr key={idx}>
                <td>
                  <div className="user-chip">
                    <div className="user-avatar">{initial}</div>
                    <span className="font-mono">{name}</span>
                  </div>
                </td>
                <td className="text-muted">{user.terminal || 'console'}</td>
                <td className="text-muted">{user.host || 'localhost'}</td>
                <td>{formatDateTime(user.started)}</td>
              </tr>
            )
          })}
        </tbody>
      </table>

    </div>
  )
}

export default SystemUsers