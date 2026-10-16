import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { projectApi, taskApi } from '../services/api'
import TopBar from '../components/TopBar'
import StatCard from '../components/ui/StatCard'

export default function ProfilePage() {
  const { user } = useAuth()
  const [stats, setStats] = useState(null)

  useEffect(() => {
    Promise.all([projectApi.list(), taskApi.list({ scope: 'all', assigned_to_me: 'true' })]).then(
      ([projectsData, tasksData]) => {
        const owned = projectsData.projects
        const assigned = tasksData.tasks
        setStats({
          projects: owned.length,
          assigned: assigned.length,
          completed: assigned.filter((t) => t.status === 'done').length,
        })
      }
    )
  }, [])

  const joined = new Date(user.created_at).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })

  return (
    <>
      <TopBar title="Profile" subtitle="Your account at a glance." />

      <div className="profile-card">
        <span className="avatar large">{user.username.slice(0, 1).toUpperCase()}</span>
        <div>
          <h2>{user.username}</h2>
          <p>Member since {joined}</p>
        </div>
      </div>

      {stats && (
        <div className="stat-grid">
          <StatCard label="Projects owned" value={stats.projects} accent="violet" />
          <StatCard label="Tasks assigned to you" value={stats.assigned} accent="cyan" />
          <StatCard label="Completed" value={stats.completed} accent="emerald" />
        </div>
      )}
    </>
  )
}
