/**
 * api/authApi.js — registration, login, and profile endpoints.
 */

import { apiClient } from './client'

export async function register(payload) {
  const { data } = await apiClient.post('/auth/register', payload)
  return data
}

export async function login(username, password) {
  const form = new URLSearchParams()
  form.append('username', username)
  form.append('password', password)

  const { data } = await apiClient.post('/auth/login', form, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
  return data
}

export async function fetchCurrentUser() {
  const { data } = await apiClient.get('/auth/me')
  return data
}
