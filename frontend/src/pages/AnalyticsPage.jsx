/**
 * pages/AnalyticsPage.jsx — recharts visualizations for tenant training metrics.
 */

import { useQuery } from '@tanstack/react-query'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import { fetchAnalyticsOverview } from '../api/analyticsApi'
import Card from '../components/ui/Card'
import LoadingSpinner from '../components/ui/LoadingSpinner'

import './pages.css'

const PIE_COLORS = ['#22d3ee', '#a78bfa', '#34d399', '#fbbf24', '#f87171']

export default function AnalyticsPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['analytics'],
    queryFn: fetchAnalyticsOverview,
  })

  if (isLoading) {
    return <LoadingSpinner fullScreen label="Loading analytics…" />
  }

  if (error) {
    return <div className="simulation-error">{error.message}</div>
  }

  return (
    <div className="analytics-page">
      <header className="page-header">
        <h1>Training Analytics</h1>
        <p>Performance metrics aggregated across your organization&apos;s sessions.</p>
      </header>

      <div className="analytics-stats grid-3">
        <Card title="Total Sessions" subtitle="All time">
          <p className="analytics-stat-value">{data.total_sessions}</p>
        </Card>
        <Card title="Completed" subtitle="Evaluated sessions">
          <p className="analytics-stat-value">{data.completed_sessions}</p>
        </Card>
        <Card title="Average Score" subtitle="Completed sessions">
          <p className="analytics-stat-value">{data.average_score}/100</p>
        </Card>
      </div>

      <div className="grid-2 analytics-charts">
        <Card title="Scores Over Time" subtitle="Recent completed sessions">
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={data.scores_over_time}>
                <CartesianGrid stroke="#1e293b" strokeDasharray="3 3" />
                <XAxis dataKey="label" stroke="#64748b" fontSize={11} />
                <YAxis domain={[0, 100]} stroke="#64748b" fontSize={11} />
                <Tooltip
                  contentStyle={{
                    background: '#111827',
                    border: '1px solid #1e293b',
                    borderRadius: 8,
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="score"
                  stroke="#22d3ee"
                  strokeWidth={2}
                  dot={{ fill: '#22d3ee' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card title="Average Score by Difficulty" subtitle="Completed sessions only">
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={data.scores_by_difficulty}>
                <CartesianGrid stroke="#1e293b" strokeDasharray="3 3" />
                <XAxis dataKey="difficulty" stroke="#64748b" fontSize={11} />
                <YAxis domain={[0, 100]} stroke="#64748b" fontSize={11} />
                <Tooltip
                  contentStyle={{
                    background: '#111827',
                    border: '1px solid #1e293b',
                    borderRadius: 8,
                  }}
                />
                <Bar dataKey="average_score" fill="#a78bfa" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card title="Difficulty Distribution" subtitle="All sessions">
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={data.difficulty_distribution}
                  dataKey="count"
                  nameKey="difficulty"
                  cx="50%"
                  cy="50%"
                  outerRadius={90}
                  label={({ difficulty, count }) => `${difficulty}: ${count}`}
                >
                  {data.difficulty_distribution.map((entry, index) => (
                    <Cell
                      key={entry.difficulty}
                      fill={PIE_COLORS[index % PIE_COLORS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    background: '#111827',
                    border: '1px solid #1e293b',
                    borderRadius: 8,
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card title="Attack Mode Distribution" subtitle="Scenario attack modes">
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={data.attack_mode_distribution}>
                <CartesianGrid stroke="#1e293b" strokeDasharray="3 3" />
                <XAxis dataKey="attack_mode" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip
                  contentStyle={{
                    background: '#111827',
                    border: '1px solid #1e293b',
                    borderRadius: 8,
                  }}
                />
                <Bar dataKey="count" fill="#34d399" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>
    </div>
  )
}
