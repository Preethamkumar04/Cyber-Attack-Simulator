/**
 * components/simulation/ScoreBreakdown.jsx
 *
 * Visual breakdown of evaluation scores by category (findings, commands, etc.).
 */

import Card from '../ui/Card'

import './simulation.css'

const CATEGORIES = [
  { key: 'findings_score', label: 'Findings', max: 35, color: '#22d3ee' },
  { key: 'commands_score', label: 'Commands', max: 25, color: '#a78bfa' },
  { key: 'severity_score', label: 'Severity', max: 15, color: '#fbbf24' },
  { key: 'root_cause_score', label: 'Root Cause', max: 15, color: '#34d399' },
  { key: 'mitigation_score', label: 'Mitigation', max: 10, color: '#f87171' },
]

export default function ScoreBreakdown({ evaluation }) {
  if (!evaluation) return null

  return (
    <Card title="Score Breakdown" subtitle={`Total: ${evaluation.score}/100`}>
      <div className="score-breakdown">
        {CATEGORIES.map(({ key, label, max, color }) => {
          const value = evaluation[key] ?? 0
          const pct = Math.round((value / max) * 100)

          return (
            <div key={key} className="score-bar">
              <div className="score-bar__header">
                <span>{label}</span>
                <span>
                  {value}/{max}
                </span>
              </div>
              <div className="score-bar__track">
                <div
                  className="score-bar__fill"
                  style={{ width: `${pct}%`, background: color }}
                />
              </div>
            </div>
          )
        })}
      </div>

      <div className="score-lists">
        {evaluation.missed_findings?.length > 0 && (
          <div className="score-list score-list--missed">
            <h4>Missed Findings</h4>
            <ul>
              {evaluation.missed_findings.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
        )}
        {evaluation.missed_commands?.length > 0 && (
          <div className="score-list score-list--missed">
            <h4>Missed Commands</h4>
            <ul>
              {evaluation.missed_commands.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
        )}
        {evaluation.matched_findings?.length > 0 && (
          <div className="score-list score-list--matched">
            <h4>Matched Findings</h4>
            <ul>
              {evaluation.matched_findings.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </Card>
  )
}
