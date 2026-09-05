import { fireEvent, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { ApiError } from '../../api/client'
import { conversationApi } from '../../api/conversation'
import { eventsApi } from '../../api/events'
import { tasksApi } from '../../api/tasks'
import { eventFixture, taskFixture } from '../../test-fixtures'
import { renderWithRouter } from '../../test-utils'
import { HomeScreen } from './HomeScreen'

vi.mock('../../api/tasks', () => ({ tasksApi: { list: vi.fn() } }))
vi.mock('../../api/events', () => ({ eventsApi: { list: vi.fn() } }))
vi.mock('../../api/conversation', () => ({ conversationApi: { send: vi.fn() } }))

// Mirrors HomeScreen's own local-date computation (not UTC) so the fixture
// always falls on "today" regardless of the machine's timezone offset.
function localTodayDateString(): string {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

describe('HomeScreen', () => {
  it('sends a message from the Home box using the same main conversation', async () => {
    vi.mocked(tasksApi.list).mockReturnValue(new Promise(() => {}))
    vi.mocked(eventsApi.list).mockReturnValue(new Promise(() => {}))
    vi.mocked(conversationApi.send).mockResolvedValue({
      id: 1,
      role: 'assistant',
      content: 'Oi!',
      created_at: '2026-01-01T00:00:00',
    })
    renderWithRouter(<HomeScreen />)

    expect(screen.getByText(/conversa com teyo/i)).toBeInTheDocument()
    fireEvent.change(screen.getByPlaceholderText(/fala com o teyo/i), {
      target: { value: 'oi teyo' },
    })
    fireEvent.click(screen.getByRole('button', { name: /enviar/i }))

    await waitFor(() => expect(conversationApi.send).toHaveBeenCalledWith('oi teyo'))
  })

  it('shows an error instead of pretending the message was sent', async () => {
    vi.mocked(tasksApi.list).mockReturnValue(new Promise(() => {}))
    vi.mocked(eventsApi.list).mockReturnValue(new Promise(() => {}))
    vi.mocked(conversationApi.send).mockRejectedValue(new ApiError(503, 'TEYO indisponível'))
    renderWithRouter(<HomeScreen />)

    fireEvent.change(screen.getByPlaceholderText(/fala com o teyo/i), {
      target: { value: 'oi' },
    })
    fireEvent.click(screen.getByRole('button', { name: /enviar/i }))

    expect(await screen.findByRole('alert')).toHaveTextContent('TEYO indisponível')
  })

  it('keeps the progress block empty until real data exists', () => {
    vi.mocked(tasksApi.list).mockReturnValue(new Promise(() => {}))
    vi.mocked(eventsApi.list).mockReturnValue(new Promise(() => {}))
    renderWithRouter(<HomeScreen />)

    expect(screen.getByText(/ainda não há dados de progresso/i)).toBeInTheDocument()
  })

  it('shows an empty daily plan when nothing is due today', async () => {
    vi.mocked(tasksApi.list).mockResolvedValue([taskFixture])
    vi.mocked(eventsApi.list).mockResolvedValue([])
    renderWithRouter(<HomeScreen />)

    expect(await screen.findByText(/nada agendado para hoje/i)).toBeInTheDocument()
  })

  it('lists a task due today in the daily plan block', async () => {
    const today = localTodayDateString()
    vi.mocked(tasksApi.list).mockResolvedValue([
      { ...taskFixture, due_date: `${today}T10:00:00` },
    ])
    vi.mocked(eventsApi.list).mockResolvedValue([])
    renderWithRouter(<HomeScreen />)

    expect(await screen.findByText(/tarefa: lavar louça/i)).toBeInTheDocument()
  })

  it('shows an agenda preview of upcoming events', async () => {
    vi.mocked(tasksApi.list).mockResolvedValue([])
    vi.mocked(eventsApi.list).mockResolvedValue([eventFixture])
    renderWithRouter(<HomeScreen />)

    expect(await screen.findByText(/reunião/i)).toBeInTheDocument()
  })
})
