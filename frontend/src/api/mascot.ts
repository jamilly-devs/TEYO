import { api } from './client'
import type { MascotState } from './types'

export const mascotApi = {
  state: () => api.get<MascotState>('/mascot/state'),
  // Única personalização visual permitida (BUSINESS_RULES.md #10).
  setColor: (color: string) => api.patch<MascotState>('/mascot/color', { color }),
}
