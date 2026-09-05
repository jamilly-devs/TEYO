import { fireEvent, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { ApiError } from '../../api/client'
import { conversationApi } from '../../api/conversation'
import { renderWithRouter } from '../../test-utils'
import { ConversationScreen } from './ConversationScreen'

vi.mock('../../api/conversation', () => ({
  conversationApi: { history: vi.fn(), send: vi.fn() },
}))

describe('ConversationScreen', () => {
  it('shows the loading state while fetching history', () => {
    vi.mocked(conversationApi.history).mockReturnValue(new Promise(() => {}))
    renderWithRouter(<ConversationScreen />)
    expect(screen.getByRole('status')).toHaveTextContent(/carregando conversa/i)
  })

  it('shows the error state when history fails to load', async () => {
    vi.mocked(conversationApi.history).mockRejectedValue(new ApiError(500, 'falha no servidor'))
    renderWithRouter(<ConversationScreen />)
    expect(await screen.findByRole('alert')).toHaveTextContent('falha no servidor')
  })

  it('renders existing history and lets the user send a new message', async () => {
    vi.mocked(conversationApi.history).mockResolvedValue([
      { id: 1, role: 'user', content: 'oi', created_at: '2026-01-01T00:00:00' },
      { id: 2, role: 'assistant', content: 'Oi! Tudo bem?', created_at: '2026-01-01T00:00:01' },
    ])
    vi.mocked(conversationApi.send).mockResolvedValue({
      id: 3,
      role: 'assistant',
      content: 'Show, e você?',
      created_at: '2026-01-01T00:01:00',
    })
    renderWithRouter(<ConversationScreen />)

    expect(await screen.findByText('Oi! Tudo bem?')).toBeInTheDocument()

    fireEvent.change(screen.getByPlaceholderText(/fala com o teyo/i), {
      target: { value: 'tudo certo' },
    })
    fireEvent.click(screen.getByRole('button', { name: /enviar/i }))

    expect(screen.getByText('tudo certo')).toBeInTheDocument()
    await waitFor(() => expect(conversationApi.send).toHaveBeenCalledWith('tudo certo'))
    expect(await screen.findByText('Show, e você?')).toBeInTheDocument()
  })

  it('never claims success when the LLM call fails, and keeps the sent message', async () => {
    vi.mocked(conversationApi.history).mockResolvedValue([])
    vi.mocked(conversationApi.send).mockRejectedValue(
      new ApiError(503, 'Não consegui falar com o TEYO agora. Tenta de novo em instantes.'),
    )
    renderWithRouter(<ConversationScreen />)

    await screen.findByPlaceholderText(/fala com o teyo/i)
    fireEvent.change(screen.getByPlaceholderText(/fala com o teyo/i), {
      target: { value: 'oi' },
    })
    fireEvent.click(screen.getByRole('button', { name: /enviar/i }))

    expect(await screen.findByRole('alert')).toHaveTextContent(/não consegui falar/i)
    expect(screen.getByText('oi')).toBeInTheDocument()
  })
})
