import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ApiError } from '../../api/client'
import { conversationApi } from '../../api/conversation'
import { eventsApi } from '../../api/events'
import { tasksApi } from '../../api/tasks'
import type { ApiResource } from '../../state/useApiResource'
import { useApiResource } from '../../state/useApiResource'
import type { Event, Task } from '../../api/types'
import { EmptyState, ErrorState, LoadingState } from '../../components/ScreenStates'

function todayDateString(): string {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function isToday(isoDateTime: string): boolean {
  return isoDateTime.slice(0, 10) === todayDateString()
}

function ConversationBlock() {
  const navigate = useNavigate()
  const [draft, setDraft] = useState('')
  const [sending, setSending] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    const text = draft.trim()
    if (!text || sending) return

    setSending(true)
    setError(null)
    try {
      // Não é um chat separado — a mesma conversa principal; ao enviar,
      // abre a tela completa (MODULES/HOME.md).
      await conversationApi.send(text)
      navigate('/conversa')
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Não consegui falar com o TEYO agora.')
      setSending(false)
    }
  }

  return (
    <section className="home-block conversation-block">
      <h2>Conversa com TEYO</h2>
      <form onSubmit={handleSubmit}>
        <input
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder="Fala com o TEYO…"
          disabled={sending}
        />
        <button type="submit" disabled={sending || !draft.trim()}>
          {sending ? 'Enviando…' : 'Enviar'}
        </button>
      </form>
      {error && <p role="alert">{error}</p>}
      <Link to="/conversa">Abrir conversa completa</Link>
    </section>
  )
}

function ProgressBlock() {
  // Os números de progresso vêm do Motor de Padrões / cálculos de sistema
  // (FASE 7+), que ainda não existem — por decisão de Jams, este bloco fica
  // em estado vazio até haver dado real, sem fórmula provisória inventada.
  return (
    <section className="home-block progress-block">
      <h2>Progresso</h2>
      <EmptyState message="Ainda não há dados de progresso disponíveis." />
    </section>
  )
}

function DailyPlanBlock({
  tasksResource,
  eventsResource,
}: {
  tasksResource: ApiResource<Task[]>
  eventsResource: ApiResource<Event[]>
}) {
  const loading = tasksResource.status === 'loading' || eventsResource.status === 'loading'
  const errorMessage = tasksResource.error ?? eventsResource.error

  return (
    <section className="home-block daily-plan-block">
      <h2>Plano do dia</h2>
      {loading && <LoadingState />}
      {!loading && errorMessage && (
        <ErrorState
          message={errorMessage}
          onRetry={() => {
            tasksResource.reload()
            eventsResource.reload()
          }}
        />
      )}
      {!loading && !errorMessage && (
        <DailyPlanList tasks={tasksResource.data ?? []} events={eventsResource.data ?? []} />
      )}
    </section>
  )
}

function DailyPlanList({ tasks, events }: { tasks: Task[]; events: Event[] }) {
  const todaysTasks = tasks.filter((task) => task.due_date && isToday(task.due_date))
  const todaysEvents = events.filter((event) => isToday(event.start_at))

  if (todaysTasks.length === 0 && todaysEvents.length === 0) {
    return <EmptyState message="Nada agendado para hoje." />
  }

  return (
    <ul>
      {todaysTasks.map((task) => (
        <li key={`task-${task.id}`}>Tarefa: {task.title}</li>
      ))}
      {todaysEvents.map((event) => (
        <li key={`event-${event.id}`}>
          Compromisso: {event.title} ({event.start_at})
        </li>
      ))}
    </ul>
  )
}

function AgendaPreviewBlock({ eventsResource }: { eventsResource: ApiResource<Event[]> }) {
  return (
    <section className="home-block agenda-preview-block">
      <h2>Agenda</h2>
      {eventsResource.status === 'loading' && <LoadingState />}
      {eventsResource.status === 'error' && eventsResource.error && (
        <ErrorState message={eventsResource.error} onRetry={eventsResource.reload} />
      )}
      {eventsResource.status === 'success' && (
        <AgendaPreviewList events={eventsResource.data ?? []} />
      )}
    </section>
  )
}

function AgendaPreviewList({ events }: { events: Event[] }) {
  const upcoming = [...events].sort((a, b) => a.start_at.localeCompare(b.start_at)).slice(0, 5)

  if (upcoming.length === 0) {
    return <EmptyState message="Nenhum compromisso cadastrado." />
  }

  return (
    <ul>
      {upcoming.map((event) => (
        <li key={event.id}>
          {event.title} — {event.start_at}
        </li>
      ))}
    </ul>
  )
}

function ModuleShortcuts() {
  return (
    <section className="home-block module-shortcuts">
      <h2>Módulos</h2>
      <nav>
        <Link to="/tasks">Tarefas</Link>
        <Link to="/agenda">Agenda</Link>
        <Link to="/goals">Objetivos</Link>
        <Link to="/market">Mercado</Link>
        <Link to="/finance">Finanças</Link>
      </nav>
    </section>
  )
}

export function HomeScreen() {
  const tasksResource = useApiResource(tasksApi.list)
  const eventsResource = useApiResource(eventsApi.list)

  return (
    <div className="home-screen">
      <ConversationBlock />
      <ProgressBlock />
      <DailyPlanBlock tasksResource={tasksResource} eventsResource={eventsResource} />
      <AgendaPreviewBlock eventsResource={eventsResource} />
      <ModuleShortcuts />
    </div>
  )
}
