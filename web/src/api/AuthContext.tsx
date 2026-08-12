import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import { api, getStoredToken, setStoredToken, type MeResponse, type Role } from './client'

interface AuthState {
  token: string | null
  email: string | null
  role: Role | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthState | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => getStoredToken())
  const [user, setUser] = useState<MeResponse | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    async function load() {
      if (!token) {
        setUser(null)
        setLoading(false)
        return
      }
      try {
        const me = await api.me(token)
        if (!cancelled) setUser(me)
      } catch {
        if (!cancelled) {
          setStoredToken(null)
          setToken(null)
          setUser(null)
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    void load()
    return () => {
      cancelled = true
    }
  }, [token])

  const applyToken = useCallback(async (accessToken: string) => {
    setStoredToken(accessToken)
    setToken(accessToken)
    const me = await api.me(accessToken)
    setUser(me)
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    const { access_token } = await api.login(email, password)
    await applyToken(access_token)
  }, [applyToken])

  const register = useCallback(async (email: string, password: string) => {
    const { access_token } = await api.register(email, password)
    await applyToken(access_token)
  }, [applyToken])

  const logout = useCallback(() => {
    setStoredToken(null)
    setToken(null)
    setUser(null)
  }, [])

  const value = useMemo<AuthState>(
    () => ({
      token,
      email: user?.email ?? null,
      role: user?.role ?? null,
      loading,
      login,
      register,
      logout,
    }),
    [token, user, loading, login, register, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return ctx
}
