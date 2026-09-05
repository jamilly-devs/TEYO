import { useState } from 'react'
import type { FormEvent } from 'react'
import { eventsApi } from '../../api/events'
import { ApiError } from '../../api/client'
import type { Event } from '../../api/types'
import { ConfirmDialog } from '../../components/ConfirmDialog'
import { EmptyState, ErrorState, LoadingState } from '../../components/ScreenStates'
import { useApiResource } from '../../state/useApiResource'

function EventCreateForm({ onCreated }: { onCreated: (event: Event) => void }) {
  const [title, setTitle] = useState('')
  const [startAt, setStartAt] = useState('')
  const [endAt, setEndAt] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      const created = await eventsApi.create({ title, start_at: startAt, end_at: endAt })
      onCreated(created)
      setTitle('')
      setStartAt('')
      setEndAt('')
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Não foi possível criar o compromisso.')
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
        Início
        <input
          type="datetime-local"
          value={startAt}
          onChange={(e) => setStartAt(e.target.value)}
          required
        />
      </label>
      <label>
        Fim
        <input
          type="datetime-local"
          value={endAt}
          onChange={(e) => setEndAt(e.target.value)}
          required
        />
      </label>
      {error && <p role="alert">{error}</p>}
      <button type="submit" disabled={submitting}>
        {submitting ? 'Criando…' : 'Criar compromisso'}
      </button>
    </form>
  )
}

function EventRow({ event, onDeleted }: { event: Event; onDeleted: (id: number) => void }) {
  const [confirmingDelete, setConfirmingDelete] = useState(false)
  const [busy, setBusy] = useState(false)

  async function handleDelete() {
    setBusy(true)
    try {
      await eventsApi.remove(event.id)
      onDeleted(event.id)
    } finally {
      setBusy(false)
      setConfirmingDelete(false)
    }
  }

  return (
    <li className="event-row">
      <span className="event-title">{event.title}</span>
      <span>{event.start_at}</span>
      <span>{event.end_at}</span>
      <button type="button" onClick={() => setConfirmingDelete(true)} disabled={busy}>
        Excluir
      </button>
      {confirmingDelete && (
        <ConfirmDialog
          message={`Excluir o compromisso "${event.title}"?`}
          onConfirm={handleDelete}
          onCancel={() => setConfirmingDelete(false)}
        />
      )}
    </li>
  )
}

export function AgendaScreen() {
  const { status, data, error, reload, setData } = useApiResource(eventsApi.list)

  function handleCreated(event: Event) {
    setData([event, ...(data ?? [])])
  }

  function handleDeleted(id: number) {
    setData((data ?? []).filter((e) => e.id !== id))
  }

  return (
    <section>
      <h1>Agenda</h1>
      <EventCreateForm onCreated={handleCreated} />

      {status === 'loading' && <LoadingState />}
      {status === 'error' && error && <ErrorState message={error} onRetry={reload} />}
      {status === 'success' && data && data.length === 0 && (
        <EmptyState message="Nenhum compromisso ainda. Crie o primeiro acima." />
      )}
      {status === 'success' && data && data.length > 0 && (
        <ul className="event-list">
          {data.map((event) => (
            <EventRow key={event.id} event={event} onDeleted={handleDeleted} />
          ))}
        </ul>
      )}
    </section>
  )
}
