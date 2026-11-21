/**
 * context/SimulationContext.jsx
 *
 * Global simulation session state shared across dashboard, workspace, and
 * results views. Avoids prop-drilling session_id, scenario metadata, and
 * evaluation results through the component tree.
 */

import { createContext, useContext, useMemo, useReducer } from 'react'

const SimulationContext = createContext(null)

const initialState = {
  step: 'select',
  session: null,
  scenario: null,
  simulation: null,
  research: null,
  difficultyAdaptation: null,
  evaluation: null,
  isStarting: false,
  error: null,
}

function simulationReducer(state, action) {
  switch (action.type) {
    case 'STARTING':
      return { ...state, isStarting: true, error: null }
    case 'STARTED':
      return {
        ...state,
        isStarting: false,
        step: 'investigate',
        session: action.payload.session,
        scenario: action.payload.scenario,
        simulation: action.payload.simulation,
        research: action.payload.research || null,
        difficultyAdaptation: action.payload.difficultyAdaptation || null,
        evaluation: null,
        error: null,
      }
    case 'SET_EVALUATION':
      return {
        ...state,
        step: 'feedback',
        evaluation: action.payload,
      }
    case 'RESET':
      return { ...initialState }
    case 'SET_STEP':
      return { ...state, step: action.payload }
    case 'ERROR':
      return { ...state, isStarting: false, error: action.payload }
    default:
      return state
  }
}

export function SimulationProvider({ children }) {
  const [state, dispatch] = useReducer(simulationReducer, initialState)

  const value = useMemo(
    () => ({
      ...state,
      dispatch,
    }),
    [state],
  )

  return (
    <SimulationContext.Provider value={value}>
      {children}
    </SimulationContext.Provider>
  )
}

export function useSimulationContext() {
  const context = useContext(SimulationContext)
  if (!context) {
    throw new Error('useSimulationContext must be used within SimulationProvider')
  }
  return context
}
