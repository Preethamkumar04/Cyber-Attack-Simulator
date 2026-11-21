/**
 * components/ui/Button.jsx
 *
 * Reusable button with variant styles for the cybersecurity dashboard.
 */

import './ui.css'

const VARIANT_CLASS = {
  primary: 'ui-btn--primary',
  secondary: 'ui-btn--secondary',
  danger: 'ui-btn--danger',
  ghost: 'ui-btn--ghost',
}

export default function Button({
  children,
  variant = 'primary',
  className = '',
  loading = false,
  disabled = false,
  ...props
}) {
  return (
    <button
      type="button"
      className={`ui-btn ${VARIANT_CLASS[variant] || ''} ${className}`.trim()}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? 'Processing…' : children}
    </button>
  )
}
