import { apiClient } from './client'

export async function fetchSessionResearch(sessionId) {
  const { data } = await apiClient.get(`/sessions/${sessionId}/research`)
  return data
}

export async function fetchMySkillProfile() {
  const { data } = await apiClient.get('/sessions/skills/me')
  return data
}
