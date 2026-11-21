/**
 * components/simulation/FeedbackPanel.jsx
 *
 * Displays Ollama-generated narrative feedback and score summary after evaluation.
 */

import { Bot, RotateCcw } from 'lucide-react'

import Badge from '../ui/Badge'
import Button from '../ui/Button'
import Card from '../ui/Card'
import ScoreBreakdown from './ScoreBreakdown'

import './simulation.css'

function scoreTone(score) {
  if (score >= 80) return 'success'
  if (score >= 60) return 'warning'
  return 'danger'
}

export default function FeedbackPanel({ evaluation, onRestart, showRestart = true }) {
  if (!evaluation) return null

  return (
    <div className="feedback-panel">
      <Card
        title="AI Mentor Feedback"
        subtitle="Powered by Ollama semantic evaluation"
        action={
          <Badge tone={scoreTone(evaluation.score)}>
            Score: {evaluation.score}/100
          </Badge>
        }
      >
        <div className="feedback-panel__content">
          <Bot size={24} className="feedback-panel__icon" />
          <div className="feedback-panel__text">
            {evaluation.feedback ? (
              evaluation.feedback.split('\n').map((paragraph, index) =>
                paragraph.trim() ? (
                  <p key={index}>{paragraph.trim()}</p>
                ) : null,
              )
            ) : (
              <p>
                Evaluation complete. Review the score breakdown for detailed results
                on matched and missed investigation items.
              </p>
            )}
          </div>
        </div>
      </Card>

      <ScoreBreakdown evaluation={evaluation} />

      {showRestart && onRestart && (
        <div className="feedback-panel__actions">
          <Button variant="secondary" onClick={onRestart}>
            <RotateCcw size={16} /> Start New Simulation
          </Button>
        </div>
      )}
    </div>
  )
}
