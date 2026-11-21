/**
 * services/attackEngine/index.js
 *
 * Frontend attack-engine abstraction. The UI calls startSimulation() without
 * knowing whether the backend uses mock log generation or Docker containers.
 * Keeps SimulationPage decoupled from deployment-specific execution details.
 */

import { startScenario } from '../../api/scenarioApi'

export async function startSimulation(difficulty) {
  return startScenario(difficulty)
}

export function getEngineLabel(engineType) {
  const labels = {
    mock: 'Mock Engine (Development)',
    docker: 'Docker Engine (Production)',
  }
  return labels[engineType] || 'Unknown Engine'
}
