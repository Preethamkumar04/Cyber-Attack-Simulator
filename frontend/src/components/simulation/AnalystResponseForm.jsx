/**
 * components/simulation/AnalystResponseForm.jsx
 *
 * Step 3 — trainee submits findings, commands used, severity assessment,
 * root cause, and mitigation steps for AI evaluation.
 */

import { useFieldArray, useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Plus, Trash2 } from 'lucide-react'

import Button from '../ui/Button'
import Card from '../ui/Card'

import './simulation.css'

const schema = z.object({
  findings: z.array(z.string()).min(1, 'Add at least one finding'),
  commands: z.array(z.string()).min(1, 'Add at least one command'),
  severity: z.enum(['Low', 'Medium', 'High', 'Critical']),
  root_cause: z.string().min(10, 'Describe the root cause (min 10 chars)'),
  mitigation: z.array(z.string()).min(1, 'Add at least one mitigation step'),
})

const defaultValues = {
  findings: [''],
  commands: [''],
  severity: 'Medium',
  root_cause: '',
  mitigation: [''],
}

export default function AnalystResponseForm({ onSubmit, loading }) {
  const {
    register,
    control,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(schema),
    defaultValues,
  })

  const findingsArray = useFieldArray({ control, name: 'findings' })
  const commandsArray = useFieldArray({ control, name: 'commands' })
  const mitigationArray = useFieldArray({ control, name: 'mitigation' })

  return (
    <Card
      title="Submit Investigation Report"
      subtitle="Document your analysis for AI-powered evaluation"
    >
      <form className="analyst-form" onSubmit={handleSubmit(onSubmit)}>
        <fieldset className="analyst-form__section">
          <legend>Key Findings</legend>
          {findingsArray.fields.map((field, index) => (
            <div key={field.id} className="analyst-form__row">
              <input
                {...register(`findings.${index}`)}
                placeholder="e.g. Phishing email led to credential compromise"
              />
              {findingsArray.fields.length > 1 && (
                <button
                  type="button"
                  className="icon-btn icon-btn--danger"
                  onClick={() => findingsArray.remove(index)}
                >
                  <Trash2 size={14} />
                </button>
              )}
            </div>
          ))}
          <Button
            type="button"
            variant="ghost"
            onClick={() => findingsArray.append('')}
          >
            <Plus size={14} /> Add Finding
          </Button>
          {errors.findings && (
            <span className="analyst-form__error">{errors.findings.message}</span>
          )}
        </fieldset>

        <fieldset className="analyst-form__section">
          <legend>Commands Used</legend>
          {commandsArray.fields.map((field, index) => (
            <div key={field.id} className="analyst-form__row">
              <input
                {...register(`commands.${index}`)}
                placeholder="e.g. grep phishing simulation.log"
                className="mono"
              />
              {commandsArray.fields.length > 1 && (
                <button
                  type="button"
                  className="icon-btn icon-btn--danger"
                  onClick={() => commandsArray.remove(index)}
                >
                  <Trash2 size={14} />
                </button>
              )}
            </div>
          ))}
          <Button
            type="button"
            variant="ghost"
            onClick={() => commandsArray.append('')}
          >
            <Plus size={14} /> Add Command
          </Button>
        </fieldset>

        <fieldset className="analyst-form__section">
          <legend>Severity Assessment</legend>
          <select {...register('severity')}>
            <option value="Low">Low</option>
            <option value="Medium">Medium</option>
            <option value="High">High</option>
            <option value="Critical">Critical</option>
          </select>
        </fieldset>

        <fieldset className="analyst-form__section">
          <legend>Root Cause</legend>
          <textarea
            {...register('root_cause')}
            rows={3}
            placeholder="Describe the primary cause of the incident…"
          />
          {errors.root_cause && (
            <span className="analyst-form__error">{errors.root_cause.message}</span>
          )}
        </fieldset>

        <fieldset className="analyst-form__section">
          <legend>Mitigation Steps</legend>
          {mitigationArray.fields.map((field, index) => (
            <div key={field.id} className="analyst-form__row">
              <input
                {...register(`mitigation.${index}`)}
                placeholder="e.g. Block malicious domain at firewall"
              />
              {mitigationArray.fields.length > 1 && (
                <button
                  type="button"
                  className="icon-btn icon-btn--danger"
                  onClick={() => mitigationArray.remove(index)}
                >
                  <Trash2 size={14} />
                </button>
              )}
            </div>
          ))}
          <Button
            type="button"
            variant="ghost"
            onClick={() => mitigationArray.append('')}
          >
            <Plus size={14} /> Add Mitigation
          </Button>
        </fieldset>

        <div className="analyst-form__submit">
          <Button type="submit" loading={loading}>
            Submit &amp; Get AI Feedback
          </Button>
        </div>
      </form>
    </Card>
  )
}
