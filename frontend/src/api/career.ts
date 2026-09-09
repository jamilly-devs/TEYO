import { api } from './client'
import type { JobApplication } from './types'

export interface JobApplicationCreatePayload {
  company: string
  role: string
  applied_on?: string
  notes?: string
}

export interface JobApplicationUpdatePayload
  extends Partial<JobApplicationCreatePayload> {
  status?: JobApplication['status']
}

// Acompanhamento manual de candidaturas (MODULES/CAREER.md). Sem busca de
// vagas.
export const careerApi = {
  list: () => api.get<JobApplication[]>('/career/applications'),
  create: (payload: JobApplicationCreatePayload) =>
    api.post<JobApplication>('/career/applications', payload),
  update: (id: number, payload: JobApplicationUpdatePayload) =>
    api.patch<JobApplication>(`/career/applications/${id}`, payload),
}
