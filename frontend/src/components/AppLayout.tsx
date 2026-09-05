import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../state/AuthContext'

export function AppLayout() {
  const { logout } = useAuth()
  const navigate = useNavigate()

  async function handleLogout() {
    await logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="app-layout">
      <nav>
        <NavLink to="/">Home</NavLink>
        <NavLink to="/conversa">Conversa</NavLink>
        <NavLink to="/tasks">Tarefas</NavLink>
        <NavLink to="/agenda">Agenda</NavLink>
        <NavLink to="/goals">Objetivos</NavLink>
        <NavLink to="/market">Mercado</NavLink>
        <NavLink to="/finance">Finanças</NavLink>
        <button type="button" onClick={handleLogout}>
          Sair
        </button>
      </nav>
      <main>
        <Outlet />
      </main>
    </div>
  )
}
