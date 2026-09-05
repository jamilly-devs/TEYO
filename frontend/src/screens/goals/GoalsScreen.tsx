import { useState } from 'react'
import type { FormEvent } from 'react'
import { ApiError } from '../../api/client'
import { goalsApi } from '../../api/goals'
import type { Goal, GoalStatus } from '../../api/types'
import { EmptyState, ErrorState, LoadingState } from '../../components/ScreenStates'
import { useApiResource } from '../../state/useApiResource'

function GoalCreateForm({ onCreated }: { onCreated: (goal: Goal) => void }) {
  const [title, setTitle] = useState('')
  const [targetDate, setTargetDate] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      const goal = await goalsApi.create({ title, target_date: targetDate || undefined })
      onCreated(goal)
      setTitle('')
      setTargetDate('')
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Não foi possível criar o objetivo.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="create-form">
      <label>
        Título
        <input value={title} onChange={(e) => setTitle(e.target.value)} required />
      </label>
      <label>
        Data alvo
        <input
          type="date"
          value={targetDate}
          onChange={(e) => setTargetDate(e.target.value)}
        />
      </label>
      {error && <p role="alert">{error}</p>}
      <button type="submit" disabled={submitting}>
        {submitting ? 'Criando…' : 'Criar objetivo'}
      </button>
    </form>
  )
}

function GoalRow({ goal, onChanged }: { goal: Goal; onChanged: (goal: Goal) => void }) {
  async function handleStatusChange(status: GoalStatus) {
    const updated = await goalsApi.update(goal.id, { status })
    onChanged(updated)
  }

  return (
    <li className="goal-row">
      <span className="goal-title">{goal.title}</span>
      <select value={goal.status} onChange={(e) => handleStatusChange(e.target.value as GoalStatus)}>
        <option value="active">Ativo</option>
        <option value="completed">Concluído</option>
        <option value="abandoned">Abandonado</option>
      </select>
      {goal.target_date && <span>{goal.target_date}</span>}
    </li>
  )
}

export function GoalsScreen() {
  const { status, data, error, reload, setData } = useApiResource(goalsApi.list)

  function handleCreated(goal: Goal) {
    setData([goal, ...(data ?? [])])
  }

  function handleChanged(goal: Goal) {
    setData((data ?? []).map((g) => (g.id === goal.id ? goal : g)))
  }

  return (
    <section>
      <h1>Objetivos</h1>
      <GoalCreateForm onCreated={handleCreated} />

      {status === 'loading' && <LoadingState />}
      {status === 'error' && error && <ErrorState message={error} onRetry={reload} />}
      {status === 'success' && data && data.length === 0 && (
        <EmptyState message="Nenhum objetivo ainda. Crie o primeiro acima." />
      )}
      {status === 'success' && data && data.length > 0 && (
        <ul className="goal-list">
          {data.map((goal) => (
            <GoalRow key={goal.id} goal={goal} onChanged={handleChanged} />
          ))}
        </ul>
      )}
    </section>
  )
}
