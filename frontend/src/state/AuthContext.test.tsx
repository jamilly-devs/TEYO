import { screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { authApi } from '../api/auth'
import { userFixture } from '../test-fixtures'
import { renderWithRouter } from '../test-utils'
import { AuthProvider, useAuth } from './AuthContext'

vi.mock('../api/auth', () => ({
  authApi: { me: vi.fn(), login: vi.fn(), register: vi.fn(), logout: vi.fn() },
}))

function Probe() {
  const { status, user } = useAuth()
  return <p>{status}:{user?.email ?? 'none'}</p>
}

describe('AuthProvider', () => {
  it('restores the session from the cookie alone on mount', async () => {
    vi.mocked(authApi.me).mockResolvedValue(userFixture)
    renderWithRouter(
      <AuthProvider>
        <Probe />
      </AuthProvider>,
    )
    expect(await screen.findByText('authenticated:user@example.com')).toBeInTheDocument()
  })

  it('is unauthenticated when there is no valid session', async () => {
    vi.mocked(authApi.me).mockRejectedValue(new Error('401'))
    renderWithRouter(
      <AuthProvider>
        <Probe />
      </AuthProvider>,
    )
    expect(await screen.findByText('unauthenticated:none')).toBeInTheDocument()
  })
})
