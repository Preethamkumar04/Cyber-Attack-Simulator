/**
 * api/analyticsApi.js — aggregated analytics for dashboard charts.
 */

import { apiClient } from './client'

export async function fetchAnalyticsOverview() {
  const { data } = await apiClient.get('/analytics/overview')
  return data
}
