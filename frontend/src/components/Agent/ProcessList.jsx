import { useState } from 'react'
import { FiX, FiAlertTriangle } from 'react-icons/fi'
import { commandsAPI } from '../../services/api'
import { getErrorMessage } from '../../utils/helpers'
import './ProcessList.css'

function ProcessList({ processes, agentId }) {
  const [killing, setKilling] = useState(null)

  const handleKillProcess = async (pid, processName) => {
    if (!confirm(`Kill process "${processName}" (PID: ${pid})?`)) {
      return
    }

    try {
      setKilling(pid)
      await commandsAPI.send(agentId, 'kill_process', { pid })
      setTimeout(() => setKilling(null), 2000)
    } catch (err) {
      alert(`Failed to kill process: ${getErrorMessage(err)}`)
      setKilling(null)
    }
  }

  if (!processes || processes.length === 0) {
    return (
      <div className="empty-state">
        <FiAlertTriangle size={48} />
        <p>No processes found</p>
        <small>Waiting for agent to send process list...</small>
      </div>
    )
  }

  return (
    <div className="process-list-container">
      <div className="process-list-header">
        <h3>Running Processes ({processes.length})</h3>
      </div>
      
      <div className="process-table-wrapper">
        <table className="data-table">
          <thead>
            <tr>
              <th>PID</th>
              <th>Name</th>
              <th>CPU %</th>
              <th>Memory (MB)</th>
              <th>Status</th>
              <th>User</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {processes.map((proc) => (
              <tr key={proc.pid}>
                <td className="font-mono">{proc.pid}</td>
                <td className="process-name">{proc.name}</td>
                <td className="font-mono" style={{ color: getCpuColor(proc.cpu_percent) }}>
                  {proc.cpu_percent?.toFixed(1) || '0.0'}%
                </td>
                <td className="font-mono">{proc.memory_mb?.toFixed(1) || '0.0'}</td>
                <td>
                  <span className={`badge badge-${getStatusColor(proc.status)}`}>
                    {proc.status || 'unknown'}
                  </span>
                </td>
                <td className="text-muted text-xs">{proc.username || 'N/A'}</td>
                <td>
                  <button
                    onClick={() => handleKillProcess(proc.pid, proc.name)}
                    disabled={killing === proc.pid || proc.pid < 10}
                    className="btn-icon btn-danger-ghost"
                    title={proc.pid < 10 ? 'System process (cannot kill)' : 'Kill process'}
                  >
                    <FiX />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function getCpuColor(percent) {
  if (!percent) return 'var(--text-secondary)'
  if (percent > 50) return 'var(--danger)'
  if (percent > 20) return 'var(--warning)'
  return 'var(--success)'
}

function getStatusColor(status) {
  if (status === 'running') return 'online'
  if (status === 'sleeping') return 'info'
  return 'offline'
}

export default ProcessList