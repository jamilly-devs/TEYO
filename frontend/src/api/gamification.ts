import { api } from './client'
import type { GamificationState } from './types'

export const gamificationApi = {
  state: () => api.get<GamificationState>('/gamification/state'),
}
