import { useAuth } from '../context/AuthContext'

export default function TopBar({ title, subtitle, actions }) {
  const { user, logout } = useAuth()

  return (
    <header className="topbar">
      <div>
        <h1>{title}</h1>
        {subtitle && <p className="topbar-subtitle">{subtitle}</p>}
      </div>
      <div className="topbar-actions">
        {actions}
        <div className="user-chip">
          <span className="avatar">{user.username.slice(0, 1).toUpperCase()}</span>
          <span>{user.username}</span>
        </div>
        <button className="ghost-btn" onClick={logout}>
          Logout
        </button>
      </div>
    </header>
  )
}
