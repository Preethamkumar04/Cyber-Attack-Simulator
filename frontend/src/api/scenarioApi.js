/**
 * api/scenarioApi.js
 *
 * Scenario lifecycle endpoints: start simulation, submit analyst response,
 * request AI-powered evaluation. Maps directly to FastAPI /scenario routes.
 */

import { apiClient } from './client'

export async function startScenario(difficulty) {
  const { data } = await apiClient.post('/scenario/start', { difficulty })
  return data
}

export async function submitAnalystResponse(payload) {
  const { data } = await apiClient.post('/scenario/submit-response', payload)
  return data
}

export async function evaluateSession(sessionId) {
  const { data } = await apiClient.post('/scenario/evaluate', {
    session_id: sessionId,
  })
  return data
}

export async function fetchHealth() {
  const { data } = await apiClient.get('/health')
  return data
}
