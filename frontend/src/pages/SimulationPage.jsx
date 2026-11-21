/**
 * pages/SimulationPage.jsx
 *
 * Main training lab orchestrating the full workflow:
 * difficulty → investigate (logs + terminal) → submit → feedback.
 */

import { useState } from 'react'

import AnalystResponseForm from '../components/simulation/AnalystResponseForm'
import DifficultySelector from '../components/simulation/DifficultySelector'
import FeedbackPanel from '../components/simulation/FeedbackPanel'
import LogsPanel from '../components/simulation/LogsPanel'
import ScenarioOverview from '../components/simulation/ScenarioOverview'
import TerminalPanel from '../components/simulation/TerminalPanel'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import StepIndicator from '../components/ui/StepIndicator'
import { useSimulationContext } from '../context/SimulationContext'
import { useSimulation } from '../hooks/useSimulation'

import './pages.css'

function getCurrentStep(state) {
  if (state.step === 'feedback' || state.evaluation) return 'feedback'
  if (state.step === 'investigate') return 'investigate'
  return 'select'
}

export default function SimulationPage() {
  const context = useSimulationContext()
  const { beginSimulation, submitResponse, requestEvaluation, resetSimulation } =
    useSimulation()
  const [submitting, setSubmitting] = useState(false)

  const currentStep = getCurrentStep(context)
  const showInvestigate = context.session && currentStep !== 'feedback'

  const handleStart = async (difficulty) => {
    await beginSimulation(difficulty)
  }

  const handleSubmit = async (formData) => {
    setSubmitting(true)
    try {
      await submitResponse(formData)
      await requestEvaluation()
    } finally {
      setSubmitting(false)
    }
  }

  const handleRestart = () => {
    resetSimulation()
  }

  if (context.isStarting) {
    return (
      <LoadingSpinner
        fullScreen
        label="Generating AI scenario and preparing the training environment…"
      />
    )
  }

  return (
    <div className="simulation-page">
      <header className="page-header">
        <h1>Training Lab</h1>
        <p>
          Complete the investigation workflow — from difficulty selection through
          AI-powered evaluation.
        </p>
      </header>

      <StepIndicator
        currentStep={
          currentStep === 'investigate' && !context.evaluation
            ? 'investigate'
            : currentStep
        }
      />

      {context.error && (
        <div className="simulation-error" role="alert">
          {context.error}
        </div>
      )}

      {currentStep === 'select' && (
        <DifficultySelector onStart={handleStart} loading={context.isStarting} />
      )}

      {showInvestigate && (
        <>
          <div className="workspace-grid">
            <ScenarioOverview
              session={context.session}
              scenario={context.scenario}
              simulation={context.simulation}
              research={context.research}
              difficultyAdaptation={context.difficultyAdaptation}
            />
            <LogsPanel
              sessionId={context.session.id}
              engine={context.simulation?.engine}
              enabled={Boolean(context.session.id)}
            />
            <TerminalPanel engine={context.simulation?.engine} />
          </div>

          <div className="simulation-workspace__respond">
            <AnalystResponseForm onSubmit={handleSubmit} loading={submitting} />
          </div>
        </>
      )}

      {currentStep === 'feedback' && context.evaluation && (
        <FeedbackPanel evaluation={context.evaluation} onRestart={handleRestart} />
      )}
    </div>
  )
}
