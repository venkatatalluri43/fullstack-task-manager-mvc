import { AuthProvider, useAuth } from './context/AuthContext'
import LoginForm from './components/LoginForm'
import Dashboard from './components/Dashboard'
import './App.css'

function AppContent() {
  const { user } = useAuth()
  return user ? <Dashboard /> : <LoginForm />
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}
