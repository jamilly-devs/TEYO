import { render, fireEvent, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import { authApi } from '../../api/auth'
import { ApiError } from '../../api/client'
import { userFixture } from '../../test-fixtures'
import { AuthProvider } from '../../state/AuthContext'
import { RegisterScreen } from './RegisterScreen'

vi.mock('../../api/auth', () => ({
  authApi: { me: vi.fn(), login: vi.fn(), register: vi.fn(), logout: vi.fn() },
}))

function renderScreen() {
  vi.mocked(authApi.me).mockRejectedValue(new Error('401'))
  return render(
    <MemoryRouter>
      <AuthProvider>
        <RegisterScreen />
      </AuthProvider>
    </MemoryRouter>,
  )
}

describe('RegisterScreen', () => {
  it('registers and then logs in with the same credentials', async () => {
    vi.mocked(authApi.register).mockResolvedValue(userFixture)
    vi.mocked(authApi.login).mockResolvedValue(userFixture)
    renderScreen()

    fireEvent.change(await screen.findByLabelText(/e-mail/i), {
      target: { value: 'user@example.com' },
    })
    fireEvent.change(screen.getByLabelText(/senha/i), { target: { value: 's3cret!' } })
    fireEvent.click(screen.getByRole('button', { name: /criar conta/i }))

    await waitFor(() =>
      expect(authApi.register).toHaveBeenCalledWith({
        email: 'user@example.com',
        password: 's3cret!',
        name: undefined,
      }),
    )
    await waitFor(() =>
      expect(authApi.login).toHaveBeenCalledWith({
        email: 'user@example.com',
        password: 's3cret!',
      }),
    )
  })

  it('shows an error message when the email is already registered', async () => {
    vi.mocked(authApi.register).mockRejectedValue(new ApiError(409, 'email already registered'))
    renderScreen()

    fireEvent.change(await screen.findByLabelText(/e-mail/i), {
      target: { value: 'user@example.com' },
    })
    fireEvent.change(screen.getByLabelText(/senha/i), { target: { value: 's3cret!' } })
    fireEvent.click(screen.getByRole('button', { name: /criar conta/i }))

    expect(await screen.findByRole('alert')).toHaveTextContent('email already registered')
  })
})
