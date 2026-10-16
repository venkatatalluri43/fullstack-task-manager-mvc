import { useEffect, useState, useCallback } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { projectApi, taskApi } from '../services/api'
import TopBar from '../components/TopBar'
import ProgressBar from '../components/ui/ProgressBar'
import EmptyState from '../components/ui/EmptyState'
import TaskCard from '../components/TaskCard'
import TaskFormModal from '../components/TaskFormModal'

export default function ProjectDetailPage() {
  const { projectId } = useParams()
  const { user } = useAuth()
  const navigate = useNavigate()
  const [project, setProject] = useState(null)
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showCreateTask, setShowCreateTask] = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const [projectData, tasksData] = await Promise.all([
        projectApi.get(projectId),
        taskApi.list({ scope: 'all', project_id: projectId }),
      ])
      setProject(projectData.project)
      setTasks(tasksData.tasks)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [projectId])

  useEffect(() => {
    load()
  }, [load])

  const handleCreateTask = async (task) => {
    await taskApi.create({ ...task, project_id: Number(projectId) })
    load()
  }

  const handleStatusChange = async (id, status) => {
    await taskApi.update(id, { status })
    load()
  }

  const handleDeleteTask = async (id) => {
    await taskApi.remove(id)
    load()
  }

  const handleDeleteProject = async () => {
    if (!window.confirm(`Delete "${project.name}" and all its tasks? This can't be undone.`)) return
    await projectApi.remove(projectId)
    navigate('/projects')
  }

  if (loading) return <div className="page-loading">Loading project...</div>

  if (error) {
    return (
      <EmptyState
        icon="⚠"
        title="Couldn't load this project"
        description={error}
        action={
          <Link to="/projects" className="primary-btn">
            Back to projects
          </Link>
        }
      />
    )
  }

  const done = tasks.filter((t) => t.status === 'done').length
  const isOwner = project.owner_id === user.id

  return (
    <>
      <TopBar
        title={project.name}
        subtitle={project.description || 'No description yet'}
        actions={
          <>
            <button className="primary-btn" onClick={() => setShowCreateTask(true)}>
              + New task
            </button>
            {isOwner && (
              <button className="icon-btn danger" onClick={handleDeleteProject} title="Delete project">
                ✕
              </button>
            )}
          </>
        }
      />

      <div className="project-progress-banner">
        <ProgressBar value={done} total={tasks.length} />
        <span>
          {done}/{tasks.length} tasks complete
        </span>
      </div>

      {tasks.length === 0 ? (
        <EmptyState
          icon="✓"
          title="No tasks yet"
          description="Add the first task to get this project moving."
          action={
            <button className="primary-btn" onClick={() => setShowCreateTask(true)}>
              + New task
            </button>
          }
        />
      ) : (
        <ul className="task-card-list">
          {tasks.map((task) => (
            <TaskCard
              key={task.id}
              task={task}
              currentUserId={user.id}
              onStatusChange={handleStatusChange}
              onDelete={handleDeleteTask}
            />
          ))}
        </ul>
      )}

      {showCreateTask && (
        <TaskFormModal onClose={() => setShowCreateTask(false)} onCreate={handleCreateTask} />
      )}
    </>
  )
}
