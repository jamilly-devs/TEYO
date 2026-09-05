import { api } from './client'
import type { Task } from './types'

export interface TaskCreatePayload {
  title: string
  description?: string
  due_date?: string
  priority?: Task['priority']
  category?: Task['category']
  goal_id?: number
  pomodoro_enabled?: boolean
}

export interface TaskUpdatePayload extends Partial<TaskCreatePayload> {
  status?: Task['status']
  is_recurring?: boolean
}

export const tasksApi = {
  list: () => api.get<Task[]>('/tasks'),
  create: (payload: TaskCreatePayload) => api.post<Task>('/tasks', payload),
  update: (id: number, payload: TaskUpdatePayload) => api.patch<Task>(`/tasks/${id}`, payload),
  remove: (id: number) => api.delete<void>(`/tasks/${id}`),
  complete: (id: number) => api.post<Task>(`/tasks/${id}/complete`),
}
