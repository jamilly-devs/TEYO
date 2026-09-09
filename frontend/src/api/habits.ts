import { api } from './client'
import type { Habit, HabitLog } from './types'

export interface HabitCreatePayload {
  title: string
  frequency_target: number
}

export type HabitUpdatePayload = Partial<HabitCreatePayload>

export const habitsApi = {
  list: () => api.get<Habit[]>('/habits'),
  create: (payload: HabitCreatePayload) => api.post<Habit>('/habits', payload),
  update: (id: number, payload: HabitUpdatePayload) =>
    api.patch<Habit>(`/habits/${id}`, payload),
  log: (id: number) => api.post<HabitLog>(`/habits/${id}/log`),
}
