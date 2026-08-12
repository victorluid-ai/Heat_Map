import { useState, type FormEvent } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from '../api/AuthContext'
import { ApiError } from '../api/client'

type Mode = 'login' | 'register'

export function AuthPage({ mode }: { mode: Mode }) {
  const { login, register, token, loading } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  if (!loading && token) {
    return <Navigate to="/shops" replace />
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      if (mode === 'login') {
        await login(email.trim(), password)
      } else {
        await register(email.trim(), password)
      }
      navigate('/shops', { replace: true })
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message
          : 'No se pudo completar la autenticación'
      setError(message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="auth-screen">
      <div className="auth-card">
        <h1>Heat Map</h1>
        <p className="lede">
          {mode === 'login'
            ? 'Accede para gestionar tus tiendas y cámaras.'
            : 'Crea una cuenta de cliente para empezar.'}
        </p>
        {error ? <div className="error-banner">{error}</div> : null}
        <form onSubmit={(e) => void onSubmit(e)}>
          <div className="field">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="tu@example.com"
            />
          </div>
          <div className="field">
            <label htmlFor="password">Contraseña</label>
            <input
              id="password"
              type="password"
              autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
              required
              minLength={6}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <button type="submit" className="btn btn-primary" style={{ width: '100%' }} disabled={submitting}>
            {submitting ? 'Espera…' : mode === 'login' ? 'Entrar' : 'Registrarse'}
          </button>
        </form>
        <p className="auth-switch">
          {mode === 'login' ? (
            <>
              ¿Sin cuenta? <Link to="/register">Regístrate</Link>
            </>
          ) : (
            <>
              ¿Ya tienes cuenta? <Link to="/login">Inicia sesión</Link>
            </>
          )}
        </p>
      </div>
    </div>
  )
}
