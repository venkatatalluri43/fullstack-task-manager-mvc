const PRIORITY_LABELS = { low: 'Low', medium: 'Medium', high: 'High' }
const STATUS_LABELS = { pending: 'Pending', in_progress: 'In Progress', done: 'Done' }

export function PriorityBadge({ priority }) {
  return <span className={`badge priority-${priority}`}>{PRIORITY_LABELS[priority] || priority}</span>
}

export function StatusBadge({ status }) {
  return <span className={`badge status-${status}`}>{STATUS_LABELS[status] || status}</span>
}

export function DueDateBadge({ dueDate }) {
  if (!dueDate) return null
  const date = new Date(`${dueDate}T00:00:00`)
  const isOverdue = date < new Date(new Date().toDateString())
  return (
    <span className={`badge due-date${isOverdue ? ' overdue' : ''}`}>
      {isOverdue ? 'Overdue · ' : ''}
      {date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
    </span>
  )
}
