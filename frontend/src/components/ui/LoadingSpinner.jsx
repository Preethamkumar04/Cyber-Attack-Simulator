/**
 * components/ui/LoadingSpinner.jsx
 *
 * Full-area or inline loading indicator for async simulation operations.
 */

import './ui.css'

export default function LoadingSpinner({ label = 'Loading…', fullScreen = false }) {
  return (
    <div className={`ui-spinner ${fullScreen ? 'ui-spinner--fullscreen' : ''}`}>
      <div className="ui-spinner__ring" />
      {label && <p className="ui-spinner__label">{label}</p>}
    </div>
  )
}
