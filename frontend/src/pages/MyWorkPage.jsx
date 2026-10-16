import { useEffect, useState, useCallback } from 'react'
import { useAuth } from '../context/AuthContext'
import { taskApi } from '../services/api'
import TopBar from '../components/TopBar'
import EmptyState from '../components/ui/EmptyState'
import TaskCard from '../components/TaskCard'

const FILTERS = [
  { value: 'all', label: 'All' },
  { value: 'pending', label: 'Pending' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'done', label: 'Done' },
]

export default function MyWorkPage() {
  const { user } = useAuth()
  const [tasks, setTasks] = useState([])
  const [filter, setFilter] = useState('all')
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    setLoading(true)
    const data = await taskApi.list({ scope: 'all', assigned_to_me: 'true' })
    setTasks(data.tasks)
    setLoading(false)
  }, [])

  useEffect(() => {
    load()
  }, [load])

  const handleStatusChange = async (id, status) => {
    await taskApi.update(id, { status })
    load()
  }

  const handleDelete = async (id) => {
    await taskApi.remove(id)
    load()
  }

  const visibleTasks = filter === 'all' ? tasks : tasks.filter((t) => t.status === filter)

  return (
    <>
      <TopBar title="My Work" subtitle="Every task assigned to you, across all projects." />

      <div className="filter-tabs">
        {FILTERS.map((f) => (
          <button
            key={f.value}
            className={filter === f.value ? 'active' : ''}
            onClick={() => setFilter(f.value)}
          >
            {f.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="page-loading">Loading your tasks...</div>
      ) : visibleTasks.length === 0 ? (
        <EmptyState icon="✓" title="Nothing here" description="No tasks match this filter." />
      ) : (
        <ul className="task-card-list">
          {visibleTasks.map((task) => (
            <TaskCard
              key={task.id}
              task={task}
              currentUserId={user.id}
              onStatusChange={handleStatusChange}
              onDelete={handleDelete}
              showProject
            />
          ))}
        </ul>
      )}
    </>
  )
}
