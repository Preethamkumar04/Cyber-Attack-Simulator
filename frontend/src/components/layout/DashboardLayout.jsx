/**
 * components/layout/DashboardLayout.jsx
 *
 * Shell layout wrapping all pages: sidebar + header + content area.
 */

import { Outlet } from 'react-router-dom'

import Header from './Header'
import Sidebar from './Sidebar'

import './layout.css'

export default function DashboardLayout() {
  return (
    <div className="dashboard-shell">
      <Sidebar />
      <div className="dashboard-main">
        <Header />
        <main className="dashboard-content">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
