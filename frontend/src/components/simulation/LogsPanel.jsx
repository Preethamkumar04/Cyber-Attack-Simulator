/**
 * components/simulation/LogsPanel.jsx
 *
 * Real-time log viewer using WebSocket streaming with HTTP fallback.
 */

import { useState } from 'react'
import { Radio, Search } from 'lucide-react'

import { LOG_TYPES } from '../../api/artifactApi'
import { useLogStream } from '../../hooks/useLogStream'
import Badge from '../ui/Badge'
import Card from '../ui/Card'
import LoadingSpinner from '../ui/LoadingSpinner'

import './simulation.css'

function highlightLine(line) {
  const lower = line.toLowerCase()
  if (lower.includes('critical') || lower.includes('privilege')) {
    return 'log-line--danger'
  }
  if (lower.includes('phishing') || lower.includes('suspicious')) {
    return 'log-line--warning'
  }
  if (lower.includes('lateral') || lower.includes('exfil')) {
    return 'log-line--info'
  }
  return ''
}

export default function LogsPanel({ sessionId, engine, enabled = true }) {
  const [activeTab, setActiveTab] = useState('simulation')
  const [filter, setFilter] = useState('')

  const { lines, lineCount, connected, error } = useLogStream(
    sessionId,
    activeTab,
    enabled,
  )

  const filteredLines = lines.filter((line) =>
    filter ? line.toLowerCase().includes(filter.toLowerCase()) : true,
  )

  return (
    <Card
      className="logs-panel"
      title="Security Logs"
      subtitle={`Real-time WebSocket stream from ${engine || 'active'} attack engine`}
      action={
        <div className="logs-panel__actions">
          <Badge tone={connected ? 'success' : 'warning'}>
            <Radio size={10} /> {connected ? 'Live' : 'Connecting…'}
          </Badge>
          <Badge tone="info">{lineCount} lines</Badge>
        </div>
      }
    >
      <div className="logs-panel__tabs">
        {LOG_TYPES.map((tab) => (
          <button
            key={tab.id}
            type="button"
            className={`logs-panel__tab ${activeTab === tab.id ? 'logs-panel__tab--active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="logs-panel__filter">
        <Search size={14} />
        <input
          type="text"
          placeholder="Filter log lines…"
          value={filter}
          onChange={(event) => setFilter(event.target.value)}
        />
      </div>

      {error && <p className="logs-panel__error">{error}</p>}

      <div className="logs-panel__viewer">
        {!connected && filteredLines.length === 0 ? (
          <LoadingSpinner label="Connecting to log stream…" />
        ) : filteredLines.length === 0 ? (
          <p className="logs-panel__empty">No log entries match your filter.</p>
        ) : (
          <pre className="logs-panel__content">
            {filteredLines.map((line, index) => (
              <code key={`${index}-${line.slice(0, 20)}`} className={highlightLine(line)}>
                {line}
                {'\n'}
              </code>
            ))}
          </pre>
        )}
      </div>
    </Card>
  )
}
