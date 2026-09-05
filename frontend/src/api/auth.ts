import { api } from './client'
import type { User } from './types'

export const authApi = {
  me: () => api.get<User>('/auth/me'),
  register: (payload: { email: string; password: string; name?: string }) =>
    api.post<User>('/auth/register', payload),
  login: (payload: { email: string; password: string }) =>
    api.post<User>('/auth/login', payload),
  logout: () => api.post<void>('/auth/logout'),
}
