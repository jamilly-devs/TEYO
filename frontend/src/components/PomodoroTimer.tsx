import { useEffect, useRef, useState } from 'react'
import { ApiError } from '../api/client'
import { pomodoroApi } from '../api/pomodoro'
import type { PomodoroSession } from '../api/types'

// Duração de foco padrão — constante de UI (o backend não fixa duração;
// só registra start/end e valida um mínimo). Sem lib de animação.
const FOCUS_MINUTES = 25

function format(totalSeconds: number): string {
  const mm = String(Math.floor(totalSeconds / 60)).padStart(2, '0')
  const ss = String(totalSeconds % 60).padStart(2, '0')
  return `${mm}:${ss}`
}

export function PomodoroTimer({
  taskId,
  onClose,
}: {
  taskId?: number
  onClose: () => void
}) {
  const [session, setSession] = useState<PomodoroSession | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [nowMs, setNowMs] = useState(() => Date.now())

  // Adota uma sessão já em andamento, se houver (o backend só permite uma).
  useEffect(() => {
    let cancelled = false
    pomodoroApi
      .active()
      .then((s) => {
        if (!cancelled && s) {
          setSession(s)
          setNowMs(Date.now())
        }
      })
      .catch(() => {})
    return () => {
      cancelled = true
    }
  }, [])

  useEffect(() => {
    if (session?.status !== 'active') return
    const id = setInterval(() => setNowMs(Date.now()), 1000)
    return () => clearInterval(id)
  }, [session?.status])

  const remaining = session
    ? Math.max(
        0,
        FOCUS_MINUTES * 60 -
          Math.floor((nowMs - Date.parse(session.started_at)) / 1000),
      )
    : FOCUS_MINUTES * 60

  async function complete() {
    if (!session) return
    try {
      await pomodoroApi.complete(session.id)
      onClose()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Não consegui concluir a sessão.')
    }
  }

  // Ao zerar, conclui automaticamente. `completeRef` guarda a versão mais
  // recente de `complete` sem que ela precise entrar nas deps do efeito.
  const completeRef = useRef(complete)
  useEffect(() => {
    completeRef.current = complete
  })
  useEffect(() => {
    if (session?.status === 'active' && remaining === 0) {
      completeRef.current()
    }
  }, [remaining, session?.status])

  async function start() {
    setError(null)
    try {
      setSession(await pomodoroApi.start(taskId))
      setNowMs(Date.now())
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Não consegui iniciar o Pomodoro.')
    }
  }

  async function pause() {
    if (session) setSession(await pomodoroApi.pause(session.id))
  }

  async function resume() {
    if (session) {
      setSession(await pomodoroApi.resume(session.id))
      setNowMs(Date.now())
    }
  }

  return (
    <div className="pomodoro-timer">
      {!session && (
        <button type="button" onClick={start}>
          Iniciar Pomodoro
        </button>
      )}
      {session && (
        <>
          <span role="timer" aria-label="Tempo restante do Pomodoro">
            {format(remaining)}
          </span>
          {session.status === 'active' && (
            <button type="button" onClick={pause}>
              Pausar
            </button>
          )}
          {session.status === 'paused' && (
            <button type="button" onClick={resume}>
              Retomar
            </button>
          )}
          <button type="button" onClick={complete}>
            Concluir
          </button>
        </>
      )}
      <button type="button" onClick={onClose}>
        Fechar
      </button>
      {error && <p role="alert">{error}</p>}
    </div>
  )
}
