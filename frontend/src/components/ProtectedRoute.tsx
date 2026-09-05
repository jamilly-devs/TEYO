import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../state/AuthContext'
import { LoadingState } from './ScreenStates'

export function ProtectedRoute() {
  const { status } = useAuth()

  if (status === 'loading') {
    return <LoadingState label="Verificando sessão…" />
  }
  if (status === 'unauthenticated') {
    return <Navigate to="/login" replace />
  }
  return <Outlet />
}
