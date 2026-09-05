import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import { authApi } from '../api/auth'
import { userFixture } from '../test-fixtures'
import { AuthProvider } from '../state/AuthContext'
import { ProtectedRoute } from './ProtectedRoute'

vi.mock('../api/auth', () => ({
  authApi: { me: vi.fn(), login: vi.fn(), register: vi.fn(), logout: vi.fn() },
}))

function renderApp() {
  return render(
    <MemoryRouter initialEntries={['/']}>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<p>tela de login</p>} />
          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<p>conteúdo protegido</p>} />
          </Route>
        </Routes>
      </AuthProvider>
    </MemoryRouter>,
  )
}

describe('ProtectedRoute', () => {
  it('redirects to /login when there is no session', async () => {
    vi.mocked(authApi.me).mockRejectedValue(new Error('401'))
    renderApp()
    expect(await screen.findByText('tela de login')).toBeInTheDocument()
  })

  it('renders the protected content when authenticated', async () => {
    vi.mocked(authApi.me).mockResolvedValue(userFixture)
    renderApp()
    expect(await screen.findByText('conteúdo protegido')).toBeInTheDocument()
  })
})
