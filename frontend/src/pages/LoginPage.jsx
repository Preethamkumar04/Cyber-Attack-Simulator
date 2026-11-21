/**
 * pages/LoginPage.jsx — user login form.
 */

import { useState } from 'react'
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Shield } from 'lucide-react'

import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import { useAuth } from '../context/AuthContext'

import './auth.css'

export default function LoginPage() {
  const { login, isAuthenticated, loading } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [submitting, setSubmitting] = useState(false)

  if (!loading && isAuthenticated) {
    return <Navigate to={location.state?.from || '/'} replace />
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setSubmitting(true)

    try {
      await login(username, password)
      toast.success('Welcome back')
      navigate(location.state?.from || '/')
    } catch (error) {
      toast.error(error.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="auth-page">
      <Card className="auth-card" title="Sign in to CyberSim">
        <div className="auth-card__brand">
          <Shield size={32} />
          <p>AI-Powered Cyber Attack Training Platform</p>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          <label>
            Username or email
            <input
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              required
              autoComplete="username"
            />
          </label>

          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
              autoComplete="current-password"
            />
          </label>

          <Button type="submit" loading={submitting} className="auth-form__submit">
            Sign In
          </Button>
        </form>

        <p className="auth-card__footer">
          No account? <Link to="/register">Create one</Link>
        </p>
      </Card>
    </div>
  )
}
