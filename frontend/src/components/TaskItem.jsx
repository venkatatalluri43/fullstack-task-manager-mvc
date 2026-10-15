const STATUS_LABELS = {
  pending: 'Pending',
  in_progress: 'In Progress',
  done: 'Done',
}

export default function TaskItem({ task, currentUsername, onStatusChange, onDelete }) {
  const isOwner = task.owner === currentUsername

  return (
    <li className={`task-item status-${task.status}`}>
      <div className="task-main">
        <h3>{task.title}</h3>
        {task.description && <p>{task.description}</p>}
        <span className="owner-tag">by {task.owner}</span>
      </div>
      <div className="task-actions">
        <select
          value={task.status}
          disabled={!isOwner}
          onChange={(e) => onStatusChange(task.id, e.target.value)}
        >
          {Object.entries(STATUS_LABELS).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
        {isOwner && (
          <button className="delete-btn" onClick={() => onDelete(task.id)}>
            Delete
          </button>
        )}
      </div>
    </li>
  )
}
