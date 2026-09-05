import { fireEvent, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { eventsApi } from '../../api/events'
import { ApiError } from '../../api/client'
import { eventFixture } from '../../test-fixtures'
import { renderWithRouter } from '../../test-utils'
import { AgendaScreen } from './AgendaScreen'

vi.mock('../../api/events', () => ({
  eventsApi: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    remove: vi.fn(),
  },
}))

describe('AgendaScreen', () => {
  it('shows the loading state while fetching', () => {
    vi.mocked(eventsApi.list).mockReturnValue(new Promise(() => {}))
    renderWithRouter(<AgendaScreen />)
    expect(screen.getByRole('status')).toHaveTextContent(/carregando/i)
  })

  it('shows the empty state when there are no events', async () => {
    vi.mocked(eventsApi.list).mockResolvedValue([])
    renderWithRouter(<AgendaScreen />)
    expect(await screen.findByText(/nenhum compromisso ainda/i)).toBeInTheDocument()
  })

  it('shows the error state when the request fails', async () => {
    vi.mocked(eventsApi.list).mockRejectedValue(new ApiError(500, 'falha no servidor'))
    renderWithRouter(<AgendaScreen />)
    expect(await screen.findByRole('alert')).toHaveTextContent('falha no servidor')
  })

  it('requires confirmation before deleting an event', async () => {
    vi.mocked(eventsApi.list).mockResolvedValue([eventFixture])
    vi.mocked(eventsApi.remove).mockResolvedValue(undefined)
    renderWithRouter(<AgendaScreen />)

    fireEvent.click(await screen.findByRole('button', { name: /excluir/i }))
    expect(screen.getByRole('dialog')).toBeInTheDocument()
    expect(eventsApi.remove).not.toHaveBeenCalled()

    fireEvent.click(screen.getByRole('button', { name: /confirmar/i }))
    await waitFor(() => expect(eventsApi.remove).toHaveBeenCalledWith(1))
  })
})
