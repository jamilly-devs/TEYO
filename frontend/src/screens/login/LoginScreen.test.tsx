import { render, fireEvent, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import { authApi } from '../../api/auth'
import { ApiError } from '../../api/client'
import { userFixture } from '../../test-fixtures'
import { AuthProvider } from '../../state/AuthContext'
import { LoginScreen } from './LoginScreen'

vi.mock('../../api/auth', () => ({
  authApi: { me: vi.fn(), login: vi.fn(), register: vi.fn(), logout: vi.fn() },
}))

function renderScreen() {
  vi.mocked(authApi.me).mockRejectedValue(new Error('401'))
  return render(
    <MemoryRouter>
      <AuthProvider>
        <LoginScreen />
      </AuthProvider>
    </MemoryRouter>,
  )
}

describe('LoginScreen', () => {
  it('submits email and password to the login endpoint', async () => {
    vi.mocked(authApi.login).mockResolvedValue(userFixture)
    renderScreen()

    fireEvent.change(await screen.findByLabelText(/e-mail/i), {
      target: { value: 'user@example.com' },
    })
    fireEvent.change(screen.getByLabelText(/senha/i), { target: { value: 's3cret!' } })
    fireEvent.click(screen.getByRole('button', { name: /entrar/i }))

    await waitFor(() =>
      expect(authApi.login).toHaveBeenCalledWith({
        email: 'user@example.com',
        password: 's3cret!',
      }),
    )
  })

  it('shows an error message on invalid credentials', async () => {
    vi.mocked(authApi.login).mockRejectedValue(new ApiError(401, 'invalid credentials'))
    renderScreen()

    fireEvent.change(await screen.findByLabelText(/e-mail/i), {
      target: { value: 'user@example.com' },
    })
    fireEvent.change(screen.getByLabelText(/senha/i), { target: { value: 'wrong' } })
    fireEvent.click(screen.getByRole('button', { name: /entrar/i }))

    expect(await screen.findByRole('alert')).toHaveTextContent('invalid credentials')
  })
})
