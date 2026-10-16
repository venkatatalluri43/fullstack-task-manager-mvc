import { Link } from 'react-router-dom'
import { PriorityBadge, StatusBadge, DueDateBadge } from './ui/Badge'

const STATUS_OPTIONS = [
  { value: 'pending', label: 'Pending' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'done', label: 'Done' },
]

export default function TaskCard({ task, currentUserId, onStatusChange, onDelete, showProject = false }) {
  const isOwner = task.user_id === currentUserId
  const isAssignee = task.assignee_id === currentUserId
  const canChangeStatus = isOwner || isAssignee

  return (
    <li className={`task-card status-${task.status}`}>
      <div className="task-card-main">
        <div className="task-card-heading">
          <h3>{task.title}</h3>
          <PriorityBadge priority={task.priority} />
        </div>
        {task.description && <p className="task-card-desc">{task.description}</p>}
        <div className="task-card-meta">
          {showProject && task.project_name && (
            <Link to={`/projects/${task.project_id}`} className="meta-link">
              {task.project_name}
            </Link>
          )}
          <DueDateBadge dueDate={task.due_date} />
          <span className="meta-assignee">
            <span className="avatar small">{task.assignee?.slice(0, 1).toUpperCase()}</span>
            {task.assignee}
          </span>
        </div>
      </div>
      <div className="task-card-actions">
        {canChangeStatus ? (
          <select value={task.status} onChange={(e) => onStatusChange(task.id, e.target.value)}>
            {STATUS_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        ) : (
          <StatusBadge status={task.status} />
        )}
        {isOwner && onDelete && (
          <button className="icon-btn danger" onClick={() => onDelete(task.id)} title="Delete task">
            ✕
          </button>
        )}
      </div>
    </li>
  )
}
