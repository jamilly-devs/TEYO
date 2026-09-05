import { api } from './client'
import type { Goal } from './types'

export interface GoalCreatePayload {
  title: string
  description?: string
  target_date?: string
}

export interface GoalUpdatePayload extends Partial<GoalCreatePayload> {
  status?: Goal['status']
}

export const goalsApi = {
  list: () => api.get<Goal[]>('/goals'),
  create: (payload: GoalCreatePayload) => api.post<Goal>('/goals', payload),
  update: (id: number, payload: GoalUpdatePayload) => api.patch<Goal>(`/goals/${id}`, payload),
}
