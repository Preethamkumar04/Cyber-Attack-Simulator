/**
 * api/client.js
 *
 * Shared Axios instance for all backend communication.
 * Attaches JWT from localStorage when present.
 */

import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || '/api'
const TOKEN_KEY = 'cybersim_token'

export const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 120000,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem(TOKEN_KEY)
      if (!window.location.pathname.startsWith('/login')) {
        window.location.href = '/login'
      }
    }

    const message =
      error.response?.data?.detail ||
      error.response?.data?.error ||
      error.message ||
      'Request failed'
    return Promise.reject(new Error(message))
  },
)

export function getStoredToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function setStoredToken(token) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearStoredToken() {
  localStorage.removeItem(TOKEN_KEY)
}

export function getWebSocketUrl(path) {
  const token = getStoredToken()
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const host = window.location.host
  const base = import.meta.env.VITE_API_URL

  if (base && base.startsWith('http')) {
    const url = new URL(base)
    const wsProtocol = url.protocol === 'https:' ? 'wss:' : 'ws:'
    return `${wsProtocol}//${url.host}${path}${token ? `?token=${token}` : ''}`
  }

  return `${protocol}//${host}/api${path}${token ? `?token=${token}` : ''}`
}

