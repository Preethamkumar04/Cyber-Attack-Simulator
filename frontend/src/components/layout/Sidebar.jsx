/**
 * components/layout/Sidebar.jsx — primary navigation including history and analytics.
 */

import { NavLink } from 'react-router-dom'
import {
  BarChart3,
  History,
  LayoutDashboard,
  Shield,
} from 'lucide-react'

import { useAuth } from '../../context/AuthContext'
import './layout.css'

const NAV_ITEMS = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/simulation', label: 'Training Lab', icon: Shield },
  { to: '/history', label: 'Session History', icon: History },
  { to: '/analytics', label: 'Analytics', icon: BarChart3 },
]

export default function Sidebar() {
  const { user } = useAuth()

  return (
    <aside className="sidebar">
      <div className="sidebar__brand">
        <Shield className="sidebar__brand-icon" size={28} />
        <div>
          <strong>CyberSim</strong>
          <span>AI Training Platform</span>
        </div>
      </div>

      <nav className="sidebar__nav">
        {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              `sidebar__link ${isActive ? 'sidebar__link--active' : ''}`
            }
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="sidebar__footer">
        {user && (
          <>
            <p>{user.username}</p>
            <small>
              {user.tenant_name} · {user.role}
            </small>
          </>
        )}
        <small>Mock Engine · FastAPI + Ollama</small>
      </div>
    </aside>
  )
}
