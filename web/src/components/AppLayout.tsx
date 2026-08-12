import { NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../api/AuthContext'

const customerLinks = [
  { to: '/shops', label: 'Mis tiendas' },
  { to: '/live', label: 'Vista en vivo' },
  { to: '/historical', label: 'Histórico' },
  { to: '/analytics', label: 'Analítica' },
]

export function AppLayout() {
  const { email, logout, role } = useAuth()

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">HM</div>
          <div className="brand-text">
            <span className="brand-name">Heat Map</span>
            <span className="brand-tag">Retail analytics</span>
          </div>
        </div>
        <nav>
          <ul className="nav-list">
            {customerLinks.map((link) => (
              <li key={link.to}>
                <NavLink
                  to={link.to}
                  className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
                >
                  {link.label}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>
        <div className="sidebar-footer">
          <div className="user-email">{email}</div>
          {role ? <div className="user-email">Rol: {role}</div> : null}
          <button type="button" className="btn btn-ghost" onClick={logout}>
            Cerrar sesión
          </button>
        </div>
      </aside>
      <main className="main">
        <Outlet />
      </main>
    </div>
  )
}
