/**
 * components/ui/StepIndicator.jsx
 *
 * Visual progress tracker for the training workflow steps.
 */

import { Check } from 'lucide-react'

import './ui.css'

const STEPS = [
  { id: 'select', label: 'Select Difficulty' },
  { id: 'investigate', label: 'Investigate' },
  { id: 'respond', label: 'Submit Analysis' },
  { id: 'feedback', label: 'AI Feedback' },
]

export default function StepIndicator({ currentStep }) {
  const stepOrder = ['select', 'investigate', 'respond', 'feedback']
  const currentIndex = stepOrder.indexOf(currentStep)

  return (
    <nav className="step-indicator" aria-label="Training progress">
      {STEPS.map((step, index) => {
        const isComplete = index < currentIndex
        const isActive = index === currentIndex

        return (
          <div
            key={step.id}
            className={`step-indicator__item ${isActive ? 'step-indicator__item--active' : ''} ${isComplete ? 'step-indicator__item--complete' : ''}`}
          >
            <span className="step-indicator__dot">
              {isComplete ? <Check size={14} /> : index + 1}
            </span>
            <span className="step-indicator__label">{step.label}</span>
            {index < STEPS.length - 1 && <span className="step-indicator__line" />}
          </div>
        )
      })}
    </nav>
  )
}
