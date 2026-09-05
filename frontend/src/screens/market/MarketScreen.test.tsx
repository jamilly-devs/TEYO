import { fireEvent, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { ApiError } from '../../api/client'
import { marketApi } from '../../api/market'
import { marketItemFixture } from '../../test-fixtures'
import { renderWithRouter } from '../../test-utils'
import { MarketScreen } from './MarketScreen'

vi.mock('../../api/market', () => ({
  marketApi: {
    list: vi.fn(),
    create: vi.fn(),
    updateStatus: vi.fn(),
    remove: vi.fn(),
  },
}))

describe('MarketScreen', () => {
  it('shows the loading state while fetching', () => {
    vi.mocked(marketApi.list).mockReturnValue(new Promise(() => {}))
    renderWithRouter(<MarketScreen />)
    expect(screen.getByRole('status')).toHaveTextContent(/carregando/i)
  })

  it('shows the empty state when the list is empty', async () => {
    vi.mocked(marketApi.list).mockResolvedValue([])
    renderWithRouter(<MarketScreen />)
    expect(await screen.findByText(/lista de mercado vazia/i)).toBeInTheDocument()
  })

  it('shows the error state when the request fails', async () => {
    vi.mocked(marketApi.list).mockRejectedValue(new ApiError(500, 'falha no servidor'))
    renderWithRouter(<MarketScreen />)
    expect(await screen.findByRole('alert')).toHaveTextContent('falha no servidor')
  })

  it('marking as purchased does not remove the item from the list', async () => {
    vi.mocked(marketApi.list).mockResolvedValue([marketItemFixture])
    vi.mocked(marketApi.updateStatus).mockResolvedValue({
      ...marketItemFixture,
      status: 'purchased',
    })
    renderWithRouter(<MarketScreen />)

    fireEvent.click(await screen.findByRole('button', { name: /marcar como comprado/i }))
    await waitFor(() => expect(marketApi.updateStatus).toHaveBeenCalledWith(1, 'purchased'))
    expect(marketApi.remove).not.toHaveBeenCalled()
    expect(screen.getByText('arroz')).toBeInTheDocument()
  })

  it('deleting requires confirmation and removes the row for good', async () => {
    vi.mocked(marketApi.list).mockResolvedValue([marketItemFixture])
    vi.mocked(marketApi.remove).mockResolvedValue(undefined)
    renderWithRouter(<MarketScreen />)

    fireEvent.click(await screen.findByRole('button', { name: /^excluir$/i }))
    expect(screen.getByRole('dialog')).toBeInTheDocument()
    expect(marketApi.remove).not.toHaveBeenCalled()

    fireEvent.click(screen.getByRole('button', { name: /confirmar/i }))
    await waitFor(() => expect(marketApi.remove).toHaveBeenCalledWith(1))
  })
})
