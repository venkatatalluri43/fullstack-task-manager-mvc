import { NavLink } from 'react-router-dom'

const NAV_ITEMS = [
  { to: '/', label: 'Dashboard', icon: '◈', end: true },
  { to: '/projects', label: 'Projects', icon: '▤' },
  { to: '/my-work', label: 'My Work', icon: '✓' },
  { to: '/profile', label: 'Profile', icon: '◎' },
]

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <span className="brand-mark">T</span>
        <span className="brand-name">Taskflow</span>
      </div>
      <nav className="sidebar-nav">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) => `sidebar-link${isActive ? ' active' : ''}`}
          >
            <span className="sidebar-icon">{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </nav>
      <div className="sidebar-footer">
        <span>Taskflow &middot; local dev</span>
      </div>
    </aside>
  )
}
