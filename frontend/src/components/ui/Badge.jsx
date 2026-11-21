/**
 * components/ui/Badge.jsx
 *
 * Status and severity chips for scenario metadata and evaluation results.
 */

import './ui.css'

const TONE_CLASS = {
  default: 'ui-badge--default',
  success: 'ui-badge--success',
  warning: 'ui-badge--warning',
  danger: 'ui-badge--danger',
  info: 'ui-badge--info',
}

export default function Badge({ children, tone = 'default' }) {
  return (
    <span className={`ui-badge ${TONE_CLASS[tone] || TONE_CLASS.default}`}>
      {children}
    </span>
  )
}
