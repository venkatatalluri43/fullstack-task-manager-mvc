import { useEffect, useState, useCallback } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { projectApi, taskApi } from '../services/api'
import TopBar from '../components/TopBar'
import StatCard from '../components/ui/StatCard'
import ProgressBar from '../components/ui/ProgressBar'
import EmptyState from '../components/ui/EmptyState'
import TaskCard from '../components/TaskCard'
import ProjectFormModal from '../components/ProjectFormModal'

export default function DashboardPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [projects, setProjects] = useState([])
  const [myWork, setMyWork] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreateProject, setShowCreateProject] = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    const [projectsData, tasksData] = await Promise.all([
      projectApi.list(),
      taskApi.list({ scope: 'all', assigned_to_me: 'true' }),
    ])
    setProjects(projectsData.projects)
    setMyWork(tasksData.tasks)
    setLoading(false)
  }, [])

  useEffect(() => {
    load()
  }, [load])

  const handleCreateProject = async (project) => {
    const data = await projectApi.create(project)
    navigate(`/projects/${data.project.id}`)
  }

  const handleStatusChange = async (id, status) => {
    await taskApi.update(id, { status })
    load()
  }

  if (loading) return <div className="page-loading">Loading dashboard...</div>

  if (projects.length === 0) {
    return (
      <>
        <TopBar title={`Welcome, ${user.username}`} subtitle="Let's get your work organized." />
        <EmptyState
          icon="◈"
          title="Create your first project"
          description="Projects group related tasks together so you and your team can track progress toward a goal."
          action={
            <button className="primary-btn" onClick={() => setShowCreateProject(true)}>
              + New project
            </button>
          }
        />
        {showCreateProject && (
          <ProjectFormModal onClose={() => setShowCreateProject(false)} onCreate={handleCreateProject} />
        )}
      </>
    )
  }

  const totalTasks = projects.reduce((sum, p) => sum + p.task_count, 0)
  const totalDone = projects.reduce((sum, p) => sum + p.done_count, 0)
  const overdueCount = myWork.filter(
    (t) => t.due_date && t.status !== 'done' && new Date(`${t.due_date}T00:00:00`) < new Date(new Date().toDateString())
  ).length

  return (
    <>
      <TopBar
        title={`Welcome back, ${user.username}`}
        subtitle="Here's what's happening across your projects."
        actions={
          <button className="primary-btn" onClick={() => setShowCreateProject(true)}>
            + New project
          </button>
        }
      />

      <div className="stat-grid">
        <StatCard label="Projects" value={projects.length} accent="violet" />
        <StatCard label="Total tasks" value={totalTasks} accent="cyan" />
        <StatCard label="Completed" value={totalDone} hint={`${totalTasks ? Math.round((totalDone / totalTasks) * 100) : 0}% done`} accent="emerald" />
        <StatCard label="Assigned to me" value={myWork.length} hint={overdueCount ? `${overdueCount} overdue` : 'on track'} accent={overdueCount ? 'rose' : 'amber'} />
      </div>

      <section className="dashboard-section">
        <div className="section-heading">
          <h2>Your projects</h2>
          <Link to="/projects" className="meta-link">
            View all
          </Link>
        </div>
        <div className="project-grid">
          {projects.slice(0, 4).map((p) => (
            <Link to={`/projects/${p.id}`} key={p.id} className="project-card">
              <h3>{p.name}</h3>
              <p>{p.description || 'No description'}</p>
              <ProgressBar value={p.done_count} total={p.task_count} />
              <span className="project-card-meta">
                {p.done_count}/{p.task_count} tasks done
              </span>
            </Link>
          ))}
        </div>
      </section>

      <section className="dashboard-section">
        <div className="section-heading">
          <h2>Assigned to you</h2>
          <Link to="/my-work" className="meta-link">
            View all
          </Link>
        </div>
        {myWork.length === 0 ? (
          <EmptyState icon="✓" title="Nothing assigned to you yet" />
        ) : (
          <ul className="task-card-list">
            {myWork.slice(0, 5).map((task) => (
              <TaskCard
                key={task.id}
                task={task}
                currentUserId={user.id}
                onStatusChange={handleStatusChange}
                showProject
              />
            ))}
          </ul>
        )}
      </section>

      {showCreateProject && (
        <ProjectFormModal onClose={() => setShowCreateProject(false)} onCreate={handleCreateProject} />
      )}
    </>
  )
}
