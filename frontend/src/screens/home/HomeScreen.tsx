import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ApiError } from '../../api/client'
import { conversationApi } from '../../api/conversation'
import { eventsApi } from '../../api/events'
import { gamificationApi } from '../../api/gamification'
import { mascotApi } from '../../api/mascot'
import { plannerApi } from '../../api/planner'
import type {
  DailyPlan,
  Event,
  GamificationState,
  MascotState,
} from '../../api/types'
import type { ApiResource } from '../../state/useApiResource'
import { useApiResource } from '../../state/useApiResource'
import { EmptyState, ErrorState, LoadingState } from '../../components/ScreenStates'
import { Mascot } from '../../components/Mascot'

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

function toHex6(color: string): string {
  const short = /^#([0-9a-fA-F])([0-9a-fA-F])([0-9a-fA-F])$/.exec(color)
  if (short) {
    const [, r, g, b] = short
    return `#${r}${r}${g}${g}${b}${b}`
  }
  return /^#[0-9a-fA-F]{6}$/.test(color) ? color : '#7c5cff'
}

function MascotColorPicker({
  current,
  onUpdated,
}: {
  current: string
  onUpdated: (state: MascotState) => void
}) {
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  async function change(color: string) {
    setSaving(true)
    setError(null)
    try {
      onUpdated(await mascotApi.setColor(color))
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Não consegui salvar a cor.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <>
      <label className="mascot-color">
        Cor do TEYO
        <input
          type="color"
          value={toHex6(current)}
          disabled={saving}
          onChange={(e) => change(e.target.value)}
        />
      </label>
      {error && <p role="alert">{error}</p>}
    </>
  )
}

function ProgressContent({
  gamification,
  mascot,
  onMascotUpdated,
}: {
  gamification: GamificationState
  mascot: MascotState
  onMascotUpdated: (state: MascotState) => void
}) {
  const pct =
    gamification.xp_for_next_level > 0
      ? Math.min(100, Math.round((gamification.xp_into_level / gamification.xp_for_next_level) * 100))
      : 0
  const streakLabel = `${gamification.streak_days} ${
    gamification.streak_days === 1 ? 'dia' : 'dias'
  } seguidos`

  return (
    <div className="progress-head">
      <Mascot
        stage={mascot.evolution_stage}
        expression={mascot.current_expression}
        color={mascot.color}
        unlockedFeatures={mascot.unlocked_features}
      />
      <div className="progress-stats">
        <p className="level-line">
          <strong>Nível {gamification.level}</strong>
          <span className="badge">{streakLabel}</span>
        </p>
        <div className="xp-bar" role="progressbar" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100}>
          <span style={{ width: `${pct}%` }} />
        </div>
        <p>
          {gamification.xp_into_level} / {gamification.xp_for_next_level} XP para o nível{' '}
          {gamification.level + 1}
        </p>
        {gamification.achievements.length > 0 && (
          <ul className="achievements">
            {gamification.achievements.map((achievement) => (
              <li key={achievement.code} className="badge" title={achievement.description}>
                {achievement.title}
              </li>
            ))}
          </ul>
        )}
        <MascotColorPicker current={mascot.color} onUpdated={onMascotUpdated} />
      </div>
    </div>
  )
}

function ProgressBlock({
  gamificationResource,
  mascotResource,
}: {
  gamificationResource: ApiResource<GamificationState>
  mascotResource: ApiResource<MascotState>
}) {
  const loading =
    gamificationResource.status === 'loading' || mascotResource.status === 'loading'
  const errorMessage = gamificationResource.error ?? mascotResource.error

  return (
    <section className="home-block progress-block">
      <h2>Progresso</h2>
      {loading && <LoadingState />}
      {!loading && errorMessage && (
        <ErrorState
          message={errorMessage}
          onRetry={() => {
            gamificationResource.reload()
            mascotResource.reload()
          }}
        />
      )}
      {!loading && !errorMessage && gamificationResource.data && mascotResource.data && (
        <ProgressContent
          gamification={gamificationResource.data}
          mascot={mascotResource.data}
          onMascotUpdated={mascotResource.setData}
        />
      )}
    </section>
  )
}

function DailyPlanBlock({ planResource }: { planResource: ApiResource<DailyPlan> }) {
  return (
    <section className="home-block daily-plan-block">
      <h2>Plano do dia</h2>
      {planResource.status === 'loading' && <LoadingState />}
      {planResource.status === 'error' && planResource.error && (
        <ErrorState message={planResource.error} onRetry={planResource.reload} />
      )}
      {planResource.status === 'success' && planResource.data && (
        <DailyPlanList plan={planResource.data} />
      )}
    </section>
  )
}

function DailyPlanList({ plan }: { plan: DailyPlan }) {
  if (plan.items.length === 0) {
    return <EmptyState message="Nada no plano de hoje." />
  }

  return (
    <ul>
      {plan.items.map((item) => (
        <li key={`${item.kind}-${item.id}`}>
          <span className="badge">{item.kind === 'event' ? 'Compromisso' : 'Tarefa'}</span>
          <span>{item.title}</span>
          {item.start_at && <span className="badge">{item.start_at.slice(11, 16)}</span>}
          {!item.start_at && item.period && <span className="badge">{item.period}</span>}
          {item.reason && (
            <span className="badge" title={item.reason}>
              sugestão: adiar
            </span>
          )}
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
  // Hierarquia da Home (NAVIGATION.md / MODULES/HOME.md):
  // 1) conversa  2) progresso (nível + mascote)  3) plano do dia  4) resto.
  const planResource = useApiResource(plannerApi.dailyPlan)
  const eventsResource = useApiResource(eventsApi.list)
  const gamificationResource = useApiResource(gamificationApi.state)
  const mascotResource = useApiResource(mascotApi.state)

  return (
    <div className="home-screen">
      <ConversationBlock />
      <ProgressBlock
        gamificationResource={gamificationResource}
        mascotResource={mascotResource}
      />
      <DailyPlanBlock planResource={planResource} />
      <AgendaPreviewBlock eventsResource={eventsResource} />
      <ModuleShortcuts />
    </div>
  )
}
