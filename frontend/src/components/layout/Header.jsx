/**
 * components/layout/Header.jsx — status bar with tenant/user context and logout.
 */

import { useQuery } from '@tanstack/react-query'
import { Activity, Cpu, LogOut } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

import { fetchHealth } from '../../api/scenarioApi'
import { useAuth } from '../../context/AuthContext'
import { useSimulationContext } from '../../context/SimulationContext'
import Badge from '../ui/Badge'
import Button from '../ui/Button'

import './layout.css'

export default function Header() {
  const { session, step } = useSimulationContext()
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: fetchHealth,
    refetchInterval: 30000,
    retry: 1,
  })

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <header className="header">
      <div className="header__left">
        <Activity size={18} className="header__pulse" />
        <span className="header__title">SOC Investigation Console</span>
        {session && (
          <Badge tone="info">
            Session #{session.id} · {session.difficulty}
          </Badge>
        )}
        {user && <Badge tone="default">{user.tenant_name}</Badge>}
      </div>

      <div className="header__right">
        {step !== 'select' && step !== 'feedback' && (
          <Badge tone="success">Live Simulation</Badge>
        )}
        <div className="header__status">
          <Cpu size={14} />
          <span>
            {health?.engine || 'mock'} · {health?.model || 'ollama'}
          </span>
        </div>
        {user && (
          <Button variant="ghost" onClick={handleLogout}>
            <LogOut size={14} /> Logout
          </Button>
        )}
      </div>
    </header>
  )
}
