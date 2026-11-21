/**
 * components/ui/Card.jsx
 *
 * Elevated panel container used throughout the dashboard and workspace.
 */

import './ui.css'

export default function Card({ title, subtitle, action, children, className = '' }) {
  return (
    <section className={`ui-card ${className}`.trim()}>
      {(title || action) && (
        <header className="ui-card__header">
          <div>
            {title && <h3 className="ui-card__title">{title}</h3>}
            {subtitle && <p className="ui-card__subtitle">{subtitle}</p>}
          </div>
          {action && <div className="ui-card__action">{action}</div>}
        </header>
      )}
      <div className="ui-card__body">{children}</div>
    </section>
  )
}
