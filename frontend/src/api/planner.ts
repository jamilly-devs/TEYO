import { api } from './client'
import type { DailyPlan } from './types'

export const plannerApi = {
  // Plano do dia já ordenado pelo sistema (PLANNER.md, FASE 8). A Home
  // consome este endpoint diretamente — sem refiltrar tasks/events no
  // cliente (pendência da FASE 8 resolvida na FASE 9).
  dailyPlan: () => api.get<DailyPlan>('/planner/daily-plan'),
}
