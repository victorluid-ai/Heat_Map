import type { ReactNode } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from './api/AuthContext'
import { AppLayout } from './components/AppLayout'
import { AnalyticsPage } from './pages/AnalyticsPage'
import { AuthPage } from './pages/AuthPage'
import { HistoricalPage } from './pages/HistoricalPage'
import { LivePage } from './pages/LivePage'
import { ShopsPage } from './pages/ShopsPage'

function ProtectedRoute({ children }: { children: ReactNode }) {
  const { token, loading } = useAuth()
  if (loading) {
    return (
      <div className="auth-screen">
        <p className="empty-state">Cargando sesión…</p>
      </div>
    )
  }
  if (!token) {
    return <Navigate to="/login" replace />
  }
  return children
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<AuthPage mode="login" />} />
      <Route path="/register" element={<AuthPage mode="register" />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/shops" replace />} />
        <Route path="shops" element={<ShopsPage />} />
        <Route path="live" element={<LivePage />} />
        <Route path="historical" element={<HistoricalPage />} />
        <Route path="analytics" element={<AnalyticsPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
