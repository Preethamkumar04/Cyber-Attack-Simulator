/**
 * components/simulation/ScenarioOverview.jsx
 *
 * Displays AI-generated scenario metadata (attack chain, mode, objectives)
 * without revealing the evaluation answer key to the trainee.
 */

import Badge from '../ui/Badge'
import Card from '../ui/Card'

import './simulation.css'

export default function ScenarioOverview({ session, scenario, simulation, research, difficultyAdaptation }) {
  if (!scenario) return null

  return (
    <Card
      className="scenario-panel"
      title={session?.name || 'Active Scenario'}
      subtitle={`Attack mode: ${scenario.attack_mode} · Engine: ${simulation?.engine || 'mock'}`}
      action={<Badge tone="info">{scenario.difficulty}</Badge>}
    >
      <div className="scenario-overview">
        <div className="scenario-overview__section">
          <h4>Attack Chain</h4>
          <ol className="attack-chain">
            {scenario.attack_chain?.map((step, index) => (
              <li key={step}>
                <span className="attack-chain__step">{index + 1}</span>
                {step}
              </li>
            ))}
          </ol>
        </div>

        <div className="scenario-overview__stats">
          <div className="stat-pill">
            <span className="stat-pill__value">{simulation?.timeline_events ?? '—'}</span>
            <span className="stat-pill__label">Events</span>
          </div>
          <div className="stat-pill">
            <span className="stat-pill__value">{simulation?.logs_generated ?? '—'}</span>
            <span className="stat-pill__label">Log Entries</span>
          </div>
          <div className="stat-pill">
            <span className="stat-pill__value">{simulation?.alerts_generated ?? '—'}</span>
            <span className="stat-pill__label">Alerts</span>
          </div>
          <div className="stat-pill">
            <span className="stat-pill__value">{simulation?.commands_generated ?? '—'}</span>
            <span className="stat-pill__label">Commands</span>
          </div>
        </div>

        <p className="scenario-overview__hint">
          Investigate the logs and terminal to uncover hidden objectives. Submit your
          analysis when ready.
        </p>
        {research && (
          <div className="scenario-overview__section">
            <h4>Research Validation</h4>
            <p className="scenario-overview__hint">
              Execution fidelity: <strong>{Math.round((research.execution_fidelity_score || 0) * 100)}%</strong>
              {' · '}Telemetry records: {research.telemetry_records?.length || 0}
              {' · '}Unexecutable steps are recorded as not executed, never as successful.
            </p>
          </div>
        )}
        {difficultyAdaptation?.mode === 'adaptive' && (
          <div className="scenario-overview__section">
            <h4>Adaptive Difficulty</h4>
            <p className="scenario-overview__hint">{difficultyAdaptation.reason}</p>
          </div>
        )}
      </div>
    </Card>
  )
}
