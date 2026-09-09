import { fireEvent, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { ApiError } from '../../api/client'
import { habitsApi } from '../../api/habits'
import type { Habit } from '../../api/types'
import { renderWithRouter } from '../../test-utils'
import { HabitsScreen } from './HabitsScreen'

vi.mock('../../api/habits', () => ({
  habitsApi: { list: vi.fn(), create: vi.fn(), update: vi.fn(), log: vi.fn() },
}))

const habit: Habit = {
  id: 1,
  title: 'ler',
  frequency_target: 3,
  created_at: '2026-01-01T00:00:00',
  streak: 2,
}

describe('HabitsScreen', () => {
  it('shows the empty state when there are no habits', async () => {
    vi.mocked(habitsApi.list).mockResolvedValue([])
    renderWithRouter(<HabitsScreen />)
    expect(await screen.findByText(/nenhum hábito ainda/i)).toBeInTheDocument()
  })

  it('shows the error state when the request fails', async () => {
    vi.mocked(habitsApi.list).mockRejectedValue(new ApiError(500, 'falha no servidor'))
    renderWithRouter(<HabitsScreen />)
    expect(await screen.findByRole('alert')).toHaveTextContent('falha no servidor')
  })

  it('creates a habit with a weekly frequency target', async () => {
    vi.mocked(habitsApi.list).mockResolvedValue([])
    vi.mocked(habitsApi.create).mockResolvedValue(habit)
    renderWithRouter(<HabitsScreen />)

    fireEvent.change(await screen.findByLabelText(/hábito/i), { target: { value: 'ler' } })
    fireEvent.change(screen.getByLabelText(/dias por semana/i), { target: { value: '3' } })
    fireEvent.click(screen.getByRole('button', { name: /criar hábito/i }))

    await waitFor(() =>
      expect(habitsApi.create).toHaveBeenCalledWith({ title: 'ler', frequency_target: 3 }),
    )
  })

  it('shows the individual streak and lets the user log today', async () => {
    vi.mocked(habitsApi.list).mockResolvedValue([habit])
    vi.mocked(habitsApi.log).mockResolvedValue({
      id: 10,
      habit_id: 1,
      completed_at: '2026-01-01T09:00:00',
    })
    renderWithRouter(<HabitsScreen />)

    expect(await screen.findByText(/2 semanas de sequência/i)).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: /registrar hoje/i }))

    await waitFor(() => expect(habitsApi.log).toHaveBeenCalledWith(1))
    // recarrega a lista para refletir o streak atualizado
    await waitFor(() => expect(habitsApi.list).toHaveBeenCalledTimes(2))
  })
})
