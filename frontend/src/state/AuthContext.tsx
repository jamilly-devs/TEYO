import { createContext, useContext, useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import { authApi } from '../api/auth'
import type { User } from '../api/types'

type AuthStatus = 'loading' | 'authenticated' | 'unauthenticated'

interface AuthContextValue {
  status: AuthStatus
  user: User | null
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, name?: string) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<AuthStatus>('loading')
  const [user, setUser] = useState<User | null>(null)

  useEffect(() => {
    authApi
      .me()
      .then((currentUser) => {
        setUser(currentUser)
        setStatus('authenticated')
      })
      .catch(() => {
        setStatus('unauthenticated')
      })
  }, [])

  async function login(email: string, password: string) {
    const currentUser = await authApi.login({ email, password })
    setUser(currentUser)
    setStatus('authenticated')
  }

  async function register(email: string, password: string, name?: string) {
    await authApi.register({ email, password, name })
  }

  async function logout() {
    await authApi.logout()
    setUser(null)
    setStatus('unauthenticated')
  }

  return (
    <AuthContext.Provider value={{ status, user, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
