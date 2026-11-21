/**
 * hooks/useSimulation.js
 *
 * Orchestrates the training workflow: start → investigate → submit → evaluate.
 * Encapsulates API calls and context updates for simulation pages.
 */

import { useCallback } from 'react'
import toast from 'react-hot-toast'
import { useQueryClient } from '@tanstack/react-query'

import { evaluateSession, submitAnalystResponse } from '../api/scenarioApi'
import { useSimulationContext } from '../context/SimulationContext'
import { startSimulation } from '../services/attackEngine'

export function useSimulation() {
  const { session, dispatch } = useSimulationContext()
  const queryClient = useQueryClient()

  const beginSimulation = useCallback(
    async (difficulty) => {
      dispatch({ type: 'STARTING' })
      try {
        const result = await startSimulation(difficulty)
        dispatch({
          type: 'STARTED',
          payload: {
            session: {
              id: result.session_id,
              name: result.session_name,
              difficulty: result.difficulty,
              status: result.status,
            },
            scenario: result.scenario,
            simulation: result.simulation,
            research: result.research,
            difficultyAdaptation: result.difficulty_adaptation,
          },
        })
        toast.success('Simulation started — investigate the artifacts')
        return result
      } catch (error) {
        dispatch({ type: 'ERROR', payload: error.message })
        toast.error(error.message)
        throw error
      }
    },
    [dispatch],
  )

  const submitResponse = useCallback(
    async (formData) => {
      if (!session?.id) {
        throw new Error('No active session')
      }

      const payload = {
        session_id: session.id,
        findings: formData.findings.filter(Boolean),
        commands: formData.commands.filter(Boolean),
        severity: formData.severity,
        root_cause: formData.root_cause,
        mitigation: formData.mitigation.filter(Boolean),
      }

      await submitAnalystResponse(payload)
      toast.success('Response submitted — generating AI feedback')
      return payload
    },
    [session],
  )

  const requestEvaluation = useCallback(async () => {
    if (!session?.id) {
      throw new Error('No active session')
    }

    const result = await evaluateSession(session.id)

    if (result.error) {
      throw new Error(result.error)
    }

    dispatch({ type: 'SET_EVALUATION', payload: result })
    queryClient.invalidateQueries({ queryKey: ['sessions'] })
    queryClient.invalidateQueries({ queryKey: ['analytics'] })
    return result
  }, [session, dispatch, queryClient])

  const resetSimulation = useCallback(() => {
    dispatch({ type: 'RESET' })
  }, [dispatch])

  return {
    beginSimulation,
    submitResponse,
    requestEvaluation,
    resetSimulation,
  }
}
