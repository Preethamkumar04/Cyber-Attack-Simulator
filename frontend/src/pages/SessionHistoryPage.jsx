/**
 * pages/SessionHistoryPage.jsx — tenant-scoped training session history.
 */

import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Clock, ExternalLink } from 'lucide-react'

import { fetchSessions } from '../api/sessionApi'
import Badge from '../components/ui/Badge'
import Card from '../components/ui/Card'
import LoadingSpinner from '../components/ui/LoadingSpinner'

import './pages.css'

function statusTone(status) {
  if (status === 'completed') return 'success'
  if (status === 'submitted') return 'warning'
  return 'info'
}

function formatDate(value) {
  if (!value) return '—'
  return new Date(value).toLocaleString()
}

export default function SessionHistoryPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['sessions'],
    queryFn: fetchSessions,
  })

  if (isLoading) {
    return <LoadingSpinner fullScreen label="Loading session history…" />
  }

  return (
    <div className="history-page">
      <header className="page-header">
        <h1>Session History</h1>
        <p>All training sessions for your organization, newest first.</p>
      </header>

      {error && <div className="simulation-error">{error.message}</div>}

      <Card title={`${data?.length || 0} Sessions`} subtitle="Tenant-scoped investigation records">
        {!data?.length ? (
          <p className="history-empty">
            No sessions yet. <Link to="/simulation">Start your first simulation</Link>.
          </p>
        ) : (
          <div className="history-table-wrap">
            <table className="history-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Session</th>
                  <th>Difficulty</th>
                  <th>Status</th>
                  <th>Score</th>
                  <th>Created</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {data.map((session) => (
                  <tr key={session.id}>
                    <td>#{session.id}</td>
                    <td>{session.session_name}</td>
                    <td>
                      <Badge tone="info">{session.difficulty}</Badge>
                    </td>
                    <td>
                      <Badge tone={statusTone(session.status)}>{session.status}</Badge>
                    </td>
                    <td>{session.score != null ? `${session.score}/100` : '—'}</td>
                    <td>
                      <span className="history-date">
                        <Clock size={12} /> {formatDate(session.created_at)}
                      </span>
                    </td>
                    <td>
                      <Link to={`/history/${session.id}`} className="history-link">
                        View <ExternalLink size={12} />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  )
}
