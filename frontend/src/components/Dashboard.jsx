import { useEffect, useState, useCallback } from 'react'
import { useAuth } from '../context/AuthContext'
import { taskApi } from '../services/api'
import TaskForm from './TaskForm'
import TaskList from './TaskList'

export default function Dashboard() {
  const { user, logout } = useAuth()
  const [tasks, setTasks] = useState([])
  const [scope, setScope] = useState('mine')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const loadTasks = useCallback(async (currentScope) => {
    setLoading(true)
    setError('')
    try {
      const data = await taskApi.list(currentScope)
      setTasks(data.tasks)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadTasks(scope)
  }, [scope, loadTasks])

  const handleCreate = async (task) => {
    await taskApi.create(task)
    await loadTasks(scope)
  }

  const handleStatusChange = async (id, status) => {
    await taskApi.update(id, { status })
    await loadTasks(scope)
  }

  const handleDelete = async (id) => {
    await taskApi.remove(id)
    await loadTasks(scope)
  }

  return (
    <div className="dashboard">
      <header>
        <h1>Task Manager</h1>
        <div className="user-bar">
          <span>Hi, {user.username}</span>
          <button onClick={logout}>Logout</button>
        </div>
      </header>

      <TaskForm onCreate={handleCreate} />

      <div className="scope-toggle">
        <button className={scope === 'mine' ? 'active' : ''} onClick={() => setScope('mine')}>
          My Tasks
        </button>
        <button className={scope === 'all' ? 'active' : ''} onClick={() => setScope('all')}>
          All Users' Tasks
        </button>
      </div>

      {loading && <p>Loading tasks...</p>}
      {error && <p className="error">{error}</p>}
      {!loading && !error && (
        <TaskList
          tasks={tasks}
          currentUsername={user.username}
          onStatusChange={handleStatusChange}
          onDelete={handleDelete}
        />
      )}
    </div>
  )
}
