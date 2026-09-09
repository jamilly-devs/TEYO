import { api } from './client'
import type { PomodoroSession } from './types'

// Pomodoro é uma experiência associada às tarefas — não tem menu próprio
// nem tool de LLM (DT-9). Estado active/paused/completed controlado pelo
// backend; persistido só em pomodoro_sessions.
export const pomodoroApi = {
  active: () => api.get<PomodoroSession | null>('/pomodoro/sessions/active'),
  start: (taskId?: number) =>
    api.post<PomodoroSession>('/pomodoro/sessions', { task_id: taskId }),
  pause: (id: number) => api.post<PomodoroSession>(`/pomodoro/sessions/${id}/pause`),
  resume: (id: number) => api.post<PomodoroSession>(`/pomodoro/sessions/${id}/resume`),
  complete: (id: number) =>
    api.post<PomodoroSession>(`/pomodoro/sessions/${id}/complete`),
}
