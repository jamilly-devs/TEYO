import { api } from './client'
import type { Event } from './types'

export interface EventCreatePayload {
  title: string
  start_at: string
  end_at: string
}

export const eventsApi = {
  list: () => api.get<Event[]>('/events'),
  create: (payload: EventCreatePayload) => api.post<Event>('/events', payload),
  update: (id: number, payload: Partial<EventCreatePayload>) =>
    api.patch<Event>(`/events/${id}`, payload),
  remove: (id: number) => api.delete<void>(`/events/${id}`),
}
