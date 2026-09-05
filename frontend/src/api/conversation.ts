import { api } from './client'
import type { ConversationMessage } from './types'

export const conversationApi = {
  history: () => api.get<ConversationMessage[]>('/conversation/history'),
  send: (content: string) =>
    api.post<ConversationMessage>('/conversation/message', { content }),
}
