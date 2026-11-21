/**
 * components/simulation/DifficultySelector.jsx
 *
 * Step 1 of the workflow — trainee selects attack difficulty before
 * the backend generates an AI scenario and runs mock simulation.
 */

import { useState } from 'react'
import { Shield, Zap, Skull, BrainCircuit } from 'lucide-react'

import Button from '../ui/Button'
import Card from '../ui/Card'

import './simulation.css'

const DIFFICULTIES = [
  {
    id: 'beginner',
    label: 'Beginner',
    icon: Shield,
    tone: 'success',
    description:
      'Single-vector attacks with obvious log indicators. Ideal for learning basic triage.',
    features: ['Clear log signatures', 'Limited attack chain', 'Guided investigation'],
  },
  {
    id: 'adaptive',
    label: 'Adaptive',
    icon: BrainCircuit,
    tone: 'info',
    description: 'Uses your completed-session skill profile to select the next safe scenario complexity.',
    features: ['Keeps manual modes available', 'Stores the decision reason', 'Adjusts future complexity'],
  },
  {
    id: 'intermediate',
    label: 'Intermediate',
    icon: Zap,
    tone: 'warning',
    description:
      'Multi-stage attacks requiring correlation across log sources and command history.',
    features: ['Multi-stage kill chain', 'Mixed log noise', 'Command correlation'],
  },
  {
    id: 'advanced',
    label: 'Advanced',
    icon: Skull,
    tone: 'danger',
    description:
      'Complex hybrid attacks with subtle indicators and lateral movement patterns.',
    features: ['Hybrid attack modes', 'Lateral movement', 'Stealth indicators'],
  },
]

export default function DifficultySelector({ onStart, loading }) {
  const [selected, setSelected] = useState('intermediate')

  return (
    <div className="difficulty-selector">
      <div className="difficulty-selector__grid">
        {DIFFICULTIES.map((level) => {
          const Icon = level.icon
          const isSelected = selected === level.id

          return (
            <button
              key={level.id}
              type="button"
              className={`difficulty-card ${isSelected ? 'difficulty-card--selected' : ''} difficulty-card--${level.tone}`}
              onClick={() => setSelected(level.id)}
            >
              <Icon size={32} className="difficulty-card__icon" />
              <h3>{level.label}</h3>
              <p>{level.description}</p>
              <ul>
                {level.features.map((feature) => (
                  <li key={feature}>{feature}</li>
                ))}
              </ul>
            </button>
          )
        })}
      </div>

      <Card
        title="Ready to begin?"
        subtitle="The AI engine will generate a unique scenario and populate investigation artifacts."
      >
        <div className="difficulty-selector__actions">
          <p>
            Selected: <strong>{selected}</strong> — mock attack engine will generate
            logs, network alerts, traffic records, and attacker command history.
          </p>
          <Button loading={loading} onClick={() => onStart(selected)}>
            Start Simulation
          </Button>
        </div>
      </Card>
    </div>
  )
}
