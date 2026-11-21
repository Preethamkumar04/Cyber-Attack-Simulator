/**
 * pages/DashboardPage.jsx
 *
 * Landing dashboard with platform overview, workflow summary, and quick-start CTA.
 */

import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ArrowRight, Brain, History, Server, Shield, Terminal } from 'lucide-react'

import { fetchHealth } from '../api/scenarioApi'
import { fetchMySkillProfile } from '../api/researchApi'
import { useAuth } from '../context/AuthContext'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'

import './pages.css'

const FEATURES = [
  {
    icon: Brain,
    title: 'AI Scenario Generation',
    description: 'Ollama generates unique attack scenarios with hidden objectives per difficulty level.',
  },
  {
    icon: Server,
    title: 'Mock Attack Engine',
    description: 'Simulates logs, traffic, alerts, and command history — Docker-ready architecture.',
  },
  {
    icon: Terminal,
    title: 'Interactive Terminal',
    description: 'Investigate artifacts using a SOC shell with grep, cat, and log analysis commands.',
  },
  {
    icon: Shield,
    title: 'Semantic Evaluation',
    description: 'AI-powered scoring and mentor feedback on findings, commands, and mitigation.',
  },
]

const WORKFLOW = [
  'Select difficulty level',
  'AI generates scenario & mock artifacts',
  'Investigate logs and terminal',
  'Submit analyst report',
  'Receive AI feedback & score',
]

export default function DashboardPage() {
  const { user } = useAuth()
  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: fetchHealth,
    retry: 1,
  })
  const { data: skillProfile } = useQuery({
    queryKey: ['skill-profile'],
    queryFn: fetchMySkillProfile,
  })

  return (
    <div className="dashboard-page">
      <header className="page-header">
        <h1>AI-Powered Cyber Attack Simulation</h1>
        <p>
          Research-grade SOC training platform for M.Tech cybersecurity education.
          {user && (
            <>
              {' '}
              Signed in as <strong>{user.username}</strong> ({user.tenant_name}).
            </>
          )}
        </p>
      </header>

      <div className="dashboard-hero">
        <div className="dashboard-hero__content">
          <Badge tone={health ? 'success' : 'warning'}>
            Backend: {health?.status || 'checking…'}
          </Badge>
          <h2>Start Your Next Investigation</h2>
          <p>
            Choose a difficulty, analyze generated security artifacts, and submit your
            findings for AI mentor feedback.
          </p>
          <div className="dashboard-hero__actions">
            <Link to="/simulation">
              <Button>
                Enter Training Lab <ArrowRight size={16} />
              </Button>
            </Link>
            <Link to="/history">
              <Button variant="secondary">
                <History size={16} /> Session History
              </Button>
            </Link>
          </div>
        </div>
        <div className="dashboard-hero__stats">
          <div className="hero-stat">
            <span className="hero-stat__value">4</span>
            <span className="hero-stat__label">Difficulty Levels</span>
          </div>
          <div className="hero-stat">
            <span className="hero-stat__value">4</span>
            <span className="hero-stat__label">Log Sources</span>
          </div>
          <div className="hero-stat">
            <span className="hero-stat__value">100</span>
            <span className="hero-stat__label">Max Score</span>
          </div>
        </div>
      </div>

      <div className="grid-2 dashboard-page__sections">
        <Card title="Platform Capabilities">
          <div className="feature-list">
            {FEATURES.map(({ icon: Icon, title, description }) => (
              <div key={title} className="feature-item">
                <Icon size={20} className="feature-item__icon" />
                <div>
                  <strong>{title}</strong>
                  <p>{description}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card title="Training Workflow">
          <ol className="workflow-list">
            {WORKFLOW.map((step, index) => (
              <li key={step}>
                <span className="workflow-list__num">{index + 1}</span>
                {step}
              </li>
            ))}
          </ol>
        </Card>

        <Card title="Observable Skill Profile" subtitle="Accumulated from completed training sessions">
          <p className="analytics-stat-value">{skillProfile?.sessions_completed || 0}</p>
          <p>completed sessions</p>
          {Object.entries(skillProfile?.skill_dimensions || {}).map(([name, value]) => (
            <p key={name}>{name.replaceAll('_', ' ')}: <strong>{Math.round(value * 100)}%</strong></p>
          ))}
        </Card>
      </div>
    </div>
  )
}
