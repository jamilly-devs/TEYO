import { fireEvent, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { ApiError } from '../../api/client'
import { financeApi } from '../../api/finance'
import { financialRecordFixture } from '../../test-fixtures'
import { renderWithRouter } from '../../test-utils'
import { FinanceScreen } from './FinanceScreen'

vi.mock('../../api/finance', () => ({
  financeApi: {
    list: vi.fn(),
    create: vi.fn(),
  },
}))

describe('FinanceScreen', () => {
  it('shows the loading state while fetching', () => {
    vi.mocked(financeApi.list).mockReturnValue(new Promise(() => {}))
    renderWithRouter(<FinanceScreen />)
    expect(screen.getByRole('status')).toHaveTextContent(/carregando/i)
  })

  it('shows the empty state when there are no records', async () => {
    vi.mocked(financeApi.list).mockResolvedValue([])
    renderWithRouter(<FinanceScreen />)
    expect(await screen.findByText(/nenhum registro financeiro ainda/i)).toBeInTheDocument()
  })

  it('shows the error state when the request fails', async () => {
    vi.mocked(financeApi.list).mockRejectedValue(new ApiError(500, 'falha no servidor'))
    renderWithRouter(<FinanceScreen />)
    expect(await screen.findByRole('alert')).toHaveTextContent('falha no servidor')
  })

  it('has no edit or delete action, matching the documented endpoints', async () => {
    vi.mocked(financeApi.list).mockResolvedValue([financialRecordFixture])
    renderWithRouter(<FinanceScreen />)
    await screen.findByText('10.00')
    expect(screen.queryByRole('button', { name: /excluir/i })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /editar/i })).not.toBeInTheDocument()
  })

  it('creates a financial record from the form', async () => {
    vi.mocked(financeApi.list).mockResolvedValue([])
    vi.mocked(financeApi.create).mockResolvedValue(financialRecordFixture)
    renderWithRouter(<FinanceScreen />)

    fireEvent.change(await screen.findByLabelText(/valor/i), { target: { value: '10.00' } })
    fireEvent.change(screen.getByLabelText(/^data$/i), { target: { value: '2026-01-01' } })
    fireEvent.click(screen.getByRole('button', { name: /registrar/i }))

    await waitFor(() =>
      expect(financeApi.create).toHaveBeenCalledWith(
        expect.objectContaining({ type: 'expense', amount: '10.00', date: '2026-01-01' }),
      ),
    )
  })
})
