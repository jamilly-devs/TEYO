import { fireEvent, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { ApiError } from '../../api/client'
import { conversationApi } from '../../api/conversation'
import { eventsApi } from '../../api/events'
import { gamificationApi } from '../../api/gamification'
import { mascotApi } from '../../api/mascot'
import { plannerApi } from '../../api/planner'
import { eventFixture } from '../../test-fixtures'
import { renderWithRouter } from '../../test-utils'
import { HomeScreen } from './HomeScreen'

vi.mock('../../api/planner', () => ({ plannerApi: { dailyPlan: vi.fn() } }))
vi.mock('../../api/events', () => ({ eventsApi: { list: vi.fn() } }))
vi.mock('../../api/gamification', () => ({ gamificationApi: { state: vi.fn() } }))
vi.mock('../../api/mascot', () => ({ mascotApi: { state: vi.fn(), setColor: vi.fn() } }))
vi.mock('../../api/conversation', () => ({ conversationApi: { send: vi.fn() } }))

const EMPTY_PLAN = { date: '2026-01-01', items: [] }
const GAMIFICATION = {
  xp_total: 30,
  level: 1,
  xp_into_level: 30,
  xp_for_next_level: 100,
  streak_days: 2,
  achievements: [],
}
const MASCOT = {
  evolution_stage: 1,
  current_expression: 'happy' as const,
  color: '#7c5cff',
  unlocked_features: [],
  updated_at: null,
}

function primeDefaults() {
  vi.mocked(plannerApi.dailyPlan).mockResolvedValue(EMPTY_PLAN)
  vi.mocked(eventsApi.list).mockResolvedValue([])
  vi.mocked(gamificationApi.state).mockResolvedValue(GAMIFICATION)
  vi.mocked(mascotApi.state).mockResolvedValue(MASCOT)
}

beforeEach(() => {
  vi.clearAllMocks()
})

describe('HomeScreen', () => {
  it('sends a message from the Home box using the same main conversation', async () => {
    primeDefaults()
    vi.mocked(conversationApi.send).mockResolvedValue({
      id: 1,
      role: 'assistant',
      content: 'Oi!',
      created_at: '2026-01-01T00:00:00',
    })
    renderWithRouter(<HomeScreen />)

    fireEvent.change(screen.getByPlaceholderText(/fala com o teyo/i), {
      target: { value: 'oi teyo' },
    })
    fireEvent.click(screen.getByRole('button', { name: /enviar/i }))

    await waitFor(() => expect(conversationApi.send).toHaveBeenCalledWith('oi teyo'))
  })

  it('shows an error instead of pretending the message was sent', async () => {
    primeDefaults()
    vi.mocked(conversationApi.send).mockRejectedValue(new ApiError(503, 'TEYO indisponível'))
    renderWithRouter(<HomeScreen />)

    fireEvent.change(screen.getByPlaceholderText(/fala com o teyo/i), {
      target: { value: 'oi' },
    })
    fireEvent.click(screen.getByRole('button', { name: /enviar/i }))

    expect(await screen.findByRole('alert')).toHaveTextContent('TEYO indisponível')
  })

  it('shows level, XP and streak from the system in the progress block', async () => {
    primeDefaults()
    renderWithRouter(<HomeScreen />)

    expect(await screen.findByText(/nível 1/i)).toBeInTheDocument()
    expect(screen.getByText(/30 \/ 100 XP/i)).toBeInTheDocument()
    expect(screen.getByText(/2 dias seguidos/i)).toBeInTheDocument()
  })

  it('renders the mascot in the progress block', async () => {
    primeDefaults()
    renderWithRouter(<HomeScreen />)

    expect(await screen.findByRole('img', { name: /mascote teyo/i })).toBeInTheDocument()
  })

  it('lets the user change only the mascot color', async () => {
    primeDefaults()
    vi.mocked(mascotApi.setColor).mockResolvedValue({ ...MASCOT, color: '#123abc' })
    renderWithRouter(<HomeScreen />)

    const picker = await screen.findByLabelText(/cor do teyo/i)
    fireEvent.change(picker, { target: { value: '#123abc' } })

    await waitFor(() => expect(mascotApi.setColor).toHaveBeenCalledWith('#123abc'))
  })

  it('shows an empty daily plan when the plan has no items', async () => {
    primeDefaults()
    renderWithRouter(<HomeScreen />)

    expect(await screen.findByText(/nada no plano de hoje/i)).toBeInTheDocument()
  })

  it('lists the daily plan from GET /planner/daily-plan', async () => {
    primeDefaults()
    vi.mocked(plannerApi.dailyPlan).mockResolvedValue({
      date: '2026-01-01',
      items: [
        {
          kind: 'task',
          id: 7,
          title: 'estudar inglês',
          period: 'manhã',
          start_at: null,
          priority: 'high',
          reason: null,
          suggested_due_date: null,
        },
      ],
    })
    renderWithRouter(<HomeScreen />)

    expect(await screen.findByText(/estudar inglês/i)).toBeInTheDocument()
  })

  it('shows an agenda preview of upcoming events', async () => {
    primeDefaults()
    vi.mocked(eventsApi.list).mockResolvedValue([eventFixture])
    renderWithRouter(<HomeScreen />)

    expect(await screen.findByText(/reunião/i)).toBeInTheDocument()
  })
})
