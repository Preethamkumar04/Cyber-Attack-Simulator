/**
 * hooks/useLogs.js
 *
 * React Query hook for polling artifact logs during an active investigation.
 * Refreshes on an interval so the logs panel stays current without manual reload.
 */

import { useQuery } from '@tanstack/react-query'

import { fetchLogContent } from '../api/artifactApi'

export function useLogs(logType, enabled = true) {
  return useQuery({
    queryKey: ['logs', logType],
    queryFn: () => fetchLogContent(logType),
    enabled,
    refetchInterval: enabled ? 5000 : false,
    staleTime: 2000,
  })
}
