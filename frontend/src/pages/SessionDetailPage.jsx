/**
 * pages/SessionDetailPage.jsx — single session report with evaluation recap.
 */

import { useQuery } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'

import { fetchSessionDetail } from '../api/sessionApi'
import { fetchSessionResearch } from '../api/researchApi'
import FeedbackPanel from '../components/simulation/FeedbackPanel'
import ScenarioOverview from '../components/simulation/ScenarioOverview'
import Badge from '../components/ui/Badge'
import Card from '../components/ui/Card'
import LoadingSpinner from '../components/ui/LoadingSpinner'

import './pages.css'

export default function SessionDetailPage() {
  const { sessionId } = useParams()

  const { data, isLoading, error } = useQuery({
    queryKey: ['session', sessionId],
    queryFn: () => fetchSessionDetail(sessionId),
    enabled: Boolean(sessionId),
  })
  const { data: research } = useQuery({
    queryKey: ['session-research', sessionId],
    queryFn: () => fetchSessionResearch(sessionId),
    enabled: Boolean(sessionId),
  })

  if (isLoading) {
    return <LoadingSpinner fullScreen label="Loading session detail…" />
  }

  if (error || !data) {
    return (
      <div className="simulation-error">
        {error?.message || 'Session not found.'}{' '}
        <Link to="/history">Back to history</Link>
      </div>
    )
  }

  return (
    <div className="history-detail-page">
      <header className="page-header">
        <h1>{data.session_name}</h1>
        <p>
          Session #{data.id} · <Badge tone="info">{data.difficulty}</Badge>{' '}
          <Badge tone={data.status === 'completed' ? 'success' : 'warning'}>
            {data.status}
          </Badge>
        </p>
      </header>

      <ScenarioOverview
        session={data}
        scenario={data.scenario}
        simulation={{
          attack_mode: data.attack_mode,
          timeline_events: '—',
          logs_generated: '—',
          alerts_generated: '—',
          commands_generated: '—',
        }}
      />

      {data.response && (
        <Card title="Submitted Analysis" subtitle="Analyst report for this session">
          <div className="detail-grid">
            <div>
              <h4>Findings</h4>
              <ul>
                {data.response.findings?.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
            <div>
              <h4>Commands</h4>
              <ul>
                {data.response.commands?.map((item) => (
                  <li key={item}>
                    <code>{item}</code>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h4>Severity</h4>
              <p>{data.response.severity}</p>
            </div>
            <div>
              <h4>Root Cause</h4>
              <p>{data.response.root_cause}</p>
            </div>
          </div>
        </Card>
      )}

      {data.evaluation && (
        <FeedbackPanel evaluation={data.evaluation} showRestart={false} />
      )}

      {research && (
        <Card title="Research Validation" subtitle="Execution, telemetry, and adaptation records">
          <p>Execution fidelity: <strong>{Math.round((research.execution_fidelity_score || 0) * 100)}%</strong></p>
          <p>Telemetry comparisons: {research.telemetry_records?.length || 0}</p>
          <p>Adaptive decisions: {research.adaptation_decisions?.length || 0}</p>
          {research.difficulty_adaptation?.mode === 'adaptive' && <p>Difficulty reason: {research.difficulty_adaptation.reason}</p>}
        </Card>
      )}

      <Link to="/history" className="history-back-link">
        ← Back to session history
      </Link>
    </div>
  )
}
