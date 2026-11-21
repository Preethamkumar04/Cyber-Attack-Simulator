/**
 * context/AuthContext.jsx — JWT auth state and multi-tenant user profile.
 */

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'

import { fetchCurrentUser, login as loginApi, register as registerApi } from '../api/authApi'
import { clearStoredToken, getStoredToken, setStoredToken } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  const loadUser = useCallback(async () => {
    const token = getStoredToken()
    if (!token) {
      setUser(null)
      setLoading(false)
      return
    }

    try {
      const profile = await fetchCurrentUser()
      setUser(profile)
    } catch {
      clearStoredToken()
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadUser()
  }, [loadUser])

  const login = useCallback(async (username, password) => {
    const { access_token: token } = await loginApi(username, password)
    setStoredToken(token)
    const profile = await fetchCurrentUser()
    setUser(profile)
    return profile
  }, [])

  const register = useCallback(async (payload) => {
    await registerApi(payload)
    return login(payload.username, payload.password)
  }, [login])

  const logout = useCallback(() => {
    clearStoredToken()
    setUser(null)
  }, [])

  const value = useMemo(
    () => ({
      user,
      loading,
      isAuthenticated: Boolean(user),
      login,
      register,
      logout,
      reloadUser: loadUser,
    }),
    [user, loading, login, register, logout, loadUser],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
