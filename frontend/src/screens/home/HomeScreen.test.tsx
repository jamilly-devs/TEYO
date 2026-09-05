import { screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { eventsApi } from '../../api/events'
import { tasksApi } from '../../api/tasks'
import { eventFixture, taskFixture } from '../../test-fixtures'
import { renderWithRouter } from '../../test-utils'
import { HomeScreen } from './HomeScreen'

vi.mock('../../api/tasks', () => ({ tasksApi: { list: vi.fn() } }))
vi.mock('../../api/events', () => ({ eventsApi: { list: vi.fn() } }))

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
  it('reserves the TEYO conversation block as disabled, not functional', () => {
    vi.mocked(tasksApi.list).mockReturnValue(new Promise(() => {}))
    vi.mocked(eventsApi.list).mockReturnValue(new Promise(() => {}))
    renderWithRouter(<HomeScreen />)

    expect(screen.getByText(/conversa com teyo/i)).toBeInTheDocument()
    expect(screen.getByPlaceholderText(/em breve/i)).toBeDisabled()
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
