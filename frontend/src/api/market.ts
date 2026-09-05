import { api } from './client'
import type { MarketItem } from './types'

export interface MarketItemCreatePayload {
  name: string
  category?: string
}

export const marketApi = {
  list: () => api.get<MarketItem[]>('/market'),
  create: (payload: MarketItemCreatePayload) => api.post<MarketItem>('/market/items', payload),
  updateStatus: (id: number, status: MarketItem['status']) =>
    api.patch<MarketItem>(`/market/items/${id}`, { status }),
  remove: (id: number) => api.delete<void>(`/market/items/${id}`),
}
