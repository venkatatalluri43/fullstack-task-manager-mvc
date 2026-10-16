export default function StatCard({ label, value, hint, accent = 'violet' }) {
  return (
    <div className={`stat-card accent-${accent}`}>
      <span className="stat-value">{value}</span>
      <span className="stat-label">{label}</span>
      {hint && <span className="stat-hint">{hint}</span>}
    </div>
  )
}
