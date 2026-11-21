/**
 * api/terminalApi.js
 *
 * Interactive terminal command execution. Delegates to backend MockTerminalService
 * today; the same contract will work when Docker exec replaces the mock backend.
 */

import { apiClient } from './client'

export async function executeTerminalCommand(command, sessionId = null) {
  const { data } = await apiClient.post('/terminal/execute', {
    command,
    session_id: sessionId,
  })
  return data
}

export async function fetchTerminalPrompt() {
  const { data } = await apiClient.get('/terminal/prompt')
  return data
}
