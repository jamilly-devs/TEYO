import { useState } from 'react'
import type { FormEvent } from 'react'
import { ApiError } from '../../api/client'
import { habitsApi } from '../../api/habits'
import type { Habit } from '../../api/types'
import { EmptyState, ErrorState, LoadingState } from '../../components/ScreenStates'
import { useApiResource } from '../../state/useApiResource'

function HabitCreateForm({ onCreated }: { onCreated: (habit: Habit) => void }) {
  const [title, setTitle] = useState('')
  const [frequencyTarget, setFrequencyTarget] = useState(3)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      const habit = await habitsApi.create({ title, frequency_target: frequencyTarget })
      onCreated(habit)
      setTitle('')
      setFrequencyTarget(3)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Não foi possível criar o hábito.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="create-form">
      <label>
        Hábito
        <input value={title} onChange={(e) => setTitle(e.target.value)} required />
      </label>
      <label>
        Dias por semana
        <select
          value={frequencyTarget}
          onChange={(e) => setFrequencyTarget(Number(e.target.value))}
        >
          {[1, 2, 3, 4, 5, 6, 7].map((n) => (
            <option key={n} value={n}>
              {n}
            </option>
          ))}
        </select>
      </label>
      {error && <p role="alert">{error}</p>}
      <button type="submit" disabled={submitting}>
        {submitting ? 'Criando…' : 'Criar hábito'}
      </button>
    </form>
  )
}

function HabitRow({ habit, onLogged }: { habit: Habit; onLogged: () => void }) {
  const [logging, setLogging] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleLog() {
    setLogging(true)
    setError(null)
    try {
      await habitsApi.log(habit.id)
      onLogged()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Não foi possível registrar.')
    } finally {
      setLogging(false)
    }
  }

  return (
    <li className="habit-row">
      <span className="habit-title">{habit.title}</span>
      <span className="badge">{habit.frequency_target}/semana</span>
      <span className="badge habit-streak">
        {habit.streak} {habit.streak === 1 ? 'semana' : 'semanas'} de sequência
      </span>
      <button type="button" onClick={handleLog} disabled={logging}>
        {logging ? 'Registrando…' : 'Registrar hoje'}
      </button>
      {error && <p role="alert">{error}</p>}
    </li>
  )
}

export function HabitsScreen() {
  const { status, data, error, reload, setData } = useApiResource(habitsApi.list)

  return (
    <section>
      <h1>Hábitos</h1>
      <HabitCreateForm onCreated={(habit) => setData([habit, ...(data ?? [])])} />

      {status === 'loading' && <LoadingState />}
      {status === 'error' && error && <ErrorState message={error} onRetry={reload} />}
      {status === 'success' && data && data.length === 0 && (
        <EmptyState message="Nenhum hábito ainda. Crie o primeiro acima." />
      )}
      {status === 'success' && data && data.length > 0 && (
        <ul className="habit-list">
          {data.map((habit) => (
            <HabitRow key={habit.id} habit={habit} onLogged={reload} />
          ))}
        </ul>
      )}
    </section>
  )
}
