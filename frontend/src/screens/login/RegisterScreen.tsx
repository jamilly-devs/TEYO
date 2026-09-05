import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ApiError } from '../../api/client'
import { useAuth } from '../../state/AuthContext'

export function RegisterScreen() {
  const { register, login } = useAuth()
  const navigate = useNavigate()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      await register(email, password, name || undefined)
      await login(email, password)
      navigate('/', { replace: true })
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Não foi possível criar a conta.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="auth-screen">
      <h1>Criar conta no TEYO</h1>
      <form onSubmit={handleSubmit}>
        <label>
          Nome (opcional)
          <input type="text" value={name} onChange={(e) => setName(e.target.value)} />
        </label>
        <label>
          E-mail
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </label>
        <label>
          Senha
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </label>
        {error && <p role="alert">{error}</p>}
        <button type="submit" disabled={submitting}>
          {submitting ? 'Criando…' : 'Criar conta'}
        </button>
      </form>
      <p>
        Já tem conta? <Link to="/login">Entrar</Link>
      </p>
    </div>
  )
}
