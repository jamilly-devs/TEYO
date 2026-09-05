import { fireEvent, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { ApiError } from '../../api/client'
import { goalsApi } from '../../api/goals'
import { goalFixture } from '../../test-fixtures'
import { renderWithRouter } from '../../test-utils'
import { GoalsScreen } from './GoalsScreen'

vi.mock('../../api/goals', () => ({
  goalsApi: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
  },
}))

describe('GoalsScreen', () => {
  it('shows the loading state while fetching', () => {
    vi.mocked(goalsApi.list).mockReturnValue(new Promise(() => {}))
    renderWithRouter(<GoalsScreen />)
    expect(screen.getByRole('status')).toHaveTextContent(/carregando/i)
  })

  it('shows the empty state when there are no goals', async () => {
    vi.mocked(goalsApi.list).mockResolvedValue([])
    renderWithRouter(<GoalsScreen />)
    expect(await screen.findByText(/nenhum objetivo ainda/i)).toBeInTheDocument()
  })

  it('shows the error state when the request fails', async () => {
    vi.mocked(goalsApi.list).mockRejectedValue(new ApiError(500, 'falha no servidor'))
    renderWithRouter(<GoalsScreen />)
    expect(await screen.findByRole('alert')).toHaveTextContent('falha no servidor')
  })

  it('has no delete action, only a status selector', async () => {
    vi.mocked(goalsApi.list).mockResolvedValue([goalFixture])
    vi.mocked(goalsApi.update).mockResolvedValue({ ...goalFixture, status: 'completed' })
    renderWithRouter(<GoalsScreen />)

    expect(await screen.findByText('aprender inglês')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /excluir/i })).not.toBeInTheDocument()

    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'completed' } })
    await waitFor(() =>
      expect(goalsApi.update).toHaveBeenCalledWith(1, { status: 'completed' }),
    )
  })
})
