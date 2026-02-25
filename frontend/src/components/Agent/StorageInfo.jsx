import { FiHardDrive } from 'react-icons/fi'
import { formatGB, formatPercent, getUsageColor } from '../../utils/helpers'
import './StorageInfo.css'

function StorageInfo({ diskPartitions }) {
  if (!diskPartitions || diskPartitions.length === 0) {
    return (
      <div className="empty-state">
        <FiHardDrive size={48} />
        <p>No disk information available</p>
      </div>
    )
  }

  return (
    <div className="storage-info">
      {diskPartitions.map((partition, idx) => (
        <div key={idx} className="storage-card">
          <div className="storage-header">
            <FiHardDrive size={24} />
            <div>
              <h4>{partition.device}</h4>
              <small className="text-muted">{partition.fstype}</small>
            </div>
          </div>
          <div className="storage-usage">
            <div className="usage-bar">
              <div 
                className={`usage-fill ${getUsageColor(partition.percent)}`}
                style={{ width: `${partition.percent}%` }}
              />
            </div>
            <div className="usage-text">
              <span>{formatGB(partition.used_gb)} used</span>
              <span className="text-muted">{formatPercent(partition.percent)}</span>
              <span>{formatGB(partition.free_gb)} free</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

export default StorageInfo