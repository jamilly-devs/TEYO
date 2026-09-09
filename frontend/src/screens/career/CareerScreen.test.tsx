import { fireEvent, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { ApiError } from '../../api/client'
import { careerApi } from '../../api/career'
import type { JobApplication } from '../../api/types'
import { renderWithRouter } from '../../test-utils'
import { CareerScreen } from './CareerScreen'

vi.mock('../../api/career', () => ({
  careerApi: { list: vi.fn(), create: vi.fn(), update: vi.fn() },
}))

const application: JobApplication = {
  id: 1,
  company: 'Acme',
  role: 'QA Engineer',
  applied_on: null,
  status: 'interested',
  notes: null,
  created_at: '2026-01-01T00:00:00',
  updated_at: '2026-01-01T00:00:00',
}

describe('CareerScreen', () => {
  it('shows the empty state when there are no applications', async () => {
    vi.mocked(careerApi.list).mockResolvedValue([])
    renderWithRouter(<CareerScreen />)
    expect(await screen.findByText(/nenhuma candidatura registrada/i)).toBeInTheDocument()
  })

  it('shows the error state when the request fails', async () => {
    vi.mocked(careerApi.list).mockRejectedValue(new ApiError(500, 'falha no servidor'))
    renderWithRouter(<CareerScreen />)
    expect(await screen.findByRole('alert')).toHaveTextContent('falha no servidor')
  })

  it('creates a manual application', async () => {
    vi.mocked(careerApi.list).mockResolvedValue([])
    vi.mocked(careerApi.create).mockResolvedValue(application)
    renderWithRouter(<CareerScreen />)

    fireEvent.change(await screen.findByLabelText(/empresa/i), { target: { value: 'Acme' } })
    fireEvent.change(screen.getByLabelText(/cargo\/vaga/i), { target: { value: 'QA Engineer' } })
    fireEvent.click(screen.getByRole('button', { name: /registrar candidatura/i }))

    await waitFor(() =>
      expect(careerApi.create).toHaveBeenCalledWith(
        expect.objectContaining({ company: 'Acme', role: 'QA Engineer' }),
      ),
    )
  })

  it('changes an application status through the simple flow selector', async () => {
    vi.mocked(careerApi.list).mockResolvedValue([application])
    vi.mocked(careerApi.update).mockResolvedValue({ ...application, status: 'interviewing' })
    renderWithRouter(<CareerScreen />)

    expect(await screen.findByText(/acme — qa engineer/i)).toBeInTheDocument()
    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'interviewing' } })

    await waitFor(() =>
      expect(careerApi.update).toHaveBeenCalledWith(1, { status: 'interviewing' }),
    )
  })
})
