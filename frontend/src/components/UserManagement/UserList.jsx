import { useState, useEffect } from 'react'
import { usersAPI, agentsAPI } from '../../services/api'
import Navbar from '../Common/Navbar'
import Sidebar from '../Common/Sidebar'
import CreateUser from './CreateUser'
import {
  FiUsers, FiPlus, FiTrash2, FiEdit2, FiShield,
  FiUser, FiX, FiCheck, FiRefreshCw, FiMonitor
} from 'react-icons/fi'
import { formatDateTime, getErrorMessage } from '../../utils/helpers'
import './UserList.css'

function UserList() {
  const [users, setUsers]       = useState([])
  const [agents, setAgents]     = useState([])
  const [loading, setLoading]   = useState(true)
  const [error, setError]       = useState(null)
  const [showCreate, setShowCreate] = useState(false)
  const [editUser, setEditUser] = useState(null)
  const [assignModal, setAssignModal] = useState(null) // user object
  const [deleting, setDeleting] = useState(null)
  const [msg, setMsg]           = useState(null)

  const fetchAll = async () => {
    try {
      setLoading(true)
      setError(null)
      const [u, a] = await Promise.all([usersAPI.getAll(), agentsAPI.getAll()])
      setUsers(u)
      setAgents(a)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchAll() }, [])

  const flash = (text, type = 'success') => {
    setMsg({ text, type })
    setTimeout(() => setMsg(null), 3500)
  }

  const handleDelete = async (userId, username) => {
    if (!window.confirm(`Delete user "${username}"? This cannot be undone.`)) return
    setDeleting(userId)
    try {
      await usersAPI.delete(userId)
      setUsers(prev => prev.filter(u => u.id !== userId))
      flash(`User "${username}" deleted.`)
    } catch (err) {
      flash(getErrorMessage(err), 'error')
    } finally {
      setDeleting(null)
    }
  }

  const handleToggleActive = async (u) => {
    try {
      const updated = await usersAPI.update(u.id, { is_active: !u.is_active })
      setUsers(prev => prev.map(x => x.id === u.id ? { ...x, ...updated } : x))
      flash(`User "${u.username}" ${updated.is_active ? 'activated' : 'deactivated'}.`)
    } catch (err) {
      flash(getErrorMessage(err), 'error')
    }
  }

  const handleAssign = async (userId, agentId) => {
    try {
      await usersAPI.assignAgent(userId, agentId)
      await fetchAll()
      flash('Agent assigned!')
    } catch (err) {
      flash(getErrorMessage(err), 'error')
    }
  }

  const handleUnassign = async (userId, agentId) => {
    try {
      await usersAPI.unassignAgent(userId, agentId)
      await fetchAll()
      flash('Agent unassigned.')
    } catch (err) {
      flash(getErrorMessage(err), 'error')
    }
  }

  return (
    <div className="page-layout">
      <Sidebar />
      <div className="page-content">
        <Navbar />
        <div className="page-inner">

          {/* Header */}
          <div className="userlist-header">
            <div>
              <h1 className="userlist-title">
                <FiUsers size={22} />
                User Management
              </h1>
              <p className="userlist-sub">Manage accounts and agent assignments</p>
            </div>
            <div className="userlist-header-actions">
              {msg && (
                <span className={`flash-msg ${msg.type}`}>{msg.text}</span>
              )}
              <button className="btn btn-ghost btn-sm" onClick={fetchAll} disabled={loading}>
                <FiRefreshCw size={13} className={loading ? 'spin-anim' : ''} />
                Refresh
              </button>
              <button className="btn btn-primary btn-sm" onClick={() => setShowCreate(true)}>
                <FiPlus size={14} />
                Add User
              </button>
            </div>
          </div>

          {/* Error */}
          {error && <div className="error-state mb-4">{error}</div>}

          {/* Users table */}
          <div className="card">
            {loading ? (
              <div className="loading-state" style={{ padding: 'var(--space-10)' }}>
                <div className="spinner" />
                <span>Loading users...</span>
              </div>
            ) : (
              <div style={{ overflowX: 'auto', borderRadius: 'var(--radius)', border: '1px solid var(--border)' }}>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>User</th>
                      <th>Email</th>
                      <th>Role</th>
                      <th>Status</th>
                      <th>Agents</th>
                      <th>Created</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map(u => (
                      <tr key={u.id}>
                        <td>
                          <div className="user-cell">
                            <div className={`user-avatar-sm ${u.role}`}>
                              {u.role === 'admin' ? <FiShield size={12} /> : <FiUser size={12} />}
                            </div>
                            <span className="user-username">{u.username}</span>
                          </div>
                        </td>
                        <td style={{ color: 'var(--text-secondary)' }}>{u.email}</td>
                        <td>
                          <span className={`role-badge ${u.role}`}>
                            {u.role === 'admin' ? <FiShield size={10} /> : <FiUser size={10} />}
                            {u.role}
                          </span>
                        </td>
                        <td>
                          <button
                            className={`status-toggle ${u.is_active ? 'active' : 'inactive'}`}
                            onClick={() => handleToggleActive(u)}
                            title="Click to toggle"
                          >
                            {u.is_active ? <FiCheck size={11} /> : <FiX size={11} />}
                            {u.is_active ? 'Active' : 'Inactive'}
                          </button>
                        </td>
                        <td>
                          <div className="agents-cell">
                            <span className="agents-count">
                              {u.assigned_agents?.length ?? 0}
                            </span>
                            <button
                              className="btn btn-ghost btn-sm assign-btn"
                              onClick={() => setAssignModal(u)}
                            >
                              <FiMonitor size={11} />
                              Assign
                            </button>
                          </div>
                        </td>
                        <td style={{ color: 'var(--text-muted)' }}>
                          {formatDateTime(u.created_at)}
                        </td>
                        <td>
                          <div className="user-actions">
                            <button
                              className="icon-action-btn danger"
                              onClick={() => handleDelete(u.id, u.username)}
                              disabled={deleting === u.id}
                              title="Delete user"
                            >
                              <FiTrash2 size={13} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                    {users.length === 0 && (
                      <tr>
                        <td colSpan={7} style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
                          No users found
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </div>

        </div>
      </div>

      {/* Create user modal */}
      {showCreate && (
        <CreateUser
          onClose={() => setShowCreate(false)}
          onCreated={(newUser) => {
            setUsers(prev => [...prev, newUser])
            setShowCreate(false)
            flash(`User "${newUser.username}" created!`)
          }}
        />
      )}

      {/* Assign agent modal */}
      {assignModal && (
        <AssignAgentModal
          user={assignModal}
          agents={agents}
          onAssign={handleAssign}
          onUnassign={handleUnassign}
          onClose={() => setAssignModal(null)}
        />
      )}
    </div>
  )
}

function AssignAgentModal({ user, agents, onAssign, onUnassign, onClose }) {
  const assignedIds = new Set((user.assigned_agents || []).map(a => a.id || a.agent_id))

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h3 className="modal-title">
            <FiMonitor size={16} />
            Assign Agents — {user.username}
          </h3>
          <button className="modal-close" onClick={onClose}><FiX size={16} /></button>
        </div>

        <div className="modal-body">
          {agents.length === 0 ? (
            <p className="text-muted text-sm">No agents registered.</p>
          ) : (
            <div className="assign-agent-list">
              {agents.map(agent => {
                const isAssigned = assignedIds.has(agent.id) || assignedIds.has(agent.agent_id)
                return (
                  <div key={agent.id} className="assign-agent-row">
                    <div className="assign-agent-info">
                      <FiMonitor size={14} />
                      <div>
                        <span className="assign-agent-name">{agent.hostname}</span>
                        <span className="assign-agent-ip">{agent.ip_address}</span>
                      </div>
                    </div>
                    <button
                      className={`btn btn-sm ${isAssigned ? 'btn-danger' : 'btn-primary'}`}
                      onClick={() => isAssigned
                        ? onUnassign(user.id, agent.id || agent.agent_id)
                        : onAssign(user.id, agent.id || agent.agent_id)
                      }
                    >
                      {isAssigned ? 'Unassign' : 'Assign'}
                    </button>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default UserList