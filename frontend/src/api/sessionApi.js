/**
 * api/sessionApi.js — tenant-scoped session history endpoints.
 */

import { apiClient } from './client'

export async function fetchSessions() {
  const { data } = await apiClient.get('/sessions/')
  return data
}

export async function fetchSessionDetail(sessionId) {
  const { data } = await apiClient.get(`/sessions/${sessionId}`)
  return data
}
