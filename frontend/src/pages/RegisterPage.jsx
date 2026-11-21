/**
 * pages/RegisterPage.jsx — multi-tenant registration (new org or join existing).
 */

import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Shield } from 'lucide-react'

import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import { useAuth } from '../context/AuthContext'

import './auth.css'

export default function RegisterPage() {
  const { register, isAuthenticated, loading } = useAuth()
  const navigate = useNavigate()
  const [mode, setMode] = useState('create')
  const [submitting, setSubmitting] = useState(false)
  const [form, setForm] = useState({
    email: '',
    username: '',
    password: '',
    tenant_name: '',
    tenant_slug: '',
  })

  if (!loading && isAuthenticated) {
    return <Navigate to="/" replace />
  }

  const updateField = (field) => (event) => {
    setForm((current) => ({ ...current, [field]: event.target.value }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setSubmitting(true)

    const payload = {
      email: form.email,
      username: form.username,
      password: form.password,
      tenant_name: mode === 'create' ? form.tenant_name : null,
      tenant_slug: mode === 'join' ? form.tenant_slug : null,
    }

    try {
      await register(payload)
      toast.success('Account created')
      navigate('/')
    } catch (error) {
      toast.error(error.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="auth-page">
      <Card className="auth-card" title="Create your account">
        <div className="auth-card__brand">
          <Shield size={32} />
          <p>Register for tenant-isolated SOC training</p>
        </div>

        <div className="auth-mode-toggle">
          <button
            type="button"
            className={mode === 'create' ? 'auth-mode-toggle__active' : ''}
            onClick={() => setMode('create')}
          >
            New Organization
          </button>
          <button
            type="button"
            className={mode === 'join' ? 'auth-mode-toggle__active' : ''}
            onClick={() => setMode('join')}
          >
            Join Existing
          </button>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          <label>
            Email
            <input type="email" value={form.email} onChange={updateField('email')} required />
          </label>

          <label>
            Username
            <input value={form.username} onChange={updateField('username')} required />
          </label>

          <label>
            Password
            <input
              type="password"
              value={form.password}
              onChange={updateField('password')}
              required
              minLength={8}
            />
          </label>

          {mode === 'create' ? (
            <label>
              Organization name
              <input
                value={form.tenant_name}
                onChange={updateField('tenant_name')}
                required
                placeholder="e.g. University SOC Lab"
              />
            </label>
          ) : (
            <label>
              Organization slug
              <input
                value={form.tenant_slug}
                onChange={updateField('tenant_slug')}
                required
                placeholder="e.g. university-soc-lab"
              />
            </label>
          )}

          <Button type="submit" loading={submitting} className="auth-form__submit">
            Register
          </Button>
        </form>

        <p className="auth-card__footer">
          Already registered? <Link to="/login">Sign in</Link>
        </p>
      </Card>
    </div>
  )
}
