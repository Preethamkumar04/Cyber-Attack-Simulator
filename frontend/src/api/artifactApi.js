/**
 * api/artifactApi.js
 *
 * Read-only access to generated simulation artifacts (logs, alerts, traffic).
 * Powers the live logs panel in the training workspace.
 */

import { apiClient } from './client'

export async function fetchLogContent(sessionId, logType) {
  const { data } = await apiClient.get(`/artifacts/logs/${sessionId}/${logType}`)
  return data
}

export async function fetchArtifactStatus(sessionId) {
  const { data } = await apiClient.get(`/artifacts/status/${sessionId}`)
  return data
}

export const LOG_TYPES = [
  { id: 'simulation', label: 'System Logs', icon: 'server' },
  { id: 'network', label: 'Network Alerts', icon: 'shield-alert' },
  { id: 'traffic', label: 'Traffic', icon: 'activity' },
  { id: 'commands', label: 'Command History', icon: 'terminal' },
]
