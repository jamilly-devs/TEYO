import { api } from './client'
import type { FinancialRecord } from './types'

export interface FinancialRecordCreatePayload {
  type: FinancialRecord['type']
  amount: string
  date: string
  category?: string
  description?: string
}

export const financeApi = {
  list: () => api.get<FinancialRecord[]>('/finance/records'),
  create: (payload: FinancialRecordCreatePayload) =>
    api.post<FinancialRecord>('/finance/records', payload),
}
