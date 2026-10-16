import { useEffect, useState, useCallback } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { projectApi } from '../services/api'
import TopBar from '../components/TopBar'
import ProgressBar from '../components/ui/ProgressBar'
import EmptyState from '../components/ui/EmptyState'
import ProjectFormModal from '../components/ProjectFormModal'

export default function ProjectsPage() {
  const navigate = useNavigate()
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreate, setShowCreate] = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    const data = await projectApi.list()
    setProjects(data.projects)
    setLoading(false)
  }, [])

  useEffect(() => {
    load()
  }, [load])

  const handleCreate = async (project) => {
    const data = await projectApi.create(project)
    navigate(`/projects/${data.project.id}`)
  }

  return (
    <>
      <TopBar
        title="Projects"
        subtitle="Everything you're working on, grouped by goal."
        actions={
          <button className="primary-btn" onClick={() => setShowCreate(true)}>
            + New project
          </button>
        }
      />

      {loading ? (
        <div className="page-loading">Loading projects...</div>
      ) : projects.length === 0 ? (
        <EmptyState
          icon="◈"
          title="No projects yet"
          description="Create a project to start organizing tasks for a goal, launch, or team."
          action={
            <button className="primary-btn" onClick={() => setShowCreate(true)}>
              + New project
            </button>
          }
        />
      ) : (
        <div className="project-grid">
          {projects.map((p) => (
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
      )}

      {showCreate && <ProjectFormModal onClose={() => setShowCreate(false)} onCreate={handleCreate} />}
    </>
  )
}
